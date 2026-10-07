from datetime import datetime, timezone

from pydantic import BaseModel, Field

SOURCE_TYPES = ("journal_article", "book", "conference_paper", "website", "dataset", "other")
READ_STATUSES = ("unread", "reading", "done")
ACCESS_STATUSES = ("open_access", "paywalled", "unknown")


class SavedResource(BaseModel):
    id: str = ""
    project_id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    abstract: str | None = None
    source: str = "manual"                  # "manual" | "semantic_scholar" | "crossref"
    embedding: list[float] | None = None
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # workspace fields (MVP)
    source_type: str = "journal_article"    # journal_article | book | conference_paper | website | dataset | other
    read_status: str = "unread"             # unread | reading | done
    source_note: str = ""                   # student's general note on this source
    access_status: str = "unknown"          # open_access | paywalled | unknown

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "SavedResource":
        data = doc.to_dict()
        # back-fill workspace fields absent in pre-MVP documents
        data.setdefault("source_type", "journal_article")
        data.setdefault("read_status", "unread")
        data.setdefault("source_note", "")
        data.setdefault("access_status", "unknown")
        return cls(id=doc.id, **data)
