"""Add a paper from any link (PDF / DOI / arXiv / OpenAlex / Semantic Scholar) and keep the PDF link."""
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services import paper_link as pl
from tests.conftest import FAKE_PROJECT

S2_ID = "a" * 40


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.parametrize("link,expected", [
    ("https://doi.org/10.1145/3540250.3549135", ("doi", "10.1145/3540250.3549135")),
    ("https://dl.acm.org/doi/pdf/10.1145/3540250.3549135", ("doi", "10.1145/3540250.3549135")),
    ("https://link.springer.com/content/pdf/10.1007/s10664-021-09993-1.pdf", ("doi", "10.1007/s10664-021-09993-1")),
    ("https://arxiv.org/abs/2401.01234", ("arxiv", "2401.01234")),
    ("https://arxiv.org/pdf/2401.01234v2", ("arxiv", "2401.01234")),
    ("https://openalex.org/W2741809807", ("openalex", "W2741809807")),
    (f"https://www.semanticscholar.org/paper/Some-Title/{S2_ID}", ("s2", S2_ID)),
    ("https://example.edu/papers/remote-work.pdf", ("url", "https://example.edu/papers/remote-work.pdf")),
])
def test_parse_link_kinds(link, expected):
    assert pl.parse(link) == expected


def test_parse_rejects_non_links():
    with pytest.raises(pl.LinkError) as e:
        pl.parse("just some words")
    assert e.value.kind == "invalid"


OA_ITEM = {
    "title": "Trust in Remote Teams", "publication_year": 2024, "doi": "https://doi.org/10.1234/abc",
    "best_oa_location": {"pdf_url": "https://repo.example.org/trust.pdf", "landing_page_url": "https://pub.example.org/x"},
    "primary_location": {"source": {"display_name": "IEEE Software"}},
    "authorships": [{"author": {"display_name": "M. Tanaka"}}],
    "abstract_inverted_index": {"Remote": [0], "work": [1]},
}


@pytest.mark.anyio
async def test_doi_link_saves_pdf_from_openalex():
    with patch("app.services.paper_link.openalex.fetch_work", new=AsyncMock(return_value=OA_ITEM)) as fw:
        info = await pl.resolve("https://doi.org/10.1234/abc")
    fw.assert_awaited_once_with("doi:10.1234/abc")
    assert info.best_url == "https://repo.example.org/trust.pdf"
    assert info.title == "Trust in Remote Teams" and info.abstract == "Remote work" and info.venue == "IEEE Software"


@pytest.mark.anyio
async def test_pasted_pdf_kept_when_no_open_pdf_known():
    item = {**OA_ITEM, "best_oa_location": {}, "locations": []}
    with patch("app.services.paper_link.openalex.fetch_work", new=AsyncMock(return_value=item)):
        info = await pl.resolve("https://dl.acm.org/doi/pdf/10.1234/abc.pdf")
    assert info.best_url == "https://dl.acm.org/doi/pdf/10.1234/abc.pdf"


@pytest.mark.anyio
async def test_no_pdf_falls_back_to_doi_not_semantic_scholar_page():
    raw = {"title": "T", "externalIds": {"DOI": "10.5555/z"}, "openAccessPdf": None,
           "url": f"https://www.semanticscholar.org/paper/{S2_ID}"}
    with patch("app.services.paper_link.ss.fetch_by_id", new=AsyncMock(return_value=raw)), \
         patch("app.services.paper_link.openalex.fetch_work", new=AsyncMock(return_value=None)):
        info = await pl.resolve(f"https://www.semanticscholar.org/paper/x/{S2_ID}")
    assert info.best_url == "https://doi.org/10.5555/z"


@pytest.mark.anyio
async def test_semantic_scholar_link_gets_pdf_from_openalex():
    raw = {"title": "T", "externalIds": {"DOI": "10.1234/abc"}, "openAccessPdf": {"url": ""}}
    with patch("app.services.paper_link.ss.fetch_by_id", new=AsyncMock(return_value=raw)), \
         patch("app.services.paper_link.openalex.fetch_work", new=AsyncMock(return_value=OA_ITEM)):
        info = await pl.resolve(f"https://www.semanticscholar.org/paper/x/{S2_ID}")
    assert info.best_url == "https://repo.example.org/trust.pdf"


