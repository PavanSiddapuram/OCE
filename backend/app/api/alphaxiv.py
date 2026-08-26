from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.connectors.alphaxiv_mcp import alphaxiv_mcp

router = APIRouter(prefix="/alphaxiv", tags=["alphaxiv"])


class DiscoverPapersRequest(BaseModel):
    keywords: List[str]
    question: str
    difficulty: int = 5
    published_after: Optional[str] = None
    prioritize: str = "default"


class PaperContentRequest(BaseModel):
    url: str
    full_text: bool = False
    queries: Optional[List[str]] = None


class ReadRepoRequest(BaseModel):
    github_url: str
    path: str = "/"


class FindResearchersRequest(BaseModel):
    query: Optional[str] = None
    topic: Optional[str] = None
    affiliation: Optional[str] = None
    role: Optional[str] = None
    limit: int = 12


class SavePaperRequest(BaseModel):
    paper_ids_or_urls: List[str]
    folder_id: Optional[str] = None


@router.post("/discover")
async def discover_papers(req: DiscoverPapersRequest):
    """Run topical literature discovery against alphaXiv corpus."""
    res = await alphaxiv_mcp.discover_papers(
        keywords=req.keywords,
        question=req.question,
        difficulty=req.difficulty,
        published_after=req.published_after,
        prioritize=req.prioritize,
    )
    return res


@router.post("/paper")
async def get_paper_content(req: PaperContentRequest):
    """Fetch paper AI report/text, or answer XML PDF queries."""
    if req.queries:
        res = await alphaxiv_mcp.answer_pdf_queries(paper=req.url, queries=req.queries)
        return res

    res = await alphaxiv_mcp.get_paper_content(url=req.url, full_text=req.full_text)
    return res


@router.post("/repo")
async def read_github_repo(req: ReadRepoRequest):
    """Read file trees and file contents from a paper's GitHub codebase repository."""
    res = await alphaxiv_mcp.read_files_from_github_repository(github_url=req.github_url, path=req.path)
    return res


@router.post("/researchers")
async def find_researchers(req: FindResearchersRequest):
    """Find researchers by topic, organization (e.g. Google DeepMind), or career history."""
    res = await alphaxiv_mcp.find_researchers(
        query=req.query,
        topic=req.topic,
        affiliation=req.affiliation,
        role=req.role,
        limit=req.limit,
    )
    return res


@router.get("/library")
async def list_library(include_papers: bool = True):
    """List library reading folders and papers."""
    res = await alphaxiv_mcp.list_library(include_papers=include_papers)
    return res


@router.post("/library/save")
async def save_paper(req: SavePaperRequest):
    """Save paper to user library folder."""
    res = await alphaxiv_mcp.save_papers_to_folder(paper_ids_or_urls=req.paper_ids_or_urls, folder_id=req.folder_id)
    return res
