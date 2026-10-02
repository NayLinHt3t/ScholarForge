# Diagram 6 — Activity: Core Workflow (D4)

End-to-end student journey from app open to outline export.
Each node traces to at least one spec requirement.

```mermaid
flowchart TD
    S(["● Start"])
    E(["◉ End — student writes paper\nin their own tool"])

    %% ── AUTH ──────────────────────────────────────────────
    A1{"Existing\naccount?"}
    A2["Sign up\nAUTH-FR-01 · BL-01"]
    A3["Log in\nAUTH-FR-02 · BL-02"]

    %% ── PROJECTS ──────────────────────────────────────────
    P1{"Has a\nproject?"}
    P2["Create project\nBL-32"]
    P3["Open project\nPROJ-FR-01 · BL-33"]

    %% ── SEARCH ────────────────────────────────────────────
    D1["Type research idea\nSRCH-FR-01 · BL-05"]
    D2{"Ollama\nreachable?"}
    D3(["⚠ Show 'Start Ollama' error\nGENC-FR-02 · BL-21"])
    D4["Query Semantic Scholar\n+ CrossRef in parallel\nSRCH-FR-01 · BL-05"]
    D5["Re-rank by embedding\ncosine similarity\nSRCH-FR-02 · BL-06"]
    D6["Display ranked result cards\nSRCH-FR-03 · BL-07"]

    %% ── LIBRARY ───────────────────────────────────────────
    L1{"Save\nthis paper?"}
    L2{"Duplicate\nin project?"}
    L3(["ℹ Blocked — already saved\nLIB-FR-02 · BL-11"])
    L4["Save paper to project library\nLIB-FR-01 · BL-10"]
    L5{"Search\nagain?"}

    %% ── GENERATE ──────────────────────────────────────────
    G0{"Library\nhas papers?"}
    G1["Tap 'Generate outline'\nBL-18"]
    G2{"Ollama\nreachable?"}
    G3(["⚠ Show 'Start Ollama' error\nGENC-FR-02 · BL-21"])
    G4["Build RAG prompt per section\nBL-18 · GEN-FR-01"]
    G5["Validate all citation markers\nGENC-FR-01 · BL-19"]
    G6{"All citations\nvalid?"}
    G7(["⚠ Reject — list invalid markers\nregenerate required\nGENC-FR-01 · BL-19"])
    G8["Render read-only outline\nBL-22 · GEN-FR-02"]

    %% ── EXPORT ────────────────────────────────────────────
    X1{"Export\nchoice"}
    X2["Copy section or full outline\nBL-22"]
    X3["Download PDF — labeled DRAFT\nEXP-FR-01 · BL-23"]
    X4["Download Markdown\nEXP-FR-01 · BL-23"]

    %% ── FLOW ──────────────────────────────────────────────
    S --> A1
    A1 -- No --> A2 --> A3
    A1 -- Yes --> A3

    A3 --> P1
    P1 -- No --> P2 --> P3
    P1 -- Yes --> P3

    P3 --> D1
    D1 --> D2
    D2 -- No --> D3
    D2 -- Yes --> D4 --> D5 --> D6

    D6 --> L1
    L1 -- Yes --> L2
    L2 -- Yes --> L3 --> L5
    L2 -- No --> L4 --> L5
    L1 -- No --> L5
    L5 -- Yes --> D1
    L5 -- No --> G0

    G0 -- No, need more papers --> D1
    G0 -- Yes --> G1 --> G2
    G2 -- No --> G3
    G2 -- Yes --> G4 --> G5 --> G6
    G6 -- No --> G7 --> G1
    G6 -- Yes --> G8

    G8 --> X1
    X1 --> X2 & X3 & X4
    X2 & X3 & X4 --> E
```

**Loops**
- `Search again → Type idea` — iterative research; student deepens or pivots the query without losing the saved library.
- `No papers in library → Type idea` — guard before generation; prevents generating from an empty context.
- `Invalid citations → Generate` — GENC-FR-01 rejection forces a clean retry; no partially-verified outline is ever shown.

**Error exits** (⚠ nodes) are terminal per-path — the student must fix the upstream condition (start Ollama, rephrase idea) before the main flow resumes. They are not shown connecting to `End` because the session is still active.

**Scope boundary** — `End` is the deliberate handoff point: the student takes the scaffold to their own word processor. Nothing in ScholarForge continues after export (no in-app editor — BL-22 / Won't-for-v1).
