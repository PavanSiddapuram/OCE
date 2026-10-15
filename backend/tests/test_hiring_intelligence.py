"""Unit tests for deterministic hiring-intelligence gates (stdlib unittest)."""
import unittest
from datetime import date, timedelta

from app.services.hiring_intelligence import (
    HiringEvidence,
    canonical_domain,
    canonical_url,
    evaluate_hiring_evidence,
    score_prospect,
)


class CanonicalizationTests(unittest.TestCase):
    def test_strips_tracking_and_normalizes_host(self):
        self.assertEqual(
            canonical_url("http://www.Example.com/careers/?utm_source=linkedin&ref=abc"),
            "https://example.com/careers",
        )

    def test_keeps_meaningful_query_parameters(self):
        self.assertEqual(
            canonical_url("https://example.com/jobs?id=42&utm_medium=email"),
            "https://example.com/jobs?id=42",
        )

    def test_domain_is_normalized(self):
        self.assertEqual(canonical_domain("https://www.example.com/jobs"), "example.com")


class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 10, 15)

    def evidence(self, **overrides):
        values = dict(
            source_url="https://company.example/careers/engineer",
            source_type="official_careers",
            verified_on=self.today,
            direct_job_listing=True,
            expansion_signal=False,
            role_location="Bengaluru, India",
            role_title="Backend Engineer",
        )
        values.update(overrides)
        return HiringEvidence(**values)

    def test_current_direct_bengaluru_role_qualifies(self):
        result = evaluate_hiring_evidence(self.evidence(), today=self.today)
        self.assertTrue(result.qualifies)
        self.assertEqual(result.hiring_score, 0.85)
        self.assertEqual(result.reasons, ())

    def test_funding_or_expansion_alone_does_not_qualify(self):
        result = evaluate_hiring_evidence(
            self.evidence(direct_job_listing=False, expansion_signal=True),
            today=self.today,
        )
        self.assertFalse(result.qualifies)
        self.assertIn("no_direct_hiring_evidence", result.reasons)
        self.assertEqual(result.hiring_score, 0.45)

    def test_stale_evidence_is_rejected(self):
        result = evaluate_hiring_evidence(
            self.evidence(verified_on=self.today - timedelta(days=46)),
            today=self.today,
        )
        self.assertFalse(result.qualifies)
        self.assertIn("evidence_stale", result.reasons)

    def test_incompatible_location_is_rejected(self):
        result = evaluate_hiring_evidence(
            self.evidence(role_location="US only; onsite"),
            today=self.today,
        )
        self.assertFalse(result.qualifies)
        self.assertIn("location_not_verified_for_target", result.reasons)

    def test_weighted_score_and_freshness(self):
        total, parts = score_prospect(
            technical_fit=1.0,
            hiring_score=0.85,
            contact_relevance=0.9,
            evidence_age_days=2,
        )
        self.assertEqual(parts["freshness"], 1.0)
        self.assertEqual(total, round(0.35 + 0.85 * 0.30 + 0.9 * 0.20 + 0.15, 4))


if __name__ == "__main__":
    unittest.main()
