---
title: "Commission: Lore-redesign Phase 5: /learn (new) + /retro reshape"
date: 2026-04-25
status: completed
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 5 of the lore-development three-directory redesign — coupled delivery of the new `/learn` skill and the `/retro` reshape.\n\nPlan: `.lore/plans/lore-redesign.md` — Phase 5 section (~lines 268–310). Read in full first.\nSpec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-14 through 17 (retro), REQ-REDESIGN-34 through 41 (learn).\nBrainstorms (BINDING):\n- `.lore/brainstorm/principles-for-capture-skills.md` — both skills are capture skills under these principles.\n- `.lore/brainstorm/learn-dialog.md` — `/learn` design source.\n\nFoundation, path fan-out, agent descriptions, `/tend migrate`, and `/distill` are all landed (Phase 4 fix at commission-Dalton-20260424-180627). Build on that.\n\n**Coupling**: ship both together. If delivery must split, `/learn` ships first, `/retro` reshape second. Reason: shipping `/retro`'s strip without `/learn` leaves users with no extraction path. Don't split unless truly forced.\n\nFiles to touch:\n- `lore-development/skills/learn/` (new directory)\n- `lore-development/skills/learn/SKILL.md` (new)\n- `lore-development/skills/retro/SKILL.md` (reshape — strip template, strip graduation, strip analysis vocabulary)\n- `lore-development/README.md` (add `/learn` entry)\n\n`/learn` SKILL.md (REQ-REDESIGN-34 through 41):\n- Frontmatter declares user-invoked only. Triggers: \"learn\", \"record a lesson\", \"/learn\".\n- Opening two-path question (REQ-REDESIGN-35): specific material or felt pattern.\n- Question-first progression (REQ-REDESIGN-36). AI never asserts; \"nothing\" is valid at any step and closes without writing a file.\n- Asymmetric shape gate (REQ-REDESIGN-37): enforced at artifact level, not as a pre-filter. \"Don't do X because Y\" or \"If you find yourself doing X, stop — here's why.\" \"Do X because it worked\" is malformed.\n- Active dedup before writing (REQ-REDESIGN-38): grep `.lore/learned/` for related entries on articulated keywords; surface matches; user decides update vs new entry.\n- Write discipline (REQ-REDESIGN-39): terse default. No length budget. Mixed content allowed. No restating. Draft is for trimming, not just approval.\n- On-request fetch (REQ-REDESIGN-40): when user names material (\"recent Thorne reviews\"), delegate to lore-researcher patterns (file path, tag query, module query). Skill does not pre-scan.\n- Default file layout (REQ-REDESIGN-41): one file per entry, kebab-case filename derived from articulated mistake, flat under `.lore/learned/`.\n- Frontmatter per REQ-REDESIGN-13: common fields only. Status `active` or `superseded`. No section scaffold in body.\n- Do NOT pre-create `.lore/learned/` (REQ-REDESIGN-4 — it's materialized by first `/learn` write).\n\n`/retro` reshape (REQ-REDESIGN-14 through 17):\n- Remove the \"What Went Well / What Could Improve / Lessons Learned\" template section in full (REQ-REDESIGN-14).\n- Remove the graduation flow (Invalid/Valid/Critical/Universal classification, graduation to project CLAUDE.md or `~/.claude/rules/lessons-learned.md`) — REQ-REDESIGN-15.\n- Rewrite the prompt to direct capture toward describing what happened, not interpreting. Forbid analysis vocabulary (`lesson`, `insight`, `we learned`, `takeaway`) in output (REQ-REDESIGN-16).\n- Output is free-form notes with structured frontmatter. Frontmatter: common fields only. Status `open` or `archived` (REQ-REDESIGN-9).\n- No pointer-note fallback needed since `/learn` ships in the same phase.\n\nVerification (REDESIGN AI Validation custom checks):\n- **Anti-template check on `/retro`**: post-rewrite SKILL.md must not contain \"What Went Well\", \"What Could Improve\", \"Lessons Learned\" as section headings, or prescriptive use of \"graduate\". Forbidden vocabulary list (`lesson`, `insight`, `we learned`, `takeaway`) appears only as \"avoid these\" instruction, never as section heading.\n- **Anti-assertion check on `/learn`**: post-build SKILL.md prompt must not contain \"propose candidate lessons\", \"identify lessons from\", or \"extract mistakes from notes\". Must contain user-invoked framing and nothing-is-valid framing.\n- Manual triggers:\n  - `/retro` on a dummy session → produces a file with common frontmatter and free-form body. No \"What Went Well\" section.\n  - `/learn` → asks two-path opening. User responds \"nothing actually\" → session closes without writing a file.\n  - `/learn` → user names a mistake → skill runs dedup grep against `.lore/learned/` → writes one file with kebab-case name, terse body.\n\nReport in your result body: files touched, anti-template / anti-assertion grep output, summary of how the rewrite honored each capture-skill principle. Two reviewers will follow: structural skill-review and brainstorm-fidelity."
dependencies:
  - commission-Dalton-20260424-180627
