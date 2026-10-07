from datetime import datetime, timezone

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
    source_type: str = "journal_article",
    read_status: str = "unread",
    source_note: str = "",
    access_status: str = "unknown",
) -> SavedResource:
    ref = _saved_ref(db, project_id)

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
        source_type=source_type,
        read_status=read_status,
        source_note=source_note,
        access_status=access_status,
    )
    doc_ref.set(resource.to_firestore())
    return resource


def update_source(
    db: firestore.Client,
    project_id: str,
    resource_id: str,
    *,
    title: str | None = None,
    authors: list[str] | None = None,
    year: int | None = None,
    venue: str | None = None,
    doi: str | None = None,
    url: str | None = None,
    abstract: str | None = None,
    source_type: str | None = None,
    read_status: str | None = None,
    source_note: str | None = None,
    access_status: str | None = None,
) -> None:
    updates: dict = {}
    if title is not None:
        updates["title"] = title
    if authors is not None:
        updates["authors"] = authors
    if year is not None:
        updates["year"] = year
    if venue is not None:
        updates["venue"] = venue
    if doi is not None:
        updates["doi"] = doi
    if url is not None:
        updates["url"] = url
    if abstract is not None:
        updates["abstract"] = abstract
    if source_type is not None:
        updates["source_type"] = source_type
    if read_status is not None:
        updates["read_status"] = read_status
    if source_note is not None:
        updates["source_note"] = source_note
    if access_status is not None:
        updates["access_status"] = access_status
    if updates:
        _saved_ref(db, project_id).document(resource_id).update(updates)


def list_resources(db: firestore.Client, project_id: str) -> list[SavedResource]:
    docs = _saved_ref(db, project_id).get()
    resources = [SavedResource.from_firestore(doc) for doc in docs]
    return sorted(resources, key=lambda r: r.added_at, reverse=True)


def get_resource(db: firestore.Client, project_id: str, resource_id: str) -> SavedResource | None:
    doc = _saved_ref(db, project_id).document(resource_id).get()
    return SavedResource.from_firestore(doc) if doc.exists else None


def delete_resource(db: firestore.Client, project_id: str, resource_id: str) -> None:
    _saved_ref(db, project_id).document(resource_id).delete()
