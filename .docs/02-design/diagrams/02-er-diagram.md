# Diagram 2 — Entity-Relationship Diagram

Updated to add **Projects** as the scoping boundary: saved resources and generated outlines belong to a project, not directly to a user, so different assignments never mix (BL-32–BL-35).

```mermaid
erDiagram
    USERS {
        int id PK
        string email
        string password_hash
        datetime created_at
    }

    SESSIONS {
        string id PK
        int user_id FK
        datetime created_at
        datetime expires_at
    }

    PROJECTS {
        int id PK
        int user_id FK
        string name
        datetime created_at
        datetime updated_at
    }

    SAVED_RESOURCES {
        int id PK
        int project_id FK
        string title
        string authors "JSON list"
        int year
        string venue
        string doi
        string arxiv_id
        string url
        string abstract
        string source "semantic_scholar | crossref"
        blob embedding "float32 vector"
        datetime added_at
    }

    OUTLINES {
        int id PK
        int project_id FK
        string label
        string citation_style "APA | MLA | Chicago | IEEE (default)"
        text content "generated idea/outline scaffold, read-only"
        string cited_resource_ids "JSON list"
        datetime created_at
        datetime updated_at
    }

    USERS ||--o{ SESSIONS : "has"
    USERS ||--o{ PROJECTS : "owns"
    PROJECTS ||--o{ SAVED_RESOURCES : "contains"
    PROJECTS ||--o{ OUTLINES : "contains"
    SAVED_RESOURCES }o--o{ OUTLINES : "cited in (via cited_resource_ids)"
```

**Notes**:
- `SAVED_RESOURCES` has a uniqueness constraint on `(project_id, doi)` and `(project_id, arxiv_id)` — scoped per project (BL-11), not per account, so the same paper can legitimately be saved into two different projects.
- Renamed `PROPOSALS` → `OUTLINES` to match the reframed scope: this table holds a read-only generated idea/outline scaffold (bullet points + short example passages), not an editable finished paper — there is no rich-text editing surface, so `content` is written once per generation/regeneration, never hand-edited in place.
- Deleting a `PROJECTS` row cascades to delete all of its `SAVED_RESOURCES` and `OUTLINES` rows (BL-34); other projects are untouched.
- Search results are still never persisted — only rows a user explicitly saves become `SAVED_RESOURCES`.
