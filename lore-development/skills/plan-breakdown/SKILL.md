---
name: plan-breakdown
description: Use before implementing a complex plan to add validation gates to each step. Produces task files implement can consume. Triggers: "break down this plan", "add validation to the plan steps", "plan-breakdown", "gate this plan".
---

# Plan Breakdown

A plan describes what to build. This skill adds what's missing: how do you know each step is done?

Use when a plan is complex enough that having explicit validation at each step matters before handing off to implement. Simple plans don't need it — implement can work from the plan directly.

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

Save task files to `.lore/work/tasks/<plan-name>/NNN-<task-name>.md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields. Set `status: pending` and include a `sequence` field for ordering.

Each task file body: What, Validation, Why, Files sections.

Stop here. The user invokes `/implement` when ready.
