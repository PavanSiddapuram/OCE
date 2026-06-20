from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import companies, contacts, crm, opportunities, outreach, pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Opportunity Creation Engine", version="0.1.0", lifespan=lifespan)

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
