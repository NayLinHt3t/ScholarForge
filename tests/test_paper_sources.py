"""Paper libraries: OpenAlex API key, clear messages when a library fails."""
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app import config
from app.clients import openalex
from app.services import search as search_service
from tests.conftest import FAKE_PROJECT


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_openalex_sends_api_key_when_set():
    with patch.object(config, "OPENALEX_API_KEY", "oa_key"), patch.object(config, "OPENALEX_MAILTO", ""):
        p = openalex._params({"search": "x"})
    assert p["api_key"] == "oa_key" and "mailto" not in p


def test_openalex_without_key_sends_no_key():
    with patch.object(config, "OPENALEX_API_KEY", ""), patch.object(config, "OPENALEX_MAILTO", ""):
        assert "api_key" not in openalex._params({"search": "x"})


def _http_error(status):
    req = httpx.Request("GET", "https://example.org")
    return httpx.HTTPStatusError("err", request=req, response=httpx.Response(status, request=req))


@pytest.mark.anyio
async def test_both_libraries_failing_gives_plain_messages():
    with (
        patch("app.services.search.semantic_scholar.search", new=AsyncMock(side_effect=_http_error(429))),
        patch("app.services.search.openalex.search", new=AsyncMock(side_effect=_http_error(429))),
    ):
        resp = await search_service.run("remote work")
    assert resp.results == []
    assert resp.source_errors == ["Semantic Scholar is busy right now", "OpenAlex isn't available right now"]
    assert not any("SEMANTIC_SCHOLAR_API_KEY" in e for e in resp.source_errors)   # no developer jargon for students


def test_search_page_explains_no_results_when_all_libraries_fail(client):
    resp_obj = search_service.SearchResponse(results=[], low_confidence=False,
                                             source_errors=["Semantic Scholar is busy right now",
                                                            "OpenAlex isn't available right now"])
    with patch("app.routers.search.project_service.get_project", return_value=FAKE_PROJECT), \
         patch("app.routers.search.search_service.run", new=AsyncMock(return_value=resp_obj)):
        html = client.get("/projects/p1/search?q=trust").text
    assert "No paper library answered" in html
    assert "remaining source only" not in html
