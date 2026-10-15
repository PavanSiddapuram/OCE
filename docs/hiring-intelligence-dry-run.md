# Hiring Intelligence Persistence and Dry Run

## Migration

After reviewing the migration and checking your database backup/target, apply from `backend/`:

```bash
alembic upgrade head
```

This adds `hiring_runs` (one run per local calendar date) and `hiring_prospects` (unique canonical job URL). It does not alter the existing eight-agent pipeline.

## Dry-run endpoint

`POST /api/hiring-intelligence/dry-run`

- Accepts 1–100 candidate records with role URL, source type, location, verification date, and fit inputs.
- Applies deterministic freshness, location, direct-job-listing, deduplication, and scoring rules.
- Returns `persisted: false`; does not call an LLM, database, Google Sheets, or email provider.
- This is an evaluation endpoint, not a live discovery endpoint. Feed it only evidence collected from sources you have actually checked.

Example request:

```json
{
  "as_of_date": "2026-10-15",
  "target_location": "Bengaluru",
  "max_evidence_age_days": 45,
  "candidates": [{
    "company_name": "Example",
    "company_website": "https://example.com",
    "role_title": "Backend Engineer",
    "job_url": "https://example.com/careers/backend",
    "role_location": "Bengaluru, India",
    "source_type": "official_careers",
    "evidence_verified_on": "2026-10-15",
    "direct_job_listing": true,
    "technical_fit": 0.9,
    "contact_relevance": 0.8
  }]
}
```

## Scope and safety

No automated email sending, Google Sheets writes, Gemini calls, or scheduler are included. Do not treat a successful dry run as proof that a job is still open; verify the source page before outreach.
