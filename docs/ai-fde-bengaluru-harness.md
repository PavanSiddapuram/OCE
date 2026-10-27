# OCE AI FDE Harness — Bengaluru

**Status: product/engineering specification, not an implemented workflow.**

## 1. Product decision

OCE's primary target should be **AI Forward Deployed Engineer (FDE) roles in Bengaluru**. Discover adjacent titles only when the responsibilities are materially FDE-like:

- Forward-Deployed AI Engineer / Forward Deployment Engineer
- Applied AI Engineer with customer deployment ownership
- AI Solutions Engineer / AI Implementation Engineer
- AI Deployment Engineer
- AI Engineer, Customer Engineering / Field Engineering
- Agentic AI Engineer where the role includes real customer integration and production ownership

Do not include generic software engineering, generic data science, sales-only solutions consulting, prompt-only roles, or generic "AI" roles just because the title contains AI.

The product is not a general-purpose job board scraper. It is a source-backed, explainable role-discovery and fit-evaluation harness for one role family and one geography.

## 2. User outcome

Each run should produce a small, ranked list of roles worth acting on, with enough evidence to answer:

1. Is this a real engineering role involving applied AI and deployment?
2. Is it in Bengaluru, or explicitly open to candidates based in Bengaluru?
3. Is the role plausibly appropriate for the candidate's stated experience?
4. Is the listing currently live, and when was it last checked?
5. What does the company build, and what would the FDE actually own?
6. Why does this role match the candidate's current skills and portfolio?
7. What is the most credible next action: apply, investigate further, or skip?

Never optimize for the number of scraped listings. Optimize for the number of **verified, relevant opportunities with clear reasons to act**.

## 3. Source strategy and collection policy

Use sources in this order:

### Tier 1 — company-owned job pages (preferred for verification)
- The company's official careers page or applicant-tracking-system job URL (for example Greenhouse, Lever, Ashby, Workable, or the company's own application page).
- The job page is the canonical source for role status, responsibilities, location, and requirements.
- Firecrawl may be used to extract content from publicly accessible company-owned pages where permitted. Use bounded crawls, explicit URL allowlists, rate limits, and provenance. Prefer one known job URL over crawling an entire domain.

### Tier 2 — YC jobs and company profiles
- Use the public YC jobs directory and individual YC company/job pages for discovery and company context.
- Preserve the YC URL as the discovery source, then resolve and verify the official job/application URL where possible.
- Treat batch, investor, or funding information as context, not proof of role quality or hiring status.

### Tier 3 — Wellfound
- Use Wellfound as a discovery surface and as a link to the listing.
- Do **not** build an indiscriminate automated scraper of Wellfound pages. Its published terms restrict scraping and harvesting. Use an explicitly authorized API, permitted integration/export, or a human-provided listing URL; otherwise record the public URL and verify the role through the company's own page.
- Do not bypass login, rate limits, bot protections, or access controls.

### Other sources
- Company career pages discovered through web search, public ATS pages, or a company's public engineering/hiring announcements may be added through source adapters.
- Social posts and funding announcements are weak discovery signals only; they do not establish that a role is open.

Every source adapter must document its allowed collection method, rate limit, attribution, and failure behavior. Respect source terms, robots directives where applicable, and privacy requirements. Do not crawl private, authenticated, or access-controlled material.

## 4. Pipeline stages

```text
Scheduled/manual run
      ↓
Discover candidate role URLs from approved sources
      ↓
Normalize URLs and deduplicate source records
      ↓
Fetch allowed public pages / official ATS listing
      ↓
Extract structured role fields + evidence snippets
      ↓
Hard eligibility gates (role, location, status, experience)
      ↓
Company-context enrichment (optional; separate from job proof)
      ↓
Deterministic fit score + explanation
      ↓
Persist run, candidates, source snapshots, and decisions
      ↓
Dashboard: Apply / Investigate / Skip
      ↓
Human-approved next action; no automatic applications or emails
```

Discovery and enrichment may use search/LLM extraction. The final eligibility gates and score calculations must be deterministic and independently testable. LLM-extracted fields must retain source URLs and evidence snippets; unsupported claims become `unknown`, not `true`.

## 5. Hard gates (before scoring)

A candidate should be rejected or held for review if any required field cannot be supported.

