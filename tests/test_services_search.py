"""Unit tests for app.services.search — url resolution and normalization."""
from app.services.search import _normalize_oa, _normalize_ss, _resolve_url


def test_resolve_url_prefers_doi_resolver_over_fallback():
    assert _resolve_url("10.1109/5.771073", None, "https://www.semanticscholar.org/paper/abc") \
        == "https://doi.org/10.1109/5.771073"


def test_resolve_url_prefers_arxiv_abstract_page_when_no_doi():
    assert _resolve_url(None, "2301.00001", "https://www.semanticscholar.org/paper/abc") \
        == "https://arxiv.org/abs/2301.00001"


def test_resolve_url_falls_back_when_no_doi_or_arxiv():
    assert _resolve_url(None, None, "https://example.com/paper") == "https://example.com/paper"


def test_resolve_url_returns_none_when_nothing_available():
    assert _resolve_url(None, None, None) is None


# ── Semantic Scholar normalization ──────────────────────────────────────────

def test_normalize_ss_uses_doi_resolver_not_semanticscholar_landing_page():
    items = [{
        "title": "Deep Learning",
        "authors": [{"name": "Y. LeCun"}],
        "year": 2015,
        "venue": "Nature",
        "externalIds": {"DOI": "10.1038/nature14539"},
        "url": "https://www.semanticscholar.org/paper/abc123",
        "abstract": "...",
        "isOpenAccess": True,
        "openAccessPdf": None,
    }]
    results = _normalize_ss(items)
    assert results[0].url == "https://doi.org/10.1038/nature14539"


def test_normalize_ss_uses_arxiv_abstract_page_when_no_doi():
    items = [{
        "title": "Attention Is All You Need",
        "authors": [{"name": "A. Vaswani"}],
        "year": 2017,
        "venue": None,
        "externalIds": {"ArXiv": "1706.03762"},
        "url": "https://www.semanticscholar.org/paper/def456",
        "abstract": "...",
        "isOpenAccess": True,
        "openAccessPdf": None,
    }]
    results = _normalize_ss(items)
    assert results[0].url == "https://arxiv.org/abs/1706.03762"


def test_normalize_ss_falls_back_to_api_url_with_no_doi_or_arxiv():
    items = [{
        "title": "Some Paper",
        "authors": [],
        "year": 2020,
        "venue": None,
        "externalIds": {},
        "url": "https://www.semanticscholar.org/paper/ghi789",
        "abstract": None,
        "isOpenAccess": True,
        "openAccessPdf": None,
    }]
    results = _normalize_ss(items)
    assert results[0].url == "https://www.semanticscholar.org/paper/ghi789"


def test_normalize_ss_skips_paywalled_papers():
    items = [
        {
            "title": "Paywalled Paper",
            "authors": [],
            "year": 2021,
            "venue": None,
            "externalIds": {"DOI": "10.1000/paywalled"},
            "url": "https://publisher.com/paper",
            "abstract": None,
            "isOpenAccess": False,
            "openAccessPdf": None,
        },
        {
            "title": "Open Paper",
            "authors": [],
            "year": 2021,
            "venue": None,
            "externalIds": {"ArXiv": "2101.00001"},
            "url": "https://arxiv.org/abs/2101.00001",
            "abstract": None,
            "isOpenAccess": True,
            "openAccessPdf": None,
        },
    ]
    results = _normalize_ss(items)
    assert len(results) == 1
    assert results[0].title == "Open Paper"


def test_normalize_ss_prefers_oa_pdf_url_over_doi_resolver():
    items = [{
        "title": "Paper With PDF",
        "authors": [{"name": "A. Author"}],
        "year": 2022,
        "venue": "Conference",
        "externalIds": {"DOI": "10.1000/pdf"},
        "url": "https://www.semanticscholar.org/paper/abc",
        "abstract": "Abstract text.",
        "isOpenAccess": True,
        "openAccessPdf": {"url": "https://arxiv.org/pdf/2201.00001.pdf"},
    }]
    results = _normalize_ss(items)
    assert results[0].url == "https://arxiv.org/pdf/2201.00001.pdf"


# ── OpenAlex normalization ───────────────────────────────────────────────────

def _oa_item(pdf_url="https://arxiv.org/pdf/2301.00001.pdf", **overrides):
    base = {
        "title": "Open Access Paper",
        "doi": "https://doi.org/10.1000/oa",
        "publication_year": 2023,
        "primary_location": {"source": {"display_name": "PLOS ONE"}},
        "open_access": {"is_oa": True, "oa_url": "https://example.org/paper"},
        "best_oa_location": {"pdf_url": pdf_url},
        "authorships": [{"author": {"display_name": "Jane Smith"}}],
        "abstract_inverted_index": None,
    }
    base.update(overrides)
    return base


def test_normalize_oa_uses_pdf_url_as_link():
    results = _normalize_oa([_oa_item(pdf_url="https://arxiv.org/pdf/2301.00001.pdf")])
    assert results[0].url == "https://arxiv.org/pdf/2301.00001.pdf"
    assert results[0].doi == "10.1000/oa"
    assert results[0].venue == "PLOS ONE"
    assert results[0].authors == ["Jane Smith"]
    assert results[0].source == "openalex"


def test_normalize_oa_skips_items_without_pdf_url():
    items = [
        _oa_item(pdf_url=None),   # no PDF — should be dropped
        _oa_item(pdf_url="https://arxiv.org/pdf/2301.00002.pdf", title="Has PDF"),
    ]
    results = _normalize_oa(items)
    assert len(results) == 1
    assert results[0].title == "Has PDF"


def test_normalize_oa_skips_items_without_title():
    items = [
        _oa_item(title=None),
        _oa_item(title="Valid Paper"),
    ]
    results = _normalize_oa(items)
    assert len(results) == 1
    assert results[0].title == "Valid Paper"


def test_normalize_oa_reconstructs_abstract_from_inverted_index():
    item = _oa_item()
    item["abstract_inverted_index"] = {"We": [0], "study": [1], "things": [2]}
    results = _normalize_oa([item])
    assert results[0].abstract == "We study things"


def test_normalize_oa_strips_doi_prefix():
    item = _oa_item()
    item["doi"] = "https://doi.org/10.9999/test"
    results = _normalize_oa([item])
    assert results[0].doi == "10.9999/test"


def test_normalize_oa_handles_missing_best_oa_location():
    item = _oa_item()
    item["best_oa_location"] = None
    results = _normalize_oa([item])
    assert results == []
