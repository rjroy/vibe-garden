---
title: "Commission: Write spec for lore directory redesign + capture-skill rework"
date: 2026-04-24
status: completed
tags: [commission]
worker: Octavia
workerDisplayTitle: "Guild Chronicler"
prompt: "Write a spec for the lore-development plugin redesign. The roadmap is `.lore/issues/roadmap-lore-redesign.md`. Read it first, then read the four dependency artifacts it names:\n\n- `.lore/brainstorm/lore-directory-redesign.md` — the three-directory model\n- `.lore/brainstorm/principles-for-capture-skills.md` — binding principles for retro/learn\n- `.lore/brainstorm/distill-function.md` — `/excavate` → `/distill` reshape\n- `.lore/brainstorm/learn-dialog.md` — `/learn` dialog design\n\nAlso consult `.lore/issues/design-learned-structure.md` and `.lore/issues/design-extraction-skill.md` for context (the latter's framing is superseded by the learn-dialog brainstorm, per the roadmap).\n\n## Scope\n\nUse `/lore-development:specify`. Write one spec covering all four concerns below. This is roadmap step 4 plus the direction items for steps 3 and 5. Keep the spec light where the brainstorms have already decided the shape — reference them, don't re-argue them.\n\n**1. Revamped directory structure (the bulk of the spec).**\n- The three-directory model: `build/`, `reference/`, `learned/`. Specify what lives where and why.\n- Path migrations for every existing skill that writes to `.lore/` — `/brainstorm`, `/specify`, `/design`, `/prep-plan`, `/ddp`, `/research`, `/retro`, `/excavate`/`/distill`, `/vision`, `/file-issue`, `/back-propagate`, `/review-ideas`, `/poke-holes`, and any others you find. Enumerate old path → new path for each.\n- Frontmatter schema consolidation: per-directory status values collapse. Define the new schema.\n- `/tend` gains a migration mode for the old → new structure. Specify what it migrates and how.\n- `/lore-researcher` agent description updates (it searches the new paths).\n- Other agent description updates (Celeste references `.lore/vision.md`; vision moves into `reference/`).\n- Any SKILL.md files that hardcode paths need enumeration.\n\n**2. `/retro` scope reduction.**\n- Strip: graduation flow, \"What Went Well / What Could Improve / Lessons Learned\" template, analysis vocabulary.\n- Output: free-form notes with structured frontmatter. Specify the frontmatter.\n- Reference the capture-skills principles brainstorm for the binding rules.\n\n**3. `/excavate` → `/distill` rewrite.**\n- Rename and reshape per the distill-function brainstorm. Two seed modes: `/distill code`, `/distill build`. Shared code-verifying core. Tightened reference shape rule: contains only what the code cannot say.\n- Spec should direct the refactor, not re-derive it. Point to the brainstorm for the reasoning.\n\n**4. `/learn` skill (new).**\n- Per the learn-dialog brainstorm: user-invoked dialog, two-path opening (specific material or felt pattern), question-first progression, \"nothing\" is a valid answer, terse write discipline, active dedup against existing `learned/` entries.\n- Spec should direct the build. Point to the brainstorm for the reasoning.\n\n## Constraints\n\n- Remember: specs for AI-guided skills should be lighter than application specs. Don't over-constrain the prompt; leave room for model judgment.\n- Coupled ordering of steps 2 and 3 from the roadmap (retro strip vs. learn existing) needs to be reflected — either `/learn` ships alongside the `/retro` strip, or `/retro` strip includes a pointer note.\n- Out-of-scope items from the roadmap stay out of scope: reference-as-a-skill, graduation to higher scopes, per-diagram splitting.\n- Write the spec to `.lore/specs/lore-redesign.md` (or wherever `/specify` normally lands it — follow the skill).\n\nReturn: path to the spec file and a one-paragraph summary of what it covers. Flag any internal inconsistencies between the brainstorms that you had to resolve."
dependencies: []
linked_artifacts:
  - .lore/specs/lore-redesign.md

