---
title: "Commission: Write spec for lore directory redesign + capture-skill rework"
date: 2026-04-24
status: dispatched
tags: [commission]
worker: Octavia
workerDisplayTitle: "Guild Chronicler"
prompt: "Write a spec for the lore-development plugin redesign. The roadmap is `.lore/issues/roadmap-lore-redesign.md`. Read it first, then read the four dependency artifacts it names:\n\n- `.lore/brainstorm/lore-directory-redesign.md` — the three-directory model\n- `.lore/brainstorm/principles-for-capture-skills.md` — binding principles for retro/learn\n- `.lore/brainstorm/distill-function.md` — `/excavate` → `/distill` reshape\n- `.lore/brainstorm/learn-dialog.md` — `/learn` dialog design\n\nAlso consult `.lore/issues/design-learned-structure.md` and `.lore/issues/design-extraction-skill.md` for context (the latter's framing is superseded by the learn-dialog brainstorm, per the roadmap).\n\n## Scope\n\nUse `/lore-development:specify`. Write one spec covering all four concerns below. This is roadmap step 4 plus the direction items for steps 3 and 5. Keep the spec light where the brainstorms have already decided the shape — reference them, don't re-argue them.\n\n**1. Revamped directory structure (the bulk of the spec).**\n- The three-directory model: `build/`, `reference/`, `learned/`. Specify what lives where and why.\n- Path migrations for every existing skill that writes to `.lore/` — `/brainstorm`, `/specify`, `/design`, `/prep-plan`, `/ddp`, `/research`, `/retro`, `/excavate`/`/distill`, `/vision`, `/file-issue`, `/back-propagate`, `/review-ideas`, `/poke-holes`, and any others you find. Enumerate old path → new path for each.\n- Frontmatter schema consolidation: per-directory status values collapse. Define the new schema.\n- `/tend` gains a migration mode for the old → new structure. Specify what it migrates and how.\n- `/lore-researcher` agent description updates (it searches the new paths).\n- Other agent description updates (Celeste references `.lore/vision.md`; vision moves into `reference/`).\n- Any SKILL.md files that hardcode paths need enumeration.\n\n**2. `/retro` scope reduction.**\n- Strip: graduation flow, \"What Went Well / What Could Improve / Lessons Learned\" template, analysis vocabulary.\n- Output: free-form notes with structured frontmatter. Specify the frontmatter.\n- Reference the capture-skills principles brainstorm for the binding rules.\n\n**3. `/excavate` → `/distill` rewrite.**\n- Rename and reshape per the distill-function brainstorm. Two seed modes: `/distill code`, `/distill build`. Shared code-verifying core. Tightened reference shape rule: contains only what the code cannot say.\n- Spec should direct the refactor, not re-derive it. Point to the brainstorm for the reasoning.\n\n**4. `/learn` skill (new).**\n- Per the learn-dialog brainstorm: user-invoked dialog, two-path opening (specific material or felt pattern), question-first progression, \"nothing\" is a valid answer, terse write discipline, active dedup against existing `learned/` entries.\n- Spec should direct the build. Point to the brainstorm for the reasoning.\n\n## Constraints\n\n- Remember: specs for AI-guided skills should be lighter than application specs. Don't over-constrain the prompt; leave room for model judgment.\n- Coupled ordering of steps 2 and 3 from the roadmap (retro strip vs. learn existing) needs to be reflected — either `/learn` ships alongside the `/retro` strip, or `/retro` strip includes a pointer note.\n- Out-of-scope items from the roadmap stay out of scope: reference-as-a-skill, graduation to higher scopes, per-diagram splitting.\n- Write the spec to `.lore/specs/lore-redesign.md` (or wherever `/specify` normally lands it — follow the skill).\n\nReturn: path to the spec file and a one-paragraph summary of what it covers. Flag any internal inconsistencies between the brainstorms that you had to resolve."
dependencies: []
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-24T20:43:03.089Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-24T20:43:03.091Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
