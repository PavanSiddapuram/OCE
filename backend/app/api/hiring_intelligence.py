"""Safe, deterministic hiring-intelligence evaluation endpoints."""
from datetime import date
from urllib.parse import urlparse

from fastapi import APIRouter
from pydantic import HttpUrl

from app.schemas.hiring_intelligence import (
    HiringDryRunItem,
    HiringDryRunRequest,
    HiringDryRunResponse,
)
from app.services.hiring_intelligence import (
    HiringEvidence,
    canonical_domain,
    canonical_url,
    evaluate_hiring_evidence,
    score_prospect,
)

router = APIRouter(prefix="/hiring-intelligence", tags=["hiring-intelligence"])


@router.post("/dry-run", response_model=HiringDryRunResponse)
async def dry_run_hiring_intelligence(payload: HiringDryRunRequest) -> HiringDryRunResponse:
    """Evaluate supplied, source-backed candidates without database or external side effects."""
    as_of_date = payload.as_of_date or date.today()
    results: list[HiringDryRunItem] = []
    seen_urls: set[str] = set()

    for candidate in payload.candidates:
        normalized_job_url = canonical_url(str(candidate.job_url))
        evidence = HiringEvidence(
            source_url=normalized_job_url,
            source_type=candidate.source_type,
            verified_on=candidate.evidence_verified_on,
            direct_job_listing=candidate.direct_job_listing,
            expansion_signal=candidate.expansion_signal,
            role_location=candidate.role_location,
            role_title=candidate.role_title,
        )
        qualification = evaluate_hiring_evidence(
            evidence,
            today=as_of_date,
            target_location=payload.target_location,
            max_age_days=payload.max_evidence_age_days,
        )
        reasons = list(qualification.reasons)
        if normalized_job_url in seen_urls:
            reasons.append("duplicate_job_url_in_request")
        seen_urls.add(normalized_job_url)

        total_score, breakdown = score_prospect(
            technical_fit=candidate.technical_fit,
            hiring_score=qualification.hiring_score,
            contact_relevance=candidate.contact_relevance,
            evidence_age_days=qualification.evidence_age_days,
        )
        qualifies = qualification.qualifies and "duplicate_job_url_in_request" not in reasons
        results.append(
            HiringDryRunItem(
                company_name=candidate.company_name,
                role_title=candidate.role_title,
                job_url=normalized_job_url,
                qualifies=qualifies,
                reasons=reasons,
                evidence_age_days=qualification.evidence_age_days,
                hiring_score=qualification.hiring_score,
                total_score=total_score,
                score_breakdown=breakdown,
            )
        )

    return HiringDryRunResponse(
        candidates_seen=len(results),
        candidates_qualified=sum(item.qualifies for item in results),
        results=results,
    )
