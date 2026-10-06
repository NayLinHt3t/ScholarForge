from google.cloud import firestore

from app.collections import PROJECTS, SAVED_RESOURCES
from app.exceptions import DuplicateResourceError
from app.models import SavedResource


def _saved_ref(db: firestore.Client, project_id: str):
    return db.collection(PROJECTS).document(project_id).collection(SAVED_RESOURCES)


def save_resource(
    db: firestore.Client,
    project_id: str,
    title: str,
    authors: list[str],
    year: int | None,
    venue: str | None,
    doi: str | None,
    arxiv_id: str | None,
    url: str | None,
    abstract: str | None,
    source: str,
    embedding: list[float] | None,
) -> SavedResource:
    ref = _saved_ref(db, project_id)

    # Duplicate check scoped to this project (BL-11)
    if doi:
        if list(ref.where(filter=firestore.FieldFilter("doi", "==", doi)).limit(1).get()):
            raise DuplicateResourceError()
    elif arxiv_id:
        if list(ref.where(filter=firestore.FieldFilter("arxiv_id", "==", arxiv_id)).limit(1).get()):
            raise DuplicateResourceError()

    doc_ref = ref.document()
    resource = SavedResource(
        id=doc_ref.id,
        project_id=project_id,
        title=title,
        authors=authors,
        year=year,
        venue=venue,
        doi=doi,
        arxiv_id=arxiv_id,
        url=url,
        abstract=abstract,
        source=source,
        embedding=embedding,
    )
    doc_ref.set(resource.to_firestore())
    return resource


def list_resources(db: firestore.Client, project_id: str) -> list[SavedResource]:
    docs = _saved_ref(db, project_id).get()
    resources = [SavedResource.from_firestore(doc) for doc in docs]
    return sorted(resources, key=lambda r: r.added_at, reverse=True)


def get_resource(db: firestore.Client, project_id: str, resource_id: str) -> SavedResource | None:
    doc = _saved_ref(db, project_id).document(resource_id).get()
    return SavedResource.from_firestore(doc) if doc.exists else None


def delete_resource(db: firestore.Client, project_id: str, resource_id: str) -> None:
    _saved_ref(db, project_id).document(resource_id).delete()
