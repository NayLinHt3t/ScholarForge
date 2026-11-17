# Case Study — ScholarForge

**Live URL**: https://scholarforge-tibn.onrender.com
**Team**: ClockChasers — see [project charter](../00-charter/project-charter.md) for roles.

## Problem

Students starting a thesis, research paper, or course project hit the same bottleneck: they have an *idea*, not yet the exact title/keyword a library search needs. Sources then scatter across bookmarks and notes, citations get hand-formatted (slow, error-prone), and going from "sources gathered" to "first words written" is the hardest step most tools stop short of helping with. Existing AI research tools add subscription cost, third-party login, and send research content to an external cloud vendor.

Full problem statement and target users: [proposal.md](../00-proposal/proposal.md).

## Process

- **Discover**: interviews ([interview-plan.md](../00-proposal/interview-plan.md), [interview-script.md](../00-proposal/interview-script.md)) validated the idea-search / fragmentation / blank-page pain points before build. Requirements captured as MoSCoW user stories in [backlog.md](../01-requirements/backlog.md), 14 feature specs in [01-requirements/01-spec/](../01-requirements/01-spec/).
- **Build**: architecture, ER, use-case, sequence, and activity diagrams in [02-design/diagrams/](../02-design/diagrams/); FastAPI + Firestore backend (`app/`); own test suite in `tests/` (20 files).
- **Test**: see [Test Plan](../../plan/) and session logs — real-user test sessions run by the team directly (see test plan folder for protocol and results).
- **Deliver**: this folder.

## Outcome

Before/after and measurement method per feature: [comparison-table.md](comparison-table.md).
AI feature proof (where/how/eval): [ai-logic.md](ai-logic.md).

## Key scope decisions

- Project-scoped data — no cross-assignment mixing.
- Read-only AI output (scaffold + copy/export) — no in-app paper-writing editor; writing stays the student's task.
- IEEE structure/citations by default; APA/MLA/Chicago available.
- AI provider is swappable (`AI_PROVIDER=ollama|groq`) — local-only for development, Groq free tier for the hosted deployment above (no GPU host required for grading access).