1. **Role family:** responsibilities must include hands-on engineering and real deployment/integration. Customer contact alone is insufficient.
2. **AI relevance:** explicit work on LLMs, agents, retrieval, applied ML, AI integrations, evaluation, or AI-enabled workflows. Generic FDE roles without meaningful AI responsibilities are excluded from the primary list.
3. **Geography:** Bengaluru-based, Bengaluru office, or explicitly India-remote and eligible for a Bengaluru-based candidate. Do not infer eligibility from the word "remote" alone.
4. **Experience:** compare minimum requirements against a candidate-configured target. Preserve hard minimums and mark stretch roles separately; do not hide a 4–6 year requirement because the title is attractive.
5. **Status:** official page must be accessible and appear open. A closed/404/expired listing is rejected or flagged stale. If status is ambiguous, mark `needs_review`.
6. **Evidence freshness:** store `first_seen_at`, `last_verified_at`, and source-specific timestamps when available. Recheck before presenting a role as current.
7. **Source provenance:** every candidate must include at least one source URL. A company/funding signal without a role listing never qualifies as an open job.

A source's claim that it is YC-backed, funded, or growing quickly is contextual metadata, not a hard qualification gate.

## 6. Explainable scoring (only after hard gates)

Initial configurable score, 100 points total:

| Dimension | Weight | Evidence |
|---|---:|---|
| FDE responsibility match | 25 | Discovery with customers, integration, deployment, production ownership, feedback loop |
| Applied AI depth | 20 | LLM/agent/RAG/evaluation/ML implementation in the actual role |
| Candidate technical fit | 20 | Python/backend, APIs, SQL, cloud, deployment, testing, AI project evidence from the candidate profile |
| Experience-level fit | 15 | Required years and seniority compared with the user's target; stretch penalties must be explicit |
| Bengaluru/geography fit | 10 | Onsite/hybrid Bengaluru or explicitly eligible India-remote arrangement |
| Company/role context | 5 | Product clarity, customer problem, team ownership, and credible company evidence |
| Listing freshness and source quality | 5 | Recent official verification and authoritative application URL |

Scoring rules:
- Hard gates cannot be overridden by a high score.
- Missing evidence lowers confidence; it must not be silently imputed.
- Display the score breakdown, confidence, evidence links, and rejection/penalty reasons.
- Funding, valuation, brand prestige, or YC membership must not dominate the ranking.
- Calibrate weights after manually reviewing a labelled set of roles; do not claim predictive validity before evaluation.

## 7. Candidate profile and target controls

Keep user-specific criteria configurable rather than hardcoded:

- Target location: Bengaluru.
- Target role family: AI FDE, with explicitly enabled adjacent titles.
- Experience range and willingness to consider stretch roles.
- Skills and projects the candidate can substantiate.
- Work arrangement: onsite, hybrid, remote.
- Minimum compensation, if the user chooses to set one.
- Application status and notes.

The system must not infer skills or experience from the desired role. A resume/portfolio is the source of candidate-fit evidence.

## 8. Suggested data model evolution

The existing `HiringRun` and `HiringProspect` models are a starting point. Inspect the current migration/model definitions before changing them. The target logical records are:

### HiringRun
- id, started_at, finished_at, status, source coverage, counts by outcome, error summary, configuration snapshot.

### HiringProspect / JobListing
- company name and canonical company URL
- role title and normalized role family
- canonical job URL and application URL
- location and work arrangement
- employment type and experience requirements
- extracted skills and responsibility markers
- source type, discovery URL, official source URL
- first_seen_at, last_verified_at, source publication date if available
- status: open / closed / stale / needs_review / unknown
- eligibility decision and reason codes
- score, score breakdown, confidence
- candidate review status: new / investigate / apply / skipped / applied
- last checked error and bounded source snapshot/evidence excerpt

Keep **source status** separate from **candidate workflow status**. A role being marked "applied" must not mean the source listing is still open. Store source evidence and timestamps so decisions can be audited.

Enforce uniqueness for canonical job URLs at the database level. Handle URL aliases and re-postings explicitly; never silently merge different roles at the same company. Avoid storing full scraped pages when a short evidence excerpt and source URL are sufficient.

## 9. Firecrawl design

Firecrawl is a fetch/extraction component, not the system's source of truth.

