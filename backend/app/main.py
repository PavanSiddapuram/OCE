from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import (
    alphaxiv,
    companies,
    contacts,
    crm,
    evidence,
    interview,
    me,
    opportunities,
    outreach,
    pipeline,
    research,
    weekly,
)
from app.database import Base, engine
from app.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try to initialize database tables on startup if PostgreSQL is running
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Warning: PostgreSQL is not reachable at localhost:5432 ({e}). Running in resilient fallback mode until Postgres is started.")
    yield


app = FastAPI(title="FRONTIER OS — Opportunity Creation Engine", version="2.0.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Permissive CORS middleware for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"},
    )


app.include_router(me.router, prefix="/api")
app.include_router(weekly.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(research.router, prefix="/api")
app.include_router(alphaxiv.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")
app.include_router(opportunities.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(outreach.router, prefix="/api")
app.include_router(crm.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "system": "FRONTIER OS"}
