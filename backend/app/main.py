from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import app_state, companies, contacts, crm, hiring_intelligence, opportunities, outreach, pipeline
from app.config import settings
from app.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Opportunity Creation Engine", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_extra_origins = [o.strip() for o in settings.extra_cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", *_extra_origins],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(opportunities.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(outreach.router, prefix="/api")
app.include_router(crm.router, prefix="/api")
app.include_router(app_state.router, prefix="/api")
app.include_router(hiring_intelligence.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
