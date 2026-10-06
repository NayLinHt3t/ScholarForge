import json
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.clients import ollama
from app.database import get_db
from app.dependencies import require_auth
from app.exceptions import DuplicateResourceError, OllamaUnavailableError
from app.models import User
from app.services import library as library_service
from app.services import projects as project_service

router = APIRouter(tags=["library"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/projects/{project_id}/library")
async def save_resource(
    project_id: str,
    title: str = Form(...),
    authors: str = Form(default="[]"),
    year: str = Form(default=""),
    venue: str = Form(default=""),
    doi: str = Form(default=""),
    arxiv_id: str = Form(default=""),
    url: str = Form(default=""),
    abstract: str = Form(default=""),
    source: str = Form(...),
    return_to: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)

    try:
        parsed_authors: list[str] = json.loads(authors)
    except (json.JSONDecodeError, ValueError):
        parsed_authors = []

    embedding: list[float] | None = None
    try:
        embedding = await ollama.embed(f"{title}. {abstract or ''}")
    except OllamaUnavailableError:
        pass  # save without embedding; RAG generation will require Ollama later

    dest = return_to if return_to else f"/projects/{project_id}"
    sep = "&" if "?" in dest else "?"

    try:
        library_service.save_resource(
            db=db,
            project_id=project_id,
            title=title,
            authors=parsed_authors,
            year=int(year) if year.strip().isdigit() else None,
            venue=venue or None,
            doi=doi or None,
            arxiv_id=arxiv_id or None,
            url=url or None,
            abstract=abstract or None,
            source=source,
            embedding=embedding,
        )
        return RedirectResponse(url=f"{dest}{sep}saved=1", status_code=303)
    except DuplicateResourceError:
        return RedirectResponse(url=f"{dest}{sep}duplicate=1", status_code=303)


@router.post("/projects/{project_id}/library/{resource_id}/delete")
async def delete_resource(
    project_id: str,
    resource_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)
    library_service.delete_resource(db, project_id, resource_id)
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
