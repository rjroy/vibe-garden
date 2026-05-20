---
name: prep-plan
description: This skill should be used when ready to build a reviewable implementation plan as a lore artifact. Input can be a spec, design, brainstorm, research, or a well-defined prompt. Triggers: "prep plan", "prepare a plan", "plan this", "make a plan", "plan the implementation", "break this into steps".
---

# Prep Plan

Build an implementation plan the user can review and approve before any code is written. The plan is the output. Implementation is a separate step via `/implement`.

**Do not use `EnterPlanMode`.** This skill authors a document, not a precursor to immediate code changes.

## Process

**Gather context.** Invoke the `lore-researcher` agent via Task tool with the topic description — wait for the result. Read any relevant lore artifacts (spec, design, brainstorm, research). Explore the codebase with an Explore subagent to understand what exists and where changes will land.

**Surface gaps before drafting.** If the input has ambiguous requirements, contradictions, or unstated assumptions that would force guesses, list them and ask the user to resolve them first. A plan built on unreviewed assumptions fails during implementation.

**Draft collaboratively.** Map the goal or requirements to concrete implementation steps. Order by dependency. Flag steps that need specialized expertise. Include a final validation step that checks the implementation against the source artifact.

**Confirm, then save.** Present the plan for user approval before saving.

**Fresh-eyes review.** After saving, invoke the `plan-reviewer` agent via Task tool on the saved plan. Present findings and offer to address issues before implementation begins.

## Saving

Save to `.lore/work/plans/[feature-name].html` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md` for the meta tag fields. The document body is freeform — what matters is that steps are concrete (files, functions, changes) and the source artifact or goal is clearly referenced so validation has something to check against.

The output is HTML — make the plan navigable. A visual step sequence with dependency indicators, expandable detail per step, and a clear reference to the source artifact at the top. If steps have validation gates, distinguish them visually from the implementation description. Inline CSS and JS are fine; no external dependencies.
