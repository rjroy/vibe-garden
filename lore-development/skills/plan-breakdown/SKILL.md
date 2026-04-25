---
name: plan-breakdown
description: This skill should be used when the user asks to "break down this plan", "decompose this plan", "create tasks from this plan", "plan-breakdown", "break plan into tasks", "scope this into tasks", "generate tasks from plan", or wants to generate task files from a plan before implementation. This skill sits between /prep-plan and /implement in the workflow.
---

# Plan Breakdown

Decompose a plan into individual task files, each scoped to one logical change with its own validation criteria and requirement reference.

## When to Use

- A plan exists in `.lore/build/plans/` and the work is complex enough that implement benefits from tighter scope control
- The plan has multiple steps that touch different concerns, and reviewing task granularity before implementation would catch problems early
- Requirement traceability matters: each piece of work should trace back to a specific requirement or goal

## When to Skip

- The plan is simple enough that implement can work from its steps directly. Plan-breakdown is optional in the workflow; it sits between `/prep-plan` and `/implement` but is not required.
- The plan has 2-3 small, obvious steps where adding task files would be ceremony without value.

## Input

Invoked as `/plan-breakdown <path>` where `<path>` is a plan artifact (`.lore/build/plans/*.md`).

Read the plan. If the plan references a spec (in its Spec Reference section or frontmatter `related` field), load the spec too. Record the spec's file path; it will be used in both the task frontmatter (`related` field) and the Why section of each task. The spec provides requirement IDs needed for the Why section. If the plan has a Goal section instead of a spec reference, the goal text serves the same purpose and the plan's own path is used in the Why section instead.

**Search for related prior work**: Use the Task tool to invoke the `lore-researcher` agent with the plan's topic description. **Do not run in background.** Wait for the result before continuing. Surface retros from related prior implementations, relevant brainstorms, and research. Use findings to inform decomposition decisions. Retros that mention over-decomposition or missed splits are directly relevant to how aggressively to split plan steps.

## Rejection Gate

Before decomposing, assess whether the plan is concrete enough to produce useful tasks. A plan is actionable when its steps contain file references, specific function or module names, or verbs that describe implementation actions (add, modify, create, remove, refactor, extract).

Reject the plan if it has fewer than 2 concrete steps, or if steps are high-level descriptions without file references or actionable verbs. Rejection is not a dead end. Provide specific feedback: name which steps are vague and what's missing. "Step 3 says 'handle errors' but doesn't specify which errors, where, or what files" is useful feedback. "Step 3 is too vague" is not.

After rejection, the user can refine the plan and re-invoke `/plan-breakdown`.

## Surface Gaps

After the plan passes the Rejection Gate, review it for semantic clarity problems that would force assumptions during decomposition. The Rejection Gate checks structure (file references, actionable verbs). This step checks meaning.

Look for:
- **Ambiguous scope**: A step is structurally concrete but could describe two different amounts of work. "Add validation to the auth middleware" has file references and an actionable verb, but doesn't say which validations, which means the task boundary depends on an assumption.
- **Unclear requirement ownership**: Multiple plan steps partially address the same spec requirement, or a requirement isn't clearly covered by any step. Decomposition needs to assign each task a Why, and split ownership creates tasks where neither fully satisfies the requirement.
- **Validation gaps**: Steps where success criteria can't be derived from the plan or spec. Better to surface these as a batch now than to flag them one at a time in generated task files.
- **Contradictions with current code**: The lore-researcher results or codebase state conflicts with what the plan assumes (e.g., the plan says "create file X" but X already exists, or "modify function Y" but Y was refactored since the plan was written).

If gaps exist, list them and ask the user to resolve them before decomposing. Decomposition decisions (what to split, how to order, what validation to assign) depend on the answers. Making those decisions first and flagging problems after produces tasks built on guesses.

If the plan is clear, say so and proceed to decomposition.

## Decomposition

Walk through the plan's implementation steps in order. The goal is to produce task files that each represent one logical change, something that could be described as one thing in a commit message.

**What makes a good task boundary.** A step becomes one task when it does one thing: adds a middleware, creates a schema, implements a validation function. Even if it touches multiple files, the work is cohesive if all the files serve the same concern and validate the same way.

**When to split a step into multiple tasks.** Split when a step bundles work that serves different concerns. Signs that a step should be split:

- It modifies files with unrelated responsibilities (auth logic and database schema in the same step)
- It requires fundamentally different validation approaches (unit tests for one part, integration tests for another)
- It addresses multiple distinct requirements from the spec, where each requirement could be satisfied and verified independently

