from google.cloud import firestore

from app.collections import PROJECTS, THEMES
from app.models.theme import Theme


def _ref(db: firestore.Client, project_id: str):
    return db.collection(PROJECTS).document(project_id).collection(THEMES)


def create_theme(
    db: firestore.Client,
    project_id: str,
    user_id: str,
    name: str,
    description: str = "",
) -> Theme:
    doc_ref = _ref(db, project_id).document()
    theme = Theme(
        id=doc_ref.id,
        project_id=project_id,
        user_id=user_id,
        name=name.strip(),
        description=description.strip(),
    )
    doc_ref.set(theme.to_firestore())
    return theme


def list_themes(db: firestore.Client, project_id: str) -> list[Theme]:
    docs = _ref(db, project_id).order_by("created_at").get()
    return [Theme.from_firestore(d) for d in docs]


def get_theme(db: firestore.Client, project_id: str, theme_id: str) -> Theme | None:
    doc = _ref(db, project_id).document(theme_id).get()
    return Theme.from_firestore(doc) if doc.exists else None


def update_theme(
    db: firestore.Client,
    project_id: str,
    theme_id: str,
    name: str,
    description: str,
) -> None:
    _ref(db, project_id).document(theme_id).update({
        "name": name.strip(),
        "description": description.strip(),
    })


def link_evidence(db: firestore.Client, project_id: str, theme_id: str, evidence_id: str) -> None:
    _ref(db, project_id).document(theme_id).update({
        "evidence_ids": firestore.ArrayUnion([evidence_id])
    })


def unlink_evidence(db: firestore.Client, project_id: str, theme_id: str, evidence_id: str) -> None:
    _ref(db, project_id).document(theme_id).update({
        "evidence_ids": firestore.ArrayRemove([evidence_id])
    })


def delete_theme(db: firestore.Client, project_id: str, theme_id: str) -> None:
    _ref(db, project_id).document(theme_id).delete()


def count_for_project(db: firestore.Client, project_id: str) -> int:
    return len(_ref(db, project_id).get())
