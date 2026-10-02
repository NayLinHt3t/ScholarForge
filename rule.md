# ClockChasers — Legal & Compliance Rules for AI Agents

Read this before writing any code that touches user data or user actions.

---

## PDPA (Personal Data Protection Act, B.E. 2562/2019)

**What it is**: Thailand's general data protection law. It governs how any organization collects, uses, or discloses personal data of identifiable individuals — modeled closely on the EU's GDPR.

**What it requires**:
- A valid legal basis for processing — usually **consent**, unless another basis applies (contract necessity, legal obligation, legitimate interest, vital interest, public task)
- **Purpose limitation** — data collected for one stated purpose can't silently be reused for another
- **Data minimisation** — collect only what's needed for the stated purpose
- **Data subject rights** — access, correction, deletion, objection, and data portability must be actually implementable, not just promised in a privacy policy
- **Sensitive data** (health, biometric, genetic, religion, race, sexual orientation/behavior, criminal record, union membership) requires **explicit** consent and stronger safeguards than ordinary personal data
- **Breach notification** — notify the regulator (and affected individuals, if high risk) within the required window once a breach is discovered
- **Retention limits** — don't keep personal data indefinitely; define and enforce a retention/deletion schedule
- **Cross-border transfer** restrictions when personal data leaves Thailand, unless the destination has adequate protection or another approved safeguard is in place

**Rules for the agent**:
- If the system collects any personal data field (name, email, phone, ID number, address, device/IP tied to a person), it must record **what legal basis** applies before storing it — don't add a new data field to a form/model without this being explicit in the code or a comment/ticket.
- If the system stores **sensitive personal data** (health, biometric, religious, sexual orientation, criminal record, etc.), it must require **explicit, separate consent** — never bundle it into a general "I agree to terms" checkbox, and never infer it silently from other data.
- If a user requests deletion or correction of their data, the system must have a real code path that fulfills it across **every** table/store the data landed in (including caches, logs, backups, and any analytics/export pipeline) — not just the primary user record.
- If the system introduces a **new third-party service/API** that receives personal data (analytics, email provider, LLM API, CDN logs), it must be checked against the current purpose/consent scope before wiring it up — don't send personal data to a new external endpoint "just to test."
- If personal data is sent to a server, subprocessor, or storage located **outside Thailand**, the system must confirm a valid transfer mechanism exists before shipping the feature — flag this to a human, don't assume it's fine.
- If the system builds a feature that combines/derives new data about a person from existing data (e.g. profiling, scoring, inferred attributes), treat the output as personal data subject to the same rules as the inputs.
- Default to the most privacy-preserving implementation when a requirement is ambiguous (e.g. shorter retention over longer, opt-in over opt-out, anonymization/pseudonymization over raw storage) and flag the ambiguity rather than silently deciding.

---

## Computer Crime Act (Computer-Related Crime Act, B.E. 2550/2007, as amended 2017) — §26

**What it is**: Thailand's law governing unauthorized computer/network access, data interference, and — for this section specifically — the obligation on **service providers** to retain traffic/log data so that individual users of a system can be identified and traced if needed for law enforcement.

**What it requires**:
- Any organization operating as a "service provider" (which in practice includes most companies running a website, app backend, or network service) must **retain computer traffic logs** for a minimum period (commonly cited as **at least 90 days**, extendable up to 1 year for specific data on request/order from the competent authority)
- Logs must be sufficient to **identify the individual user** who performed an action — not just an anonymous session or IP address in isolation, but something that can be tied back to a real account/identity when combined with other records the provider holds
- Logs must be kept **secure and unaltered** — tamper-evidence matters, since they may be used as evidence

