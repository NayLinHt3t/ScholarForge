import re

import httpx

_BASE = "https://api.crossref.org"
_HEADERS = {"User-Agent": "ScholarForge/1.0 (mailto:user@scholarforge.local)"}
_SELECT = "title,author,published-print,published-online,container-title,DOI,abstract,URL"


def _strip_jats(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


async def search(query: str, limit: int = 15) -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{_BASE}/works",
            params={"query": query, "rows": limit, "select": _SELECT},
            headers=_HEADERS,
        )
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        for item in items:
            if item.get("abstract"):
                item["abstract"] = _strip_jats(item["abstract"])
        return items
