from datetime import datetime, timezone

from google.cloud import firestore

from app.collections import (
    CLAIMS,
    EVIDENCE,
    NOTES,
    OUTLINE_SECTIONS,
    OUTLINES,
    PROJECTS,
    SAVED_RESOURCES,
    THEMES,
)
from app.models import Project

_ALL_SUBCOLLECTIONS = (
    SAVED_RESOURCES,
    OUTLINES,
    EVIDENCE,
    NOTES,
    THEMES,
    CLAIMS,
    OUTLINE_SECTIONS,
)


def create_project(
    db: firestore.Client, user_id: str, name: str, research_question: str = ""
) -> Project:
    doc_ref = db.collection(PROJECTS).document()
    project = Project(
        id=doc_ref.id,
        user_id=user_id,
        name=name.strip(),
        research_question=research_question.strip(),
    )
    doc_ref.set(project.to_firestore())
    return project


def list_projects(db: firestore.Client, user_id: str) -> list[Project]:
    docs = (
        db.collection(PROJECTS)
        .where(filter=firestore.FieldFilter("user_id", "==", user_id))
        .get()
    )
    projects = [Project.from_firestore(doc) for doc in docs]
    return sorted(projects, key=lambda p: p.created_at, reverse=True)


def get_project(db: firestore.Client, project_id: str) -> Project | None:
    doc = db.collection(PROJECTS).document(project_id).get()
    return Project.from_firestore(doc) if doc.exists else None


def update_project(
    db: firestore.Client, project_id: str, name: str, research_question: str
) -> None:
    db.collection(PROJECTS).document(project_id).update({
        "name": name.strip(),
        "research_question": research_question.strip(),
        "updated_at": datetime.now(timezone.utc),
    })


def update_citation_style(db: firestore.Client, project_id: str, style: str) -> None:
    from app.services.citations import STYLES
    if style not in STYLES:
        return
    db.collection(PROJECTS).document(project_id).update({
        "citation_style": style,
        "updated_at": datetime.now(timezone.utc),
    })


def get_dashboard_counts(db: firestore.Client, project_id: str) -> dict[str, int]:
    project_ref = db.collection(PROJECTS).document(project_id)
    return {
        "sources": len(project_ref.collection(SAVED_RESOURCES).get()),
        "evidence": len(project_ref.collection(EVIDENCE).get()),
        "notes": len(project_ref.collection(NOTES).get()),
        "themes": len(project_ref.collection(THEMES).get()),
        "claims": len(project_ref.collection(CLAIMS).get()),
        "sections": len(project_ref.collection(OUTLINE_SECTIONS).get()),
    }


def delete_project(db: firestore.Client, project_id: str) -> None:
    project_ref = db.collection(PROJECTS).document(project_id)
    for sub in _ALL_SUBCOLLECTIONS:
        for doc in project_ref.collection(sub).get():
            doc.reference.delete()
    project_ref.delete()
