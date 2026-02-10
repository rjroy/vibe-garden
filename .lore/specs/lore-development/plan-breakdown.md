---
title: Plan breakdown skill
date: 2026-02-10
status: draft
tags: [skill-design, implementation, scope-constraint, task-decomposition, orchestration]
modules: [lore-development]
related:
  - .lore/specs/lore-development/implementation-skill.md
  - .lore/retros/lore-development/remove-breakdown-execute.md
  - .lore/brainstorm/lore-development/plan-implementation-drift.md
req-prefix: PBD
---

# Spec: Plan Breakdown

## Overview

A skill that decomposes a plan into individual task files, each scoped to one logical change with its own validation criteria and documentation reference. Implement is modified to consume these files as its phase list, feeding one task at a time to the implementation agent.

The purpose is scope constraint. The implementation agent's view is deliberately restricted: it receives one task file and nothing else. It cannot see the full plan, cannot anticipate future steps, cannot wander into adjacent work. Each task file is a leash that keeps the agent focused on exactly one thing.

## Prior Art

A previous `/breakdown` skill was removed (see retro) because it wrapped native Claude Code capability with ceremony. That skill just reformatted plan steps into chunks, adding no new information. This skill is different in three ways:

1. **Adds information the plan doesn't have.** Each task carries its own validation criteria and a reference to the documentation that justifies its existence. Plans describe what to build in what order. Tasks add "how do I know this one piece is done" and "why am I doing this."
2. **Constrains implement's scope.** Implement feeds one task file to the implementation agent. The agent can't see the rest of the plan, can't anticipate future steps, can't wander into adjacent work.
3. **Creates a reviewable checkpoint.** After breakdown, the user can inspect task granularity, reorder, remove, or adjust validation criteria before implementation starts.

## Entry Points

- User invokes `/plan-breakdown <path-to-plan>` after running `/prep-plan`, before running `/implement`
- The input must be a plan artifact (`.lore/plans/*.md`)

## Requirements

### Task Decomposition

- REQ-PBD-1: The skill reads a plan and decomposes its steps into task files. Each plan step becomes one or more tasks. A step that does one logical thing becomes one task. Split a step into multiple tasks when it modifies files with different concerns (e.g., auth logic vs database schema), requires validation in distinct ways (e.g., unit tests vs integration tests), or addresses multiple distinct requirements from the spec.
- REQ-PBD-2: Each task represents one logical change. A logical change is work that: (1) can be validated without depending on incomplete work from other tasks, (2) traces to a single requirement or goal, and (3) would be described as one thing in a commit message. "Add auth middleware" is one task even if it touches three files. "Add auth middleware and update the database schema" is two tasks because they serve different requirements and validate differently.
- REQ-PBD-3: Tasks are ordered. The sequence reflects dependencies: task N can assume tasks 1 through N-1 are complete. The skill determines order from the plan's step sequence and any dependency signals in the plan. If dependencies are circular or ambiguous, the skill presents the conflict to the user and asks for ordering guidance before generating task files.

### Task File Format

- REQ-PBD-4: Each task file contains four sections:

  **What**: Concrete description of what to implement. Specific enough that an implementation agent can act on it without seeing the broader plan.

  **Validation**: How to verify this task is done correctly. This is not "run the tests." It describes what specifically to test or check for this task. Derived from the plan's spec requirements, success criteria, or goal. If a plan step lacks clear validation criteria, the skill infers validation from the What section (e.g., "What: Add login form" becomes "Validation: Form renders with email and password fields, submits to the auth endpoint"). If validation cannot be inferred, flag the task for user review.

  **Why**: The requirement ID and a short excerpt so the implementation agent understands the justification without opening another file. If the plan has a spec, include the requirement ID and the requirement text (e.g., `REQ-AUTH-3: "All API endpoints require authentication except /health and /login"`). If the plan has a goal (no spec), quote the relevant part of the goal directly. If a plan step has no traceable requirement or goal, flag the task for user review.

  **Files**: Expected files to be created or modified. Carried forward from the plan step. This is guidance, not a constraint. If the implementation agent discovers additional files need changing, that's fine.

- REQ-PBD-5: Task files use lore frontmatter with a `source` field pointing to the plan, a `sequence` field for ordering, and status tracking (`pending`, `complete`, `skipped`).

### Storage

- REQ-PBD-6: Task files are saved to `.lore/tasks/<plan-name>/NNN-<task-name>.md` where NNN is a zero-padded sequence number (001, 002, ...) and task-name is a kebab-case description.
- REQ-PBD-7: The plan-name directory matches the plan's filename without extension. If the plan is `.lore/plans/auth-flow.md`, tasks go in `.lore/tasks/auth-flow/`.

### Implement Integration

