# Legal Requirements — Applied to ScholarForge

This maps the general rules in [`rule.md`](../../rule.md) to this specific app's features. Read `rule.md` first for *why* each rule exists; this document says *where in ScholarForge* it applies and what concretely must be built to satisfy it.

## PDPA — where it applies here

| App feature | Personal/sensitive data involved | Concrete requirement | Implementing module (per the approved plan) |
|---|---|---|---|
| Signup (BL-01) | Email, password | Explicit signup action = consent to store these two fields for account purposes only; password never stored in plaintext (bcrypt hash only). | `app/auth/security.py` |
| Session/login (BL-02, BL-03) | Session token tied to account | Session data used only to keep the user authenticated — not repurposed for tracking/analytics without separate disclosure. | `app/auth/dependencies.py` |
| Idea search (BL-05) | The idea text itself, if it reveals something personal (rare, but possible e.g. a health-related research idea) | Idea text is sent to Semantic Scholar/CrossRef as a search query only — never stored against the user's identity beyond the transient request; not logged with content, only logged as an access event (see Computer Crime Act section below). | `app/search/pipeline.py` |
| Project deletion (BL-34) | Bibliographic metadata + generated outline content, tied to a project | Deleting a project must cascade to **all** of that project's `saved_resources` and `outlines` rows — this is now the primary way a user exercises the PDPA right to erasure for a specific piece of work, without needing to delete their whole account. | `app/projects/service.py` |
| Saved library (BL-10–BL-13) | Bibliographic metadata (not personal data about the *user*, but tied to their account via a project) | Deletable per-item within a project (BL-12), and in bulk via project deletion (BL-34). | `app/resources/service.py` |
| Generated outlines (BL-18, BL-22) | User-facing generated text, tied to a project | Same deletability/export expectations as saved resources — a user can export (BL-23) and delete via project deletion; there is no in-app editing to create additional retained versions (no rich-text editor, per the current scope). | `app/outlines/routes.py` |
| Account deletion (not yet in backlog — **gap**) | All of the above, across every project | **Action item**: add a "delete my account" flow that cascades to `sessions` and every `project` (which in turn cascades to that project's `saved_resources`/`outlines`) for that `user_id`. Currently missing from the backlog — add as a Must-have before any real users onboard. | New: `app/auth/routes.py` (delete endpoint) |

**Sensitive personal data**: this app is not designed to elicit sensitive categories (health, biometric, religion, etc.) as a matter of course. If a student's research idea happens to touch one of these categories, no special handling is required *for the app*, because the app doesn't classify or act on the content of the idea beyond running a search — it doesn't retain or profile based on the idea's subject matter beyond what the user explicitly saves.

## Computer Crime Act §26 — where it applies here

| App feature | Log requirement | Concrete requirement | Implementing module |
|---|---|---|---|
| Every authenticated request (search, save, generate, edit) | Access/traffic log, ≥90 days retention, tied to a real user | Add a request-logging middleware in FastAPI that records: timestamp, source IP, authenticated `user_id` (or "unauthenticated"), method + path. Store in a dedicated `access_logs` table or append-only log file, not the same table as application data. | **Gap — not yet in the file structure.** Add `app/logging/access_log.py` + middleware registration in `app/main.py`. |
| Log retention | ≥90 days before rotation/deletion eligibility | Set retention policy explicitly (e.g. a scheduled cleanup job that only deletes rows older than 90 days) — don't rely on an unbounded table with no policy, and don't set a shorter default. | Same module as above |
| Log integrity | Tamper-evident, append-only | Application code should never `UPDATE` or `DELETE` individual log rows outside the retention-cleanup job. | Same module as above |

**Action item**: the approved plan's file structure did not originally include an access-logging module — this is a compliance gap to close in Epic 7 (Reliability) or as its own small epic before the app is used with real accounts. Backlog items BL-27 already flags this; this document makes it concrete.

## Electronic Transactions Act §9/26/28 — where it applies here

ScholarForge does **not** currently implement any electronic-signature feature — there's no "sign and submit" flow (e.g. submitting a proposal to an institution with a binding signature). The relevant sections apply narrowly today, but should be tracked for when/if that changes:

| App feature | Applies? | Concrete requirement |
|---|---|---|
| Signup consent ("I agree" to terms, if added) | §9-adjacent | If a terms/privacy consent checkbox is added at signup (BL-29), record **who** (user_id), **what** (a version identifier of the terms text), **when** (timestamp), **how** (checkbox click event) — this is the same evidence trail §9 requires for signature validity, applied to a consent action rather than a contract signature. |
| Proposal export/submission | Not yet — **watch item** | If a future version lets a student submit a proposal directly to an advisor/institution through the app (rather than just downloading it), that submission likely becomes something the §9 validity test and possibly the §26 reliability presumption apply to. At that point: do not label it "digitally signed" unless the sole-control + tamper-detectable criteria in `rule.md` are actually met. |
| Third-party CA integration | Not applicable — no CA involved | No action needed while the app has no signature feature. |

**Net effect for now**: no code changes required under this Act today, but the consent-recording requirement (BL-29) should be built the same way a signature audit trail would be, so the app doesn't need rework if a signing feature is added later.

## Summary of gaps to add to the backlog

1. **Account deletion** (PDPA right to erasure) — cascading delete across sessions and every project (which itself cascades to that project's resources/outlines — verify this project-level cascade, BL-34, actually works before relying on it for account-level deletion too).
2. **Access-log middleware with ≥90-day retention** (Computer Crime Act §26) — currently the single biggest concrete gap between the approved technical plan and this compliance review.
3. **Consent-recording at signup** (BL-29, supports both PDPA and a future ETA-adjacent signature feature) — record who/what/when/how, not just a boolean "agreed" flag.