**Rules for the agent**:
- If the system exposes any **network-facing endpoint** (API, web app, auth flow), it must write an access/traffic log entry containing at minimum: timestamp, source IP, the authenticated user/account ID (or "unauthenticated" if not logged in), and the action/endpoint accessed.
- If a log entry records an action, it must be linkable to a **real user identity** where the user is authenticated — don't log only an ephemeral session token without also recording the account it resolves to at that time.
- If the system has any log storage or log rotation, it must **retain logs for at least 90 days** before deletion/rotation eligibility — don't set a shorter default TTL on request logs, auth logs, or audit logs without flagging it.
- If logs are deleted, rotated, or moved to cold storage, the process must preserve integrity (e.g. no in-place edits to historical entries) — treat logs as append-only.
- If the system adds a new service/microservice that handles user requests, it must not be exempted from logging just because it's "internal" — trace requests end-to-end where personal/user-identifying actions occur.

---

## Electronic Transactions Act (B.E. 2544/2001, as amended) — §9, §26, §28

**What it is**: Thailand's law giving legal recognition to electronic records and electronic signatures, and setting rules for when an e-signature is valid, when it's presumed reliable, and what duties a Certification Authority (CA) has.

**What it requires**:
- **§9 — validity test for an electronic signature**: an electronic signature is legally valid if it uses a method that (a) can **identify the signatory**, and (b) indicates the signatory's **intention to approve** the information in the electronic record, and (c) the method is **as reliable as appropriate for the purpose** for which the record was created, given all surrounding circumstances.
- **§26 — presumption of a reliable signature**: a signature is *presumed* reliable (stronger legal standing, shifts burden of proof) if it meets stricter criteria — e.g. the signature creation data is linked **only** to the signatory, was under the **sole control** of the signatory at the time of signing, and any subsequent alteration to the signature or the signed data is **detectable**.
- **§28 — duties of a Certification Authority (CA)**: an entity issuing digital certificates (binding a public key / identity to a signatory) must verify the signatory's identity before issuing a certificate, maintain accurate and accessible records, disclose its practices/policies, and can be held liable for failing these duties.

**Rules for the agent**:
- If the user clicks "I agree"/"I accept" on any contract, consent form, or terms acceptance, the system must record: **who** (authenticated identity), **what** exact document/version they agreed to, **when** (timestamp), and **how** (the UI action taken) — this is the minimum evidence needed to later show §9's identification + intention-to-approve test was met.
- If the system implements an "e-signature" feature (beyond a simple checkbox — e.g. typed name, drawn signature, uploaded signature image, or a cryptographic signature), it must document **which reliability tier** it's aiming for (basic §9 validity vs. the stronger §26 presumption) — don't market or label something as a "secure/legally binding signature" in the UI unless it actually meets the §26 sole-control + tamper-detectable criteria.
- If a signed record can be edited after signing, the system must either **block edits** after signing or **version/re-sign** on any change — an editable-after-the-fact "signed" document undermines both §9 reliability and any §26 claim.
- If the system stores signed records, it must keep them **tamper-evident** (e.g. hash/checksum at signing time, or an audit trail of any change) so reliability can be demonstrated later if disputed.
- If the system integrates a **third-party CA or e-signature provider**, it must confirm that provider's identity-verification and record-keeping practices before relying on their signatures for anything requiring the §26 presumption — don't assume "the vendor is a CA" is proof of §28 compliance without checking.
- If a workflow depends on proving *when* something was signed (e.g. deadlines, statute-of-limitations-sensitive actions), the system must timestamp using a trustworthy clock source and store it immutably alongside the signature record.

---

## How to use this file

- Treat every "Rules for the agent" bullet as a **gate**, not a suggestion — if a change you're implementing matches the "if" clause, the "must" clause is a requirement, not a nice-to-have.
- When a change doesn't clearly match any rule here, don't assume it's exempt — flag the ambiguity to a human rather than deciding silently, especially for anything touching personal data, logs, or signed/consented records.
- This file should be updated whenever the company's data flows, third-party integrations, or signature features change — stale rules are worse than no rules because they create false confidence.
