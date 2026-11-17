from app.models import SavedResource
from app.services import citations


def _resource(**overrides) -> SavedResource:
    defaults = dict(
        project_id="p1",
        title="Parameter-Efficient Transfer Learning for NLP",
        authors=["Neil Houlsby", "Andrei Giurgiu"],
        year=2019,
        venue="International Conference on Machine Learning",
        doi="10.48550/arXiv.1902.00751",
    )
    defaults.update(overrides)
    return SavedResource(**defaults)


class TestIEEE:
    def test_formats_with_number_and_two_authors(self):
        out = citations.format_ieee(_resource(), number=1)
        assert out.startswith("[1] N. Houlsby and A. Giurgiu, ")
        assert '"Parameter-Efficient Transfer Learning for NLP"' in out
        assert out.endswith("2019.")

    def test_three_plus_authors_use_et_al(self):
        out = citations.format_ieee(_resource(authors=["A B", "C D", "E F"]), number=2)
        assert "A. B et al." in out

    def test_missing_year_and_venue_degrade_cleanly(self):
        out = citations.format_ieee(_resource(year=None, venue=None), number=3)
        assert "n.d." in out
        assert ", , " not in out  # no empty-field artifacts


class TestAPA:
    def test_formats_authors_last_first(self):
        out = citations.format_apa(_resource())
        assert out.startswith("Houlsby, N., & Giurgiu, A.")
        assert "(2019)" in out
        assert "https://doi.org/10.48550/arXiv.1902.00751" in out

    def test_falls_back_to_url_without_doi(self):
        out = citations.format_apa(_resource(doi=None, url="https://example.com/paper"))
        assert "https://example.com/paper" in out
        assert "doi.org" not in out


class TestMLAChicago:
    def test_mla_includes_title_and_year(self):
        out = citations.format_mla(_resource())
        assert '"Parameter-Efficient Transfer Learning for NLP"' in out
        assert "2019" in out

    def test_chicago_inverts_each_author(self):
        out = citations.format_chicago(_resource(authors=["Neil Houlsby", "Andrei Giurgiu"]))
        assert "Houlsby, Neil" in out
        assert "Giurgiu, Andrei" in out


class TestFormatOneAndBibliography:
    def test_format_one_dispatches_by_style_case_insensitive(self):
        assert citations.format_one(_resource(), "apa") == citations.format_apa(_resource())
        assert citations.format_one(_resource(), "IEEE", number=1) == citations.format_ieee(_resource(), number=1)

    def test_unknown_style_falls_back_to_ieee(self):
        assert citations.format_one(_resource(), "harvard", number=1) == citations.format_ieee(_resource(), number=1)

    def test_build_bibliography_numbers_ieee_sequentially(self):
        resources = [_resource(title="First"), _resource(title="Second")]
        out = citations.build_bibliography(resources, "IEEE")
        lines = out.split("\n")
        assert lines[0].startswith("[1]")
        assert lines[1].startswith("[2]")

    def test_build_bibliography_apa_has_no_numbering(self):
        out = citations.build_bibliography([_resource()], "APA")
        assert not out.startswith("[1]")


class TestBibtex:
    def test_builds_key_from_first_author_surname_and_year(self):
        out = citations.format_bibtex(_resource())
        assert out.startswith("@article{Houlsby2019,")
        assert "title   = {Parameter-Efficient Transfer Learning for NLP}" in out

    def test_escapes_special_characters(self):
        out = citations.format_bibtex(_resource(title="A & B: 100% {test} #1_x^y"))
        assert r"\&" in out
        assert r"\{" in out and r"\}" in out
        assert r"\%" in out
        assert r"\#" in out
        assert r"\_" in out
        assert r"\^" in out

    def test_duplicate_keys_get_suffixed(self):
        seen: set[str] = set()
        r = _resource()
        first = citations.format_bibtex(r, 1, seen)
        second = citations.format_bibtex(r, 2, seen)
        assert "Houlsby2019," in first
        assert "Houlsby2019a," in second

    def test_build_bibtex_all_joins_with_blank_line(self):
        out = citations.build_bibtex_all([_resource(title="First"), _resource(title="Second")])
        assert out.count("@article{") == 2
        assert "\n\n@article{" in out
