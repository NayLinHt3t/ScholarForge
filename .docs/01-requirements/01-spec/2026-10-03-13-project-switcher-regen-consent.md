# Spec: Project Switcher, Per-Section Regeneration, and Consent Recording

> **File:** `.docs/01-requirements/01-spec/2026-10-03-13-project-switcher-regen-consent.md`
> **Date:** 2026-10-03
> **Pain notes summary:** Three related Should-priority gaps: students need a way to navigate between projects without losing their place (BL-35); students need to regenerate a single outline section without discarding the rest (BL-37); and the system needs to record consent at signup in a way that satisfies both PDPA and the ETA §9 evidence trail (BL-29).
> **Open questions resolved:** 3 (Q2: project switcher = "Back to projects" link only, navigating to the project list; Q7: per-section regeneration uses the same project library as the original full-generation run; Q6: BL-29 remains Should priority, but AUTH-LW-01 activates as a legal gate the moment the consent checkbox is implemented)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| PROJ-FR-03 | student | reach a "Back to projects" link from any in-project screen | I can return to the project list and open a different project without needing the browser back button | Should | A "Back to projects" link (or equivalent navigation element) is visible and reachable on every in-project page (library view, outline view, search results view); clicking it navigates to the project list page; the project list shows all of the student's projects and the student can open any one from there; no stale data from the just-left project remains visible after opening the new project (PROJ-FR-01 scoping rules apply immediately). | BL-35 |
| GEN-FR-03 | student | regenerate only one section of an existing outline (e.g. only "III. Proposed Methodology") without affecting the other sections | I can iterate on a weak section without discarding ideas I am happy with elsewhere in the outline | Should | Each generated IEEE section (I. Introduction, II. Related Work, III. Proposed Methodology, IV. Expected Contribution) has a "Regenerate this section" action; activating it re-runs the generation pipeline for that section only, using the same project library that was used for the original full-generation run (no re-selection required); every other section in the outline is left byte-for-byte unchanged; the newly generated section passes the same post-generation citation validator as GENC-FR-01 (all `[N]` markers must resolve to saved resources) before it replaces the old section; if the validator rejects the new section, the old section is preserved and an error message prompts the student to try again. | BL-37 |
| AUTH-FR-06 | student | have my acceptance of the terms and privacy policy recorded when I sign up | I can verify what I agreed to, and the system can demonstrate my informed consent if required | Should | At signup, before the account is created: a checkbox labeled with the exact version identifier of the current terms/privacy document (e.g. "I have read and agree to the Terms of Service v1.0 and Privacy Policy v1.0") must be presented and must be checked before the signup form submits; on form submission the system records: (a) the authenticated or newly created `user_id`, (b) the exact version string of the terms document agreed to, (c) a UTC timestamp, (d) the UI action that recorded agreement (checkbox checked + form submit); these four fields are stored in a dedicated `consent_records` table separate from the `users` table; signup is blocked if the checkbox is unchecked; the stored record is not deletable via the account-deletion flow (it must be retained as a legal record even after the account is removed). | BL-29 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| GEN-NFR-01 | Section-regeneration isolation | After a per-section regeneration (GEN-FR-03), a byte-level comparison of every section other than the regenerated one must show no changes; the outline persistence layer must update only the targeted section row/field | Should | BL-46 |
| AUTH-NFR-03 | Consent record immutability | The `consent_records` table must have no UPDATE or DELETE path reachable from application code outside a court-ordered legal-hold procedure; the account-deletion flow (AUTH-FR-05) must explicitly skip this table and leave consent records intact | Should | BL-47 |

## Legal / Compliance Requirements

| ID | Law | Obligation | Concrete requirement | Applies to |
|----|-----|------------|---------------------|------------|
| AUTH-LR-04 | ETA §9 | Electronic consent evidence trail | ETA §9 requires that an electronic action indicating intention to approve a document use a method that can (a) identify the signatory and (b) demonstrate intention to approve; AUTH-FR-06 satisfies this by recording who (user_id), what (terms version string), when (UTC timestamp), and how (checkbox + form-submit event) — these four fields are the minimum evidence to demonstrate §9 identification + intention-to-approve if the consent record is ever contested | AUTH-FR-06, AUTH-NFR-03 |
| AUTH-LR-05 | PDPA | Consent scope documentation | The version-string recorded in AUTH-FR-06 must correspond to a retrievable snapshot of the terms/privacy document so that the exact scope of data-processing purposes the user agreed to can be produced at audit or upon a data-subject access request; the document snapshot must be stored in a location not editable after the version is published | AUTH-FR-06 |
| AUTH-LR-06 | CCA §26 | Signup-action logging | The signup action (account creation + consent checkbox event) must emit a standard access-log entry (timestamp UTC, source IP, newly created user_id, action = signup) via the logging middleware (COMP-FR-01) — the consent record in `consent_records` is distinct from and supplements the access log; both must be written | AUTH-FR-06 |

### Legal watch items

- **AUTH-LW-01** (ETA §9): The moment the consent checkbox (AUTH-FR-06) is implemented in the UI, the four-field recording obligation (who / what / when / how) becomes a legal gate — not a should. Shipping the checkbox without the `consent_records` write would create a feature that implies consent was captured while providing no evidence it was. Do not ship the checkbox UI without the backend record write in the same release. Flag to a human before merging any PR that adds the signup consent checkbox.
