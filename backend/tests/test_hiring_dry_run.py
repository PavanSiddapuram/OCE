import unittest
from datetime import date

from app.schemas.hiring_intelligence import HiringDryRunRequest
from app.api.hiring_intelligence import dry_run_hiring_intelligence


class HiringDryRunTests(unittest.IsolatedAsyncioTestCase):
    async def test_dry_run_does_not_persist_and_rejects_duplicate(self):
        request = HiringDryRunRequest.model_validate({
            "as_of_date": "2026-10-15",
            "candidates": [
                {
                    "company_name": "Example",
                    "company_website": "https://example.com",
                    "role_title": "Backend Engineer",
                    "job_url": "https://example.com/careers/backend?utm_source=test",
                    "role_location": "Bengaluru, India",
                    "source_type": "official_careers",
                    "evidence_verified_on": "2026-10-15",
                    "direct_job_listing": True,
                    "technical_fit": 0.9,
                    "contact_relevance": 0.8
                },
                {
                    "company_name": "Example",
                    "company_website": "https://example.com",
                    "role_title": "Backend Engineer",
                    "job_url": "https://www.example.com/careers/backend",
                    "role_location": "Bengaluru, India",
                    "source_type": "official_careers",
                    "evidence_verified_on": "2026-10-15",
                    "direct_job_listing": True,
                    "technical_fit": 0.9,
                    "contact_relevance": 0.8
                }
            ]
        })
        response = await dry_run_hiring_intelligence(request)
        self.assertEqual(response.persisted, False)
        self.assertEqual(response.candidates_seen, 2)
        self.assertEqual(response.candidates_qualified, 1)
        self.assertIn("duplicate_job_url_in_request", response.results[1].reasons)

    async def test_dry_run_rejects_funding_only(self):
        request = HiringDryRunRequest.model_validate({
            "as_of_date": "2026-10-15",
            "candidates": [{
                "company_name": "Example",
                "role_title": "Backend Engineer",
                "job_url": "https://example.com/careers",
                "role_location": "Bengaluru",
                "source_type": "company_blog",
                "evidence_verified_on": "2026-10-15",
                "direct_job_listing": False,
                "expansion_signal": True
            }]
        })
        response = await dry_run_hiring_intelligence(request)
        self.assertEqual(response.candidates_qualified, 0)
        self.assertIn("no_direct_hiring_evidence", response.results[0].reasons)
