# Spec: Project Management

> **File:** `.docs/01-requirements/01-spec/2026-10-02-03-project-management.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Must-priority backlog rows BL-33 and BL-34 covering project scoping and cascading project deletion.
> **Open questions resolved:** 0 (requirements were sufficiently defined in the source backlog rows)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| PROJ-FR-01 | student | open a project and have every subsequent search, save, generate, list, and delete action scoped to that project | data from different assignments never appears in the same view | Must | Entering a project sets the active project_id for the user's session context; every query that reads or writes project-scoped data (saved_resources, outlines) is parameterized with WHERE project_id = ? AND user_id = ?; switching to a different project immediately updates the scope — no resources or outlines from the previous project are visible. | BL-33 |
| PROJ-FR-02 | student | delete a project I no longer need, with a confirmation step | my workspace stays clean and no data from that project remains in the system | Must | Clicking "Delete project" shows a confirmation prompt stating the project name and warning that all its resources and outlines will be permanently deleted; on confirmation, the project row and all of its saved_resources and outlines are deleted in a single atomic database transaction; every other project is completely unaffected; the deleted project disappears from the project list immediately after the transaction commits. | BL-34 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| PROJ-NFR-01 | Data isolation | Every query on project-scoped tables must be parameterized with both project_id and user_id; a database-level foreign key (projects.user_id → users.id) must enforce ownership at the storage layer, not only in application code | Must | BL-33 |
| PROJ-NFR-02 | Atomic delete | Project deletion (project row + all saved_resources + all outlines) must be executed inside a single database transaction; if any part of the cascade fails, the entire operation rolls back and the project remains fully intact | Must | BL-34 |

## Legal / Compliance Requirements

| ID | Law | Obligation | Concrete requirement | Applies to |
|----|-----|------------|---------------------|------------|
| PROJ-LR-01 | PDPA | Per-project erasure path | Project deletion is the primary per-project PDPA erasure mechanism; the cascade must cover all project application data (saved_resources, outlines) but must NOT delete access-log entries — those must be retained per CCA §26 (see COMP-NFR-01) | PROJ-FR-02 |
| PROJ-LR-02 | CCA §26 | Project-action logging | Opening a project and deleting a project must each generate an access-log entry containing: timestamp (UTC), source IP, user_id, action name (open-project / delete-project), project_id | PROJ-FR-01, PROJ-FR-02 |
