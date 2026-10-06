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
