from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import library as library_service
from app.services import outline as outline_service
from app.services import projects as project_service
from app.services.citations import STYLES as CITATION_STYLES

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
async def projects_list(
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    projects = project_service.list_projects(db, user.id)
    return templates.TemplateResponse(
        "projects/list.html",
        {"request": request, "user": user, "projects": projects},
    )


@router.post("")
async def create_project(
    request: Request,
    name: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    name = name.strip()
    if not name:
        projects = project_service.list_projects(db, user.id)
        return templates.TemplateResponse(
            "projects/list.html",
            {"request": request, "user": user, "projects": projects, "error": "Project name cannot be empty."},
            status_code=400,
        )
    project_service.create_project(db, user.id, name)
    return RedirectResponse(url="/projects", status_code=303)


@router.get("/{project_id}")
async def project_detail(
    project_id: str,
    request: Request,
    saved: str = "",
    duplicate: str = "",
    ollama_down: str = "",
    gen_error: str = "",
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)
    resources = library_service.list_resources(db, project_id)
    outlines = outline_service.list_outlines(db, project_id)
    return templates.TemplateResponse(
        "projects/detail.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "resources": resources,
            "outlines": outlines,
            "citation_styles": CITATION_STYLES,
            "flash_saved": bool(saved),
            "flash_duplicate": bool(duplicate),
            "flash_ollama_down": bool(ollama_down),
            "flash_gen_error": bool(gen_error),
        },
    )


@router.get("/{project_id}/delete")
async def confirm_delete_page(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)
    return templates.TemplateResponse(
        "projects/confirm_delete.html",
        {"request": request, "project": project},
    )


@router.post("/{project_id}/delete")
async def delete_project(
    project_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if project and project.user_id == user.id:
        project_service.delete_project(db, project_id)
    return RedirectResponse(url="/projects", status_code=303)
