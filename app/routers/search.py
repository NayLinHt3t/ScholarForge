from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.exceptions import OllamaUnavailableError
from app.models import User
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
