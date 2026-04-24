---
title: "Commission: Prep plan for lore redesign spec"
date: 2026-04-24
status: completed
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Octavia wrote a spec at `.lore/specs/lore-redesign.md` (confirm the path — she may have placed it elsewhere; check her commission result `commission-Octavia-20260424-134303` for the actual location).\n\nBuild an implementation plan for the spec using `/lore-development:prep-plan`. The skill generates, persists, and reviews plans as first-class lore artifacts.\n\n## Context\n\nThe spec covers four concerns:\n1. Directory structure revamp (`build/`, `reference/`, `learned/`) — plugin-wide path migrations\n2. `/retro` scope reduction\n3. `/excavate` → `/distill` rename + reshape\n4. New `/learn` skill\n\nThis is a plugin-wide refactor of `lore-development`. Blast radius: every SKILL.md that writes to `.lore/`, frontmatter schema, agent descriptions, `/tend` migration mode.\n\n## Plan requirements\n\n- **Phasing matters.** A 7-skill refactor across path strings, frontmatter schema, and agent descriptions is too much for one commission. Break into right-sized phases (2–3 phases worth of work per future commission). Each phase should fit in a single context window.\n- **Foundation phase fans out.** The directory structure + frontmatter schema is the foundation. Multiple skills get updated against it. Foundation phase needs an implement → review → fix gate before any fan-out.\n- **Coupling between `/retro` strip and `/learn`.** Per the roadmap, stripping `/retro` before `/learn` exists leaves a window with no extraction path. Plan must address — either ship `/learn` alongside or include a pointer note in the stripped `/retro`.\n- **Migration mode for `/tend`.** Existing `.lore/` content needs migration to the new structure. Specify when this lands relative to the skill path updates.\n- **Per-phase test verification.** Plugin skills are user-invocable. Each phase needs a verification step (the skill still loads, paths resolve, the migration runs cleanly on a test fixture).\n- **Delegation guide.** Name the worker for each phase and the reviewer. Foundation phases get Thorne reviews before fan-out.\n\nRead the spec carefully. Read the four brainstorms it references (`.lore/brainstorm/lore-directory-redesign.md`, `.lore/brainstorm/principles-for-capture-skills.md`, `.lore/brainstorm/distill-function.md`, `.lore/brainstorm/learn-dialog.md`) so the plan reflects the *why* behind the spec's directives.\n\nReturn: path to the plan file and a phase-by-phase summary with worker assignments and review gates. Flag any spec gaps you hit while planning."
dependencies:
  - commission-Octavia-20260424-134303
