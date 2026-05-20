---
name: plan-breakdown
description: This skill should be used when a plan exists and needs validation gates added to each step before implementation begins. Produces task files that implement can consume. Triggers: "break down this plan", "add validation to the plan steps", "plan-breakdown", "gate this plan".
---

# Plan Breakdown

A plan describes what to build. This skill adds what's missing: how do you know each step is done?

Invoke when a plan is complex enough that explicit validation at each step matters before handing off to implement. Simple plans don't need it — implement can work from the plan directly.

## Input

Invoked as `/plan-breakdown <path>` where `<path>` is a plan in `.lore/work/plans/`. Read the plan and any spec it references.

## What to Add

For each plan step, define:
- **What**: concrete enough that an agent reading only this task knows what to build
- **Validation**: specific criteria, not "run the tests" — "the CLI outputs X when called with Y", "Playwright confirms the button triggers Z", "unit test covers the rejection path"
- **Why**: the requirement or goal this step satisfies, with a reference back to the source
- **Files**: affected files (guidance, not a constraint)

Split a step only when it bundles genuinely different concerns with different validation needs. Resist over-decomposition — the value is the validation gates, not artificial granularity.

Present the task list to the user for review before saving. Adjust ordering, validation, or scope based on feedback.

## Output

Save task files to `.lore/work/tasks/<plan-name>/NNN-<task-name>.html`. Load `${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md` for the meta tag fields. Set `status: pending` and include a `sequence` meta field for ordering.

Each task file body: What, Validation, Why, Files sections.

The output is HTML — give each task file a clear visual status chip (pending / in progress / complete / skipped), the sequence position prominently displayed, and the validation criteria visually separated from the implementation description so a reviewing agent can find them without reading everything. Inline CSS and JS are fine; no external dependencies.

Stop here. The user invokes `/implement` when ready.
