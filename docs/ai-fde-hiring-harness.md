# AI Forward Deployed Engineer (FDE) Opportunity Harness

## 1. Product decision

OCE's hiring-intelligence track should specialize in **AI Forward Deployed Engineer opportunities in Bengaluru**, prioritizing funded startups whose products are deployed into real customer workflows.

This is not a general job aggregator. The goal is to help one candidate find a small number of unusually relevant opportunities, understand the company and its customer problems, build a credible proof-of-work artifact, and prepare a thoughtful founder or engineering-lead message.

The harness must distinguish an **advertised open role** from a **company worth approaching**. A target company without a verified FDE opening must never be represented as actively hiring for that role.

## 2. Target profile

### Role family

Include roles with substantial hands-on engineering and customer deployment responsibility:

- Forward Deployed Engineer / Forward Deployment Engineer
- AI FDE / AI Deployment Engineer
- Customer Engineer, when the role ships code and production integrations
- AI Implementation Engineer / Solutions Engineer, when hands-on building is central
- Applied AI Engineer, when the role includes customer discovery and deployment

Exclude or heavily down-rank pure pre-sales, demos-only, account management, and non-coding customer success roles; generic software jobs with no customer deployment or applied-AI signal; roles outside Bengaluru / India eligibility; and roles with unverified or stale job evidence.

### Company profile

Prioritize companies that satisfy all of the following:

1. **Funding/accelerator evidence:** a verifiable funding event, credible investor portfolio page, or official YC company profile/batch.
2. **Applied AI product:** AI agents, enterprise AI, voice AI, workflow automation, AI infrastructure, or another AI product deployed into real workflows.
3. **Customer delivery signal:** evidence that engineers implement integrations, run pilots, embed with customers, own go-lives, or adapt the product to client systems.
4. **Bengaluru relevance:** a Bengaluru office/role or explicit India-remote eligibility.
5. **Candidate relevance:** the role or company's engineering needs plausibly match the candidate's current skills and portfolio.

Funding is a qualification signal for this product's target market, not proof of hiring, product quality, or a good working environment.

## 3. Two separate prospect lanes

### Lane A — Verified open role

A direct job posting exists and can be opened. OCE records the canonical job URL, role title, location, source, evidence timestamp, funding evidence, and the reason it fits the FDE profile.

This lane may be labeled **Verified open role** only while its direct listing remains verifiable and sufficiently fresh.

### Lane B — Proactive company outreach

The company matches the funded, applied-AI, client-deployment profile, but no FDE opening has been verified.

OCE records it as **Target company — no verified opening**. It may suggest a founder, CTO, engineering lead, or deployment lead to contact and draft a message anchored in public evidence. It must not invent a vacancy or imply the company is hiring.

Keeping these lanes separate avoids turning funding announcements, customer wins, or generic company growth into false job listings.

## 4. Source strategy

Use source adapters rather than embedding site-specific parsing in the scoring service.

1. **YC Jobs and official YC company pages:** discover FDE roles and verify batch/company information.
2. **Wellfound public job pages:** discover roles and capture canonical listing URLs and posting details where publicly accessible.
3. **Official careers pages and ATS pages:** verify openings on company sites and providers such as Greenhouse, Lever, and Ashby.
4. **Official funding evidence:** company announcements, investor portfolio/announcement pages, and official accelerator profiles. Use reputable reporting as corroboration when primary evidence is unavailable.
5. **Company product/customer pages:** establish that the company deploys AI into customer workflows and that customer-facing engineering is relevant.

Tavily can help discover candidate URLs. Firecrawl can extract public page content when access is permitted. Official job pages should be the preferred verification source.

Respect website terms, robots directives, rate limits, and access controls. Do not bypass logins, anti-bot mechanisms, paywalls, or other restrictions. If a page cannot be verified, mark it **unverified** instead of inferring its contents.

Every material claim should retain:
- source URL
- source type
- captured/verified timestamp
- relevant extracted evidence snippet
- extraction status or error
- normalized company identity and canonical job URL, when applicable

Do not treat a search-result snippet alone as definitive proof that a job is still open.

## 5. Qualification and scoring

Hard gates must run before ranking. AI/LLM extraction may help normalize a role or summarize evidence, but it must not override deterministic gates.

### Lane A hard gates

- Valid direct job URL and readable listing evidence
- Role fits the FDE role family and includes hands-on engineering
- Location is explicitly Bengaluru or the posting explicitly allows the candidate's location
- Posting is currently accessible and evidence is fresh enough for the configured threshold
- Funding/accelerator status has a recorded source
- No clear evidence that the role is closed or restricted to an incompatible location

Do not treat the word “remote” alone as proof of India eligibility. Do not treat funding, customer wins, or expansion news as direct hiring evidence.

### Lane B hard gates

- Funding/accelerator status is verified
- Public evidence supports an applied-AI product and customer deployment/integration work
- Bengaluru/India fit is grounded in public evidence
- There is a plausible, specific FDE-shaped contribution to explore
- No claim is made that a role is open unless a direct listing is verified

### Ranking dimensions

For an initial transparent 0–100 ranking, use:

