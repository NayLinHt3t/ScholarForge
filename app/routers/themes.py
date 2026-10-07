from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import evidence as evidence_service
from app.services import library as library_service
from app.services import projects as project_service
from app.services import themes as themes_service

router = APIRouter(prefix="/projects/{project_id}/themes", tags=["themes"])
templates = Jinja2Templates(directory="app/templates")


def _guard(db, project_id, user):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return None, RedirectResponse(url="/projects", status_code=303)
    return project, None


@router.get("")
async def themes_list(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    themes = themes_service.list_themes(db, project_id)
    return templates.TemplateResponse("projects/themes.html", {
        "request": request,
        "user": user,
        "project": project,
        "themes": themes,
    })


@router.post("")
async def create_theme(
    project_id: str,
    name: str = Form(...),
    description: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    name = name.strip()
    if name:
        themes_service.create_theme(db, project_id, user.id, name=name, description=description)
    return RedirectResponse(url=f"/projects/{project_id}/themes", status_code=303)


@router.get("/{theme_id}")
async def theme_detail(
    project_id: str,
    theme_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    theme = themes_service.get_theme(db, project_id, theme_id)
    if not theme:
        return RedirectResponse(url=f"/projects/{project_id}/themes", status_code=303)
    all_evidence = evidence_service.list_evidence_for_project(db, project_id)
    sources = library_service.list_resources(db, project_id)
    source_map = {s.id: s for s in sources}
    linked_ids = set(theme.evidence_ids)
    return templates.TemplateResponse("projects/theme_detail.html", {
        "request": request,
        "user": user,
        "project": project,
        "theme": theme,
        "all_evidence": all_evidence,
        "source_map": source_map,
        "linked_ids": linked_ids,
    })


@router.post("/{theme_id}/edit")
async def edit_theme(
    project_id: str,
    theme_id: str,
    name: str = Form(...),
    description: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    name = name.strip()
    if name:
        themes_service.update_theme(db, project_id, theme_id, name=name, description=description)
    return RedirectResponse(url=f"/projects/{project_id}/themes/{theme_id}", status_code=303)


@router.post("/{theme_id}/link")
async def link_evidence(
    project_id: str,
    theme_id: str,
    evidence_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    themes_service.link_evidence(db, project_id, theme_id, evidence_id)
    return RedirectResponse(url=f"/projects/{project_id}/themes/{theme_id}", status_code=303)


@router.post("/{theme_id}/unlink")
async def unlink_evidence(
    project_id: str,
    theme_id: str,
    evidence_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    themes_service.unlink_evidence(db, project_id, theme_id, evidence_id)
    return RedirectResponse(url=f"/projects/{project_id}/themes/{theme_id}", status_code=303)


@router.post("/{theme_id}/delete")
async def delete_theme(
    project_id: str,
    theme_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    themes_service.delete_theme(db, project_id, theme_id)
    return RedirectResponse(url=f"/projects/{project_id}/themes", status_code=303)
