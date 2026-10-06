import asyncio
import httpx

from app.config import SEMANTIC_SCHOLAR_API_KEY

_BASE = "https://api.semanticscholar.org/graph/v1"
_FIELDS = "title,authors,year,venue,abstract,externalIds,url"


def _headers() -> dict:
    h = {"User-Agent": "ScholarForge/1.0"}
    if SEMANTIC_SCHOLAR_API_KEY:
        h["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
    return h


async def fetch_by_id(paper_id: str) -> dict | None:
    """Fetch a single paper by its Semantic Scholar paper ID."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        for attempt in range(4):
            r = await client.get(
                f"{_BASE}/paper/{paper_id}",
                params={"fields": _FIELDS},
                headers=_headers(),
            )
            if r.status_code == 404:
                return None
            if r.status_code == 429:
                await asyncio.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        r.raise_for_status()
    return None


def extract_paper_id(url: str) -> str | None:
    """Extract the paper ID hash from a semanticscholar.org paper URL."""
    import re
    m = re.search(r"semanticscholar\.org/paper/[^/]+/([a-f0-9]{40})", url)
    if m:
        return m.group(1)
    # Also accept bare 40-char hex IDs
    m = re.fullmatch(r"[a-f0-9]{40}", url.strip())
    return m.group(0) if m else None


async def search(query: str, limit: int = 15) -> list[dict]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        for attempt in range(3):
            r = await client.get(
                f"{_BASE}/paper/search",
                params={"query": query, "fields": _FIELDS, "limit": limit},
                headers=_headers(),
            )
            if r.status_code == 429:
                # Rate limited — back off then retry; give up after 3 attempts
                await asyncio.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json().get("data", [])
        # All retries exhausted
        r.raise_for_status()
    return []
