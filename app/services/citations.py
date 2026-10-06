import re

from app.models import SavedResource

STYLES = ("IEEE", "APA", "MLA", "Chicago")


def _initials(full_name: str) -> str:
    parts = full_name.strip().split()
    if len(parts) < 2:
        return full_name
    initials = ". ".join(p[0].upper() for p in parts[:-1])
    return f"{initials}. {parts[-1]}"


def _authors_ieee(authors: list[str]) -> str:
    if not authors:
        return ""
    first = _initials(authors[0])
    if len(authors) == 1:
        return first
    if len(authors) == 2:
        return f"{first} and {_initials(authors[1])}"
    return f"{first} et al."


def _authors_apa(authors: list[str]) -> str:
    if not authors:
        return ""
    def apa_one(name: str) -> str:
        parts = name.strip().split()
        if len(parts) < 2:
            return name
        last = parts[-1]
        initials = " ".join(p[0].upper() + "." for p in parts[:-1])
        return f"{last}, {initials}"
    formatted = [apa_one(a) for a in authors]
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + ", & " + formatted[-1]


def format_ieee(r: SavedResource, number: int | None = None) -> str:
    prefix = f"[{number}] " if number is not None else ""
    authors = _authors_ieee(r.authors)
    year = str(r.year) if r.year else "n.d."
    venue = r.venue or ""
    parts = [p for p in [authors, f'"{r.title}"', venue, year] if p]
    return prefix + ", ".join(parts) + "."


def format_apa(r: SavedResource) -> str:
    authors = _authors_apa(r.authors)
    year = f"({r.year})" if r.year else "(n.d.)"
    venue = f"*{r.venue}*" if r.venue else ""
    doi = f"https://doi.org/{r.doi}" if r.doi else (r.url or "")
    parts = [p for p in [authors, year, f"*{r.title}*", venue, doi] if p]
    return ". ".join(parts) + "."


def format_mla(r: SavedResource) -> str:
    authors = ", ".join(r.authors[:2]) if r.authors else ""
    title = f'"{r.title}"'
    venue = f"*{r.venue}*" if r.venue else ""
    year = str(r.year) if r.year else "n.d."
    parts = [p for p in [authors, title, venue, year] if p]
    return ". ".join(parts) + "."


def format_chicago(r: SavedResource) -> str:
    def chicago_one(name: str) -> str:
        parts = name.strip().split()
        return f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) >= 2 else name
    authors = ", ".join(chicago_one(a) for a in r.authors) if r.authors else ""
    title = f'"{r.title}"'
    venue = f"*{r.venue}*" if r.venue else ""
    year = str(r.year) if r.year else "n.d."
    parts = [p for p in [authors, title, venue, year] if p]
    return ". ".join(parts) + "."


def format_one(r: SavedResource, style: str, number: int | None = None) -> str:
    style = style.upper()
    if style == "IEEE":
        return format_ieee(r, number)
    if style == "APA":
        return format_apa(r)
    if style == "MLA":
        return format_mla(r)
    if style == "CHICAGO":
        return format_chicago(r)
    return format_ieee(r, number)


def build_bibliography(resources: list[SavedResource], style: str = "IEEE") -> str:
    lines = []
    for i, r in enumerate(resources, 1):
        number = i if style.upper() == "IEEE" else None
        lines.append(format_one(r, style, number))
    return "\n".join(lines)


# ── BibTeX export ──────────────────────────────────────────────────────────────

def _bibtex_escape(s: str) -> str:
    return (s.replace('\\', '\\\\')
             .replace('{', r'\{')
             .replace('}', r'\}')
             .replace('&', r'\&')
             .replace('%', r'\%')
             .replace('#', r'\#')
             .replace('_', r'\_')
             .replace('^', r'\^')
             .replace('~', r'\~'))


def _bibtex_key(r: SavedResource, index: int, seen: set[str]) -> str:
    first = r.authors[0].strip() if r.authors else ""
    last = re.sub(r'[^a-zA-Z]', '', first.split()[-1]) if first else ""
    year = str(r.year) if r.year else "nd"
    base = (last or "ref") + year
    key, suffix = base, ord('a')
    while key in seen:
        key = base + chr(suffix)
        suffix += 1
    seen.add(key)
    return key


def format_bibtex(r: SavedResource, index: int = 1, seen: set[str] | None = None) -> str:
    if seen is None:
        seen = set()
    key = _bibtex_key(r, index, seen)
    fields = []
    if r.authors:
        fields.append(f"  author  = {{{_bibtex_escape(' and '.join(r.authors))}}}")
    fields.append(f"  title   = {{{_bibtex_escape(r.title)}}}")
    if r.year:
        fields.append(f"  year    = {{{r.year}}}")
    if r.venue:
        fields.append(f"  journal = {{{_bibtex_escape(r.venue)}}}")
    if r.doi:
        fields.append(f"  doi     = {{{_bibtex_escape(r.doi)}}}")
    elif r.url:
        fields.append(f"  url     = {{{_bibtex_escape(r.url)}}}")
    return "@article{" + key + ",\n" + ",\n".join(fields) + "\n}"


def build_bibtex_all(resources: list[SavedResource]) -> str:
    seen: set[str] = set()
    return "\n\n".join(format_bibtex(r, i, seen) for i, r in enumerate(resources, 1))
