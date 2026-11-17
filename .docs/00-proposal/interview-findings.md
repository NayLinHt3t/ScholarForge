# Interview Findings — ScholarForge (Real Users)

**Method**: structured survey (Google Form), not the originally-planned 30-min live interview — see [interview-plan.md](interview-plan.md) for the original protocol and [interview-script.md](interview-script.md) for question design; this survey implements the same question set in self-serve form. **n = 12** respondents, collected 2026-10-06 to 2026-10-07. Raw data: [interview-survey-raw.csv](interview-survey-raw.csv) (contains respondent email addresses — handle accordingly; this file is the anonymized write-up).

**Disclosure — 2 of 12 respondents are team members**: U02 (email `6631503067@...`) = Min Htet Kaung Pyae (Tech Lead), U03 (email `6631503066@...`) = Lin Myat Oo (AI Lead/Designer). Their responses are kept in the dataset below but flagged `[TEAM]` — treat the **n=10 external** figure as the real validation signal; the n=12 figures include team self-responses and may skew slightly positive.

## Respondent codes (anonymized)

| Code | Level | Field | Project stage | Note |
|---|---|---|---|---|
| U01 | Undergrad | Software Engineering | Revising/editing | |
| U02 | Undergrad | Software Engineering | Revising/editing | **[TEAM — Tech Lead]** |
| U03 | Undergrad | Software Engineering | Searching for sources | **[TEAM — AI Lead/Designer]** |
| U04 | Master's | Computer Engineering | Recently completed | |
| U05 | Undergrad | Engineering | Organizing/analyzing sources | |
| U06 | Undergrad | Computer Engineering | Searching for sources | |
| U07 | Undergrad | Computer Engineering | Recently completed | |
| U08 | Undergrad | International development | Currently writing | |
| U09 | Undergrad | DTBI | Recently completed | |
| U10 | Undergrad | BA | Searching for sources | |
| U11 | Master's | Computer Science | Recently completed | |
| U12 | Other | Software Engineering | Recently completed | |

## Quantitative summary (1=low, 5=high; n=12)

| Metric | Mean | Range | Read |
|---|---|---|---|
| Discovery difficulty (conceptually-relevant papers are hard to find) | 3.50 | 2–4 | Confirms **H1** |
| Citation-formatting frustration | 3.08 | 1–5 | Confirms **H2**, but milder than discovery pain |
| Blank-page difficulty (starting to write) | 3.67 | 2–5 | Confirms **H3** |
| Importance that research data/ideas stay local, not sent to cloud AI | 3.67 | 3–5 | Partial support for privacy angle — real, but not universal (several rated 3/"depends") |
| Concept usefulness (reaction to the actual pitch) | 3.67 | 2–5 | Supports **H4**, one clear detractor (U10, scored 2) |

**Idea-before-keyword gap (H1 direct check)**: "Have you known what you wanted to research but not the right keyword/title?" — 8/12 "Sometimes", 3/12 "Frequently", 1/12 "Rarely". **11 of 12 respondents have hit this at least sometimes.**

**Would actually use the tool**: 3 "Definitely", 5 "Probably", 4 "Maybe", 0 "No" — nobody ruled it out, but nobody outside the "Definitely" group is a lock either.

**Reaction to "scaffold only, not full ghostwriter" (H4 direction check)**: split — 5/12 prefer/strongly prefer the limited-AI approach, 4/12 neutral, **2/12 explicitly want the tool to write most of the paper** (U10, U12), 1/12 wants "some limited assistance" (U07). This is a real signal that the "not a ghostwriter" positioning will not satisfy every user — worth stating as a known trade-off, not hiding it.

## Pain points — representative quotes

**H1 — discovery gap, keyword mismatch**
> "The biggest challenge is paywalls blocking full text access, along with struggling to find exact keyword combinations when I know a general concept but don't know the specific technical jargon used by researchers." — U02 [TEAM]

> "Accessibility because some requires student account to access the source link" — U04

**H2 — fragmentation + citation tedium**
> "The most frustrating part is dealing with inconsistent citation formatting across different style guides (APA, IEEE, MLA) and losing track of where a specific paper or quote was saved across scattered folders and bookmarks." — U02 [TEAM]

> "Citation tools often misformat references when pasted into Google Docs or Word, forcing me to manually adjust spacing, indentations, and special characters." — U12

> "The biggest friction right now is having to juggle multiple separate tools—Google Scholar/Semantic Scholar for discovery, Zotero/Word for citations, and AI for brainstorming." — U11

**H3 — blank-page problem**
> "I don't know how to structure the paper; I don't know how to connect the sources; I am worried about whether my argument is strong enough; I struggle to turn research into an outline." — U02 [TEAM]

> "I usually ask AI tools like ChatGPT or Claude to generate a basic outline first... or talk through my ideas with a peer to figure out where to begin." — U02 [TEAM]

**Privacy / trust (mixed — not universal)**
> "I want to keep my unpublished research ideas confidential and avoid potential copyright or privacy issues that come with uploading personal project drafts or sensitive data to third-party cloud servers." — U02 [TEAM]

> "No one will use my research paper anyway if it leak so it doesn't matter." — U04 (low privacy concern — counter-evidence)

> "I don't mind sending general prompts, outlines, or publicly available text to cloud AI, but I prefer keeping novel research ideas and unpublished proprietary data local." — U11 (nuanced — selective, not absolute)

**Direction check — scaffold vs. ghostwriter (H4)**
> "It maintains academic integrity and ensures I am doing the actual thinking and synthesis myself, while still saving time on initial structure and source mapping." — U02 [TEAM], in favor of scaffold-only

> "I would prefer the tool to write most of the paper." — U10, U12 — against scaffold-only positioning

> "Guaranteed accuracy with zero hallucinated citations, where every point in the outline is strictly linked to direct quotes, specific page numbers, and verified DOIs" would be the must-have bar. — U11

## What this validates vs. what it doesn't

- **Validated**: the idea-before-keyword discovery gap (11/12 hit it), citation tedium is real but milder than expected, blank-page problem is the single highest-rated pain (mean 3.67).
- **Not fully validated**: the "no cloud AI, ever" framing — importance-of-local rating is middling (3.67/5) and two respondents explicitly don't mind cloud AI for non-sensitive content. The app's `AI_PROVIDER=ollama|groq` configurability (see root README) already hedges this correctly rather than forcing pure-local.
- **Open risk, not resolved by this data**: 2/12 respondents want full AI writing, which the product has explicitly scoped out ("Won't-do for v1" in the backlog). This is a known, accepted trade-off — not a gap to fix before Wednesday, but worth being ready to defend in Q&A.

## Limitations

- Survey, not live 30-minute interviews as originally planned — loses follow-up probing depth.
- 2/12 respondents are team members (self-administered, not blind) — kept in the raw count but flagged; treat n=10 as the external signal.
- Sample skews CS/Engineering/MFU-affiliated — see field distribution above; not a broad cross-discipline sample despite the original plan's intent to mix STEM and humanities.
