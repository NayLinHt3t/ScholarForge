# User Interview Plan — ScholarForge

## Purpose

Before investing further engineering effort, validate whether the three hypothesized pain points and the target-user profile in [proposal.md](proposal.md) are real to actual students, and get honest reactions to the chosen direction — idea-based search + project library + a read-only idea/outline scaffold (deliberately *not* a full AI-written paper) — while it's still cheap to adjust.

## Hypotheses to validate

- **H1 (discovery gap)**: Students frequently want to search literature by an idea/concept, not a title, and keyword-only search fails them at exactly that stage.
- **H2 (fragmentation + citation tedium)**: Sources end up scattered across bookmarks/notes/tools, and manually formatting citations is a genuine time cost, not a minor annoyance.
- **H3 (blank-page + AI trust)**: Students hit a real barrier going from gathered sources to a first outline, and are wary of subscriptions, third-party logins, or sending research ideas to an external cloud AI provider.
- **H4 (direction check)**: A locally-run, "scaffold only, not ghostwriter" tool is something students would actually adopt — as opposed to secretly wanting a tool that writes the whole paper for them, which would mean the chosen direction is wrong.

## Target interviewees & recruitment

- **Screening**: currently enrolled undergrad/grad students actively working on, or recently finished, a thesis, capstone, research paper, or major course project requiring citations.
- **Sample size**: 8–12 interviews — enough to reach saturation on qualitative pain-point validation.
- **Mix to sample**: early-stage (has an idea, no sources yet) vs. late-stage (already drafting) students; and across disciplines (STEM/CS vs. humanities/social science) since citation-style needs differ — this also tests whether defaulting to IEEE actually fits most interviewees or only some.
- **Recruit via** (same channels identified in the target-user reach plan): thesis/capstone course instructors, library/writing-center referrals, department mailing lists, student research clubs, peer/study-group referral.

## Format & logistics

- 30-minute, one-on-one, semi-structured interviews, remote or in person.
- Ask permission to record audio for note-taking; anonymize in the write-up.
- Two rounds if time allows:
  1. **Round 1** (5–6 interviews) — pain-point and behavior validation only, no concept shown yet, to avoid leading answers.
  2. **Round 2** (remaining interviewees) — walk through the existing clickable prototype (`.docs/02-design/prototype.html`) and gauge reaction to the actual concept.

## Interview guide

### 1. Warm-up / context (2 min)
- What are you currently working on that needs research sources or citations?
- What stage are you at — just have an idea, actively searching, or already writing?

### 2. Current behavior & pain points (10 min)
- Walk me through the last time you needed to find a research paper. Where did you start, and what did you search for?
- Have you ever known roughly what you wanted to research but not the right keywords or a specific title? What did you do then?
- Where do you keep track of papers/sources you've found?
- How do you currently format citations, and how much time or frustration does that take?
- Tell me about the last time you sat down to start writing a proposal or paper section from scratch. What was that like?
- Have you used AI tools (e.g. ChatGPT) for research or writing help? What did you use them for, and what made you hesitate, if anything — cost, privacy, accuracy?

### 3. Reaction to the concept (10 min, Round 2 only — show the prototype)
- Describe/demonstrate the core workflow: *describe your idea in plain English → get back conceptually relevant papers → save into a project → generate a bullet-point outline scaffold with citations, which you then write from yourself.*
- What's your first reaction?
- Would this fit into how you actually do research, or would it change your workflow a lot?
- The tool deliberately does **not** write the finished paper for you — only ideas, structure, and citations. How do you feel about that boundary?
- Would it matter to you that everything runs on your own machine — no account elsewhere, no cloud AI? Why or why not?
- Does IEEE-style output by default fit your field, or would you need a different default?

### 4. Adoption & willingness (5 min)
- Would you actually use this for your current work? What would stop you?
- What would make this a "must-have" instead of a "nice-to-have" for you?
- Who else do you know who'd want this, and how would you describe it to them?

### 5. Closing (3 min)
- Anything we didn't ask about that's relevant to how you research or write?
- Can we follow up once there's a working (non-prototype) version?

## Analysis & success criteria for this round

- **H1–H3** considered validated if ≥70% of interviewees independently describe the pain point unprompted, or strongly agree once it's described.
- **H4** considered validated if most interviewees react positively to the "scaffold, not ghostwriter" boundary and the local-only architecture, without consistently pushing for a different core direction.
- Any consistent disconfirming pattern (e.g., "I'd only use this if it wrote the whole paper for me") is treated as a pivot signal, not noise — flag it before further build investment.
- Findings feed back into [proposal.md](proposal.md)'s Problem Statement/Target Users and the [backlog](../01-requirements/backlog.md)'s priorities — this plan is meant to be revisited, not treated as one-and-done.

## Timeline

| Step | Duration |
|---|---|
| Recruit interviewees | 1 week |
| Round 1 interviews (pain-point validation) | 1 week |
| Synthesize findings, adjust concept if needed | Few days |
| Round 2 interviews (prototype walkthrough) | 1 week |
| Write up findings, update docs | Few days |
