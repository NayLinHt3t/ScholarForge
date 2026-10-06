# ScholarForge

**ScholarForge is a privacy-focused research assistant that uses semantic retrieval and locally hosted LLMs to help students discover, organize, summarize, and develop research ideas from academic sources while maintaining deterministic citation traceability.**

No third-party login, no external LLM API. Everything runs on the student's own machine.

### Engineering highlights
- Semantic search with embedding-based cosine-similarity ranking
- Project-scoped data isolation enforced at every API and database layer
- Local LLM/RAG pipeline (Ollama — no external AI API)
- Deterministic citation generation — LLM produces `[N]` markers only; the application owns numbering, metadata, and formatting
- LLM output validation — every generated `[N]` marker is validated before persistence; invalid outputs are rejected with a retry path
- Structured observability — search, embedding, ranking, and generation latencies logged per request
- Prompt injection protection — retrieved paper abstracts are explicitly marked as data, not instructions, in every prompt
- REST API architecture (FastAPI) with external API integration (Semantic Scholar, CrossRef)

## Features

- **Semantic paper search** — free-text idea query re-ranked by embedding cosine similarity against Semantic Scholar and CrossRef results; low-confidence results trigger a "try rephrasing" notice
- **Project-scoped library** — save papers into named projects; duplicate detection per project; delete without affecting other projects
- **Citation formatting** — IEEE (default), APA, MLA, Chicago; instant client-side style switch with server-side persistence; BibTeX export per resource and for the whole library
- **Outline generation (RAG)** — Ollama-powered IEEE scaffold (Title / Abstract / Index Terms / I–IV sections / References) grounded in saved sources; post-generation citation validator rejects hallucinated references; per-section regeneration
- **Draft callout** — each section's AI-drafted paragraph is labeled "Draft — revise before use" in a distinct callout box
- **Source summarization** — select sources, generate a 150–300 word cited synthesis headed by the project name; citation validator enforced
- **Export** — copy any section or the full outline; download as `.md` or PDF

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12 · FastAPI · Jinja2 |
| Database | Google Cloud Firestore |
| AI | Ollama — `nomic-embed-text` (embeddings) · `llama3.2:3b` (generation) |
| External APIs | Semantic Scholar · CrossRef |
| PDF export | fpdf2 |

## Prerequisites

1. **Ollama** running locally with the required models:
   ```bash
   ollama pull nomic-embed-text
   ollama pull llama3.2:3b
   ollama serve
   ```

2. **Google Cloud Firestore** — create a Firebase project, download a service-account key, and set:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=./serviceAccountKey.json
   ```

3. **Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running

```bash
cp .env.example .env   # fill in GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS
uvicorn app.main:app --port 8000 --reload
```

Open `http://localhost:8000` — sign up, create a project, and start researching.

## Repo structure

```
.
├── app/                        # FastAPI application
│   ├── main.py
│   ├── config.py               # SEARCH_LOW_CONFIDENCE_THRESHOLD and other constants
│   ├── routers/                # auth, projects, search, library, outline, summary
│   ├── services/               # search, citations, outline (RAG), summary, export
│   ├── models/                 # Pydantic models (User, Project, SavedResource, Outline)
│   └── templates/              # Jinja2 HTML templates (dark sidebar UI)
├── requirements.txt
├── rule.md                     # Legal/compliance rules (PDPA, CCA §26, ETA §9)
└── .docs/
    ├── 00-charter/             # Project charter
    ├── 00-proposal/            # Problem statement, interview plan/script
    ├── 01-requirements/        # Backlog (MoSCoW) and spec files
    ├── 02-design/              # Feature list, user journeys, diagrams, prototype
    └── 03-compliance/          # Legal requirements mapped to features
```

## Key scope decisions

- **Projects, not one big pile.** Every saved resource and generated outline belongs to a project. Deleting a project cascades only within itself.
- **No in-app text editor.** The app produces a read-only scaffold with Copy/Regenerate/Export. Writing the actual paper is the student's task.
- **IEEE by default.** Structure and citations default to IEEE; APA/MLA/Chicago are available.
- **Local-only.** No third-party identity provider, no external LLM API.

## Compliance

[rule.md](rule.md) covers PDPA, Computer Crime Act §26, and Electronic Transactions Act §9/26/28. [legal-requirements.md](.docs/03-compliance/legal-requirements.md) maps each rule to specific features, including flagged gaps (consent recording, access-log middleware) not yet implemented.
