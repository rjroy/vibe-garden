---
title: "Commission: Prep plan for lore redesign spec"
date: 2026-04-24
status: dispatched
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Octavia wrote a spec at `.lore/specs/lore-redesign.md` (confirm the path — she may have placed it elsewhere; check her commission result `commission-Octavia-20260424-134303` for the actual location).\n\nBuild an implementation plan for the spec using `/lore-development:prep-plan`. The skill generates, persists, and reviews plans as first-class lore artifacts.\n\n## Context\n\nThe spec covers four concerns:\n1. Directory structure revamp (`build/`, `reference/`, `learned/`) — plugin-wide path migrations\n2. `/retro` scope reduction\n3. `/excavate` → `/distill` rename + reshape\n4. New `/learn` skill\n\nThis is a plugin-wide refactor of `lore-development`. Blast radius: every SKILL.md that writes to `.lore/`, frontmatter schema, agent descriptions, `/tend` migration mode.\n\n## Plan requirements\n\n- **Phasing matters.** A 7-skill refactor across path strings, frontmatter schema, and agent descriptions is too much for one commission. Break into right-sized phases (2–3 phases worth of work per future commission). Each phase should fit in a single context window.\n- **Foundation phase fans out.** The directory structure + frontmatter schema is the foundation. Multiple skills get updated against it. Foundation phase needs an implement → review → fix gate before any fan-out.\n- **Coupling between `/retro` strip and `/learn`.** Per the roadmap, stripping `/retro` before `/learn` exists leaves a window with no extraction path. Plan must address — either ship `/learn` alongside or include a pointer note in the stripped `/retro`.\n- **Migration mode for `/tend`.** Existing `.lore/` content needs migration to the new structure. Specify when this lands relative to the skill path updates.\n- **Per-phase test verification.** Plugin skills are user-invocable. Each phase needs a verification step (the skill still loads, paths resolve, the migration runs cleanly on a test fixture).\n- **Delegation guide.** Name the worker for each phase and the reviewer. Foundation phases get Thorne reviews before fan-out.\n\nRead the spec carefully. Read the four brainstorms it references (`.lore/brainstorm/lore-directory-redesign.md`, `.lore/brainstorm/principles-for-capture-skills.md`, `.lore/brainstorm/distill-function.md`, `.lore/brainstorm/learn-dialog.md`) so the plan reflects the *why* behind the spec's directives.\n\nReturn: path to the plan file and a phase-by-phase summary with worker assignments and review gates. Flag any spec gaps you hit while planning."
dependencies:
  - commission-Octavia-20260424-134303
linked_artifacts: []

resource_overrides:
  model: opus

activity_timeline:
  - timestamp: 2026-04-24T22:16:47.673Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-24T22:16:47.675Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
