import asyncio
import logging
import math
import time
from dataclasses import dataclass, field

from app import config
from app.clients import ai, openalex, semantic_scholar
from app.config import SEARCH_LOW_CONFIDENCE_THRESHOLD, SEARCH_MAX_PER_SOURCE, SEARCH_TOP_K
from app.exceptions import OllamaUnavailableError
from app.models.search import SearchResult

logger = logging.getLogger(__name__)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _resolve_url(doi: str | None, arxiv_id: str | None, fallback: str | None) -> str | None:
    """Prefer a stable resolver link over an aggregator/raw API url.

    DOI resolves to the publisher's actual page; arXiv's abstract page always
    has the full text. Both outlive and outrank whatever `url`/`URL` the
    source API happened to return (semanticscholar.org paper pages are S2's
    own landing page, not the real source; CrossRef's `URL` field is often
    stale or missing).
    """
    if doi:
        return f"https://doi.org/{doi}"
    if arxiv_id:
        return f"https://arxiv.org/abs/{arxiv_id}"
    return fallback


def _normalize_ss(items: list[dict]) -> list[SearchResult]:
    results = []
    for item in items:
        if not item.get("title"):
            continue
        if not item.get("isOpenAccess"):
            continue
        ext = item.get("externalIds") or {}
        doi = ext.get("DOI")
        arxiv_id = ext.get("ArXiv")
        oa_pdf = (item.get("openAccessPdf") or {}).get("url")
        results.append(SearchResult(
            title=item["title"],
            authors=[a["name"] for a in (item.get("authors") or [])],
            year=item.get("year"),
            venue=item.get("venue") or None,
            doi=doi,
            arxiv_id=arxiv_id,
            url=oa_pdf or _resolve_url(doi, arxiv_id, item.get("url")),
            abstract=item.get("abstract"),
            source="semantic_scholar",
        ))
    return results


def _normalize_oa(items: list[dict]) -> list[SearchResult]:
    results = []
    for item in items:
        if not item.get("title"):
            continue
        best = item.get("best_oa_location") or {}
        pdf_url = best.get("pdf_url")
        if not pdf_url:
            continue  # skip — no direct PDF means user hits a paywall
        doi_full = item.get("doi") or ""
        doi = doi_full.removeprefix("https://doi.org/") or None
        primary = item.get("primary_location") or {}
        venue = (primary.get("source") or {}).get("display_name")
        authors = [
            a["author"]["display_name"]
            for a in (item.get("authorships") or [])
            if (a.get("author") or {}).get("display_name")
        ]
        abstract_inv = item.get("abstract_inverted_index")
        abstract = openalex.reconstruct_abstract(abstract_inv) if abstract_inv else None
        results.append(SearchResult(
            title=item["title"],
            authors=authors,
            year=item.get("publication_year"),
            venue=venue,
            doi=doi,
            url=pdf_url,
            abstract=abstract,
            source="openalex",
        ))
    return results


@dataclass
class SearchResponse:
    results: list[SearchResult]
    low_confidence: bool
    source_errors: list[str] = field(default_factory=list)
    ranked: bool = True        # False → smart ranking unavailable, results in source order


async def run(idea: str) -> SearchResponse:
    t0 = time.perf_counter()

    t_api = time.perf_counter()
    ss_raw, oa_raw = await asyncio.gather(
        semantic_scholar.search(idea, limit=SEARCH_MAX_PER_SOURCE),
        openalex.search(idea, limit=SEARCH_MAX_PER_SOURCE),
        return_exceptions=True,
    )
    api_ms = int((time.perf_counter() - t_api) * 1000)

    candidates: list[SearchResult] = []
    source_errors: list[str] = []

    from httpx import HTTPStatusError

    def _status(err) -> int | None:
        return err.response.status_code if isinstance(err, HTTPStatusError) else None

    # Messages shown to students are plain; the technical reason goes to the server log.
    if isinstance(ss_raw, Exception):
        if _status(ss_raw) == 429:
            source_errors.append("Semantic Scholar is busy right now")
            logger.warning("search.api.rate_limited source=semantic_scholar "
                           "hint=set SEMANTIC_SCHOLAR_API_KEY for a higher limit")
        else:
            source_errors.append("Semantic Scholar didn't respond")
            logger.warning("search.api.error source=semantic_scholar error=%s", ss_raw)
    else:
        candidates.extend(_normalize_ss(ss_raw))

    if isinstance(oa_raw, Exception):
        source_errors.append("OpenAlex isn't available right now")
        st = _status(oa_raw)
        if st in (401, 403, 429) or not config.OPENALEX_API_KEY:
            logger.warning("search.api.error source=openalex status=%s key_set=%s "
                           "hint=OpenAlex needs a free API key (OPENALEX_API_KEY, openalex.org/settings/api)",
                           st, bool(config.OPENALEX_API_KEY))
        else:
            logger.warning("search.api.error source=openalex error=%s", oa_raw)
    else:
        candidates.extend(_normalize_oa(oa_raw))

    if not candidates:
        logger.info("search.no_candidates api_ms=%d sources_failed=%s", api_ms, source_errors)
        return SearchResponse(results=[], low_confidence=False, source_errors=source_errors)

    t_embed = time.perf_counter()
    texts = [idea] + [f"{c.title}. {c.abstract or ''}" for c in candidates]
    try:
        embeddings = await ai.embed_many(texts)
    except OllamaUnavailableError:
        # Ranking model unavailable (not running / not enough memory / turned off):
        # still show the papers, in the order the libraries returned them.
        logger.warning("search.unranked reason=embeddings_unavailable candidates=%d", len(candidates))
        return SearchResponse(results=candidates[:SEARCH_TOP_K], low_confidence=False,
                              source_errors=source_errors, ranked=False)
    embed_ms = int((time.perf_counter() - t_embed) * 1000)

    t_rank = time.perf_counter()
    query_emb = embeddings[0]
    for candidate, emb in zip(candidates, embeddings[1:]):
        candidate.score = _cosine(query_emb, emb)
    candidates.sort(key=lambda c: c.score, reverse=True)
    top = candidates[:SEARCH_TOP_K]
    rank_ms = int((time.perf_counter() - t_rank) * 1000)

    low_confidence = bool(top) and top[0].score < SEARCH_LOW_CONFIDENCE_THRESHOLD
    total_ms = int((time.perf_counter() - t0) * 1000)

    logger.info(
        "search.ok candidates=%d top_k=%d top_score=%.3f low_confidence=%s "
        "api_ms=%d embed_ms=%d rank_ms=%d total_ms=%d",
        len(candidates), len(top),
        top[0].score if top else 0.0,
        low_confidence,
        api_ms, embed_ms, rank_ms, total_ms,
    )

    return SearchResponse(results=top, low_confidence=low_confidence, source_errors=source_errors)
