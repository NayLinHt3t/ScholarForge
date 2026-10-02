# Diagram 0 — System Context (D1)

```mermaid
C4Context
    title System Context — ScholarForge (D1)

    Person(student, "Student", "Undergraduate or graduate student. Searches for papers by idea, builds a per-project library, generates an IEEE outline scaffold, and exports it to write their paper.")

    Enterprise_Boundary(machine, "Student's machine — localhost") {
        System(scholarforge, "ScholarForge", "FastAPI web app + SQLite. Semantic paper search, per-project research library, citation formatting (APA / MLA / IEEE), IEEE outline generation, and PDF / Markdown export.")
        System_Ext(ollama, "Ollama", "Local LLM process (nomic-embed-text + llama3.2:3b). Computes paper embeddings for search re-ranking and generates section-by-section outline scaffold text.")
    }

    System_Ext(semantic_scholar, "Semantic Scholar", "External academic paper search API. Returns paper metadata (title, authors, year, venue, abstract) for free-text idea queries.")
    System_Ext(crossref, "CrossRef", "External DOI registry and bibliographic metadata API. Queried in parallel with Semantic Scholar.")

    Rel(student, scholarforge, "Signs up · searches · saves papers · generates outline · exports", "Browser")
    Rel(scholarforge, semantic_scholar, "Paper candidate query (idea text only — no account data)", "HTTPS")
    Rel(scholarforge, crossref, "Paper candidate query (idea text only — no account data)", "HTTPS")
    Rel(scholarforge, ollama, "Embedding requests + RAG prompt with saved resource metadata", "HTTP · localhost:11434")
    Rel(ollama, scholarforge, "Embedding vectors + generated outline text", "HTTP · localhost:11434")
```

**Trust boundary** — the `Enterprise_Boundary` marks what stays on the student's machine. Only the idea-text search query crosses the boundary (to Semantic Scholar and CrossRef); account credentials, saved library content, and outline text never leave localhost.

**Ollama note** — Ollama is a separately-deployed process the student installs independently. ScholarForge pings it before generation (GENC-FR-02); if unreachable, it shows a specific "Start Ollama" error rather than a hang.
