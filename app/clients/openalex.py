import httpx

from app import config

_BASE = "https://api.openalex.org/works"
_SELECT = "id,doi,title,publication_year,primary_location,open_access,best_oa_location,authorships,abstract_inverted_index"


def _params(p: dict) -> dict:
    """Add the API key (required since Feb 2026) and optional contact email."""
    if config.OPENALEX_API_KEY:
        p["api_key"] = config.OPENALEX_API_KEY
    if config.OPENALEX_MAILTO:
        p["mailto"] = config.OPENALEX_MAILTO
    return p


def reconstruct_abstract(inverted: dict) -> str:
    positions: dict[int, str] = {}
    for word, idxs in inverted.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


async def search(query: str, limit: int = 15) -> list[dict]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            _BASE,
            params=_params({
                "search": query,
                "filter": "is_oa:true",
                "per_page": limit,
                "select": _SELECT,
            }),
        )
        r.raise_for_status()
        return r.json().get("results", [])


async def fetch_work(identifier: str) -> dict | None:
    """One work by OpenAlex id (W123…) or "doi:10.…". Returns None when not found."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{_BASE}/{identifier}",
            params=_params({"select": _SELECT + ",locations,display_name"}),
        )
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()
