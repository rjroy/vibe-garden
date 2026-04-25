---
title: "Commission: Lore-redesign Phase 6: plugin docs + full audit (NO guild-hall)"
date: 2026-04-25
status: dispatched
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 6 of the lore-development three-directory redesign — plugin documentation, marketplace touch-ups, and a full path-string audit. **CRITICAL SCOPE LIMIT**: do NOT touch any file outside `lore-development/` and the repo-root `.claude-plugin/marketplace.json`. Specifically, **do NOT edit Celeste or any other guild-hall file** — REQ-REDESIGN-45 is explicitly delegated to a separate guild-hall-scoped commission and is out of scope for this work.\n\nPlan: `.lore/plans/lore-redesign.md` — Phase 6 section (~lines 312–346). Read in full first.\nSpec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-46 (SKILL.md path audit final pass), REQ-REDESIGN-48 (plugin README/SKILL.md). REQ-REDESIGN-45 is OUT OF SCOPE.\n\nFoundation through Phase 5 are landed (Phase 5 fix at commission-Dalton-20260424-222413).\n\nFiles to touch (lore-development scope only):\n- `lore-development/README.md` — rewrite the `.lore/` structure section to describe the three-directory model: `build/` (work scaffolding, session-bound), `reference/` (solidified, system-oriented), `learned/` (mistakes-only, worker-oriented). Update skill list to show `/distill` (not `/excavate`) and add `/learn`. Add a short \"Migrating from the old layout\" pointer to `/tend migrate`.\n- `lore-development/.claude-plugin/` — if a top-level SKILL.md or manifest there describes directory structure, update it to match.\n- `.claude-plugin/marketplace.json` (repo root) — if it references skill names by `excavate`, update to `distill`. If it doesn't reference skills, leave it.\n\nFull spec AI Validation custom checks (REQ-REDESIGN-46):\n1. **Path-string audit**: grep `lore-development/` for every legacy `.lore/` path:\n   - `\\.lore/(brainstorm|specs|design|plans|tasks|notes|research|retros|issues|ideas|validation|stubs|excavations|diagrams)/`\n   - `\\.lore/vision\\.md`\n   Any hit outside (a) intentional migration documentation, (b) the migrate script's detection logic, or (c) `/tend migrate`'s reference docs is a miss. Fix every miss in place. Report all hits and how each was classified.\n2. **Anti-template re-check** on `/retro` SKILL.md (Phase 5 already verified; re-confirm).\n3. **Anti-assertion re-check** on `/learn` SKILL.md (Phase 5 already verified; re-confirm).\n4. **End-to-end `/tend migrate` fixture test**: re-run the fixture-tree pytest. Confirm target layout, link resolution, and idempotency on re-run. Report pass/fail.\n\n**Real-world dry-run** (validation step, not a \"do it\" step):\n- Run `python lore-development/scripts/tend_migrate.py` against this repo's own `.lore/` in dry-run mode. **Do NOT apply.** Inspect the move plan and link rewrites. Report the dry-run output in your result body. The user will decide whether to run apply later as a separate dogfooding step.\n\nCross-plugin coordination:\n- REQ-REDESIGN-45 (Celeste vision path): **delegated, do NOT touch**. Note in your result body that this requirement is out of scope for the current commission and remains pending for a separate guild-hall-scoped commission.\n\nVerification checklist (spec lines 195–203 / Success Criteria):\n- All grep audits report clean (or only documented exceptions).\n- `pytest lore-development/scripts/tests/` — full test suite passes.\n- `lore-development/README.md` shows the three-directory model and lists `/distill` + `/learn`.\n- All requirements except REQ-REDESIGN-45 are addressable from within `lore-development/` (or marketplace.json) and have been addressed.\n\nReport in your result body: every file touched, full grep audit output (each hit classified), pytest output, dry-run output against this repo's `.lore/`, and an explicit note that REQ-REDESIGN-45 (Celeste) is delegated to a guild-hall commission and not addressed here. Two reviewers will follow: Thorne for the audit, Octavia for README clarity."
dependencies:
  - commission-Dalton-20260424-222413
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-25T05:24:41.866Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T05:24:41.868Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
  - timestamp: 2026-04-25T05:34:56.467Z
    event: status_pending
    reason: "Dependencies satisfied"
    from: "blocked"
    to: "pending"
  - timestamp: 2026-04-25T05:34:56.470Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
