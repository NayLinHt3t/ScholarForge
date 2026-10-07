from google.cloud import firestore

from app.collections import CLAIMS, PROJECTS
from app.models.claim import Claim


def _ref(db: firestore.Client, project_id: str):
    return db.collection(PROJECTS).document(project_id).collection(CLAIMS)


def create_claim(
    db: firestore.Client,
    project_id: str,
    user_id: str,
    statement: str,
) -> Claim:
    doc_ref = _ref(db, project_id).document()
    claim = Claim(
        id=doc_ref.id,
        project_id=project_id,
        user_id=user_id,
        statement=statement.strip(),
    )
    doc_ref.set(claim.to_firestore())
    return claim


def list_claims(db: firestore.Client, project_id: str) -> list[Claim]:
    docs = _ref(db, project_id).order_by("created_at").get()
    return [Claim.from_firestore(d) for d in docs]


def get_claim(db: firestore.Client, project_id: str, claim_id: str) -> Claim | None:
    doc = _ref(db, project_id).document(claim_id).get()
    return Claim.from_firestore(doc) if doc.exists else None


def update_claim_statement(
    db: firestore.Client, project_id: str, claim_id: str, statement: str
) -> None:
    _ref(db, project_id).document(claim_id).update({"statement": statement.strip()})


def link_evidence(db: firestore.Client, project_id: str, claim_id: str, evidence_id: str) -> None:
    _ref(db, project_id).document(claim_id).update({
        "evidence_ids": firestore.ArrayUnion([evidence_id])
    })


def unlink_evidence(db: firestore.Client, project_id: str, claim_id: str, evidence_id: str) -> None:
    _ref(db, project_id).document(claim_id).update({
        "evidence_ids": firestore.ArrayRemove([evidence_id])
    })


def link_theme(db: firestore.Client, project_id: str, claim_id: str, theme_id: str) -> None:
    _ref(db, project_id).document(claim_id).update({
        "theme_ids": firestore.ArrayUnion([theme_id])
    })


def unlink_theme(db: firestore.Client, project_id: str, claim_id: str, theme_id: str) -> None:
    _ref(db, project_id).document(claim_id).update({
        "theme_ids": firestore.ArrayRemove([theme_id])
    })


def delete_claim(db: firestore.Client, project_id: str, claim_id: str) -> None:
    _ref(db, project_id).document(claim_id).delete()


def count_for_project(db: firestore.Client, project_id: str) -> int:
    return len(_ref(db, project_id).get())
