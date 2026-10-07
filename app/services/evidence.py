from google.cloud import firestore

from app.collections import EVIDENCE, PROJECTS
from app.models.evidence import Evidence


def _ref(db: firestore.Client, project_id: str):
    return db.collection(PROJECTS).document(project_id).collection(EVIDENCE)


def add_evidence(
    db: firestore.Client,
    project_id: str,
    source_id: str,
    user_id: str,
    quote: str,
    page_reference: str = "",
    student_note: str = "",
) -> Evidence:
    doc_ref = _ref(db, project_id).document()
    ev = Evidence(
        id=doc_ref.id,
        project_id=project_id,
        source_id=source_id,
        user_id=user_id,
        quote=quote.strip(),
        page_reference=page_reference.strip(),
        student_note=student_note.strip(),
    )
    doc_ref.set(ev.to_firestore())
    return ev


def list_evidence_for_project(db: firestore.Client, project_id: str) -> list[Evidence]:
    docs = _ref(db, project_id).order_by("created_at").get()
    return [Evidence.from_firestore(d) for d in docs]


def list_evidence_for_source(
    db: firestore.Client, project_id: str, source_id: str
) -> list[Evidence]:
    docs = (
        _ref(db, project_id)
        .where(filter=firestore.FieldFilter("source_id", "==", source_id))
        .get()
    )
    items = [Evidence.from_firestore(d) for d in docs]
    return sorted(items, key=lambda e: e.created_at)


def get_evidence(db: firestore.Client, project_id: str, evidence_id: str) -> Evidence | None:
    doc = _ref(db, project_id).document(evidence_id).get()
    return Evidence.from_firestore(doc) if doc.exists else None


def update_evidence(
    db: firestore.Client,
    project_id: str,
    evidence_id: str,
    quote: str,
    page_reference: str,
    student_note: str,
) -> None:
    _ref(db, project_id).document(evidence_id).update({
        "quote": quote.strip(),
        "page_reference": page_reference.strip(),
        "student_note": student_note.strip(),
    })


def delete_evidence(db: firestore.Client, project_id: str, evidence_id: str) -> None:
    _ref(db, project_id).document(evidence_id).delete()


def count_for_project(db: firestore.Client, project_id: str) -> int:
    return len(_ref(db, project_id).get())


def count_for_source(db: firestore.Client, project_id: str, source_id: str) -> int:
    docs = (
        _ref(db, project_id)
        .where(filter=firestore.FieldFilter("source_id", "==", source_id))
        .get()
    )
    return len(docs)
