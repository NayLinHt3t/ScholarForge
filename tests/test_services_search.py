"""Unit tests for app.services.search — url resolution."""
from app.services.search import _normalize_cr, _normalize_ss, _resolve_url


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


def test_normalize_ss_uses_doi_resolver_not_semanticscholar_landing_page():
    items = [{
        "title": "Deep Learning",
        "authors": [{"name": "Y. LeCun"}],
        "year": 2015,
        "venue": "Nature",
        "externalIds": {"DOI": "10.1038/nature14539"},
        "url": "https://www.semanticscholar.org/paper/abc123",
        "abstract": "...",
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
    }]
    results = _normalize_ss(items)
    assert results[0].url == "https://www.semanticscholar.org/paper/ghi789"


def test_normalize_cr_uses_doi_resolver_over_raw_url_field():
    items = [{
        "title": ["A CrossRef Paper"],
        "author": [{"given": "J.", "family": "Doe"}],
        "published-print": {"date-parts": [[2019]]},
        "container-title": ["Journal of Examples"],
        "DOI": "10.1000/xyz123",
        "URL": "https://api.crossref.org/works/10.1000%2Fxyz123",
        "abstract": "...",
    }]
    results = _normalize_cr(items)
    assert results[0].url == "https://doi.org/10.1000/xyz123"


def test_normalize_cr_falls_back_to_raw_url_when_no_doi():
    items = [{
        "title": ["No DOI Paper"],
        "author": [],
        "container-title": [],
        "URL": "https://example.org/paper",
        "abstract": None,
    }]
    results = _normalize_cr(items)
    assert results[0].url == "https://example.org/paper"
