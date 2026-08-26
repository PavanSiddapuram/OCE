# FRONTIER OS — Personal Research-to-Evidence-to-Opportunity Operating System (OCE 2.0)

> **Core Philosophy**: Build only what compounds real work. Problem → Proof → People → Opportunity.

**FRONTIER OS** is a high-signal operating system built on top of the Opportunity Creation Engine (OCE) codebase. It is engineered specifically for a 6-to-7 month trajectory targeting **Google SWE / AI-ML / DeepMind Research Engineering** (Bengaluru & Global) while remaining adaptable for top high-growth tech startups.

---

## 🏛 System Architecture

```
                                  FRONTIER OS (OCE 2.0)
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Next.js 15 Web Application                              │
│                                                                                         │
│  Daily Command Center │ Track A: Mock Interview OS │ Track B: Research Lab & alphaXiv  │
│  Gemini Deep Research Agent (Interactions API) │ Evidence & Proof Studio │ People CRM   │
│  7-Signal Opportunity Engine │ Weekly Coordinator Control Plane                         │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │ HTTPS / SSE
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FastAPI Modular Monolith                                │
│                                                                                         │
│  ┌───────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────────┐  │
│  │   Interview Engine    │  │   Research Engine    │  │      Opportunity Engine      │  │
│  │  Adaptive Mock &      │  │ Deep Research Runner │  │  7-Signal Weighted Matcher   │  │
│  │  Failure Fingerprint  │  │ & Paper/Repo Lab     │  │   & Brief Generator          │  │
│  └───────────────────────┘  └──────────┬───────────┘  └──────────────────────────────┘  │
└──────────────┬─────────────────────────┼─────────────────────────────┼──────────────────┘
               │                         │                             │
               ▼                         ▼                             ▼
      ┌─────────────────┐       ┌─────────────────┐          ┌───────────────────┐
      │ PostgreSQL 16   │       │ Gemini Deep     │          │ alphaXiv MCP      │
      │ + pgvector      │       │ Research API    │          │ Client Connector  │
      └─────────────────┘       └────────┬────────┘          └─────────┬─────────┘
                                         │                             │
                                         ▼                             ▼
                               Gemini Interactions API        alphaXiv Server
                               (deep-research-max)            (https://api.alphaxiv.org)
```

---

## 🔑 Key Features & Components

### 1. Track A: Mock Interview Studio (`/interview`)
- **Frontier Question Sets**: 3D ray casting, ray-sphere intersection invariants, Bounding Volume Hierarchy (BVH) with Surface Area Heuristic (SAH), and memory-constrained pressure coding.
- **Failure Fingerprinting**: Automatically logs recurring candidate mistakes (e.g. boundary checks, time complexity derivations) to adjust question difficulty.
- **Rubric Scorecard**: Evaluates correctness, time/space complexity, communication, and edge case handling.

### 2. Track B: Research & Experiment Lab (`/research`)
- **Baseline & Ablation Experiment Tracker**: Logs commit SHAs, hardware configs, datasets, metrics (FPS, PSNR, VRAM), and automatically writes evidence claims.
- **alphaXiv MCP Corpus Explorer**: Native integration with the 19 tools of the alphaXiv Model Context Protocol server (`https://api.alphaxiv.org/mcp/v1`) for literature search, AI paper reports, and GitHub repo file tree browsing.
- **Gemini Deep Research Agent (Google Interactions API)**: Autonomous background analyst agent (`deep-research-preview-04-2026` & `deep-research-max-preview-04-2026`) supporting:
  - `background=True` async execution.
  - **Collaborative Planning**: Multi-turn plan review, refinement, and approval before execution.
  - `visualization="auto"`: Auto-generated benchmark charts and visualizations.
  - Remote alphaXiv MCP tool binding.

### 3. 7-Signal Opportunity Engine (`/opportunities`)
Calculates composite fit scores across 7 key weighted dimensions:
$$\text{Composite Score} = 0.30 \text{Fit} + 0.20 \text{Proof} + 0.15 \text{Problem} + 0.10 \text{Gap} + 0.10 \text{Network} + 0.10 \text{Role} + 0.05 \text{Edge}$$
- Generates structured **Opportunity Briefs** containing core problem, why now, why you, missing proof, build next, and conversation hooks.

### 4. People & Researcher CRM (`/crm`)
- **Kanban Pipeline**: `Not Contacted` → `Messaged` → `Replied` → `Meeting` → `Interview` → `Offer`.
- **alphaXiv Researcher Finder**: Graph search across paper authors, current affiliations ("Google DeepMind"), and citation metrics.

### 5. Evidence & Public Proof Studio (`/evidence`)
- Stores citation-grade evidence claims backed by repository URLs, benchmark numbers, and paper XML citations.

### 6. Weekly Coordinator Control Plane (`/weekly`)
- Sunday planner allocating max 3 "must-win" priorities and setting daily 60–90 minute focus blocks.

---

## 🛠 Tech Stack

- **Backend**: FastAPI + Python 3.14 / 3.11, AsyncSQLAlchemy, Pydantic v2.
- **Frontend**: Next.js 15 (App Router), React 19, Tailwind CSS, Lucide Icons.
- **LLM Engine**: Multi-provider adapter supporting Gemini 2.5/3.7 Pro & Flash (Default), Moonshot Kimi API, and DeepSeek V3/R1.
- **MCP Connector**: HTTP JSON-RPC 2.0 client for alphaXiv MCP server.
- **Research Agent**: Google Gemini Interactions API (`v1beta/interactions`, revision `2026-05-20`).
- **Database**: PostgreSQL 16 + pgvector (with automatic offline fallback mode).

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js 18+ & npm
- Python 3.11+
- (Optional) Docker & Docker Compose for PostgreSQL persistence

### 1. Environment Configuration
Create or edit `.env` in the workspace root:

```env
# Primary LLM Provider Configuration
LLM_PROVIDER=gemini

# Gemini API Key (Google AI Studio / Interactions API)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-pro

# alphaXiv MCP Configuration
ALPHAXIV_MCP_URL=https://api.alphaxiv.org/mcp/v1
ALPHAXIV_API_KEY=

# External Tools
TAVILY_API_KEY=
FIRECRAWL_API_KEY=

# Database Connection (Optional if running Postgres container)
DATABASE_URL=postgresql+asyncpg://oce:oce_dev@localhost:5432/oce
```

### 2. Start Backend API Server
```bash
cd backend
python -m py_compile app/main.py  # Verify syntax
uvicorn app.main:app --reload --port 8000
```
Backend API interactive docs: `http://localhost:8000/docs`

### 3. Start Frontend UI Server
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000/command` in your browser.

---

## 🧪 Verification & Testing

To run the Next.js production build check:
```bash
cd frontend
npm run build
```

To run PostgreSQL container:
```bash
docker compose up -d postgres
```
