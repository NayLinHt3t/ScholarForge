# ScholarForge

A local, account-based research assistant for students: describe a research idea in plain language, get back semantically relevant papers, save them into a project-scoped library with auto-formatted citations, and generate a read-only idea/outline scaffold (not a finished paper) to kick-start the actual writing — which stays the student's own task.

No third-party login, no external LLM API, no cloud hosting. Everything runs on the student's own machine.

## Status

**Documentation and design complete; implementation not yet started.** This repo currently holds the case-study deliverables (proposal, backlog, design artifacts, compliance mapping) and a clickable static prototype. The build order and technical plan are ready to execute — see [Implementation plan](#implementation-plan) below.

## Repo structure

```
.
├── rule.md                                  # Legal/compliance rules for AI agents (PDPA, Computer Crime Act, ETA)
└── .docs/
    ├── 00-proposal/
    │   └── proposal.md                      # Problem statement, target users, solution summary
    ├── 01-requirements/
    │   └── backlog.md                       # Full product backlog (epics, user stories, MoSCoW priority)
    ├── 02-design/
    │   ├── feature-list.md                  # Consolidated feature list by area
    │   ├── user-journey.md                  # Key user journeys (A/B/C)
    │   ├── prototype.md                     # What the clickable prototype demonstrates
    │   ├── prototype.html                   # Static, no-backend clickable mockup — open directly in a browser
    │   └── diagrams/
    │       ├── 01-architecture-diagram.md   # System architecture (Mermaid)
    │       ├── 02-er-diagram.md             # Entity-relationship diagram (Mermaid)
    │       ├── 03-idea-search-sequence.md   # Idea → ranked papers sequence diagram
    │       └── 04-proposal-generation-sequence.md  # Idea & outline generation (RAG) sequence diagram
    └── 03-compliance/
        └── legal-requirements.md            # rule.md's rules mapped to this app's specific features + gaps
```

## Try the prototype

`.docs/02-design/prototype.html` is a self-contained, static HTML mockup — no server, no dependencies. Open it directly in any browser to click through: sign up → create a project → search an idea → save results → generate a read-only outline → regenerate a section → see project isolation by creating a second project and deleting one without affecting the other.

## Key scope decisions

- **Projects, not one big pile.** Every saved resource and generated outline belongs to a project the student creates. Deleting a project cascades only within itself — other projects are untouched.
- **No in-app text editor.** The app generates a read-only scaffold — bullet-point ideas and short example passages per section, grounded in the project's saved sources — with Copy/Regenerate/Export actions. Writing the actual paper is explicitly the student's task, done in their own tool.
- **IEEE by default.** Citations and the generated outline's structure (Title/Abstract/Index Terms/Roman-numeral sections/numbered references) default to IEEE style; APA/MLA/Chicago remain available.
- **Local-only.** FastAPI + SQLite + Ollama (local embeddings + generation), all on `localhost`. "No third party" means no third-party identity provider and no external LLM API — not "no backend."

Full rationale for each decision is in [proposal.md](.docs/00-proposal/proposal.md) and the backlog's scope-correction notes.

## Compliance

See [rule.md](rule.md) for the general legal rules (PDPA, Computer Crime Act §26, Electronic Transactions Act §9/26/28) and [legal-requirements.md](.docs/03-compliance/legal-requirements.md) for how they map to this app's specific features — including flagged gaps (account deletion, access-log middleware, consent recording) still to be added before real users onboard.

## Implementation plan

The approved technical plan (stack, data model, file structure, RAG pipeline, build order, and manual verification steps) is tracked separately from this repo's docs and is ready to execute:

- **Stack**: Python + FastAPI, SQLite via SQLAlchemy, Jinja2 + htmx + vanilla JS, Ollama for local embeddings (`nomic-embed-text`) and generation (`llama3.2:3b`).
- **Build order**: auth → projects CRUD → external API clients (Semantic Scholar, CrossRef) → Ollama smoke test → idea search pipeline → project-scoped library → citation formatting → outline generation (RAG) → per-section regeneration → copy/export → polish.
- **Prerequisites**:
  ```bash
  ollama pull nomic-embed-text
  ollama pull llama3.2:3b
  pip install weasyprint   # HTML/CSS -> PDF for outline export
  ```
  Ollama must be running (`ollama serve`) whenever the backend runs.
