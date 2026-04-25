---
title: "Commission: Lore-redesign Phase 2: review agent description updates"
date: 2026-04-25
status: blocked
tags: [commission]
worker: Thorne
workerDisplayTitle: "Guild Warden"
prompt: "Review Phase 2 of the lore-development three-directory redesign — agent description updates.\n\nPredecessor commission: `commission-Dalton-20260424-171700` (Phase 2 build). Read its result body first.\n\nAuthoritative sources:\n- Plan: `.lore/plans/lore-redesign.md` (Phase 2, ~lines 154–179)\n- Spec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-42, 43, 44\n\nWhat to inspect (semantic + path):\n- `lore-development/agents/lore-researcher.md` — search paths updated to new tree; **search priority is now learned → reference → build, not the reverse**. This is a behavior change, not just a path edit. Verify the prompt actually drives this priority order, not just lists the directories.\n- `lore-development/agents/spec-reviewer.md` — `.lore/specs/` → `.lore/build/specs/`; fallback save path `.lore/reviews/` → `.lore/build/reviews/`.\n- `lore-development/agents/design-reviewer.md` — `.lore/design/` → `.lore/build/design/`; same fallback pattern.\n- `lore-development/agents/plan-reviewer.md` — `.lore/plans/` → `.lore/build/plans/`; same fallback pattern.\n- `lore-development/agents/fresh-lore.md` — path examples updated.\n\nRun independently:\n- Grep `lore-development/agents/` for any legacy `.lore/` path. Acceptable hits: surface-surveyor.md (deferred to Phase 4), Celeste does not live here. Any other legacy hit is a miss.\n\nOut of scope (do not flag):\n- surface-surveyor.md (Phase 4).\n- Celeste (Phase 6, outside lore-development).\n- Skill files (Phase 1, running in parallel).\n\nFindings format: enumerate every issue with severity (blocker / fix-now / nit), file:line, and the fix. Pay particular attention to the priority inversion in lore-researcher.md — if the prompt phrasing doesn't actually invert the search behavior, that's a fix-now.\n\nCapture findings in your commission result body."
dependencies:
  - commission-Dalton-20260424-171700
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-25T00:17:31.021Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T00:17:31.022Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
current_progress: ""
projectName: vibe-garden
---
