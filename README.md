# ScholarForge

A local, account-based research assistant for students: describe a research idea in plain language, get back semantically relevant papers, save them into a project-scoped library with auto-formatted citations, and generate a read-only IEEE outline scaffold to kick-start writing — which stays the student's own task.

No third-party login, no external LLM API. Everything runs on the student's own machine.

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
