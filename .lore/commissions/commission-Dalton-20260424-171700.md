---
title: "Commission: Lore-redesign Phase 2: agent description updates"
date: 2026-04-25
status: dispatched
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 2 of the lore-development three-directory redesign.\n\nPlan: `.lore/plans/lore-redesign.md` — Phase 2 section. Read in full first.\nSpec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-42, 43, 44.\n\nFoundation (Phase 0) is landed via commission-Dalton-20260424-164331. Build on the new schema and three-directory model.\n\nScope: prompt updates to lore-development agent descriptions. These are load-bearing prompts — search-priority inversion (REQ-REDESIGN-42) is semantic, not mechanical.\n\nFiles to touch:\n- `lore-development/agents/lore-researcher.md` — rewrite search paths to `.lore/build/{brainstorm,specs,design,plans,notes,research,retros,issues,ideas,tasks,validation,stubs,excavations}/`, `.lore/reference/*`, `.lore/learned/*`. Invert search priority per REQ-REDESIGN-42: `learned/` first (operational imperatives), `reference/` second (solidified knowledge), `build/` third (session material). This reverses the current retro-first bias.\n- `lore-development/agents/spec-reviewer.md` — `.lore/specs/` → `.lore/build/specs/`. Fallback-review-save `.lore/reviews/` → `.lore/build/reviews/`.\n- `lore-development/agents/design-reviewer.md` — `.lore/design/` → `.lore/build/design/`. Same fallback rename pattern.\n- `lore-development/agents/plan-reviewer.md` — `.lore/plans/` → `.lore/build/plans/`. Same fallback rename pattern.\n- `lore-development/agents/fresh-lore.md` — update path examples to the new tree.\n\nDo NOT touch:\n- `lore-development/agents/surface-surveyor.md` — Phase 4 owns this (it references `/excavate` invocation that becomes `/distill`).\n- Celeste agent (outside `lore-development/`) — Phase 6 owns this.\n- Skill files — Phase 1 owns those (running in parallel; do not touch).\n\nVerification:\n1. Grep `lore-development/agents/` for any legacy `.lore/` path — must be zero hits outside intentional migration documentation or surface-surveyor.md (deferred to Phase 4).\n2. Confirm lore-researcher.md's priority order is now learned → reference → build, not the reverse.\n\nReport in your result body: each agent file's diff summary, the grep audit output, and any decisions on edge cases. The next commission is a Thorne review focused on the priority-inversion semantics."
dependencies:
  - commission-Dalton-20260424-164331
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-25T00:17:00.682Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T00:17:00.684Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
