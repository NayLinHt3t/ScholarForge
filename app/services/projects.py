from google.cloud import firestore

from app.collections import OUTLINES, PROJECTS, SAVED_RESOURCES
from app.models import Project


def create_project(db: firestore.Client, user_id: str, name: str) -> Project:
    doc_ref = db.collection(PROJECTS).document()
    project = Project(id=doc_ref.id, user_id=user_id, name=name.strip())
    doc_ref.set(project.to_firestore())
    return project


def list_projects(db: firestore.Client, user_id: str) -> list[Project]:
    docs = (
        db.collection(PROJECTS)
        .where(filter=firestore.FieldFilter("user_id", "==", user_id))
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .get()
    )
    return [Project.from_firestore(doc) for doc in docs]


def get_project(db: firestore.Client, project_id: str) -> Project | None:
    doc = db.collection(PROJECTS).document(project_id).get()
    return Project.from_firestore(doc) if doc.exists else None


def delete_project(db: firestore.Client, project_id: str) -> None:
    project_ref = db.collection(PROJECTS).document(project_id)
    for sub in (SAVED_RESOURCES, OUTLINES):
        for doc in project_ref.collection(sub).get():
            doc.reference.delete()
    project_ref.delete()
