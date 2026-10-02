# Skill: audit-backlog

Audit the two-way traceability between Must-priority requirements and the product backlog.

## What this skill does

1. Collects every Must-priority requirement from every spec file in `.docs/01-requirements/01-spec/`.
2. Collects every row from `.docs/01-requirements/backlog.md`.
3. Checks **forward**: every Must requirement has a matching backlog row.
4. Checks **backward**: every backlog row traces to a real requirement ID.
5. Reports gaps and orphans clearly.
6. **Never silently merges two items that might be the same thing — always asks the user first.**

---

## Steps

### Step 1 — Collect Must requirements from the spec

Read every file under `.docs/01-requirements/01-spec/` (create the path in your head even if it is empty; list it first with Bash so you know what exists).

For each file, extract rows or lines that:
- Are marked with a priority of **Must** (case-insensitive: "Must", "MUST", "must-have", etc.)
- Have an identifier — a requirement ID like `REQ-01`, `FR-01`, `NFR-03`, or any `LETTERS-DIGITS` pattern in that file's ID column.

Build a list:
```
{id: "REQ-01", summary: "<first ~10 words of the requirement text>", file: "<filename>"}
```

If the `01-spec/` directory does not exist or is empty, print a warning:
> **Warning:** `.docs/01-requirements/01-spec/` is empty or missing. No spec requirements to audit against. Backlog orphan check will still run.

### Step 2 — Collect backlog rows

Read `.docs/01-requirements/backlog.md`.

For every table row (lines that start with `|`), skip header/separator rows and extract:
- The **ID** in the first column (e.g. `BL-01`)
- Whether the **Priority** column says **Must** (also capture rows of other priorities — you need them for the backward check)
- A short summary of the user story / requirement text

Build a list:
```
{id: "BL-01", summary: "<first ~10 words>", priority: "Must|Should|Could|Won't"}
```

### Step 3 — Forward check (spec → backlog)

For each Must requirement from Step 1, look for a matching backlog row.

**Matching rules (in order of confidence):**
1. **Exact ID match** — the spec ID appears verbatim inside the backlog row's ID or in its text. High confidence.
2. **Cross-reference in text** — the backlog row's user story or acceptance criteria explicitly names the spec ID. High confidence.
3. **Semantic similarity** — the subject matter overlaps strongly (same feature, same actor, same constraint). Low confidence — **do not auto-match**.

For each Must requirement:
- If a high-confidence match exists → mark as **covered**.
- If only a low-confidence candidate exists → **stop and ask the user**:
  > "Spec requirement `{id}` (`{summary}`) might match backlog row `{bl-id}` (`{bl-summary}`). Are these the same item, or are they distinct and both needed?"
  Wait for the user's answer before continuing.
- If no match exists → mark as **gap**.

### Step 4 — Backward check (backlog → spec)

For each backlog row (any priority), look for a real spec requirement it traces to.

A backlog row **traces** to a spec requirement when:
1. Its ID or text explicitly cites a spec ID (e.g. `REQ-01`), **or**
2. A matching spec requirement was confirmed in Step 3.

If a backlog row's claimed spec ID does not exist in any spec file → mark as **orphan** (broken link).

If a backlog row has no spec citation at all → mark as **untraced** (not necessarily wrong, but call it out so the user can decide).

### Step 5 — Report

Print a structured report in this order:

```
## Audit report — backlog vs. spec (Must only)
Date: <today>

### Gaps (Must requirements with no backlog row)
| Spec ID | Summary | File |
|---------|---------|------|
| ...     | ...     | ...  |
(none — all Must requirements are covered.) ← if empty

### Orphaned backlog rows (ID cites a spec requirement that doesn't exist)
| Backlog ID | Claimed Spec ID | Summary |
|------------|-----------------|---------|
| ...        | ...             | ...     |
(none) ← if empty

### Untraced backlog rows (no spec citation at all)
| Backlog ID | Priority | Summary |
|------------|----------|---------|
| ...        | ...      | ...     |
(none) ← if empty

### Confirmed coverage
| Spec ID | Backlog ID | Match type |
|---------|------------|------------|
| ...     | ...        | exact / cross-ref |
```

End with one-line summary:
> `N` Must requirements, `M` covered, `G` gaps, `O` orphans, `U` untraced rows.

---

## Constraints

- **Ask, never assume.** If a spec requirement and a backlog row might be the same thing but you are not certain, ask the user before marking them as matched. The cost of a false merge is higher than the cost of one question.
- Do not create, edit, or delete any files. This skill is read-only.
- Do not invent requirement IDs. Only cite IDs that literally appear in the files.
- If the spec directory does not exist, say so clearly and still run the backward check on the backlog.
