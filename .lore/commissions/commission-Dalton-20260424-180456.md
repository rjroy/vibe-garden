---
title: "Commission: Lore-redesign Phase 3: /tend migrate mode"
date: 2026-04-25
status: dispatched
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 3 of the lore-development three-directory redesign — `/tend migrate` mode plus non-migrate-mode updates.\n\nPlan: `.lore/plans/lore-redesign.md` — Phase 3 section (~lines 181–227). Read in full first.\nSpec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-18 through 25.\n\nFoundation (Phase 0), path fan-out (Phase 1), and agent descriptions (Phase 2) are landed. Build on the new schema, three-directory model, and updated tend reference files.\n\nScope: a new Python migration script with strong unit-test coverage (90%+ AI Validation default) plus tend/SKILL.md and reference updates to expose the new mode.\n\nFiles to touch:\n- `lore-development/skills/tend/SKILL.md` — add `migrate` row to the Modes table; add invocation line `/tend migrate` to the Invocation section. Note: `migrate` is separate from the sequential `status → tags → filenames → directories` chain. Do NOT touch the distill-before-archive prompt hook — Phase 4 owns that.\n- `lore-development/skills/tend/references/migrate.md` (new) — describe mode invocation, dry-run behavior, detection logic, protected paths, idempotency guarantee.\n- `lore-development/scripts/tend_migrate.py` (new) — the migration script.\n- `lore-development/scripts/tests/test_tend_migrate.py` (new) — unit tests.\n- `lore-development/scripts/tests/fixtures/pre-migration/` (new fixture tree).\n- `lore-development/skills/tend/references/directories.md` — second pass: when legacy top-levels are detected by `directories` mode, emit \"legacy structure detected; run `/tend migrate`\" (REQ-REDESIGN-25).\n\nMigration script requirements (REQ-REDESIGN-19 through 24):\n1. Detect legacy structure: scan for any of the 14 old top-level dirs + `.lore/vision.md`.\n2. Build move plan per migration table from REQ-REDESIGN-6.\n3. Diagrams default to `build/diagrams/` (REQ-REDESIGN-21).\n4. Rewrite `related:` and `source:` frontmatter values.\n5. Rewrite in-body markdown links `[text](.lore/old/path)` to new paths.\n6. Dry-run by default; emit full move + link-rewrite plan. Apply only with explicit flag + user confirmation (REQ-REDESIGN-22).\n7. Idempotent: re-run on already-migrated tree reports zero changes (REQ-REDESIGN-23).\n8. Skip `.lore/commissions/`, `.lore/meetings/`, `.lore/heartbeat.md`, `.lore/lore-agents.md`, and anything in `.lore/lore-config.md`'s `custom_directories` (REQ-REDESIGN-24).\n\nUnit tests (load-bearing — link-rewriting across three contexts is the highest-bug-density area):\n- Fixture tree with every legacy dir + one document each + at least one cross-link per type.\n- Dry-run output matches expected moves.\n- Apply produces target layout.\n- Internal links resolve post-migrate.\n- Idempotency: second apply is a no-op.\n- Protected paths untouched.\n- **Fenced-code-block preservation**: fixture with a fenced bash block referencing an old path. Script leaves block content as-is.\n- **Migration-documentation exception**: fixture with a marker (e.g., frontmatter tag `migration-doc` or front-comment) — body unmodified. Pick a stable convention and document it in `migrate.md`.\n\nVerification (run all and report):\n1. `pytest lore-development/scripts/tests/test_tend_migrate.py` — all cases pass.\n2. Coverage report on `tend_migrate.py` shows 90%+.\n3. Run `python tend_migrate.py` against a copy of this repo's own `.lore/` as a real-world fixture. **Do NOT apply to the working tree** — only inspect dry-run output. Report the dry-run plan in your result body for spot-check.\n4. Run `/tend status`, `/tend tags`, `/tend filenames`, `/tend directories` modes against a post-migration fixture tree — confirm they treat `build/`, `reference/`, `learned/` as standard and flag no false orphans.\n\nOpen Question 6 from the plan: REQ-REDESIGN-4 says `.lore/learned/` is created on first `/learn` invocation. The migrate script must not pre-create `.lore/learned/`. Confirm.\n\nPre-existing `.lore/reference/` (excavate/SKILL.md already uses `artifact_path: .lore/reference`): if `.lore/reference/` already exists in a target tree, don't recreate it; just place vision.md inside.\n\nReport in your result body: files created/modified, pytest output, coverage report, dry-run plan against this repo's `.lore/`, decisions on edge cases. The next commission is a Thorne review (blast radius is high — link rewriting is the most likely bug site)."
dependencies:
  - commission-Dalton-20260424-171739
  - commission-Dalton-20260424-171745
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-25T01:04:56.574Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T01:04:56.577Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
