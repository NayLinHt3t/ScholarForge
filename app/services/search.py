import asyncio
import logging
import math
import time
from dataclasses import dataclass, field

from app.clients import crossref, ollama, semantic_scholar
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


def _normalize_ss(items: list[dict]) -> list[SearchResult]:
    results = []
    for item in items:
        if not item.get("title"):
            continue
        ext = item.get("externalIds") or {}
        results.append(SearchResult(
            title=item["title"],
            authors=[a["name"] for a in (item.get("authors") or [])],
            year=item.get("year"),
            venue=item.get("venue") or None,
            doi=ext.get("DOI"),
            arxiv_id=ext.get("ArXiv"),
            url=item.get("url"),
            abstract=item.get("abstract"),
            source="semantic_scholar",
        ))
    return results


def _normalize_cr(items: list[dict]) -> list[SearchResult]:
    results = []
    for item in items:
        titles = item.get("title") or []
        if not titles:
            continue
        authors = []
        for a in item.get("author") or []:
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)
        year = None
        for key in ("published-print", "published-online"):
            parts = (item.get(key) or {}).get("date-parts", [[]])
            if parts and parts[0]:
                year = parts[0][0]
                break
        venues = item.get("container-title") or []
        results.append(SearchResult(
            title=titles[0],
            authors=authors,
            year=year,
            venue=venues[0] if venues else None,
            doi=item.get("DOI"),
            url=item.get("URL"),
            abstract=item.get("abstract"),
            source="crossref",
        ))
    return results


@dataclass
class SearchResponse:
    results: list[SearchResult]
    low_confidence: bool
    source_errors: list[str] = field(default_factory=list)


async def run(idea: str) -> SearchResponse:
    t0 = time.perf_counter()

    if not await ollama.is_alive():
        raise OllamaUnavailableError()

    t_api = time.perf_counter()
    ss_raw, cr_raw = await asyncio.gather(
        semantic_scholar.search(idea, limit=SEARCH_MAX_PER_SOURCE),
        crossref.search(idea, limit=SEARCH_MAX_PER_SOURCE),
        return_exceptions=True,
    )
    api_ms = int((time.perf_counter() - t_api) * 1000)

    candidates: list[SearchResult] = []
    source_errors: list[str] = []

    if isinstance(ss_raw, Exception):
        from httpx import HTTPStatusError
        if isinstance(ss_raw, HTTPStatusError) and ss_raw.response.status_code == 429:
            source_errors.append("Semantic Scholar (rate-limited — add SEMANTIC_SCHOLAR_API_KEY to .env for higher limits)")
            logger.warning("search.api.rate_limited source=semantic_scholar")
        else:
            source_errors.append("Semantic Scholar")
            logger.warning("search.api.error source=semantic_scholar error=%s", ss_raw)
    else:
        candidates.extend(_normalize_ss(ss_raw))

    if isinstance(cr_raw, Exception):
        source_errors.append("CrossRef")
        logger.warning("search.api.error source=crossref error=%s", cr_raw)
    else:
        candidates.extend(_normalize_cr(cr_raw))

    if not candidates:
        logger.info("search.no_candidates api_ms=%d sources_failed=%s", api_ms, source_errors)
        return SearchResponse(results=[], low_confidence=False, source_errors=source_errors)

    t_embed = time.perf_counter()
    texts = [idea] + [f"{c.title}. {c.abstract or ''}" for c in candidates]
    embeddings = await asyncio.gather(*[ollama.embed(t) for t in texts])
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