- **30% — FDE role / responsibility fit:** hands-on engineering, customer problem-solving, production ownership
- **25% — Customer deployment signal:** pilots, integrations, enterprise workflows, go-lives, customer-site work
- **20% — Funding and company momentum:** verified funding/YC evidence plus grounded, current product or customer activity
- **15% — Hiring evidence:** direct open role ranks above indirect hiring signals; Lane B uses an outreach-fit signal but remains a separate lane
- **10% — Contact path:** a credible public founder/CTO/engineering-lead route and a relevant reason to contact

Evidence freshness is also a **hard freshness control**, not just a score bonus. Scores must show a component breakdown and source-backed reasons. These weights are a starting hypothesis and should be calibrated against a manually reviewed set of real roles.

## 6. Founder/team outreach

Outreach is a research and drafting workflow, not a bulk messaging bot.

For each Lane B company (or a high-fit Lane A role), OCE should produce:

1. A concise company/product summary with sources.
2. One concrete, public-evidence-based reason an FDE contribution could matter.
3. The most relevant public contact route and why that person is appropriate.
4. A draft message with one specific observation, one relevant capability/proof link, and a low-pressure question.
5. An uncertainty note identifying anything not verified.

Never claim to know an internal problem based only on public pages. Phrase the idea as a hypothesis and invite correction. Never invent contact details, customer deployments, job openings, or candidate experience.

**Human approval is required before any message is sent.** The first implementation should generate copyable drafts only. No automated LinkedIn DMs, email sending, or bulk outreach.

## 7. Suggested architecture in OCE

Keep the existing startup eight-agent pipeline independent. Build the FDE harness as a separate vertical slice that reuses shared infrastructure only where appropriate.

Suggested modules:

- hiring sources: adapter interface, YC jobs, permitted Wellfound public pages, official company career pages, funding evidence
- normalization: canonical URLs and company identity
- qualification: deterministic FDE hard gates
- scoring: explainable ranking
- outreach drafts: evidence-grounded message generation
- run service: orchestration, persistence, and error handling
- API: run, prospect listing/detail, evidence, and review status

This is a proposed organization, not a claim that these modules already exist. Keep the current deterministic hiring-intelligence service as a small foundation or migrate it behind tested interfaces without duplicating scoring logic.

### Persistence

The existing HiringRun and HiringProspect models can be the starting point. Before relying on them, review whether they can represent:

- prospect lane and status (open role vs target company/no verified opening)
- funding evidence and source URL
- job evidence and last-verified timestamp
- company deployment/customer signal with citations
- score components and qualification/rejection reasons
- public contact identity, source, and confidence
- outreach draft, approval status, and outcome
- last-seen / closed / stale status and audit history

Consider a separate evidence table if storing multiple claims and sources as JSON becomes difficult to query or audit. Database uniqueness should protect canonical job URLs; company identity needs its own normalization strategy. Persisting a new run should be idempotent and should not reset human review state.

## 8. API and user experience

Recommended first endpoints:

- POST /api/hiring-intelligence/runs — manually start a discovery/qualification run
- GET /api/hiring-intelligence/runs/{run_id} — inspect status and counts
- GET /api/hiring-intelligence/prospects — filter by lane, score, location, funding, and review state
- GET /api/hiring-intelligence/prospects/{id} — view evidence, sources, score breakdown, and history
- POST /api/hiring-intelligence/prospects/{id}/draft-outreach — create a draft, not send it
- PATCH /api/hiring-intelligence/prospects/{id}/review — mark reviewed, shortlisted, dismissed, or contacted

The dashboard should prioritize evidence and actionability over a huge list: company, role/lane, funding evidence, customer deployment signal, location, last verification, score breakdown, direct source links, and the next recommended action.

Keep the current /dry-run endpoint side-effect-free for deterministic rule testing.

## 9. Implementation sequence

### Slice 1 — Define and test the FDE policy
- Add typed evidence structures for funding, role responsibilities, customer deployment, and location eligibility.
- Add hard-gate tests for US-only remote roles, stale/closed jobs, funding-only signals, pre-sales-only roles, and unverified openings.
- Keep Lane A and Lane B separate.

### Slice 2 — Real discovery, read-only
- Implement YC and permitted public job-page adapters.
- Capture canonical URLs, timestamps, and source snippets.
- Verify official job pages before a listing qualifies.
- Store a run report without sending messages.

### Slice 3 — Persist and review
- Connect qualification to database persistence and duplicate handling.
- Add prospect listing/detail/review APIs and a small dashboard.
- Preserve human decisions across reruns.

### Slice 4 — Evidence-grounded outreach drafts
- Build a public-contact research step and draft generator.
- Require source citations in the draft's research context.
- Add copy/review controls; no automated send.

### Slice 5 — Daily operation
- Add scheduling only after manual runs are reliable.
- Add retries, source-level error reporting, stale-role rechecks, metrics, and safe recovery.
- Add Sheets integration only if it improves the review workflow.

## 10. Definition of done for the first useful release

A manually triggered run can discover a real FDE listing from a permitted source, verify the official job page, confirm funding/accelerator evidence, check Bengaluru/India eligibility, deduplicate the URL, produce an explainable score, persist the result, and show the sources in a reviewable UI.

A company without a verified vacancy can appear only in the proactive-outreach lane. The app produces a draft for human approval and never sends it automatically.

The first release should optimize for **a small number of high-confidence, evidence-rich opportunities**, not maximum scrape volume.