activity_timeline:
  - timestamp: 2026-04-24T20:43:03.089Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-24T20:43:03.091Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
  - timestamp: 2026-04-24T20:43:03.110Z
    event: status_in_progress
    reason: "Execution started"
    from: "dispatched"
    to: "in_progress"
  - timestamp: 2026-04-24T20:43:39.981Z
    event: progress_report
    reason: "Read roadmap and all four brainstorm dependencies. Now surveying existing lore-development skill structure to enumerate path migrations."
  - timestamp: 2026-04-24T20:45:45.111Z
    event: progress_report
    reason: "Surveyed all skill SKILL.md files, frontmatter schema, agent definitions. Drafting spec now."
  - timestamp: 2026-04-24T20:48:49.520Z
    event: result_submitted
    reason: "Spec written to `.lore/specs/lore-redesign.md`. Covers all four concerns in one light-touch refactor spec with 48 requirements (prefix REDESIGN):\n\n(1) **Directory structure** — the three-directory model (`build/`, `reference/`, `learned/`), per-skill path migration table enumerating 19 skills + 1 hook, diagram splitting by purpose, vision's move into `reference/`, and SKILL.md path audits.\n\n(2) **Frontmatter consolidation** — common fields unchanged; status values collapse into three sets keyed to directory (build keeps per-type lifecycle nuance; reference = `current`/`outdated`/`archived`; learned = `active`/`superseded` as a minimum set, deferring richer lifecycle to `design-learned-structure.md`).\n\n(3) **`/retro` reshape** — strips template, graduation flow, and analysis vocabulary per the capture-skill principles; free-form notes with structured frontmatter; pointer-note fallback if `/retro` ships before `/learn`.\n\n(4) **`/excavate` → `/distill` rewrite** — rename, two seed modes, code-verifying core, reference-shape rule, null-output-valid, `/tend` distill-before-archive prompt on implemented specs.\n\n(5) **`/learn` new skill** — user-invoked dialog, two-path opening, question-first, nothing-valid, asymmetric shape at artifact level, active dedup, terse write discipline, no auto-invoke.\n\n(6) **`/tend migrate`** — new dry-run mode that detects legacy structure, moves files, rewrites internal links, is idempotent, respects guild-hall paths.\n\n(7) **Agent description updates** — `lore-researcher` (plus search priority inversion — `learned/` first), `spec-reviewer`, `design-reviewer`, `plan-reviewer`, `fresh-lore`, and Celeste's vision-path reference (flagged as a cross-plugin coordination point).\n\nAI Validation adds custom checks: path-string audit grep, anti-template check on `/retro`, anti-assertion check on `/learn`, and an end-to-end `/tend migrate` fixture test.\n\n**Brainstorm inconsistencies resolved in the spec:**\n- `/learn` as auto-extractor (directory-redesign framing) vs user-invoked dialog (learn-dialog framing). Resolved to dialog; `design-extraction-skill.md`'s auto-scan framing is formally retired.\n- \"No named promotion verb\" open question from directory-redesign. Resolved by distill-function's rename + second seed mode; explicitly closed.\n\nOrdering constraint is captured: `/learn` must ship at-or-before `/retro` strip, or `/retro` carries a pointer note.\n\nOut-of-scope items preserved from the roadmap: reference-as-a-skill, higher-scope graduation, per-diagram splits, full `learned/` internal structure."
  - timestamp: 2026-04-24T20:48:58.891Z
    event: status_completed
    reason: "Execution completed"
    from: "in_progress"
    to: "completed"
current_progress: "Surveyed all skill SKILL.md files, frontmatter schema, agent definitions. Drafting spec now."
projectName: vibe-garden
---
Spec written to `.lore/specs/lore-redesign.md`. Covers all four concerns in one light-touch refactor spec with 48 requirements (prefix REDESIGN):

(1) **Directory structure** — the three-directory model (`build/`, `reference/`, `learned/`), per-skill path migration table enumerating 19 skills + 1 hook, diagram splitting by purpose, vision's move into `reference/`, and SKILL.md path audits.

(2) **Frontmatter consolidation** — common fields unchanged; status values collapse into three sets keyed to directory (build keeps per-type lifecycle nuance; reference = `current`/`outdated`/`archived`; learned = `active`/`superseded` as a minimum set, deferring richer lifecycle to `design-learned-structure.md`).

(3) **`/retro` reshape** — strips template, graduation flow, and analysis vocabulary per the capture-skill principles; free-form notes with structured frontmatter; pointer-note fallback if `/retro` ships before `/learn`.

(4) **`/excavate` → `/distill` rewrite** — rename, two seed modes, code-verifying core, reference-shape rule, null-output-valid, `/tend` distill-before-archive prompt on implemented specs.

(5) **`/learn` new skill** — user-invoked dialog, two-path opening, question-first, nothing-valid, asymmetric shape at artifact level, active dedup, terse write discipline, no auto-invoke.

(6) **`/tend migrate`** — new dry-run mode that detects legacy structure, moves files, rewrites internal links, is idempotent, respects guild-hall paths.

(7) **Agent description updates** — `lore-researcher` (plus search priority inversion — `learned/` first), `spec-reviewer`, `design-reviewer`, `plan-reviewer`, `fresh-lore`, and Celeste's vision-path reference (flagged as a cross-plugin coordination point).

AI Validation adds custom checks: path-string audit grep, anti-template check on `/retro`, anti-assertion check on `/learn`, and an end-to-end `/tend migrate` fixture test.

**Brainstorm inconsistencies resolved in the spec:**
- `/learn` as auto-extractor (directory-redesign framing) vs user-invoked dialog (learn-dialog framing). Resolved to dialog; `design-extraction-skill.md`'s auto-scan framing is formally retired.
- "No named promotion verb" open question from directory-redesign. Resolved by distill-function's rename + second seed mode; explicitly closed.

Ordering constraint is captured: `/learn` must ship at-or-before `/retro` strip, or `/retro` carries a pointer note.

Out-of-scope items preserved from the roadmap: reference-as-a-skill, higher-scope graduation, per-diagram splits, full `learned/` internal structure.
