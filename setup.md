# OCE Setup Guide

## 1. Add your API keys

Copy `.env.example` to `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
FIRECRAWL_API_KEY=fc-...
```

## 2. Start the database and Redis

```bash
docker compose up -d postgres redis
```

Wait ~5 seconds for postgres to be healthy, then run migrations:

```bash
cd backend
pip install -e .
alembic upgrade head
```

## 3. Start the backend

In one terminal:
```bash
cd backend
uvicorn app.main:app --reload
```

## 4. Start the ARQ worker

In another terminal:
```bash
cd backend
python -m arq app.tasks.worker.WorkerSettings
```

## 5. Start the frontend

In another terminal:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## 6. Run your first pipeline

1. Go to http://localhost:3000/discover
2. Select city: Bengaluru, sector: AI
3. Set max companies to 10
4. Paste your resume text
5. Click **Run Pipeline**
6. Watch companies appear as Agent 1 runs
7. Navigate to /companies to see intelligence and opportunities

## Pipeline flow

```
Agent 1 → discovers startups (Tavily search)
Agent 2 → scrapes each company website (Firecrawl)
Agent 3 → detects 3-5 opportunities per company (Claude)
Agent 4 → scores your fit per opportunity (Claude)
Agent 5 → generates PoW mini-project ideas (Claude)
Agent 6 → researches founders (Tavily + Jina)
Agent 7 → writes personalized outreach (Claude)
Agent 8 → creates CRM contacts
```

Typical time for 10 companies: ~15-25 minutes

## Full Docker setup (optional)

To run everything in Docker:
```bash
docker compose up
```

Then open http://localhost:3000
