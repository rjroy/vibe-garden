---
title: "Commission: Lore-redesign Phase 0: schema foundation build"
date: 2026-04-24
status: dispatched
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 0 of the lore-development three-directory redesign.\n\nPlan: `.lore/plans/lore-redesign.md` — read this in full first.\nSpec: `.lore/specs/lore-redesign.md` — authoritative requirements.\nBrainstorms (binding context): `.lore/brainstorm/lore-directory-redesign.md`, `.lore/brainstorm/principles-for-capture-skills.md`, `.lore/brainstorm/distill-function.md`, `.lore/brainstorm/learn-dialog.md`.\n\nScope of THIS commission: Phase 0 only — schema foundation + directory canon. Addresses REQ-REDESIGN-1, 2, 3 (canon), 8–13 (schema), 47 (tend references).\n\nFiles to touch (per Phase 0 in the plan):\n- `lore-development/shared/frontmatter-schema.md` (rewrite per the three-status-set model)\n- `lore-development/scripts/frontmatter_schema.py` (regenerate per-directory status sets)\n- `lore-development/scripts/tests/test_frontmatter_schema.py` (update SCHEMA_DOCUMENT_TYPES list and any other fixtures)\n- `lore-development/scripts/validate_frontmatter.py` (update if it hardcodes paths beyond frontmatter_schema.py)\n- `lore-development/skills/tend/references/directories.md` (rewrite standard-directory list to new tree; flag legacy top-levels as orphans pointing to /tend migrate)\n- `lore-development/skills/tend/references/status.md` (align with new status sets)\n- `lore-development/skills/tend/references/lore-config.md` (read first; update if old-layout assumptions present)\n- `lore-development/scripts/tests/fixtures/` (reorganize into `fixtures/build/`, `fixtures/reference/`, `fixtures/learned/`)\n\nDo NOT touch in this phase:\n- Any other SKILL.md path strings (Phase 1 owns those).\n- Agent descriptions (Phase 2).\n- `tend/SKILL.md` modes table (Phase 3 adds `migrate`).\n- excavate/distill rename (Phase 4).\n- learn/retro (Phase 5).\n- README or cross-plugin (Phase 6).\n\nStatus sets you must encode (REQ-REDESIGN-9):\n- Build: per-type lifecycle retained — brainstorm `open/parked/resolved/archived`, spec `draft/approved/implemented/superseded/archived`, design same as spec, plan `draft/approved/executed/archived`, task `pending/complete/skipped`, notes `in_progress/complete/archived`, research `active/archived`, retro `open/archived` (note: `complete` is collapsed out — see REQ-REDESIGN-14), issue `open/resolved/wontfix/archived`.\n- Reference: `current` / `outdated` / `archived`.\n- Learned: `active` / `superseded`.\n\nVision: lives at `.lore/reference/vision.md`, statuses are the reference set.\n\nVerification (you must run these and report):\n1. `pytest lore-development/scripts/tests/test_frontmatter_schema.py` passes.\n2. `python lore-development/scripts/validate_frontmatter.py` runs against the new fixture tree and reports clean.\n3. Grep `lore-development/shared/frontmatter-schema.md` for `.lore/` paths — every occurrence uses the new tree (or is explicitly documented as a legacy/migration example).\n\nOpen Question 3 from the plan: verify at phase start whether existing fixtures use old-layout paths and migrate them as part of this phase.\n\nReport in your result body: files touched, test output, any deviations from the plan and the reason. The next commission is a Thorne review of this work, then a fix commission. Phase 1 and 2 do NOT begin until Thorne's review gate closes."
dependencies: []
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-24T23:43:03.511Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-24T23:43:03.515Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
