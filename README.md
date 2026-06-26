# Opportunity Creation Engine (OCE)

> Turn yourself from applicant into opportunity creator.

OCE is a multi-agent system that helps engineers discover startups, understand their business, find hidden problems, build proof-of-work, and generate founder-specific outreach — automatically.

Think: **Perplexity + YC Research + CRM + Founder Intelligence** for ambitious engineers.

---

## What It Does

Instead of finding job openings, OCE **creates openings** by running an 8-agent pipeline every week:

```
100 Startups
      ↓
Top 20 (by sector/city fit)
      ↓
Top 5 Opportunities (scored against your resume)
      ↓
Build 1 Prototype (proof-of-work idea generated)
      ↓
Publish Build Log
      ↓
Contact Founder (personalized narrative written)
      ↓
Interview
```

---

## Architecture

### 8-Agent Pipeline

| Agent | What It Does |
|-------|-------------|
| **Agent 1: Discovery** | Searches YC, Accel, Peak XV, Nexus, Blume, AngelList for startups matching your city + sector |
| **Agent 2: Intelligence** | Scrapes website, blog, changelog, hiring page → mission, product, tech stack, recent launches |
| **Agent 3: Opportunity Detection** | "Acts as a founder" to find 3–5 specific things a software engineer could build or improve |
| **Agent 4: Skill Match** | Scores your fit (0–100) against each opportunity based on your resume |
| **Agent 5: Proof-of-Work** | Designs a concrete mini-project/prototype to demonstrate capability |
| **Agent 6: Founder Research** | Finds what founders repeatedly complain about (via interviews, blogs, podcasts) |
| **Agent 7: Narrative** | Writes founder-specific outreach: hook referencing their complaint + PoW in the body |
| **Agent 8: CRM Updater** | Creates contact records and sets follow-up dates |

### Tech Stack

```
Backend          FastAPI + Python 3.11
Database         PostgreSQL 16
Queue            Redis 7 + ARQ (async task queue)
AI               Pydantic AI + Anthropic Claude
Search           Tavily (web search)
Scraping         Firecrawl (website content)
Doc Reading      Jina Reader (LinkedIn, articles)
Frontend         Next.js 15 + React 19 + Tailwind CSS
Drag & Drop      @hello-pangea/dnd (CRM Kanban)
Data Fetching    TanStack Query v5
Infrastructure   Docker Compose
```

---

## Project Structure

```
OCE/
├── docker-compose.yml          # Postgres + Redis + backend + worker + frontend
├── .env.example                # API key template
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── config.py           # Settings via pydantic-settings
│   │   ├── database.py         # Async SQLAlchemy engine
│   │   ├── models/             # SQLAlchemy ORM (7 tables)
│   │   ├── schemas/            # Pydantic v2 request/response shapes
│   │   ├── api/                # FastAPI routers (pipeline, companies, opportunities, contacts, outreach, crm)
│   │   ├── agents/             # 8 Pydantic AI agents (agent1–agent8)
│   │   ├── tasks/              # ARQ worker + job queue
│   │   └── tools/              # Tavily, Firecrawl, Jina wrappers
│   └── alembic/                # Database migrations
└── frontend/
    └── src/
        ├── app/                # Next.js App Router pages
        │   ├── discover/       # Pipeline control room
        │   ├── companies/      # Company list + detail (Intel/Opps/Founders/Outreach tabs)
        │   ├── opportunities/  # Ranked by fit_score
        │   ├── crm/            # Kanban board (drag-and-drop)
        │   └── outreach/       # Message library with copy buttons
        ├── hooks/              # usePipeline, useCompanies, useOpportunities, useCRM
        ├── lib/                # API client + QueryClient
        └── types/              # TypeScript types
```

---

## Database Schema

| Table | Key Columns |
|-------|-------------|
| `companies` | name, website, mission, product_summary, tech_stack[], recent_launches[], status |
| `founders` | name, role, complaints[], background, raw_research |
| `opportunities` | title, category, description, impact, fit_score, fit_reasoning, pow_idea |
| `research` | agent_name, raw_input, raw_output, tokens_used, duration_ms |
| `contacts` | name, role, contact_type, status (not_contacted→offer) |
| `outreach` | channel, hook, why_company, why_problem, why_me, what_i_built, call_to_action, body |
| `pipeline_runs` | filters, status, current_agent, agents_done[], total_companies |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/pipeline/run` | Start pipeline (city, sector, max_companies, resume_text) |
| GET | `/api/pipeline/{id}/status` | Poll pipeline status |
| GET | `/api/companies` | List with filters |
| GET | `/api/companies/{id}` | Detail with nested opportunities, founders, outreach |
| GET | `/api/opportunities` | Ranked by fit_score |
| GET | `/api/outreach/{company_id}` | Outreach messages for a company |
| GET | `/api/crm/board` | Kanban grouped by status |
| POST | `/api/contacts` | Create contact |
| PATCH | `/api/contacts/{id}/status` | Move CRM stage |

---

## Setup

### Prerequisites

- Docker Desktop
- Python 3.11+
- Node.js 20+
- API keys: Anthropic, Tavily, Firecrawl

### 1. Clone and configure

```bash
git clone https://github.com/PavanSiddapuram/OCE.git
cd OCE
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Start infrastructure

```bash
docker compose up -d postgres redis
```

### 3. Run database migrations

```bash
cd backend
pip install -e .
alembic upgrade head
```

### 4. Start backend + worker

Terminal 1:
```bash
cd backend
uvicorn app.main:app --reload
```

Terminal 2:
```bash
cd backend
python -m arq app.tasks.worker.WorkerSettings
```

### 5. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

### Full Docker setup (optional)

```bash
docker compose up
```

---

## Usage

1. Go to **Discover** — select city, sector, set company limit, paste your resume
2. Click **Run Pipeline** — watch companies appear in real-time
3. Go to **Companies** — click any company to see Intelligence, Opportunities, Founders, Outreach tabs
4. Go to **Opportunities** — ranked by fit score, filter by category
5. Go to **Outreach** — copy LinkedIn/email/Twitter messages with one click
6. Go to **CRM** — drag contacts through the pipeline (Not Contacted → Offer)

---

## Build Order (Progress)

- [x] Phase 1: Foundation — docker-compose, models, alembic, FastAPI skeleton
- [x] Phase 2: Tools + Agent 1 — Tavily/Firecrawl/Jina wrappers, discovery agent, ARQ worker
- [x] Phase 3: Agents 2 + 3 — company intelligence + opportunity detection
- [x] Phase 4: Agents 4 + 5 — skill matching + proof-of-work generation
- [x] Phase 5: Agents 6 + 7 + 8 — founder research + narrative + CRM
- [x] Phase 6: Frontend — all pages, Kanban board, copy buttons, React Query polling
- [x] Phase 7: Hardening — rate limiting, retries, dedup, error states

---

## What Makes This Different

Most job tools optimize for **finding openings**.

This optimizes for **creating openings**.

The pipeline reinforces:

```
Skills → Build prototype
Visibility → Publish build log
Opportunity → Target startup
Consistency → Run every week
```

---

## License

MIT
