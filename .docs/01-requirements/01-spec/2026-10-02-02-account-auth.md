# Spec: Account & Authentication

> **File:** `.docs/01-requirements/01-spec/2026-10-02-02-account-auth.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Must-priority backlog rows BL-01 – BL-04 covering signup, session management, logout, and per-account data isolation. PDPA gap (account deletion, BL-39) promoted to Must and added here.
> **Open questions resolved:** 2 (account deletion → new Must BL-39; bcrypt cost floor → ≥ 12)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| AUTH-FR-01 | student | sign up with a unique email address and a password | I have my own private account with no third-party login required | Must | Signup form accepts email + password; email format is validated (RFC-5321 local@domain); duplicate email is rejected with a clear error before any row is written; password is stored only as a bcrypt hash (cost ≥ 12, see AUTH-NFR-01); no plaintext password appears in any log, column, or in-memory cache after hashing. | BL-01 |
| AUTH-FR-02 | returning student | log in with my email and password and stay logged in across browser restarts | I don't have to re-authenticate on every visit | Must | Successful login issues a signed session cookie with HttpOnly=true, SameSite=Lax, Max-Age=2592000 (30 days); failed login returns HTTP 401 with a generic "invalid credentials" message that does not distinguish between wrong email and wrong password; session persists across browser restarts until expiry or logout. | BL-02 |
| AUTH-FR-03 | student | log out | my session ends on this device immediately | Must | Logout invalidates the session row server-side synchronously before the response is returned to the client; the session cookie is cleared in the Set-Cookie response header; any subsequent request with the invalidated cookie is rejected with HTTP 401. | BL-03 |
| AUTH-FR-04 | student | have all my projects, saved resources, and outlines visible only to my account | no other person on the same machine can read or modify my data | Must | Every database query on project-scoped tables (projects, saved_resources, outlines) is parameterized with the authenticated user_id; requests without a valid session, or with a session belonging to a different user_id, are rejected with HTTP 401/403 before any data is read or written. | BL-04 |
| AUTH-FR-05 | student | permanently delete my account and all its data | I can exercise my right to erasure and no personal data remains in the system | Must | "Delete account" action (1) invalidates all active sessions for the user, (2) cascades to delete every project owned by the user — each project cascade also deletes that project's saved_resources and outlines (per BL-34 / PROJ-FR-02) — then (3) deletes the user record itself; all deletions are committed in a single atomic transaction; a confirmation step requiring the student to re-type their email prevents accidental deletion. | BL-39 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| AUTH-NFR-01 | Password security | Password stored only as a bcrypt hash with work factor (cost) ≥ 12; plaintext password must not exist in any log entry, database column, or in-memory cache after the hash is computed | Must | BL-01 |
| AUTH-NFR-02 | Session cookie hygiene | Session cookie must be: Signed (server-generated opaque token), HttpOnly=true, SameSite=Lax, Max-Age=2592000 (30 days); Secure flag must be set in any environment not running on localhost | Must | BL-02 |

## Legal / Compliance Requirements

| ID | Law | Obligation | Concrete requirement | Applies to |
|----|-----|------------|---------------------|------------|
| AUTH-LR-01 | PDPA | Legal basis for personal data collection | Email address is personal data; the legal basis for collection is contract necessity (user registers to use the service); this basis must be documented in a data-processing record or a code comment at the point of user record creation before the INSERT is executed | AUTH-FR-01 |
| AUTH-LR-02 | PDPA | Right to erasure — end-to-end deletion | Account deletion must cascade to every table holding the user's personal data: users, sessions, projects, and within each project: saved_resources and outlines; no row referencing the deleted user_id must remain in any application table after the transaction commits | AUTH-FR-05 |
| AUTH-LR-03 | CCA §26 | Auth-flow access logging | Every signup, login attempt (successful and failed), and logout must write an access-log entry containing: timestamp (UTC), source IP, action name (signup / login / logout), and user_id (for failed logins, hash the email — do not log plaintext email in the access log); access log must be retained ≥ 90 days (see COMP-FR-01 / COMP-NFR-01) | AUTH-FR-01, AUTH-FR-02, AUTH-FR-03 |

### Legal watch items

- **AUTH-LW-01** (ETA §9): If a "I agree to terms / privacy policy" checkbox is added at signup (linked to BL-29), this triggers the Electronic Transactions Act §9 evidence requirement. At that point the system must record: user_id, exact document version or hash of the terms text, UTC timestamp, UI action type (checkbox checked). Flag to a human before implementing signup consent UI — do not add the checkbox without this record-keeping in place.