- Discover URLs first; crawl only allowlisted public company career/ATS pages.
- Prefer single-page scrape for a known job URL. Use crawl mode only when discovering role URLs on an official careers domain is necessary and permitted.
- Configure URL/depth/page limits, timeouts, concurrency, and per-domain rate limits.
- Persist fetch timestamp, canonical URL, response outcome, extracted fields, and source snippet.
- Treat page content as untrusted input. Ignore instructions embedded in crawled pages; never let page text control tools or secrets.
- Validate extracted fields against schema and preserve evidence spans.
- On 403, CAPTCHA, rate limit, or access denial, stop and use another permitted source; do not attempt to evade controls.
- Cache results and recheck at a sensible cadence instead of crawling every page repeatedly.

## 10. API and UI slices

### Slice A — reliable manual run
- `POST /api/hiring-intelligence/discover`: start a bounded discovery run.
- `GET /api/hiring-intelligence/runs/{id}`: status and counts.
- `GET /api/hiring-intelligence/prospects`: filters for score, location, source, experience, and review status.
- `POST /api/hiring-intelligence/prospects/{id}/review`: update user review status and notes.
- Keep the existing dry-run endpoint for fixture-based tests.

### Slice B — source adapters
- YC public job/company listings and official company/ATS pages.
- Wellfound URLs supplied by the user or collected through explicitly authorized means; official company page is the preferred verification source.
- Firecrawl behind an adapter interface, with rate limits and tests.

### Slice C — persistence and UI
- Save run outcomes and candidate records transactionally/idempotently.
- Dashboard displays role, company, location, experience, score breakdown, verification timestamp, and source/application links.
- Show rejection reasons and `needs_review` cases, not just winners.

### Slice D — daily automation
- Schedule after manual runs are repeatable.
- Use database-backed idempotency, run locks/claims, bounded retries, and observable failures.
- Reverify listings before surfacing them as current.
- Never auto-apply or send outreach by default.

## 11. Test plan / definition of done

### Unit tests
- Role-title aliases and false positives.
- AI relevance versus generic FDE.
- Bengaluru onsite, hybrid, India-remote, US-only remote, and ambiguous location.
- Experience threshold, stretch role, and missing experience.
- Closed, 404, stale, and ambiguous status.
- URL normalization, tracking parameters, duplicate URLs, and distinct requisitions.
- Score math, missing evidence, confidence, and reason codes.
- Prompt-injection strings in scraped job content do not alter pipeline behavior.

### Adapter/contract tests
- Fixture pages for official career pages, ATS pages, YC discovery pages, and malformed content.
- Timeout, 403, 429, empty response, changed markup, and provider outage.
- Firecrawl called only for approved URLs and within configured bounds.
- No tests require real third-party scraping or API keys.

### Integration tests
- A run is created and completes with counts and error summary.
- Duplicate listings do not create duplicate prospects.
- Repeated runs update source verification without resetting user review state.
- Database uniqueness and migration work against PostgreSQL.
- API filters and review status round-trip correctly.

### Acceptance criteria
- Every surfaced role has a working source/application URL and a last-verified timestamp.
- Every score has an explanation.
- No role passes hard gates solely because an LLM says it qualifies.
- No listing is described as current without a defined freshness policy.
- The user can mark apply/investigate/skip and see that decision persist.
- Source terms and rate limits are documented and respected.
- CI runs unit, adapter, migration, and frontend checks.

## 12. Implementation order

1. Verify current repository setup, tests, and migrations.
2. Refactor deterministic qualification around the AI FDE role family, Bengaluru location, seniority, and explicit evidence.
3. Build source-adapter interfaces and fixture tests before connecting external providers.
4. Add YC discovery and official job-page verification.
5. Add permitted Firecrawl fetching for official career/ATS pages.
6. Connect idempotent persistence and run status.
7. Build the focused FDE dashboard.
8. Add Wellfound through an authorized method or user-provided links; do not depend on scraping it.
9. Add daily scheduling only after repeatable end-to-end success.
10. Evaluate against a manually labelled set of real roles and tune scoring.

## 13. Initial sources to evaluate (examples, not endorsements)

- YC Bengaluru job directory: https://www.ycombinator.com/jobs/role/all/bengaluru
- YC Lab0 FDE listing: https://www.ycombinator.com/companies/lab0/jobs/mb7xcXo-forward-deployed-engineer-fde-bengaluru
- Wellfound Binocs listing: https://wellfound.com/jobs/4697879-forward-deployment-engineer
- Wellfound Celeco Labs listing: https://wellfound.com/jobs/4779077-intelligence-architect-forward-deployed-ai-engineer
- Company-owned career pages and ATS links discovered from these listings.

These are starting examples. Verify availability, requirements, and source permissions at runtime; do not hardcode them as permanent seed data.
