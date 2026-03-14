---
title: "Frontmatter validation"
date: 2026-03-10
status: closed
tags: [meeting]
worker: Guild Master
workerDisplayTitle: "Guild Master"
agenda: "Front matter validation"
deferred_until: ""
linked_artifacts: []
meeting_log:
  - timestamp: 2026-03-10T21:00:06.297Z
    event: opened
    reason: "User started audience"
  - timestamp: 2026-03-10T21:02:16.833Z
    event: renamed
    reason: "Renamed to: Frontmatter validation planning"
  - timestamp: 2026-03-10T21:03:04.393Z
    event: renamed
    reason: "Renamed to: Frontmatter validation"
  - timestamp: 2026-03-13T08:23:06.025Z
    event: closed
    reason: "User closed audience"
---
**MEETING NOTES: Frontmatter Validation**

**Summary**

The Guild Master opened with an agenda on YAML frontmatter validation for the tend skill, building on a completed brainstorm that explored error taxonomy, placement options, tooling approaches, and strictness tiers. The natural next step was moving from brainstorm findings into actionable specification and implementation. The user confirmed readiness to proceed and requested that Verity prepare an implementation plan from the existing spec document.

The spec was read and confirmed in place. The spec defines a Python validation script that detects frontmatter errors (parse failures, missing required fields, type violations, invalid status values) and integrates as a pre-check in tend's status mode, with Claude-driven repair following a confirmation pattern. The solution separates deterministic detection work (script) from synthesis and repair work (Claude).

After the plan was produced, the user commissioned four sequential implementation steps for Dalton, each dependent on the prior: schema data module, core validation script, lore-config.md support, and tend integration with repair. The user also commissioned a separate brainstorm with Octavia exploring how retrospectives can capture lessons learned from commission activity and meeting summaries, given that current artifacts are activity records rather than reflection.

**Key Decisions Made**

- Move forward with implementation rather than further refinement of the brainstorm. The plan is ready for commissioned work.
- Decompose implementation into four sequential steps with explicit dependencies, allowing parallel testing and incremental validation.
- Treat schema representation as a separate, independently testable step (Step 1) before the script depends on it.
- Commission retro skill brainstorm separately to explore whether the existing retro skill or new writer cleanup capabilities are sufficient for synthesis across commission logs and meeting summaries, or if the skill needs Guild Hall-specific evolution.
- Create PR to capture work in progress.

**Artifacts Referenced**

- `.lore/specs/frontmatter-validation.md` (spec defining script behavior, schema validation, integration points, and repair flow)
- `.lore/plans/frontmatter-validation.md` (implementation plan with four sequential steps and dependency graph)
- `.lore/brainstorm/lore-development/yaml-frontmatter-validation.md` (prior brainstorm on error taxonomy and tooling approach)
- `lore-development/shared/frontmatter-schema.md` (source of truth for frontmatter schema, input to Step 1)

**Open Items**

- Four commissions in flight with Dalton (Steps 1–4 of frontmatter validation implementation); first commission is active, subsequent three await completion of prior step.
- Octavia brainstorm on retro skill sufficiency and potential Guild Hall-specific evolution; awaiting report.
- PR #130 created; awaiting review and merge.
