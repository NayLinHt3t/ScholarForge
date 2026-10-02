# Spec: Outline Generation — Core Reliability

> **File:** `.docs/01-requirements/01-spec/2026-10-02-07-outline-generation-core.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Must-priority backlog rows BL-19 and BL-21 covering citation-validity enforcement and the actionable Ollama-unreachable error state.
> **Open questions resolved:** 1 (citation validation failure → block and reject the whole outline; do not deliver an outline with unverified markers)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| GENC-FR-01 | student | every [N] citation marker in my generated outline to reference a real resource I have saved | I can trust the outline without manually fact-checking every reference | Must | After generation, a validator checks 100% of [N] markers in the full outline text (section bodies, bullet points, draft passages if present, and bibliography) against the project's saved_resources; if any marker has no matching saved resource, the outline is rejected — it is not saved and not shown to the student; the error message lists each invalid marker (e.g. "[3] does not match any saved resource") and prompts the student to regenerate. | BL-19 |
| GENC-FR-02 | student | see a specific, actionable error message when the local AI engine is not running | I know why generation failed and exactly what to do next | Must | Before starting generation, the system sends a liveness ping to Ollama; if Ollama does not respond within 5 s, the UI displays: "The local AI engine (Ollama) is not running. Start Ollama and try again." — not a generic error message and not a raw stack trace; the ping check must not block or freeze the rest of the UI while waiting. | BL-21 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| GENC-NFR-01 | Citation-validation coverage | The validator must scan 100% of [N] markers in the generated outline before the outline is accepted; partial validation is not acceptable; the validation must be run even if the generator reported no citation errors itself | Must | BL-19 |
| GENC-NFR-02 | Ollama ping timeout | The Ollama liveness check must resolve (success or failure) within 5 s; the system must never hang indefinitely waiting for a connection; the UI must remain responsive during the check | Must | BL-21 |

## Legal / Compliance Requirements

*(None newly triggered — outline content is project-scoped application data already covered by the erasure cascade in PROJ-LR-01 (BL-34). The local Ollama model receives only the project's saved bibliographic metadata as input; no external hosted LLM is contacted — calling an external hosted LLM API is a Won't-for-v1 constraint.)*