linked_artifacts:
  - .lore/plans/lore-redesign.md

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
  - timestamp: 2026-04-24T22:16:47.696Z
    event: status_in_progress
    reason: "Execution started"
    from: "dispatched"
    to: "in_progress"
  - timestamp: 2026-04-24T22:16:58.576Z
    event: progress_report
    reason: "Starting work. Reading Octavia's commission result, spec, and referenced brainstorms before invoking prep-plan."
  - timestamp: 2026-04-24T22:19:17.286Z
    event: progress_report
    reason: "Context complete. Read spec + 4 brainstorms + roadmap + Octavia's result. Surveyed plugin surface: 20 skills, 6 agents, shared frontmatter schema, frontmatter_schema.py + validate_frontmatter.py scripts, idea_hook.py, tend references. Drafting 6-phase plan grouped into 3 commissions with delegation guide."
  - timestamp: 2026-04-24T22:35:37.544Z
    event: result_submitted
    reason: "Plan written to `.lore/plans/lore-redesign.md`. Reviewed by plan-reviewer (lore-development:plan-reviewer), findings integrated.\n\n**Structure**: 6 implementation phases + a final validation phase, grouped into 3 follow-on commissions.\n\n**Phase-by-phase summary (worker / reviewer / review gate):**\n\n- **Phase 0 — Schema foundation** (Dalton / Thorne GATE). Rewrites `shared/frontmatter-schema.md` with the three per-directory status sets (REQ-REDESIGN-8 – 13), regenerates `frontmatter_schema.py`, updates `test_frontmatter_schema.py`'s `SCHEMA_DOCUMENT_TYPES` and reorganizes fixture trees, rewrites `tend/references/{directories,status,lore-config}.md`. **Thorne gate is mandatory before any fan-out.** Foundation errors otherwise propagate N files deep.\n\n- **Phase 1 — Path string fan-out** (Dalton / fresh-lore). Updates 18 SKILL.md files + `idea_hook.py` per the REQ-REDESIGN-6 migration table. Strictly path strings only — retro content reshape and excavate rename deferred to Phases 5 and 4. Verification: path-string audit grep.\n\n- **Phase 2 — Agent descriptions** (Dalton / Thorne). Updates `lore-researcher` (incl. search-priority inversion — learned > reference > build), `spec-reviewer`, `design-reviewer`, `plan-reviewer`, `fresh-lore`. Fallback-review-save path moves to `.lore/build/reviews/`.\n\n- **Phase 3 — `/tend migrate`** (Dalton / Thorne + unit+e2e tests). New dry-run-default mode, idempotent, link rewriting across frontmatter `related:`, `source:`, and in-body markdown links. Tests cover protected paths, fenced-code-block preservation, and migration-doc exception (last two added from review).\n\n- **Phase 4 — `/excavate` → `/distill`** (Dalton / plugin-dev:skill-reviewer + fresh-lore). Rename + reshape per distill brainstorm. Two seed modes (`code`, `build`), shared code-verifying core, reference-shape rule, null output valid. `surface-surveyor` agent added to file list (was missing from v1 — caught by reviewer). Tend archive prompt: soft (not hard) per rationale noted.\n\n- **Phase 5 — `/learn` + `/retro`** (Dalton / plugin-dev:skill-reviewer). Coupled ship — both in one phase. If delivery splits, **`/learn` ships first, `/retro` holds** (strictly additive). Anti-template and anti-assertion custom AI validation checks are the merge gate.\n\n- **Phase 6 — Cross-plugin + full audit** (Dalton / Thorne + Octavia). Celeste update, README rewrite, full spec AI Validation custom checks, real-world `/tend migrate` on this repo.\n\n- **Phase 7 — Spec validation** (fresh sub-agent). Requirement-by-requirement sweep.\n\n**Commission grouping**: A = phases 0+1+2, B = 3+4, C = 5+6. Phase 7 closes the refactor.\n\n**Spec gaps flagged**:\n- REQ-REDESIGN-33 (tend-archive enforcement vs prompt): spec defers; plan adopts soft prompt with rationale.\n- REQ-REDESIGN-41 (/learn file layout): spec defers; plan adopts \"one-file-per-entry, kebab-case, flat\" starting default.\n- REQ-REDESIGN-45 (Celeste cross-plugin): spec flags coordination. Plan requires the decision (expand Commission C scope, or file separate guild-hall commission) made **before Commission C is commissioned**, not deferred to runtime.\n- Pre-existing test fixtures hardcode old-path keys (`SCHEMA_DOCUMENT_TYPES` list in `test_frontmatter_schema.py`) and fail Phase 0's own gate if not updated — made explicit in plan step 6.\n\n**Reviewer findings applied**: `surface-surveyor` added to Phase 4; fixture reorganization made explicit in Phase 0; code-block + migration-doc fixtures added to Phase 3 tests; /learn-before-/retro ordering made explicit in Phase 5; Celeste decision elevated to pre-commission planning."
  - timestamp: 2026-04-24T22:35:47.426Z
    event: status_completed
    reason: "Execution completed"
    from: "in_progress"
    to: "completed"
current_progress: "Context complete. Read spec + 4 brainstorms + roadmap + Octavia's result. Surveyed plugin surface: 20 skills, 6 agents, shared frontmatter schema, frontmatter_schema.py + validate_frontmatter.py scripts, idea_hook.py, tend references. Drafting 6-phase plan grouped into 3 commissions with delegation guide."
projectName: vibe-garden
---
Plan written to `.lore/plans/lore-redesign.md`. Reviewed by plan-reviewer (lore-development:plan-reviewer), findings integrated.

