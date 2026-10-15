# Daily Hiring Intelligence: Repository Audit and Implementation Plan

## Repository baseline

Audited the `master` tree on 2026-10-15. OCE currently contains:

- FastAPI API and SQLAlchemy async database layer.
- PostgreSQL models and three Alembic migrations.
- Redis/ARQ workers that execute the existing eight-agent startup research pipeline.
- Tavily, Firecrawl, and Jina integrations.
- Company, founder, opportunity, research, contact, outreach, and pipeline-run models.
- A Next.js CRM and a structured master resume in `backend/data/resume/`.
- DeepSeek configured as the current LLM provider in `backend/app/config.py` and `.env.example`.

## Confirmed gaps relative to Daily Hiring Intelligence

1. Agent 1 discovers startups from investor/portfolio searches; it does not require a current engineering job listing or other explicit hiring evidence.
2. Existing domain deduplication is an in-memory pre-check, not a database uniqueness guarantee. Concurrent runs can still race.
3. Existing outreach is generated from company/founder research and stored as channel/body records. There is no durable email approval/send lifecycle or provider message reconciliation.
4. The ARQ worker has retry and supervisor logic for the existing pipeline, but no daily hiring-intelligence run keyed by the Asia/Kolkata local date.
5. Current configuration contains DeepSeek, Tavily, and Firecrawl settings only. Gemini, Google Sheets, and Gmail integrations are not configured in the checked-in baseline.
6. The repository has Alembic migrations, but a live database migration state and production credentials cannot be verified from a repository-only audit.
7. No claim is made here that an integration or test suite has run successfully; this audit was based on source inspection.

## Design decisions

- Preserve the existing eight-agent workflow. Add a separate hiring-first workflow instead of repurposing its current discovery assumptions.
- PostgreSQL is authoritative. Sheets is a reconciled operator view, not a second source of truth.
- Require explicit, current evidence before a prospect qualifies. Funding alone is not active-hiring evidence.
- Keep email sending disabled by default. The first production trial is draft-only and approval-gated.
- Treat model output as untrusted until deterministic validation checks pass.
- Do not invent the requested model identifier. Verify it against the configured Google API; require an explicit configured alternative if unavailable.
- Prefer official career pages and company-owned sources; retain source URLs and verification timestamps.
- Return fewer than five prospects when fewer than five pass the gates.

## Incremental implementation order

1. **Evidence and qualification core** — deterministic URL normalization, evidence freshness/location gates, weighted score calculation, and unit tests.
2. **Persistence** — hiring prospect and daily-run models, migrations, uniqueness constraints, and atomic daily-run claiming.
3. **Discovery adapters** — use current search/scrape integrations to collect source-backed role evidence and reject stale or unsupported claims.
4. **Contact verification and grounded drafts** — evidence bundle, candidate-profile grounding, explicit Gemini model preflight, structured output, and validation.
5. **Sheets reconciliation** — stable OCE record IDs, human approval pull-through, retry-safe upserts, and Daily Runs reporting.
6. **Approval and email delivery** — provider integration, durable lifecycle, suppression, daily caps, and ambiguous-send reconciliation.
7. **Scheduling and operations** — 09:00 Asia/Kolkata schedule, manual run, dry run, recovery, metrics, tests, and runbook.

## First slice acceptance criteria

- Qualification is deterministic and does not depend on an LLM.
- A funding-only signal cannot pass as direct hiring evidence.
- Stale evidence and incompatible location are rejected.
- Scoring uses the specified 35/30/20/15 weights.
- Unit tests cover URL normalization and qualification/score behavior.