**When not to split.** Resist the urge to over-decompose. A task that touches one function in one file and can be verified with a single assertion is likely too granular. The skill adds validation criteria and requirement traceability, not artificial granularity. If a plan step is already atomic (one logical change, clear validation), it becomes one task without further splitting. The task gains What/Validation/Why/Files sections that the plan step didn't have, and that's the value.

**Ordering.** Arrange tasks so that task N can assume tasks 1 through N-1 are complete. The plan's step sequence is the starting point, but splitting a step may introduce ordering considerations within the split. If dependencies are circular or ambiguous, present the conflict to the user and ask for ordering guidance before generating task files.

## Output

### Task File Template

Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for field definitions and status values.

Each task file follows this structure:

```markdown
---
title: [Short task description]
date: YYYY-MM-DD
status: pending
tags: [task]
source: .lore/build/plans/[plan-name].md
related: [.lore/build/specs/[spec-name].md]   # omit if plan has no spec
sequence: N
modules: [affected-modules]
---

# Task: [Short Description]

## What

[Concrete implementation description. Specific enough to act on without seeing
the broader plan. Name the functions, modules, or components involved. An
implementation agent reading only this section should understand what to build.]

## Validation

[What specifically to test or verify for this task. Not "run the tests" but
concrete criteria: "Middleware rejects requests without a valid token and
returns 401. Middleware passes requests with a valid token to the next handler.
Unit test covers both paths."

Derive validation from the plan's spec requirements or success criteria. If the
plan step lacks clear validation criteria, infer from the What section. If
validation cannot be inferred, flag the task for user review with a note
explaining what's missing.]

## Why

[Requirement ID, source file path, and excerpt so the implementation agent
understands the justification and can find the original context.

With spec: From `.lore/build/specs/auth-flow.md`, REQ-AUTH-3: "All API endpoints
require authentication except /health and /login"

Without spec (goal-based plan): From `.lore/build/plans/auth-flow.md`, Goal: "Ensure
all API access is authenticated" followed by the relevant excerpt.

If a plan step has no traceable requirement or goal, flag the task for user
review.]

## Files

- `path/to/file.ts` (create)
- `path/to/other.ts` (modify)
- `tests/path/to/file.test.ts` (create)

[Carried forward from the plan step. This is guidance, not a constraint. The
implementation agent may discover additional files need changing.]
```

### Storage

Save task files to `.lore/build/tasks/<plan-name>/NNN-<task-name>.md` where:

- `<plan-name>` matches the plan's filename without extension (e.g., plan `.lore/build/plans/auth-flow.md` produces directory `.lore/build/tasks/auth-flow/`)
- `NNN` is a zero-padded sequence number starting at 001
- `<task-name>` is a kebab-case description derived from the task's purpose

Create the directory if it doesn't exist. If the directory already contains task files from a previous run, warn the user and ask whether to overwrite or abort.

## User Review

After generating all task files, present a summary to the user before considering the work complete:

- Total task count
- Ordered list showing sequence number and task name for each task
- Any plan steps that were split into multiple tasks, with a brief note on why the split was necessary

The user has three options:

1. **Approve**: Tasks are ready for `/implement`
2. **Edit**: Modify task files directly (reorder, adjust validation, change scope) or edit the plan and re-run `/plan-breakdown`
3. **Reject**: Discard generated tasks entirely

Do not proceed to implementation. Plan-breakdown produces task files and stops. The user invokes `/implement` separately when ready.

## Relationship to Other Skills

Plan-breakdown sits in a chain: `/prep-plan` produces the plan, `/plan-breakdown` decomposes it into tasks, `/implement` executes the tasks. Each handoff is explicit and user-controlled. No skill auto-invokes the next.

When `/implement` receives a plan that has corresponding task files in `.lore/build/tasks/<plan-name>/`, it uses those tasks as its phase list instead of deriving phases from the plan's steps. This is the consumption side of what plan-breakdown produces. The contract between the two skills is the task file format defined above and the directory convention in `.lore/build/tasks/`. Implement also performs a staleness check, comparing the plan's modification time against the task files, and warns the user if the plan has been modified since decomposition.

## What Plan-Breakdown Adds

A previous `/breakdown` skill was removed because it wrapped native capability without adding information. This skill exists specifically because it adds three things the plan doesn't have:

1. **Validation criteria per task.** Plans describe what to build. Tasks add "how do I know this piece is done." The implementation agent gets a concrete checklist, not a general "run the tests."

2. **Requirement traceability per task.** Each task carries the specific requirement or goal it satisfies. The implementation agent understands why it's doing the work, not just what the work is.

3. **A reviewable checkpoint.** After decomposition and before implementation, the user can inspect task granularity, reorder tasks, adjust validation criteria, or remove tasks entirely. This is the last point where changing scope is cheap.

If the plan is simple enough that these three things don't add value, skip this skill and let implement work from the plan directly.
