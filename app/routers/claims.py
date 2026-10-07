from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import claims as claims_service
from app.services import evidence as evidence_service
from app.services import library as library_service
from app.services import projects as project_service
from app.services import themes as themes_service

router = APIRouter(prefix="/projects/{project_id}/claims", tags=["claims"])
templates = Jinja2Templates(directory="app/templates")


def _guard(db, project_id, user):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return None, RedirectResponse(url="/projects", status_code=303)
    return project, None


@router.get("")
async def claims_list(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    all_claims = claims_service.list_claims(db, project_id)
    return templates.TemplateResponse("projects/claims.html", {
        "request": request,
        "user": user,
        "project": project,
        "claims": all_claims,
    })


@router.post("")
async def create_claim(
    project_id: str,
    statement: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    statement = statement.strip()
    if statement:
        claims_service.create_claim(db, project_id, user.id, statement=statement)
    return RedirectResponse(url=f"/projects/{project_id}/claims", status_code=303)


@router.get("/{claim_id}")
async def claim_detail(
    project_id: str,
    claim_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    claim = claims_service.get_claim(db, project_id, claim_id)
    if not claim:
        return RedirectResponse(url=f"/projects/{project_id}/claims", status_code=303)
    all_evidence = evidence_service.list_evidence_for_project(db, project_id)
    sources = library_service.list_resources(db, project_id)
    source_map = {s.id: s for s in sources}
    all_themes = themes_service.list_themes(db, project_id)
    return templates.TemplateResponse("projects/claim_detail.html", {
        "request": request,
        "user": user,
        "project": project,
        "claim": claim,
        "all_evidence": all_evidence,
        "source_map": source_map,
        "all_themes": all_themes,
        "linked_evidence_ids": set(claim.evidence_ids),
        "linked_theme_ids": set(claim.theme_ids),
    })


@router.post("/{claim_id}/edit")
async def edit_claim(
    project_id: str,
    claim_id: str,
    statement: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    statement = statement.strip()
    if statement:
        claims_service.update_claim_statement(db, project_id, claim_id, statement)
    return RedirectResponse(url=f"/projects/{project_id}/claims/{claim_id}", status_code=303)


@router.post("/{claim_id}/link-evidence")
async def link_evidence(
    project_id: str,
    claim_id: str,
    evidence_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    claims_service.link_evidence(db, project_id, claim_id, evidence_id)
    return RedirectResponse(url=f"/projects/{project_id}/claims/{claim_id}", status_code=303)


@router.post("/{claim_id}/unlink-evidence")
async def unlink_evidence(
    project_id: str,
    claim_id: str,
    evidence_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    claims_service.unlink_evidence(db, project_id, claim_id, evidence_id)
    return RedirectResponse(url=f"/projects/{project_id}/claims/{claim_id}", status_code=303)


@router.post("/{claim_id}/link-theme")
async def link_theme(
    project_id: str,
    claim_id: str,
    theme_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    claims_service.link_theme(db, project_id, claim_id, theme_id)
    return RedirectResponse(url=f"/projects/{project_id}/claims/{claim_id}", status_code=303)


@router.post("/{claim_id}/unlink-theme")
async def unlink_theme(
    project_id: str,
    claim_id: str,
    theme_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    claims_service.unlink_theme(db, project_id, claim_id, theme_id)
    return RedirectResponse(url=f"/projects/{project_id}/claims/{claim_id}", status_code=303)


@router.post("/{claim_id}/delete")
async def delete_claim(
    project_id: str,
    claim_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    claims_service.delete_claim(db, project_id, claim_id)
    return RedirectResponse(url=f"/projects/{project_id}/claims", status_code=303)
