import httpx

_BASE = "https://api.semanticscholar.org/graph/v1"
_FIELDS = "title,authors,year,venue,abstract,externalIds,url"
_HEADERS = {"User-Agent": "ScholarForge/1.0"}


async def search(query: str, limit: int = 15) -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{_BASE}/paper/search",
            params={"query": query, "fields": _FIELDS, "limit": limit},
            headers=_HEADERS,
        )
        r.raise_for_status()
        return r.json().get("data", [])