- REQ-PBD-8: When implement is invoked with a plan, it checks for a corresponding `.lore/tasks/<plan-name>/` directory. If task files exist, implement uses them as its phase list instead of deriving phases from the plan's steps.
- REQ-PBD-9: Implement feeds one task file at a time to the implementation agent. The agent receives the task's What, Validation, Why, and Files sections. It does not receive the full plan or other task files.
- REQ-PBD-10: As each task completes the implement/test/review cycle, implement marks the task file's status as `complete`. The orchestrator marks a task `skipped` if the implementation agent reports the work is already done, or if the user explicitly requests skipping via AskUserQuestion. The orchestrator does not skip tasks on its own judgment.
- REQ-PBD-11: When implement resumes from notes, it reads task file statuses to determine where to pick up. Tasks marked `complete` or `skipped` are not re-run.

### User Review

- REQ-PBD-12: After generating task files, the skill presents a summary: task count, ordered list of task names, and any tasks that were split from a single plan step. The user can approve, request changes (by editing the plan and re-running `/plan-breakdown`, or by editing task files directly), or reject.

### Plan Staleness

- REQ-PBD-13: When implement detects task files for a plan, it compares the plan's modification timestamp against the oldest task file's timestamp. If the plan is newer than the task files, implement warns the user and asks whether to re-run `/plan-breakdown`, use the existing task files, or abort.

### Rejection

- REQ-PBD-14: The skill rejects a plan as too vague to decompose if it has fewer than 2 concrete steps, or if steps are only high-level descriptions without file references or actionable verbs. The rejection includes specific feedback: which steps are vague and what's missing (e.g., "Step 3 says 'handle errors' but doesn't specify which errors, where, or what files").

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Tasks saved | Decomposition complete, user approves | `.lore/tasks/<plan-name>/` directory with task files |
| User adjusts | User wants to modify task granularity or order | Re-generate or user edits manually, then re-summarize |
| Rejection | Plan lacks actionable steps (see REQ-PBD-14) | User, with specific feedback on what's missing |

## Task File Structure

```markdown
---
title: [task description]
date: YYYY-MM-DD
status: pending
tags: [task]
source: .lore/plans/[plan-name].md
sequence: N
---

# Task: [Short Description]

## What
[Concrete implementation description. Specific enough to act on without broader plan context.]

## Validation
[What specifically to test or verify for this task.
Not "run the tests" but "verify that the middleware rejects requests without a valid token and returns 401."]

## Why
REQ-AUTH-3: "All API endpoints require authentication except /health and /login"
[Or for plans without specs: Goal reference with relevant quote]

## Files
- `src/middleware/auth.ts` (create)
- `src/routes/index.ts` (modify)
- `tests/middleware/auth.test.ts` (create)
```

## Success Criteria

- [ ] Skill reads a plan and produces task files in `.lore/tasks/`
- [ ] Each task file contains What, Validation, Why, and Files sections
- [ ] Tasks are ordered and independently actionable
- [ ] Implement detects task files and uses them as its phase list
- [ ] Implement feeds one task at a time to the implementation agent (agent does not see full plan)
- [ ] Task status is updated as implement progresses
- [ ] Continuation from notes respects task file status
- [ ] Implement warns when task files are stale relative to the plan
- [ ] Vague plans are rejected with specific feedback
- [ ] A user running implement with task files sees progress per task, not per plan step

## AI Validation

**Defaults** (apply unless overridden):
- Unit tests with mocked time/network/filesystem/LLM calls
- 90%+ coverage on new code
- Code review by fresh-context sub-agent

## Terminology

Plans contain **steps**. Plan-breakdown decomposes steps into **tasks** (one step may produce multiple tasks). Implement treats tasks as **phases** in its orchestration loop. One term per concept: steps are input, tasks are output, phases are what implement calls them internally.

## Constraints

- This is a prompt-based skill, not a code application. The "implementation" is a SKILL.md file for plan-breakdown and modifications to the existing implement SKILL.md.
- Task files are a new lore artifact type. The frontmatter schema needs a `tasks` entry with status values `pending`, `complete`, `skipped`.
- The skill should not over-decompose. If a plan step is already atomic (one logical change, clear validation), it becomes one task without further splitting. A task that touches one function in one file and can be verified with a single assertion is likely over-decomposed. The skill adds validation and why, not granularity for its own sake.
- Plan-breakdown is optional. Implement continues to work directly from plans that don't have task files. The task file detection in REQ-PBD-8 is an enhancement, not a replacement for the existing flow.

## Context

- Implementation skill spec: `.lore/specs/lore-development/implementation-skill.md`
- Retro (why old breakdown was removed): `.lore/retros/lore-development/remove-breakdown-execute.md`
- Brainstorm (plan drift): `.lore/brainstorm/lore-development/plan-implementation-drift.md`
