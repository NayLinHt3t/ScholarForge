from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SavedResource(BaseModel):
    id: str = ""
    project_id: str                         # stored in doc for easy querying
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    abstract: str | None = None
    source: str                             # "semantic_scholar" | "crossref"
    embedding: list[float] | None = None    # nomic-embed-text float32 vector (768-dim)
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "SavedResource":
        return cls(id=doc.id, **doc.to_dict())
