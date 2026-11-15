import httpx

_BASE = "https://api.openalex.org/works"
_MAILTO = "linmyatooa7@gmail.com"
_SELECT = "id,doi,title,publication_year,primary_location,open_access,best_oa_location,authorships,abstract_inverted_index"


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
            params={
                "search": query,
                "filter": "is_oa:true",
                "per_page": limit,
                "select": _SELECT,
                "mailto": _MAILTO,
            },
        )
        r.raise_for_status()
        return r.json().get("results", [])
