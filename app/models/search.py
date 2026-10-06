from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    authors: list[str] = []
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    abstract: str | None = None
    source: str          # "semantic_scholar" | "crossref"
    score: float = 0.0