linked_artifacts:
  - lore-development/skills/learn/SKILL.md

  - lore-development/skills/retro/SKILL.md
  - lore-development/README.md
  - lore-development/skills/retro/SKILL.md
  - lore-development/README.md
activity_timeline:
  - timestamp: 2026-04-25T05:23:41.785Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T05:23:41.788Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
  - timestamp: 2026-04-25T05:23:41.809Z
    event: status_in_progress
    reason: "Execution started"
    from: "dispatched"
    to: "in_progress"
  - timestamp: 2026-04-25T05:24:30.303Z
    event: progress_report
    reason: "Read plan/spec/brainstorms. Starting Phase 5: writing /learn SKILL.md, then reshaping /retro, then README update."
  - timestamp: 2026-04-25T05:29:09.383Z
    event: result_submitted
    reason: "## Phase 5 — `/learn` (new) + `/retro` reshape (coupled)\n\nBoth skills shipped in this commission. No split needed.\n\n### Files touched\n\n- `lore-development/skills/learn/SKILL.md` — new file, full prompt for the user-invoked `/learn` dialog.\n- `lore-development/skills/retro/SKILL.md` — reshape; template, graduation flow, and analysis vocabulary stripped.\n- `lore-development/README.md` — added `/learn` entry to the skill table; updated `/retro` row to reflect the reshape.\n\n(`.lore/learned/` is intentionally not pre-created per REQ-REDESIGN-4 — it's materialized by the first `/learn` write.)\n\n### Anti-template grep on `/retro` SKILL.md\n\nSection headings (`^#`):\n\n```\n7:# Retro\n11:## When to Use\n19:## Stance\n30:## Process\n41:## Output\n45:### Frontmatter\n67:### Body Discipline\n84:## Recording vs Recording-and-Acting\n94:## Frontmatter Tips\n101:## Specialized Agents\n105:## Verification Pass\n```\n\nNo \"What Went Well\", \"What Could Improve\", or \"Lessons Learned\" section headings. Those strings appear only inline at line 110 inside the verification pass, where the prompt instructs the AI to confirm those headings do **not** appear in retro output — the legitimate \"avoid these\" framing.\n\n`graduate` grep: zero matches. Graduation flow removed in full.\n\nForbidden vocabulary (`lesson`, `insight`, `we learned`, `takeaway`) appears only in the Stance section as the explicit \"avoid these in body\" instruction, and once each in Verification Pass and Frontmatter Tips as the same gate. Never as a section heading.\n\nStatus set in frontmatter examples: `open` or `archived` only (REQ-REDESIGN-9).\n\n### Anti-assertion grep on `/learn` SKILL.md\n\nForbidden phrase grep — `propose candidate lessons|identify lessons from|extract mistakes from notes`: **no matches**.\n\nRequired framings present:\n- `User-invoked` / `user-invoked`: line 3 (description), line 13 (Invocation section). Description states the skill is never auto-triggered.\n- \"Nothing\"-is-valid framing: line 28 (Stance), line 43 (Opening), line 58 (Question-First Progression), and the third dialog example \"Nothing-to-record path\".\n\nTwo-path opening question: Stance + dedicated \"Opening: Two-Path Question\" section ask the user \"specific material in front of you, or describing a felt pattern?\"\n\nAsymmetric shape gate: enforced at the artifact level in the \"Asymmetric Shape Gate\" section. Valid: \"Don't do X because Y\" / \"If you find yourself doing X, stop\". Malformed: \"Do X because it worked.\" Gate is applied at draft-review time, not as a pre-filter on input.\n\nActive dedup before writing: described in the \"Active Dedup Before Writing\" section. Grep `.lore/learned/` on keywords pulled from the user's articulation, surface every match with file path and excerpt, user decides update / supersede / new / cancel. Skip step described for the case where `.lore/learned/` doesn't yet exist.\n\nOn-request fetch: \"On-Request Fetch\" section. Three patterns — file path, tag/module query (delegated to `lore-researcher`), recent-N. Skill does not pre-scan.\n\nDefault file layout: one file per entry, kebab-case filename, flat under `.lore/learned/`. Section flags this default as revisable when `design-learned-structure.md` resolves.\n\nFrontmatter: common fields only, `status: active` (default) or `superseded` (when superseded by a later entry, paired with a `related:` link). No body section scaffold.\n\n### How the rewrite honored each capture-skill principle\n\n**Principle 1 — templates that demand N things cause N hallucinations.** `/retro` no longer has named sections with implied counts. `/learn` has no length budget, no \"aim for N sentences\" prompt, no body section scaffold. Both skills explicitly instruct: length follows what actually happened.\n\n**Principle 2 — learn from mistakes only, never from success.** `/learn`'s asymmetric shape gate at the artifact level rejects \"do X because it worked\" entries by construction. `/retro` removed the \"What Went Well\" framing in full, with the Stance section calling out why: success-extraction trains the model to invent best-practice tips that don't survive the next project.\n\n**Principle 3 — separate observation from interpretation.** `/retro` is now witness-only: describes what happened, no interpretation, no analysis vocabulary, no graduation. `/learn` is the analyst step, user-invoked, decoupled from the moment data is captured. The retro's \"Recording vs Recording-and-Acting\" section explicitly directs the user to invoke `/learn` separately when they notice a rule worth recording — observation and interpretation across two skills, two timings, two files.\n\n### Citations to source brainstorms\n\nBoth SKILL.md files cite `.lore/brainstorm/principles-for-capture-skills.md` and `.lore/brainstorm/learn-dialog.md` (the `/learn` SKILL.md cites both). The legacy `.lore/brainstorm/` path is used for these citations to match the convention established in the Phase-4-landed `distill/SKILL.md`. After `/tend migrate` runs on this repo's own `.lore/` in Phase 6, those citations will need to follow the migrated paths — same fix-up as the existing distill citations.\n\n### Reviewers next\n\n- `plugin-dev:skill-reviewer` on `learn/SKILL.md` and `retro/SKILL.md` (structural review).\n- `fresh-lore` cross-checks both SKILL.md files against `.lore/brainstorm/principles-for-capture-skills.md` and `.lore/brainstorm/learn-dialog.md` (brainstorm fidelity)."
  - timestamp: 2026-04-25T05:29:16.588Z
    event: status_completed
    reason: "Execution completed"
    from: "in_progress"
    to: "completed"
