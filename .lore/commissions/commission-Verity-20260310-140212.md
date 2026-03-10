---
title: "Commission: Plan frontmatter validation from spec"
date: 2026-03-10
status: completed
type: one-shot
tags: [commission]
worker: Verity
workerDisplayTitle: "Guild Pathfinder"
prompt: "Create an implementation plan from the spec at `.lore/specs/frontmatter-validation.md`.\n\nThe plan should break the work into ordered, commissionable steps. For each step, identify:\n- What gets built\n- Which files are created or modified\n- Dependencies on other steps\n- What gets tested\n\nKey context:\n- The script lives at `lore-development/scripts/validate_frontmatter.py`\n- The frontmatter schema source of truth is `lore-development/shared/frontmatter-schema.md` — the script needs a machine-readable representation\n- Integration point is the tend skill's status mode (look at how status mode currently works in `lore-development/skills/tend/`)\n- The spec calls for JSON lines output, exit codes 0/1/2, and PyYAML dependency handling\n- Repair is Claude-driven using tend's existing confirmation pattern\n\nRead the spec, the existing tend skill implementation, and the frontmatter schema. Then write the plan to `.lore/plans/frontmatter-validation.md` following lore artifact conventions (YAML frontmatter with title, date, status, tags, related fields).\n\nFocus on producing a plan that can be directly decomposed into commissions for Dalton."
dependencies: []
linked_artifacts:
  - .lore/plans/frontmatter-validation.md

activity_timeline:
  - timestamp: 2026-03-10T21:02:12.965Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-10T21:02:12.966Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
  - timestamp: 2026-03-10T21:02:12.993Z
    event: status_in_progress
    reason: "Execution started"
    from: "dispatched"
    to: "in_progress"
  - timestamp: 2026-03-10T21:02:32.993Z
    event: progress_report
    reason: "Starting research phase: reading the spec, frontmatter schema, and tend skill implementation to understand the full scope before planning."
  - timestamp: 2026-03-10T21:04:23.915Z
    event: progress_report
    reason: "Finished reading all source materials: spec (11 requirements across detection/integration/repair), frontmatter schema (11 document types, 4 required fields, type-specific fields), tend skill + status mode reference (three-pass verification, report categories, confirmation pattern), lore-config reference (custom directories), and existing plan format conventions. Now synthesizing into the implementation plan."
  - timestamp: 2026-03-10T21:06:16.567Z
    event: result_submitted
    reason: "Created implementation plan at `.lore/plans/frontmatter-validation.md`.\n\nThe plan breaks the spec into 4 sequential, commissionable steps:\n\n1. **Schema data module** (`frontmatter_schema.py`): Machine-readable encoding of frontmatter-schema.md as importable Python constants. No dependencies.\n\n2. **Core validation script** (`validate_frontmatter.py`): Directory scanning, YAML parsing, structural checks, required fields, field types, status values, JSON lines output, exit codes 0/1/2, PyYAML graceful fallback. Covers REQ-FMVAL-1 through 6, 8 through 10. Full test suite with fixtures targeting 90%+ coverage.\n\n3. **lore-config.md support**: Extends the script to read custom_directories from lore-config.md and merge with schema defaults (REQ-FMVAL-7).\n\n4. **Tend integration + repair**: Modifies status.md to invoke the script as pre-check, adds Malformed/Invalid Frontmatter report categories, excludes parse-failed files from subsequent passes, adds Claude-driven repair using tend's confirmation pattern (REQ-FMVAL-11 through 15).\n\nEach step includes which files get created/modified, what context the commission needs, and what gets tested. All 15 spec requirements are traced to specific steps."
  - timestamp: 2026-03-10T21:06:20.614Z
    event: status_completed
    reason: "Execution completed"
    from: "in_progress"
    to: "completed"
current_progress: "Finished reading all source materials: spec (11 requirements across detection/integration/repair), frontmatter schema (11 document types, 4 required fields, type-specific fields), tend skill + status mode reference (three-pass verification, report categories, confirmation pattern), lore-config reference (custom directories), and existing plan format conventions. Now synthesizing into the implementation plan."
projectName: vibe-garden
---
Created implementation plan at `.lore/plans/frontmatter-validation.md`.

The plan breaks the spec into 4 sequential, commissionable steps:

1. **Schema data module** (`frontmatter_schema.py`): Machine-readable encoding of frontmatter-schema.md as importable Python constants. No dependencies.

2. **Core validation script** (`validate_frontmatter.py`): Directory scanning, YAML parsing, structural checks, required fields, field types, status values, JSON lines output, exit codes 0/1/2, PyYAML graceful fallback. Covers REQ-FMVAL-1 through 6, 8 through 10. Full test suite with fixtures targeting 90%+ coverage.

3. **lore-config.md support**: Extends the script to read custom_directories from lore-config.md and merge with schema defaults (REQ-FMVAL-7).

4. **Tend integration + repair**: Modifies status.md to invoke the script as pre-check, adds Malformed/Invalid Frontmatter report categories, excludes parse-failed files from subsequent passes, adds Claude-driven repair using tend's confirmation pattern (REQ-FMVAL-11 through 15).

Each step includes which files get created/modified, what context the commission needs, and what gets tested. All 15 spec requirements are traced to specific steps.
