from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.exceptions import OllamaUnavailableError
from app.models import User
from app.services import library as library_service
from app.services import projects as project_service
from app.services import summary as summary_service

router = APIRouter(tags=["summary"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/projects/{project_id}/summarize")
async def summarize_page(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)
    resources = library_service.list_resources(db, project_id)
    return templates.TemplateResponse(
        "projects/summary.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "resources": resources,
            "result": None,
            "ollama_down": False,
            "invalid_markers": [],
        },
    )


@router.post("/projects/{project_id}/summarize")
async def generate_summary(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)

    form = await request.form()
    resource_ids = form.getlist("resource_ids")
    resources = library_service.list_resources(db, project_id)

    if not resource_ids:
        return templates.TemplateResponse(
            "projects/summary.html",
            {
                "request": request,
                "user": user,
                "project": project,
                "resources": resources,
                "result": None,
                "ollama_down": False,
                "invalid_markers": [],
                "error": "Select at least one source to summarize.",
            },
        )

    try:
        result = await summary_service.generate(
            db=db,
            project_id=project_id,
            project_name=project.name,
            resource_ids=resource_ids,
            citation_style=project.citation_style,
        )
    except OllamaUnavailableError:
        return templates.TemplateResponse(
            "projects/summary.html",
            {
                "request": request,
                "user": user,
                "project": project,
                "resources": resources,
                "result": None,
                "ollama_down": True,
                "invalid_markers": [],
                "selected_ids": resource_ids,
            },
        )
    except ValueError:
        return RedirectResponse(url=f"/projects/{project_id}/summarize", status_code=303)

    return templates.TemplateResponse(
        "projects/summary.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "resources": resources,
            "result": result,
            "ollama_down": False,
            "invalid_markers": result.invalid_markers if not result.success else [],
            "selected_ids": resource_ids,
        },
    )
