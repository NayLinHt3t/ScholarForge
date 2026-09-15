# Diagram 4 — Sequence: Idea & Outline Generation (RAG)

Covers BL-18 / BL-19 / BL-20 / BL-21 / BL-37. Output is a **read-only** scaffold (bullet ideas + short starter passages), not an editable finished draft — there is no in-app text editor (see [backlog scope note](../../01-requirements/backlog.md)).

```mermaid
sequenceDiagram
    actor Student
    participant UI as Browser
    participant API as FastAPI /projects/{id}/outlines/generate
    participant DB as SQLite
    participant Ollama as Ollama (local)
    participant Val as citation_validator
    participant Cite as citations.formatters

    Student->>UI: click "Generate outline" (within current project)
    UI->>API: POST /projects/{project_id}/outlines/generate {style}
    API->>DB: load saved_resources for project_id
    DB-->>API: resources[] (with embeddings)

    loop for each section (Intro, Related Work, Methodology, ...)
        Note over API: select subset of resources most<br/>similar to this section's topic
        API->>API: build numbered reference list + prompt<br/>(ask for bullet ideas + one short example passage,<br/>not full prose)
        API->>Ollama: generate(section_prompt)
        Ollama-->>API: section_text (bullets + [N] markers)
        API->>Val: validate(section_text, allowed_ids)
        Val-->>API: cleaned_section_text (strips/flags invalid [N])
    end

    API->>Cite: format bibliography(resources_cited, style)
    Cite-->>API: bibliography_text
    Note over API: bibliography is generated deterministically —<br/>never authored by the LLM (BL-19/BL-20)

    API->>DB: save outline {project_id, content, cited_resource_ids}
    API-->>UI: assembled outline + bibliography
    UI-->>Student: render READ-ONLY outline with copy/export actions<br/>(no editing surface — BL-22)

    alt Ollama unreachable at any generate() call
        API-->>UI: 503 "AI engine unavailable, outline not generated"
        UI-->>Student: clear error banner, no partial/corrupt outline saved
    end

    opt Regenerate one section (BL-37)
        Student->>UI: click "Regenerate" on a single section
        UI->>API: POST /projects/{project_id}/outlines/{id}/sections/{n}/regenerate
        API->>Ollama: generate(section_prompt) — same as above, one section only
        API->>DB: update only that section's content
        API-->>UI: updated section
        UI-->>Student: only that section re-renders; rest untouched
    end
```
