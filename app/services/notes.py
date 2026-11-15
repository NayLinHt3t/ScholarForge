from datetime import datetime, timezone

from google.cloud import firestore

from app.collections import NOTES, PROJECTS
from app.models.note import Note


def _ref(db: firestore.Client, project_id: str):
    return db.collection(PROJECTS).document(project_id).collection(NOTES)


def create_note(
    db: firestore.Client,
    project_id: str,
    user_id: str,
    body: str,
    title: str = "",
    source_id: str | None = None,
    source_title: str = "",
) -> Note:
    doc_ref = _ref(db, project_id).document()
    note = Note(
        id=doc_ref.id,
        project_id=project_id,
        user_id=user_id,
        title=title.strip(),
        body=body.strip(),
        source_id=source_id,
        source_title=source_title,
    )
    doc_ref.set(note.to_firestore())
    return note


def list_notes(db: firestore.Client, project_id: str) -> list[Note]:
    docs = _ref(db, project_id).order_by("created_at", direction=firestore.Query.DESCENDING).get()
    return [Note.from_firestore(d) for d in docs]


def get_note(db: firestore.Client, project_id: str, note_id: str) -> Note | None:
    doc = _ref(db, project_id).document(note_id).get()
    return Note.from_firestore(doc) if doc.exists else None


def update_note(
    db: firestore.Client, project_id: str, note_id: str, title: str, body: str,
    **link,
) -> None:
    """Update a note. Pass source_id=/source_title= to change the linked paper."""
    updates = {
        "title": title.strip(),
        "body": body.strip(),
        "updated_at": datetime.now(timezone.utc),
    }
    for key in ("source_id", "source_title"):
        if key in link:
            updates[key] = link[key]
    _ref(db, project_id).document(note_id).update(updates)


def delete_note(db: firestore.Client, project_id: str, note_id: str) -> None:
    _ref(db, project_id).document(note_id).delete()


def count_for_project(db: firestore.Client, project_id: str) -> int:
    return len(_ref(db, project_id).get())
