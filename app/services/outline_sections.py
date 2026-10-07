from google.cloud import firestore

from app.collections import OUTLINE_SECTIONS, PROJECTS
from app.models.outline_section import OutlineSection


def _ref(db: firestore.Client, project_id: str):
    return db.collection(PROJECTS).document(project_id).collection(OUTLINE_SECTIONS)


def add_section(
    db: firestore.Client,
    project_id: str,
    user_id: str,
    title: str,
    order_index: int,
) -> OutlineSection:
    doc_ref = _ref(db, project_id).document()
    section = OutlineSection(
        id=doc_ref.id,
        project_id=project_id,
        user_id=user_id,
        title=title.strip(),
        order_index=order_index,
    )
    doc_ref.set(section.to_firestore())
    return section


def list_sections(db: firestore.Client, project_id: str) -> list[OutlineSection]:
    docs = _ref(db, project_id).order_by("order_index").get()
    return [OutlineSection.from_firestore(d) for d in docs]


def get_section(db: firestore.Client, project_id: str, section_id: str) -> OutlineSection | None:
    doc = _ref(db, project_id).document(section_id).get()
    return OutlineSection.from_firestore(doc) if doc.exists else None


def update_section(
    db: firestore.Client,
    project_id: str,
    section_id: str,
    title: str,
    writing_notes: str,
) -> None:
    _ref(db, project_id).document(section_id).update({
        "title": title.strip(),
        "writing_notes": writing_notes.strip(),
    })


def reorder_section(
    db: firestore.Client, project_id: str, section_id: str, new_index: int
) -> None:
    _ref(db, project_id).document(section_id).update({"order_index": new_index})


def link_claim(db: firestore.Client, project_id: str, section_id: str, claim_id: str) -> None:
    _ref(db, project_id).document(section_id).update({
        "claim_ids": firestore.ArrayUnion([claim_id])
    })


def unlink_claim(db: firestore.Client, project_id: str, section_id: str, claim_id: str) -> None:
    _ref(db, project_id).document(section_id).update({
        "claim_ids": firestore.ArrayRemove([claim_id])
    })


def link_evidence(db: firestore.Client, project_id: str, section_id: str, evidence_id: str) -> None:
    _ref(db, project_id).document(section_id).update({
        "evidence_ids": firestore.ArrayUnion([evidence_id])
    })


def unlink_evidence(db: firestore.Client, project_id: str, section_id: str, evidence_id: str) -> None:
    _ref(db, project_id).document(section_id).update({
        "evidence_ids": firestore.ArrayRemove([evidence_id])
    })


def delete_section(db: firestore.Client, project_id: str, section_id: str) -> None:
    _ref(db, project_id).document(section_id).delete()


def count_for_project(db: firestore.Client, project_id: str) -> int:
    return len(_ref(db, project_id).get())
