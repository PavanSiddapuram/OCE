# Opportunity Creation Engine (OCE)

> Turn yourself from applicant into opportunity creator.

OCE is a FastAPI + Next.js application for researching startups, identifying engineering opportunities, generating proof-of-work ideas, and preparing founder-specific outreach. The repository is also being extended with a separate **Daily Hiring Intelligence** workflow for evaluating fresh engineering job listings.

**Important:** the repository has been updated through merged pull requests, but a full local end-to-end run has not yet been verified. Treat the setup and test steps below as the validation checklist, not as evidence that the application has already passed them.

## Current capabilities and status

OCE currently has two related but distinct workflows:

### 1. Startup opportunity creation

The existing eight-agent pipeline is launched manually from the Discover page. It discovers startups and runs company research, opportunity detection, skill matching, proof-of-work planning, founder research, outreach drafting, and CRM updates.

### 2. Daily Hiring Intelligence — foundation only

The first foundation is present:

- Deterministic job-URL canonicalization and duplicate detection.
- Evidence freshness, direct-hiring-evidence, and location qualification gates.
- A weighted prospect score (technical fit 35%, hiring evidence 30%, contact relevance 20%, freshness 15%).
- PostgreSQL models and Alembic migration for hiring runs and prospects.
- `POST /api/hiring-intelligence/dry-run`, which evaluates candidate records supplied by the caller.

**The hiring workflow is not yet end-to-end.** The dry-run endpoint does not discover jobs, independently verify live pages, persist prospects, schedule daily runs, populate a hiring dashboard, write to Google Sheets, or send email. A successful dry run is not proof that a job is still open. See [the dry-run notes](docs/hiring-intelligence-dry-run.md).

## Architecture

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Python 3.11+ |
| Validation/settings | Pydantic v2, pydantic-settings |
| Database | PostgreSQL 16, SQLAlchemy async |
| Migrations | Alembic |
| Background jobs | Redis 7 + ARQ |
| AI provider | DeepSeek through Pydantic AI |
| Search/scraping | Tavily, Firecrawl; Jina Reader wrapper |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Data fetching | TanStack Query v5 |
| Local infrastructure | Docker Compose |

## Repository layout

```text
OCE/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── agents/       # Existing eight-agent startup workflow
│   │   ├── models/       # SQLAlchemy models, including hiring intelligence
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/    # Deterministic hiring-intelligence logic
│   │   ├── tasks/       # ARQ worker and pipeline jobs
│   │   └── tools/       # Search, scrape, and reading adapters
│   ├── tests/           # unittest-based tests
│   └── alembic/         # Database migrations
├── docs/
│   └── hiring-intelligence-dry-run.md
└── frontend/
    └── src/
        ├── app/         # Discover, companies, opportunities, CRM, outreach
        ├── hooks/
        ├── lib/
        └── types/
```

## Prerequisites

- Docker Desktop / Docker Engine with Compose
- Python 3.11+
- Node.js 20+
- DeepSeek, Tavily, and Firecrawl API keys for running the existing startup research pipeline

The hiring dry-run endpoint itself does not need external provider keys. Do not commit your real `.env` file or API keys.

## Local setup

### 1. Clone and configure

```bash
git clone https://github.com/PavanSiddapuram/OCE.git
cd OCE
cp .env.example .env
```

Edit `.env` and replace the example values with your actual API keys.

### 2. Start PostgreSQL and Redis

From the repository root:

```bash
docker compose up -d postgres redis
```

### 3. Install the backend and apply migrations

```bash
cd backend
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Then run:

```bash
python -m pip install --upgrade pip
pip install -e .
alembic upgrade head
```

### 4. Start the API and worker

Open two terminals, both in `OCE/backend` with the virtual environment activated.

Terminal 1:

```bash
uvicorn app.main:app --reload
```

Terminal 2:

```bash
python -m arq app.tasks.worker.WorkerSettings
```

The API should be available at `http://localhost:8000`. Check `http://localhost:8000/health` and open `http://localhost:8000/docs` to inspect the routes.

### 5. Start the frontend

In a third terminal:

```bash
cd OCE/frontend
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Docker Compose setup

From the repository root, configure `.env` first, then apply migrations before starting the application:

```bash
docker compose up -d postgres redis
docker compose run --rm backend alembic upgrade head
docker compose up --build
```

The Compose configuration supplies container-specific database and Redis URLs. The migration command is explicit; starting the API container alone does not create the database tables.

## Useful endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Basic API liveness check |
| GET | `/docs` | Interactive OpenAPI / Swagger UI |
| POST | `/api/pipeline/run` | Start the existing startup research pipeline |
| GET | `/api/pipeline/{id}/status` | Read startup pipeline status |
| GET | `/api/companies` | List researched companies |
| GET | `/api/opportunities` | List ranked opportunities |
| GET | `/api/crm/board` | Read the CRM board |
| POST | `/api/hiring-intelligence/dry-run` | Evaluate supplied hiring evidence without side effects |
| GET | `/api/state/{key}` | Read shared application state |
| PUT | `/api/state/{key}` | Create/update shared application state |

### Try the hiring dry run

Use the example request in [docs/hiring-intelligence-dry-run.md](docs/hiring-intelligence-dry-run.md). The request accepts caller-supplied candidate evidence and returns qualification reasons and score breakdowns. It explicitly returns `persisted: false`.

## Tests and validation

From `OCE/backend`:

```bash
python -m unittest discover -s tests -v
alembic upgrade head
```

From `OCE/frontend`:

```bash
npm ci
npx tsc --noEmit
npm run build
```

These commands must be run successfully before considering the repository verified. A successful `/health` response alone does not prove the database migrations, background worker, external integrations, frontend, or either workflow works end to end.

## Next steps for Daily Hiring Intelligence

1. Discover jobs from real sources and preserve the source URL plus verification timestamp.
2. Validate direct job evidence and location eligibility; keep deterministic gates as the final qualification authority.
3. Persist qualified prospects and run outcomes idempotently using the database uniqueness constraints.
4. Add a manual review/dashboard surface for candidates, evidence, scores, and rejection reasons.
5. Add a daily scheduler and operational logging/recovery.
6. Add optional Sheets reconciliation and human-approved outreach only after discovery, qualification, persistence, and tests are reliable.

No automated email sending or external write action is enabled by the current hiring-intelligence dry run.
