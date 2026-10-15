"""Deterministic evidence gates for OCE's hiring-intelligence workflow.

This module intentionally does not call an LLM. Models may summarize evidence, but
qualification and score calculation must remain deterministic and testable.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


_TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "gh_src",
    "ref",
    "source",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def canonical_url(raw_url: str) -> str:
    """Normalize a URL for identity/deduplication without changing its path meaning."""
    raw_url = (raw_url or "").strip()
    if not raw_url:
        return ""

    parsed = urlparse(raw_url if "://" in raw_url else f"https://{raw_url}")
    scheme = "https" if parsed.scheme in {"", "http", "https"} else parsed.scheme
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if not host:
        return ""

    # Preserve non-default ports; discard default HTTP(S) ports.
    port = parsed.port
    netloc = host
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{host}:{port}"

    path = "/" + "/".join(part for part in parsed.path.split("/") if part)
    if path == "/":
        path = ""
    query = urlencode(
        sorted(
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key.lower() not in _TRACKING_PARAMS
        )
    )
    return urlunparse((scheme, netloc, path, "", query, ""))


def canonical_domain(raw_url: str) -> str:
    """Return normalized host identity; this intentionally does not infer registrable domains."""
    normalized = canonical_url(raw_url)
    return urlparse(normalized).hostname or ""


@dataclass(frozen=True)
class HiringEvidence:
    source_url: str
    source_type: str
    verified_on: date
    direct_job_listing: bool
    expansion_signal: bool = False
    role_location: str = ""
    role_title: str = ""


@dataclass(frozen=True)
class Qualification:
    qualifies: bool
    reasons: tuple[str, ...]
    evidence_age_days: int
    hiring_score: float


def evaluate_hiring_evidence(
    evidence: HiringEvidence,
    *,
    today: date,
    target_location: str = "Bengaluru",
    max_age_days: int = 45,
) -> Qualification:
    """Apply hard evidence gates; funding/expansion alone never proves an open role."""
    reasons: list[str] = []
    age = (today - evidence.verified_on).days

    if not evidence.source_url.startswith(("https://", "http://")):
        reasons.append("missing_valid_source_url")
    if age < 0:
        reasons.append("verification_date_in_future")
    elif age > max_age_days:
        reasons.append("evidence_stale")
    if not evidence.direct_job_listing:
        reasons.append("no_direct_hiring_evidence")

    location = evidence.role_location.casefold()
    target = target_location.casefold()
    if not location or not any(
        marker in location
        for marker in (target, "remote", "hybrid", "work from anywhere")
    ):
        reasons.append("location_not_verified_for_target")

    if evidence.direct_job_listing and evidence.expansion_signal:
        hiring_score = 1.0
    elif evidence.direct_job_listing:
        hiring_score = 0.85
    elif evidence.expansion_signal:
        hiring_score = 0.45
    else:
        hiring_score = 0.0

    return Qualification(
        qualifies=not reasons,
        reasons=tuple(reasons),
        evidence_age_days=age,
        hiring_score=hiring_score,
    )


def score_prospect(
    *,
    technical_fit: float,
    hiring_score: float,
    contact_relevance: float,
    evidence_age_days: int,
) -> tuple[float, dict[str, float]]:
    """Return a 0..1 weighted score using the configured 35/30/20/15 rubric."""
    def bounded(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    if evidence_age_days < 0:
        freshness = 0.0
    elif evidence_age_days <= 7:
        freshness = 1.0
    elif evidence_age_days <= 21:
        freshness = 0.75
    elif evidence_age_days <= 45:
        freshness = 0.40
    else:
        freshness = 0.0

    breakdown = {
        "technical_fit": bounded(technical_fit),
        "hiring_evidence": bounded(hiring_score),
        "contact_relevance": bounded(contact_relevance),
        "freshness": freshness,
    }
    total = round(
        breakdown["technical_fit"] * 0.35
        + breakdown["hiring_evidence"] * 0.30
        + breakdown["contact_relevance"] * 0.20
        + breakdown["freshness"] * 0.15,
        4,
    )
    breakdown["total"] = total
    return total, breakdown
