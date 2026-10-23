# OCE — Opportunity Creation Engine

> **Don't just apply for a role. Find a consequential problem, build proof that you can solve it, and earn a conversation with the people building the company.**

OCE is being built for ambitious engineers who want more than another application tracker. It helps you discover fast-moving startups, understand what they are building, identify meaningful engineering opportunities, and turn your skills into proof-of-work and thoughtful founder outreach.

The ambition is simple: help talented people find places where their work can matter early — where the team is small, the problems are real, and ownership is something you can earn rather than wait years for.

[Explore the code](https://github.com/PavanSiddapuram/OCE) · [Setup guide](#getting-started) · [Current status](#where-the-project-stands)

---

## The idea: create opportunity, don't just search for it

Most job-search workflows start with a vacancy. They ask you to match keywords, submit a resume, and wait in a queue with hundreds of other applicants.

OCE starts with a different question:

**Which ambitious companies have important problems that I could help solve — and how can I prove it before asking for a job?**

A fast-moving startup may be building a new product, scaling a system, entering a market, or struggling with a technical bottleneck. A conventional job description only shows part of that story. OCE's thesis is that company research, technical judgment, and a small, relevant proof-of-work can help an engineer make a more compelling case than a generic application.

This is especially relevant when exploring:

- **YC companies and venture-backed startups** building in AI, developer tools, deep tech, robotics, fintech, SaaS, and other ambitious markets.
- **Small, fast-moving teams** where engineers can work close to founders, customers, and product decisions.
- **Roles with room for ownership** — not just completing tickets, but taking responsibility for a problem from understanding through implementation.
- **Companies where your specific skills create leverage**, even when the perfect job title or public opening is difficult to find.

Funding or a famous accelerator is a discovery signal, not proof of quality. OCE should help you investigate the actual product, team, technical context, hiring evidence, and fit — then make your own informed decision.

## Who OCE is for

OCE is designed for engineers who want to be deliberate about where they spend their effort:

- Students and early-career engineers who want to stand out through real work rather than volume applications.
- Software engineers moving toward AI, infrastructure, developer tools, or other high-growth technical areas.
- Builders who would rather demonstrate how they think than send another generic cold message.
- Candidates looking for environments with meaningful responsibility, fast feedback, and room to grow.

The goal is not to promise a job, a reply, or startup success. It is to make the process of finding a strong opportunity and making a credible case for yourself more thoughtful, evidence-based, and repeatable.

---

## How OCE works

The original startup-opportunity workflow is built around an eight-agent research pipeline:

```text
Discover promising startups
          ↓
Research product, team, technology, and recent activity
          ↓
Identify concrete problems an engineer could help solve
          ↓
Match opportunities against your skills and resume
          ↓
Design a focused proof-of-work project
          ↓
Research founders and their public perspectives
          ↓
Draft specific, context-rich outreach
          ↓
Track contacts and follow-ups in a CRM
```

### From “I want to work there” to “Here is what I could help with”

| Stage | What OCE is intended to help you answer |
|---|---|
| Discover | Which companies are worth investigating, based on sector, location, and signals of momentum? |
| Understand | What does the company build? What is changing? Which technologies and product constraints are visible? |
| Find an opportunity | What specific improvement, prototype, or engineering problem might be worth exploring? |
| Match | Where do my existing skills fit, and what gaps should I be honest about? |
| Prove | What small, relevant artifact could demonstrate my judgment and execution? |
| Reach out | How can I explain why this company, why this problem, and why my work may be relevant? |
| Follow through | How do I track conversations and follow-ups without losing context? |

AI-generated research and ideas are starting points, not unquestionable facts. A candidate should verify important claims, respect company boundaries, and build original work rather than misrepresenting access or experience.

---

## A second track: Daily Hiring Intelligence

OCE is also being extended toward a more direct workflow: finding **fresh, relevant engineering job listings** and ranking them using transparent evidence and fit signals.

The intended flow is:

```text
Find real job listings
        ↓
Preserve source URLs and verification dates
        ↓
Check direct hiring evidence and location eligibility
        ↓
Remove duplicates and stale / ineligible evidence
        ↓
Score technical fit, hiring evidence, contact relevance, and freshness
        ↓
Save prospects and show the evidence for human review
        ↓
Run daily and support approved follow-up workflows
```

The current repository contains the deterministic qualification/scoring foundation, SQLAlchemy models, an Alembic migration, and a dry-run API. **It does not yet implement the complete workflow above.** In particular, live job discovery, independent source verification, prospect persistence through the new endpoint, a dedicated hiring dashboard, daily scheduling, Google Sheets sync, and email delivery are not yet established.

The dry-run endpoint accepts candidate evidence supplied by the caller and returns `persisted: false`. It is useful for testing qualification logic; it is not a live job search and does not prove that a role remains open. See [the dry-run notes](docs/hiring-intelligence-dry-run.md).

---

## Product principles

### Evidence before confidence
A funding announcement, company growth story, or vague careers page is not proof of an open role. Hiring claims should point to verifiable sources and show when they were checked.

### Build for agency
The point is not to automate every human decision. It is to give an engineer enough useful context to choose a company, understand a problem, and take a meaningful next step.

### Specific beats generic
A small, thoughtful prototype or well-researched message should be connected to a real problem — not generated as generic busywork for every company.

### Deterministic gates, explainable scores
Hard eligibility checks should be explicit and testable. Scores should come with a breakdown and reasons, so a candidate can understand why an opportunity ranked well or was rejected.

### Human judgment stays in the loop
Research can be wrong, pages can be stale, and fit scores are estimates. Verify claims before acting. Outreach should remain reviewable and under the user's control.

### Separate workflows, shared foundations
The startup-opportunity pipeline and hiring-intelligence workflow serve related but different needs. They should share infrastructure where useful without becoming one tangled agent chain.

---

## Architecture and technology

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Python 3.11+ |
| Data validation and configuration | Pydantic v2, pydantic-settings |
| Database | PostgreSQL 16, SQLAlchemy async |
| Database migrations | Alembic |
| Background jobs | Redis 7 + ARQ |
| AI provider | DeepSeek through Pydantic AI |
| Search and scraping | Tavily, Firecrawl; Jina Reader wrapper |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Client data fetching | TanStack Query v5 |
| Local development | Docker Compose |

### Repository map

```text
OCE/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── agents/       # Eight-agent startup research pipeline
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Request and response validation
│   │   ├── services/     # Deterministic hiring-intelligence logic
│   │   ├── tasks/        # ARQ worker and pipeline jobs
│   │   └── tools/        # Search, scrape, and reading adapters
│   ├── tests/
│   └── alembic/          # Database migrations
├── docs/
│   └── hiring-intelligence-dry-run.md
└── frontend/
    └── src/
        ├── app/          # Discover, companies, opportunities, CRM, outreach
        ├── hooks/
        ├── lib/
        └── types/
```

---

## Where the project stands

OCE is an actively evolving codebase. The repository has not yet been verified through a full local end-to-end run, so implementation status and runtime status must not be confused.

### Present in the codebase

- Existing startup discovery and eight-agent research pipeline.
- FastAPI API, PostgreSQL models and migrations, Redis/ARQ worker, and Next.js interface.
- Deterministic job URL canonicalization, evidence freshness/location checks, qualification reasons, and weighted scoring.
- Hiring run/prospect model definitions and migration.
- `POST /api/hiring-intelligence/dry-run` for caller-supplied candidate evidence.
- Tests for the hiring-intelligence logic and dry-run behavior (execution still needs to be confirmed in CI).

### Still to build or verify

- Run the complete setup, migrations, backend tests, frontend checks, and startup pipeline locally or in CI.
- Verify existing startup-pipeline behavior against real provider responses.
- Build live job-source adapters and independently verify listings.
- Connect hiring runs and prospects to real persistence with idempotent updates.
- Add a hiring-prospect API and a dedicated dashboard for evidence, scores, rejection reasons, and review status.
- Add daily scheduling, observability, retries, and failure recovery.
- Consider Google Sheets integration and human-approved outreach after the core workflow is reliable.

The next priority is reliability and end-to-end verification, followed by the smallest complete vertical slice of Daily Hiring Intelligence. This README intentionally distinguishes the product vision from what is already implemented.

---

## Getting started

### Requirements

- Docker Desktop / Docker Engine with Compose
- Python 3.11+
- Node.js 20+
- DeepSeek, Tavily, and Firecrawl API keys for the existing startup research pipeline

The hiring dry-run endpoint does not itself call external providers. Never commit a real `.env` file or API keys.

### 1. Clone and configure

```bash
git clone https://github.com/PavanSiddapuram/OCE.git
cd OCE
cp .env.example .env
```

Edit `.env` and replace the example values with your own API keys.

### 2. Start PostgreSQL and Redis

From the repository root:

```bash
docker compose up -d postgres redis
```

### 3. Install backend dependencies and apply migrations

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Then run:

```bash
python -m pip install --upgrade pip
pip install -e .
alembic upgrade head
```

### 4. Start the API and background worker

Open two terminals, both in `OCE/backend` with the virtual environment activated.

Terminal 1 — API:

```bash
uvicorn app.main:app --reload
```

Terminal 2 — worker:

```bash
python -m arq app.tasks.worker.WorkerSettings
```

The API should be available at `http://localhost:8000`.

- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Start the frontend

In a third terminal:

```bash
cd OCE/frontend
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Docker Compose alternative

From the repository root, configure `.env`, then run:

```bash
docker compose up -d postgres redis
docker compose run --rm backend alembic upgrade head
docker compose up --build
```

Migrations are explicit: starting the API container does not automatically create the database tables.

---

## Useful endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Basic API liveness check |
| GET | `/docs` | Interactive OpenAPI documentation |
| POST | `/api/pipeline/run` | Start the startup research pipeline |
| GET | `/api/pipeline/{id}/status` | Read pipeline status |
| GET | `/api/companies` | List researched companies |
| GET | `/api/opportunities` | List ranked opportunities |
| GET | `/api/crm/board` | Read the CRM board |
| POST | `/api/hiring-intelligence/dry-run` | Evaluate supplied hiring evidence without side effects |
| GET | `/api/state/{key}` | Read shared application state |
| PUT | `/api/state/{key}` | Create or update shared application state |

For the dry-run request example, response shape, and limitations, see [docs/hiring-intelligence-dry-run.md](docs/hiring-intelligence-dry-run.md).

---

## Validation

Run backend tests and migrations from `OCE/backend`:

```bash
python -m unittest discover -s tests -v
alembic upgrade head
```

Run frontend checks from `OCE/frontend`:

```bash
npm ci
npx tsc --noEmit
npm run build
```

These checks must pass before calling the repository verified. A healthy API response alone does not prove that database migrations, the background worker, external integrations, the frontend, or either workflow operates end to end.

---

## Roadmap

- [x] Deterministic hiring evidence gates and scoring foundation
- [x] Hiring run/prospect model definitions and database migration
- [x] No-side-effect hiring dry-run endpoint
- [ ] Repeatable CI and verified clean setup
- [ ] Live job discovery with source-backed evidence
- [ ] Persistent, idempotent prospect processing
- [ ] Hiring dashboard and human review flow
- [ ] Reliable daily scheduler and run observability
- [ ] Optional Sheets reconciliation
- [ ] Human-approved outreach workflow

## Contributing

Keep changes small, testable, and honest about their implementation status. Prefer complete vertical slices, explicit evidence, deterministic business rules, and tests over adding more agents before the underlying workflow is reliable.

## License

MIT
