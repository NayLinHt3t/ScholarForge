from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.clients import ollama, semantic_scholar as ss_client
from app.database import get_db
from app.dependencies import require_auth
from app.exceptions import DuplicateResourceError, OllamaUnavailableError
from app.models import User
from app.services import library as library_service
from app.services import projects as project_service
from app.services import search as search_service

router = APIRouter(tags=["search"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/projects/{project_id}/search")
async def search_page(
    project_id: str,
    request: Request,
    q: str = "",
    saved: str = "",
    duplicate: str = "",
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)

    results = []
    low_confidence = False
    source_errors: list[str] = []
    ollama_down = False

    if q.strip():
        try:
            resp = await search_service.run(q.strip())
            results = resp.results
            low_confidence = resp.low_confidence
            source_errors = resp.source_errors
        except OllamaUnavailableError:
            ollama_down = True

    return templates.TemplateResponse(
        "projects/search.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "q": q,
            "results": results,
            "low_confidence": low_confidence,
            "source_errors": source_errors,
            "ollama_down": ollama_down,
            "flash_saved": bool(saved),
            "flash_duplicate": bool(duplicate),
            "current_url": f"/projects/{project_id}/search?q={quote(q)}",
        },
    )


@router.post("/projects/{project_id}/search/add-by-url")
async def add_by_url(
    project_id: str,
    request: Request,
    paper_url: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)

    base = f"/projects/{project_id}/search"
    paper_id = ss_client.extract_paper_id(paper_url.strip())
    if not paper_id:
        return RedirectResponse(url=f"{base}?url_error=invalid", status_code=303)

    try:
        raw = await ss_client.fetch_by_id(paper_id)
    except Exception:
        return RedirectResponse(url=f"{base}?url_error=fetch", status_code=303)

    if not raw:
        return RedirectResponse(url=f"{base}?url_error=notfound", status_code=303)

    ext = raw.get("externalIds") or {}
    title = raw.get("title") or ""
    authors = [a["name"] for a in (raw.get("authors") or [])]
    abstract = raw.get("abstract")

    embedding = None
    try:
        embedding = await ollama.embed(f"{title}. {abstract or ''}")
    except OllamaUnavailableError:
        pass

    try:
        library_service.save_resource(
            db, project_id,
            title=title,
            authors=authors,
            year=raw.get("year"),
            venue=raw.get("venue") or None,
            doi=ext.get("DOI"),
            arxiv_id=ext.get("ArXiv"),
            url=raw.get("url"),
            abstract=abstract,
            source="semantic_scholar",
            embedding=embedding,
        )
    except DuplicateResourceError:
        return RedirectResponse(url=f"{base}?duplicate=1", status_code=303)
    return RedirectResponse(url=f"{base}?saved=1", status_code=303)
