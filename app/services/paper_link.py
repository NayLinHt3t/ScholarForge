"""Turn any paper link a student pastes into paper details — with a PDF link when one exists.

Understands:
  * direct PDF / publisher links that contain a DOI     (…/10.1145/123456.pdf, doi.org/10.…)
  * arXiv links                                        (arxiv.org/abs/2401.01234, arxiv.org/pdf/2401.01234v2)
  * OpenAlex links                                      (openalex.org/W123…)
  * Semantic Scholar links                              (semanticscholar.org/paper/…/<40-hex id>)
Any other http(s) link (e.g. a PDF with no DOI in its address) can't be looked up,
so the student is sent to "Add a paper by hand" with the link already filled in.

The saved link is chosen in this order: open-access PDF → DOI → arXiv → landing page.
A Semantic Scholar page is only used when nothing else exists.
"""
import re
from dataclasses import dataclass, field
from urllib.parse import unquote

import httpx

from app.clients import openalex
from app.clients import semantic_scholar as ss


class LinkError(Exception):
    """kind: invalid | notfound | busy | fetch | manual"""

    def __init__(self, kind: str, link: str = ""):
        super().__init__(kind)
        self.kind = kind
        self.link = link


@dataclass
class PaperInfo:
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    pdf_url: str | None = None
    landing_url: str | None = None
    abstract: str | None = None
    source: str = "link"

    @property
    def best_url(self) -> str | None:
        if self.pdf_url:
            return self.pdf_url
        if self.doi:
            return f"https://doi.org/{self.doi}"
        if self.arxiv_id:
            return f"https://arxiv.org/pdf/{self.arxiv_id}"
        return self.landing_url


_ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf|html)/([a-z\-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?", re.I)
_OPENALEX_RE = re.compile(r"openalex\.org/(?:works/)?(W\d+)", re.I)
_DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s?#\"<>]+)", re.I)


def _clean_doi(doi: str) -> str:
    doi = unquote(doi).strip().rstrip(".,;)")
    for suffix in (".pdf", "/pdf", "/full", "/abstract", "/fulltext"):
        if doi.lower().endswith(suffix):
            doi = doi[: -len(suffix)]
    return doi


def parse(link: str) -> tuple[str, str]:
    """Return (kind, id): kind is s2 | arxiv | openalex | doi | url. Raises LinkError('invalid')."""
    link = (link or "").strip()
    if not link:
        raise LinkError("invalid")
    s2_id = ss.extract_paper_id(link)
    if s2_id:
        return "s2", s2_id
    m = _ARXIV_RE.search(link)
    if m:
        return "arxiv", m.group(1)
    m = _OPENALEX_RE.search(link)
    if m:
        return "openalex", m.group(1).upper()
    m = _DOI_RE.search(unquote(link))
    if m:
        return "doi", _clean_doi(m.group(1))
    if re.match(r"https?://[^\s/]+\.[^\s/]+", link, re.I):
        return "url", link
    raise LinkError("invalid")


# ── turning API answers into PaperInfo ─────────────────────────────────────

def _from_openalex(item: dict) -> PaperInfo:
    best = item.get("best_oa_location") or {}
    primary = item.get("primary_location") or {}
    pdf = best.get("pdf_url") or primary.get("pdf_url")
    if not pdf:
        pdf = next((loc.get("pdf_url") for loc in (item.get("locations") or []) if loc.get("pdf_url")), None)
    doi = (item.get("doi") or "").removeprefix("https://doi.org/") or None
    inv = item.get("abstract_inverted_index")
    return PaperInfo(
        title=item.get("title") or item.get("display_name") or "",
        authors=[a["author"]["display_name"] for a in (item.get("authorships") or [])
                 if (a.get("author") or {}).get("display_name")],
        year=item.get("publication_year"),
        venue=((primary.get("source") or {}).get("display_name")),
        doi=doi,
        pdf_url=pdf,
        landing_url=best.get("landing_page_url") or primary.get("landing_page_url"),
        abstract=openalex.reconstruct_abstract(inv) if inv else None,
        source="openalex",
    )


def _from_s2(raw: dict) -> PaperInfo:
    ext = raw.get("externalIds") or {}
    return PaperInfo(
        title=raw.get("title") or "",
        authors=[a["name"] for a in (raw.get("authors") or []) if a.get("name")],
        year=raw.get("year"),
        venue=raw.get("venue") or None,
        doi=ext.get("DOI"),
        arxiv_id=ext.get("ArXiv"),
        pdf_url=(raw.get("openAccessPdf") or {}).get("url") or None,
        landing_url=raw.get("url"),          # semanticscholar.org page — last resort only
        abstract=raw.get("abstract"),
        source="semantic_scholar",
    )


async def _openalex(identifier: str) -> PaperInfo | None:
    item = await openalex.fetch_work(identifier)
    return _from_openalex(item) if item else None


async def _s2(identifier: str) -> PaperInfo | None:
    raw = await ss.fetch_by_id(identifier)
    return _from_s2(raw) if raw else None


async def _first_found(*lookups) -> PaperInfo | None:
    """Try lookups in order; return the first paper found. Remember the first error."""
    first_error: Exception | None = None
    for lookup in lookups:
        try:
            info = await lookup()
        except Exception as e:  # noqa: BLE001
            first_error = first_error or e
            continue
        if info and info.title:
            return info
    if first_error:
        raise first_error
    return None


async def resolve(link: str) -> PaperInfo:
    kind, ident = parse(link)
    if kind == "url":
        raise LinkError("manual", link)
    try:
        if kind == "s2":
            info = await _first_found(lambda: _s2(ident))
            if info and not info.pdf_url and info.doi:      # Semantic Scholar had no PDF — ask OpenAlex
                try:
                    oa = await _openalex(f"doi:{info.doi}")
                    if oa and oa.pdf_url:
                        info.pdf_url = oa.pdf_url
                except Exception:  # noqa: BLE001 — extra lookup only
                    pass
        elif kind == "arxiv":
            info = await _first_found(lambda: _openalex(f"doi:10.48550/arXiv.{ident}"),
                                      lambda: _s2(f"arXiv:{ident}"))
            if info:
                info.arxiv_id = ident
                info.pdf_url = f"https://arxiv.org/pdf/{ident}"
        elif kind == "openalex":
            info = await _first_found(lambda: _openalex(ident))
        else:  # doi
            info = await _first_found(lambda: _openalex(f"doi:{ident}"), lambda: _s2(f"DOI:{ident}"))
            if info and not info.pdf_url and link.lower().split("?")[0].endswith(".pdf"):
                info.pdf_url = link.strip()                 # the student pasted the PDF itself
    except httpx.HTTPStatusError as e:
        raise LinkError("busy" if e.response.status_code == 429 else "fetch", link) from e
    except LinkError:
        raise
    except Exception as e:  # noqa: BLE001 — network problems
        raise LinkError("fetch", link) from e
    if not info:
        raise LinkError("notfound", link)
    return info