@pytest.mark.anyio
async def test_arxiv_link_uses_arxiv_pdf():
    with patch("app.services.paper_link.openalex.fetch_work", new=AsyncMock(return_value={**OA_ITEM, "best_oa_location": {}})):
        info = await pl.resolve("https://arxiv.org/abs/2401.01234v3")
    assert info.best_url == "https://arxiv.org/pdf/2401.01234" and info.arxiv_id == "2401.01234"


@pytest.mark.anyio
async def test_unknown_pdf_link_goes_to_manual():
    with pytest.raises(pl.LinkError) as e:
        await pl.resolve("https://example.edu/papers/remote-work.pdf")
    assert e.value.kind == "manual"


@pytest.mark.anyio
async def test_rate_limit_is_busy():
    req = httpx.Request("GET", "https://x")
    err = httpx.HTTPStatusError("x", request=req, response=httpx.Response(429, request=req))
    with patch("app.services.paper_link.openalex.fetch_work", new=AsyncMock(side_effect=err)), \
         patch("app.services.paper_link.ss.fetch_by_id", new=AsyncMock(side_effect=err)):
        with pytest.raises(pl.LinkError) as e:
            await pl.resolve("https://doi.org/10.1234/abc")
    assert e.value.kind == "busy"


@pytest.mark.anyio
async def test_not_found():
    with patch("app.services.paper_link.openalex.fetch_work", new=AsyncMock(return_value=None)), \
         patch("app.services.paper_link.ss.fetch_by_id", new=AsyncMock(return_value=None)):
        with pytest.raises(pl.LinkError) as e:
            await pl.resolve("https://doi.org/10.1234/missing")
    assert e.value.kind == "notfound"


# ── route ───────────────────────────────────────────────────────────────────

def _route_patches():
    return (
        patch("app.routers.search.project_service.get_project", return_value=FAKE_PROJECT),
        patch("app.routers.search.ai.embed", new=AsyncMock(return_value=[0.1])),
    )


def test_route_saves_pdf_link(client):
    info = pl.PaperInfo(title="T", doi="10.1234/abc", pdf_url="https://repo.example.org/t.pdf", source="openalex")
    p1, p2 = _route_patches()
    with p1, p2, patch("app.routers.search.paper_link.resolve", new=AsyncMock(return_value=info)), \
         patch("app.routers.search.library_service.save_resource") as save:
        resp = client.post("/projects/p1/search/add-by-url", data={"paper_url": "https://doi.org/10.1234/abc"})
    assert resp.headers["location"].endswith("saved=1")
    kw = save.call_args.kwargs
    assert kw["url"] == "https://repo.example.org/t.pdf" and kw["access_status"] == "open_access"


def test_route_unknown_link_prefills_manual_form(client):
    p1, p2 = _route_patches()
    with p1, p2, patch("app.routers.search.paper_link.resolve",
                       new=AsyncMock(side_effect=pl.LinkError("manual", "https://x.edu/a.pdf"))):
        resp = client.post("/projects/p1/search/add-by-url", data={"paper_url": "https://x.edu/a.pdf"})
    assert resp.headers["location"] == "/projects/p1/sources?link=https%3A//x.edu/a.pdf"


def test_manual_form_shows_prefilled_link(client):
    with patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT), \
         patch("app.routers.sources.library_service.list_resources", return_value=[]):
        html = client.get("/projects/p1/sources?link=https://x.edu/a.pdf").text
    assert 'value="https://x.edu/a.pdf"' in html and "couldn't read the paper's details" in html


def test_reader_button_says_open_pdf(client):
    from tests.conftest import FAKE_SOURCE
    src = FAKE_SOURCE.model_copy(update={"url": "https://repo.example.org/t.pdf"})
    with patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT), \
         patch("app.routers.sources.library_service.get_resource", return_value=src), \
         patch("app.routers.sources.library_service.update_source"), \
         patch("app.routers.sources.evidence_service.list_evidence_for_source", return_value=[]):
        html = client.get("/projects/p1/sources/s1").text
    assert "Open PDF" in html


def test_reader_replaces_old_semantic_scholar_link_with_doi(client):
    from tests.conftest import FAKE_SOURCE
    src = FAKE_SOURCE.model_copy(update={"url": f"https://www.semanticscholar.org/paper/{S2_ID}", "doi": "10.5555/z"})
    with patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT), \
         patch("app.routers.sources.library_service.get_resource", return_value=src), \
         patch("app.routers.sources.library_service.update_source"), \
         patch("app.routers.sources.evidence_service.list_evidence_for_source", return_value=[]):
        html = client.get("/projects/p1/sources/s1").text
    assert 'href="https://doi.org/10.5555/z"' in html
