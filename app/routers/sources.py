from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.models.resource import ACCESS_STATUSES, READ_STATUSES, SOURCE_TYPES
from app.services import library as library_service
from app.services import projects as project_service
from app.services import evidence as evidence_service
from app.services.citations import STYLES as CITATION_STYLES, format_one

router = APIRouter(prefix="/projects/{project_id}/sources", tags=["sources"])
templates = Jinja2Templates(directory="app/templates")


def _guard(db, project_id, user):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return None, RedirectResponse(url="/projects", status_code=303)
    return project, None


@router.get("")
async def sources_list(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sources = library_service.list_resources(db, project_id)
    ev_counts = {
        s.id: evidence_service.count_for_source(db, project_id, s.id)
        for s in sources
    }
    return templates.TemplateResponse("projects/sources.html", {
        "request": request,
        "user": user,
        "project": project,
        "sources": sources,
        "ev_counts": ev_counts,
        "source_types": SOURCE_TYPES,
        "read_statuses": READ_STATUSES,
        "access_statuses": ACCESS_STATUSES,
    })


@router.post("")
async def add_source(
    project_id: str,
    request: Request,
    title: str = Form(...),
    authors_raw: str = Form(default=""),
    year: str = Form(default=""),
    venue: str = Form(default=""),
    doi: str = Form(default=""),
    url: str = Form(default=""),
    abstract: str = Form(default=""),
    source_type: str = Form(default="journal_article"),
    access_status: str = Form(default="unknown"),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir

    title = title.strip()
    if not title:
        sources = library_service.list_resources(db, project_id)
        ev_counts = {s.id: evidence_service.count_for_source(db, project_id, s.id) for s in sources}
        return templates.TemplateResponse("projects/sources.html", {
            "request": request,
            "user": user,
            "project": project,
            "sources": sources,
            "ev_counts": ev_counts,
            "source_types": SOURCE_TYPES,
            "read_statuses": READ_STATUSES,
            "access_statuses": ACCESS_STATUSES,
            "error": "Title is required.",
        }, status_code=400)

    authors = [a.strip() for a in authors_raw.split(",") if a.strip()]
    year_int = int(year.strip()) if year.strip().isdigit() else None

    try:
        library_service.save_resource(
            db=db,
            project_id=project_id,
            title=title,
            authors=authors,
            year=year_int,
            venue=venue.strip() or None,
            doi=doi.strip() or None,
            arxiv_id=None,
            url=url.strip() or None,
            abstract=abstract.strip() or None,
            source="manual",
            embedding=None,
            source_type=source_type if source_type in SOURCE_TYPES else "journal_article",
            read_status="unread",
            source_note="",
            access_status=access_status if access_status in ACCESS_STATUSES else "unknown",
        )
    except Exception:
        pass  # duplicate or other error — continue to list

    return RedirectResponse(url=f"/projects/{project_id}/sources", status_code=303)


@router.get("/{source_id}")
async def source_detail(
    project_id: str,
    source_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    source = library_service.get_resource(db, project_id, source_id)
    if not source:
        return RedirectResponse(url=f"/projects/{project_id}/sources", status_code=303)
    evidence_items = evidence_service.list_evidence_for_source(db, project_id, source_id)
    citation = format_one(source, project.citation_style)
    return templates.TemplateResponse("projects/source_detail.html", {
        "request": request,
        "user": user,
        "project": project,
        "source": source,
        "evidence_items": evidence_items,
        "citation": citation,
        "read_statuses": READ_STATUSES,
        "access_statuses": ACCESS_STATUSES,
        "source_types": SOURCE_TYPES,
    })


@router.post("/{source_id}/status")
async def update_read_status(
    project_id: str,
    source_id: str,
    read_status: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    if read_status in READ_STATUSES:
        library_service.update_source(db, project_id, source_id, read_status=read_status)
    return RedirectResponse(url=f"/projects/{project_id}/sources/{source_id}", status_code=303)


@router.post("/{source_id}/note")
async def update_source_note(
    project_id: str,
    source_id: str,
    source_note: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    library_service.update_source(db, project_id, source_id, source_note=source_note.strip())
    return RedirectResponse(url=f"/projects/{project_id}/sources/{source_id}", status_code=303)


@router.post("/{source_id}/delete")
async def delete_source(
    project_id: str,
    source_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    # delete all evidence for this source first
    ev_items = evidence_service.list_evidence_for_source(db, project_id, source_id)
    for ev in ev_items:
        evidence_service.delete_evidence(db, project_id, ev.id)
    library_service.delete_resource(db, project_id, source_id)
    return RedirectResponse(url=f"/projects/{project_id}/sources", status_code=303)