**Structure**: 6 implementation phases + a final validation phase, grouped into 3 follow-on commissions.

**Phase-by-phase summary (worker / reviewer / review gate):**

- **Phase 0 — Schema foundation** (Dalton / Thorne GATE). Rewrites `shared/frontmatter-schema.md` with the three per-directory status sets (REQ-REDESIGN-8 – 13), regenerates `frontmatter_schema.py`, updates `test_frontmatter_schema.py`'s `SCHEMA_DOCUMENT_TYPES` and reorganizes fixture trees, rewrites `tend/references/{directories,status,lore-config}.md`. **Thorne gate is mandatory before any fan-out.** Foundation errors otherwise propagate N files deep.

- **Phase 1 — Path string fan-out** (Dalton / fresh-lore). Updates 18 SKILL.md files + `idea_hook.py` per the REQ-REDESIGN-6 migration table. Strictly path strings only — retro content reshape and excavate rename deferred to Phases 5 and 4. Verification: path-string audit grep.

- **Phase 2 — Agent descriptions** (Dalton / Thorne). Updates `lore-researcher` (incl. search-priority inversion — learned > reference > build), `spec-reviewer`, `design-reviewer`, `plan-reviewer`, `fresh-lore`. Fallback-review-save path moves to `.lore/build/reviews/`.

- **Phase 3 — `/tend migrate`** (Dalton / Thorne + unit+e2e tests). New dry-run-default mode, idempotent, link rewriting across frontmatter `related:`, `source:`, and in-body markdown links. Tests cover protected paths, fenced-code-block preservation, and migration-doc exception (last two added from review).

- **Phase 4 — `/excavate` → `/distill`** (Dalton / plugin-dev:skill-reviewer + fresh-lore). Rename + reshape per distill brainstorm. Two seed modes (`code`, `build`), shared code-verifying core, reference-shape rule, null output valid. `surface-surveyor` agent added to file list (was missing from v1 — caught by reviewer). Tend archive prompt: soft (not hard) per rationale noted.

- **Phase 5 — `/learn` + `/retro`** (Dalton / plugin-dev:skill-reviewer). Coupled ship — both in one phase. If delivery splits, **`/learn` ships first, `/retro` holds** (strictly additive). Anti-template and anti-assertion custom AI validation checks are the merge gate.

- **Phase 6 — Cross-plugin + full audit** (Dalton / Thorne + Octavia). Celeste update, README rewrite, full spec AI Validation custom checks, real-world `/tend migrate` on this repo.

- **Phase 7 — Spec validation** (fresh sub-agent). Requirement-by-requirement sweep.

**Commission grouping**: A = phases 0+1+2, B = 3+4, C = 5+6. Phase 7 closes the refactor.

**Spec gaps flagged**:
- REQ-REDESIGN-33 (tend-archive enforcement vs prompt): spec defers; plan adopts soft prompt with rationale.
- REQ-REDESIGN-41 (/learn file layout): spec defers; plan adopts "one-file-per-entry, kebab-case, flat" starting default.
- REQ-REDESIGN-45 (Celeste cross-plugin): spec flags coordination. Plan requires the decision (expand Commission C scope, or file separate guild-hall commission) made **before Commission C is commissioned**, not deferred to runtime.
- Pre-existing test fixtures hardcode old-path keys (`SCHEMA_DOCUMENT_TYPES` list in `test_frontmatter_schema.py`) and fail Phase 0's own gate if not updated — made explicit in plan step 6.

**Reviewer findings applied**: `surface-surveyor` added to Phase 4; fixture reorganization made explicit in Phase 0; code-block + migration-doc fixtures added to Phase 3 tests; /learn-before-/retro ordering made explicit in Phase 5; Celeste decision elevated to pre-commission planning.
