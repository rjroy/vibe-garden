---
title: "Commission: Plan frontmatter validation from spec"
date: 2026-03-10
status: dispatched
type: one-shot
tags: [commission]
worker: Verity
workerDisplayTitle: "Guild Pathfinder"
prompt: "Create an implementation plan from the spec at `.lore/specs/frontmatter-validation.md`.\n\nThe plan should break the work into ordered, commissionable steps. For each step, identify:\n- What gets built\n- Which files are created or modified\n- Dependencies on other steps\n- What gets tested\n\nKey context:\n- The script lives at `lore-development/scripts/validate_frontmatter.py`\n- The frontmatter schema source of truth is `lore-development/shared/frontmatter-schema.md` — the script needs a machine-readable representation\n- Integration point is the tend skill's status mode (look at how status mode currently works in `lore-development/skills/tend/`)\n- The spec calls for JSON lines output, exit codes 0/1/2, and PyYAML dependency handling\n- Repair is Claude-driven using tend's existing confirmation pattern\n\nRead the spec, the existing tend skill implementation, and the frontmatter schema. Then write the plan to `.lore/plans/frontmatter-validation.md` following lore artifact conventions (YAML frontmatter with title, date, status, tags, related fields).\n\nFocus on producing a plan that can be directly decomposed into commissions for Dalton."
dependencies: []
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-10T21:02:12.965Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-10T21:02:12.966Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