current_progress: "Read plan/spec/brainstorms. Starting Phase 5: writing /learn SKILL.md, then reshaping /retro, then README update."
projectName: vibe-garden
---
## Phase 5 — `/learn` (new) + `/retro` reshape (coupled)

Both skills shipped in this commission. No split needed.

### Files touched

- `lore-development/skills/learn/SKILL.md` — new file, full prompt for the user-invoked `/learn` dialog.
- `lore-development/skills/retro/SKILL.md` — reshape; template, graduation flow, and analysis vocabulary stripped.
- `lore-development/README.md` — added `/learn` entry to the skill table; updated `/retro` row to reflect the reshape.

(`.lore/learned/` is intentionally not pre-created per REQ-REDESIGN-4 — it's materialized by the first `/learn` write.)

### Anti-template grep on `/retro` SKILL.md

Section headings (`^#`):

```
7:# Retro
11:## When to Use
19:## Stance
30:## Process
41:## Output
45:### Frontmatter
67:### Body Discipline
84:## Recording vs Recording-and-Acting
94:## Frontmatter Tips
101:## Specialized Agents
105:## Verification Pass
```

No "What Went Well", "What Could Improve", or "Lessons Learned" section headings. Those strings appear only inline at line 110 inside the verification pass, where the prompt instructs the AI to confirm those headings do **not** appear in retro output — the legitimate "avoid these" framing.

`graduate` grep: zero matches. Graduation flow removed in full.

Forbidden vocabulary (`lesson`, `insight`, `we learned`, `takeaway`) appears only in the Stance section as the explicit "avoid these in body" instruction, and once each in Verification Pass and Frontmatter Tips as the same gate. Never as a section heading.

Status set in frontmatter examples: `open` or `archived` only (REQ-REDESIGN-9).

### Anti-assertion grep on `/learn` SKILL.md

Forbidden phrase grep — `propose candidate lessons|identify lessons from|extract mistakes from notes`: **no matches**.

Required framings present:
- `User-invoked` / `user-invoked`: line 3 (description), line 13 (Invocation section). Description states the skill is never auto-triggered.
- "Nothing"-is-valid framing: line 28 (Stance), line 43 (Opening), line 58 (Question-First Progression), and the third dialog example "Nothing-to-record path".

Two-path opening question: Stance + dedicated "Opening: Two-Path Question" section ask the user "specific material in front of you, or describing a felt pattern?"

Asymmetric shape gate: enforced at the artifact level in the "Asymmetric Shape Gate" section. Valid: "Don't do X because Y" / "If you find yourself doing X, stop". Malformed: "Do X because it worked." Gate is applied at draft-review time, not as a pre-filter on input.

Active dedup before writing: described in the "Active Dedup Before Writing" section. Grep `.lore/learned/` on keywords pulled from the user's articulation, surface every match with file path and excerpt, user decides update / supersede / new / cancel. Skip step described for the case where `.lore/learned/` doesn't yet exist.

On-request fetch: "On-Request Fetch" section. Three patterns — file path, tag/module query (delegated to `lore-researcher`), recent-N. Skill does not pre-scan.

Default file layout: one file per entry, kebab-case filename, flat under `.lore/learned/`. Section flags this default as revisable when `design-learned-structure.md` resolves.

Frontmatter: common fields only, `status: active` (default) or `superseded` (when superseded by a later entry, paired with a `related:` link). No body section scaffold.

### How the rewrite honored each capture-skill principle

**Principle 1 — templates that demand N things cause N hallucinations.** `/retro` no longer has named sections with implied counts. `/learn` has no length budget, no "aim for N sentences" prompt, no body section scaffold. Both skills explicitly instruct: length follows what actually happened.

**Principle 2 — learn from mistakes only, never from success.** `/learn`'s asymmetric shape gate at the artifact level rejects "do X because it worked" entries by construction. `/retro` removed the "What Went Well" framing in full, with the Stance section calling out why: success-extraction trains the model to invent best-practice tips that don't survive the next project.

**Principle 3 — separate observation from interpretation.** `/retro` is now witness-only: describes what happened, no interpretation, no analysis vocabulary, no graduation. `/learn` is the analyst step, user-invoked, decoupled from the moment data is captured. The retro's "Recording vs Recording-and-Acting" section explicitly directs the user to invoke `/learn` separately when they notice a rule worth recording — observation and interpretation across two skills, two timings, two files.

### Citations to source brainstorms

Both SKILL.md files cite `.lore/brainstorm/principles-for-capture-skills.md` and `.lore/brainstorm/learn-dialog.md` (the `/learn` SKILL.md cites both). The legacy `.lore/brainstorm/` path is used for these citations to match the convention established in the Phase-4-landed `distill/SKILL.md`. After `/tend migrate` runs on this repo's own `.lore/` in Phase 6, those citations will need to follow the migrated paths — same fix-up as the existing distill citations.

### Reviewers next

- `plugin-dev:skill-reviewer` on `learn/SKILL.md` and `retro/SKILL.md` (structural review).
- `fresh-lore` cross-checks both SKILL.md files against `.lore/brainstorm/principles-for-capture-skills.md` and `.lore/brainstorm/learn-dialog.md` (brainstorm fidelity).
