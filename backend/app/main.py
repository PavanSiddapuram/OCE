from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import companies, contacts, crm, opportunities, outreach, pipeline
from app.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Opportunity Creation Engine", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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


@app.get("/health")
async def health():
    return {"status": "ok"}
