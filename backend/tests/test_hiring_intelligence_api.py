"""Endpoint-level tests for the no-side-effect hiring dry-run."""
import asyncio
import unittest
from datetime import date

from app.api.hiring_intelligence import dry_run_hiring_intelligence
from app.schemas.hiring_intelligence import HiringDryRunRequest


class HiringDryRunTests(unittest.TestCase):
    def request(self):
        return HiringDryRunRequest(
            as_of_date=date(2026, 10, 15),
            candidates=[
                {
                    "company_name": "Example AI",
                    "company_website": "https://example.ai",
                    "role_title": "Backend Engineer",
                    "job_url": "https://example.ai/careers/backend?utm_source=test",
                    "role_location": "Bengaluru, India",
                    "source_type": "official_careers",
                    "evidence_verified_on": "2026-10-14",
                    "direct_job_listing": True,
                    "technical_fit": 0.9,
                    "contact_relevance": 0.7,
                },
                {
                    "company_name": "Example AI",
                    "company_website": "https://example.ai",
                    "role_title": "Backend Engineer (duplicate)",
                    "job_url": "https://www.example.ai/careers/backend",
                    "role_location": "Bengaluru, India",
                    "source_type": "official_careers",
                    "evidence_verified_on": "2026-10-14",
                    "direct_job_listing": True,
                    "technical_fit": 0.9,
                    "contact_relevance": 0.7,
                },
            ],
        )

    def test_dry_run_does_not_persist_and_flags_duplicate(self):
        response = asyncio.run(dry_run_hiring_intelligence(self.request()))
        self.assertFalse(response.persisted)
        self.assertEqual(response.candidates_seen, 2)
        self.assertEqual(response.candidates_qualified, 1)
        self.assertTrue(response.results[0].qualifies)
        self.assertFalse(response.results[1].qualifies)
        self.assertIn("duplicate_job_url_in_request", response.results[1].reasons)
        self.assertEqual(response.results[0].job_url, "https://example.ai/careers/backend")


if __name__ == "__main__":
    unittest.main()
