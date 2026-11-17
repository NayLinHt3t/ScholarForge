from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from app.templating import templates
from google.cloud import firestore

from app.clients import ai, semantic_scholar as ss_client
from app.database import get_db
from app.dependencies import require_auth
from app.exceptions import DuplicateResourceError, OllamaUnavailableError
from app.models import User
from app.services import library as library_service
from app.services import paper_link
from app.services import projects as project_service
from app.services import search as search_service

router = APIRouter(tags=["search"])


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
    ranked = True

    if q.strip():
        try:
            resp = await search_service.run(q.strip())
            results = resp.results
            low_confidence = resp.low_confidence
            source_errors = resp.source_errors
            ranked = resp.ranked
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
            "ranked": ranked,
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
    try:
        info = await paper_link.resolve(paper_url)
    except paper_link.LinkError as e:
        if e.kind == "manual":
            # A link we can't look up (e.g. a PDF with no DOI): let the student type the
            # details, with the link already filled in.
            return RedirectResponse(
                url=f"/projects/{project_id}/sources?link={quote(paper_url.strip())}", status_code=303)
        return RedirectResponse(url=f"{base}?url_error={e.kind}", status_code=303)

    embedding = None
    try:
        embedding = await ai.embed(f"{info.title}. {info.abstract or ''}")
    except OllamaUnavailableError:
        pass

    try:
        library_service.save_resource(
            db, project_id,
            title=info.title,
            authors=info.authors,
            year=info.year,
            venue=info.venue,
            doi=info.doi,
            arxiv_id=info.arxiv_id,
            url=info.best_url,          # PDF first, then DOI / arXiv / landing page
            abstract=info.abstract,
            source=info.source,
            embedding=embedding,
            access_status="open_access" if info.pdf_url else "unknown",
        )
    except DuplicateResourceError:
        return RedirectResponse(url=f"{base}?duplicate=1", status_code=303)
    return RedirectResponse(url=f"{base}?saved=1", status_code=303)
