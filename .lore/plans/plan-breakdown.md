---
title: Plan breakdown skill implementation
date: 2026-02-10
status: executed
tags: [skill-design, implementation, scope-constraint, task-decomposition, orchestration]
modules: [lore-development]
related:
  - .lore/specs/lore-development/plan-breakdown.md
  - .lore/specs/lore-development/implementation-skill.md
  - .lore/retros/lore-development/remove-breakdown-execute.md
  - .lore/retros/lore-development/implementation-skill.md
  - .lore/brainstorm/lore-development/plan-implementation-drift.md
---

# Plan: Plan Breakdown Skill

## Spec Reference

**Spec**: `.lore/specs/lore-development/plan-breakdown.md`

Requirements addressed:
- REQ-PBD-5: Task file frontmatter schema → Step 1
- REQ-PBD-1: Decompose plan steps into tasks → Step 2
- REQ-PBD-2: One logical change per task → Step 2
- REQ-PBD-3: Task ordering by dependency → Step 2
- REQ-PBD-4: Task file format (What/Validation/Why/Files) → Step 2
- REQ-PBD-6: Storage path `.lore/tasks/<plan-name>/NNN-<task-name>.md` → Step 2
- REQ-PBD-7: Directory naming from plan filename → Step 2
- REQ-PBD-12: User review after generation → Step 2
- REQ-PBD-14: Rejection of vague plans → Step 2
- REQ-PBD-8: Implement detects task files → Step 3
- REQ-PBD-9: Implement feeds one task at a time → Step 3
- REQ-PBD-10: Task status updates during implementation → Step 3
- REQ-PBD-11: Resume respects task file status → Step 3
- REQ-PBD-13: Plan staleness warning → Step 3

## Codebase Context

**Existing files to modify:**
- `lore-development/shared/frontmatter-schema.md` (205 lines): Defines frontmatter fields and status values for all lore document types. Needs a task type entry.
- `lore-development/skills/implement/SKILL.md` (160 lines): Current orchestrator skill. Phase detection happens in Section 1 (Initialize, line 88). Phase execution in Section 2 (lines 104-116). Resume logic at line 90.

**New files to create:**
- `lore-development/skills/plan-breakdown/SKILL.md`: The new skill.

**Patterns to follow:**
- Skills are directories under `lore-development/skills/<name>/SKILL.md`
- Skill frontmatter uses `name` and `description` fields
- Skills reference `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for frontmatter loading
- Existing skills (implement, prep-plan) are the style reference for tone and structure
- Plugin uses auto-discovery; no plugin.json update needed

**Lessons from prior work:**
- Old `/breakdown` removed for wrapping native capability. New skill must add information the plan doesn't have (validation criteria, requirement traceability, scope constraint).
- "Prompts are not programs." The 14 spec requirements should inform the skill's guidance, not become a mechanical checklist the model follows step by step.
- Cross-skill contracts (plan-breakdown produces, implement consumes) need explicit documentation on both sides.

## Implementation Steps

### Step 1: Add task type to frontmatter schema

**Files**: `lore-development/shared/frontmatter-schema.md` (modify)
**Addresses**: REQ-PBD-5

Add a `task` row to the "Status Values by Document Type" table with directory `.lore/tasks/` and statuses `pending`, `complete`, `skipped`.

Add a "Task-Specific Fields" section (parallel to the existing "Notes-Specific Fields" section) documenting:
- `source` (required): Path to the plan this task was decomposed from
- `sequence` (required): Integer ordering within the task set

Add a task frontmatter example to the Examples section.

This is a small, contained edit to an existing reference document. The changes follow the exact pattern already used for notes-specific fields.

### Step 2: Create plan-breakdown skill

**Files**: `lore-development/skills/plan-breakdown/SKILL.md` (create)
**Addresses**: REQ-PBD-1, REQ-PBD-2, REQ-PBD-3, REQ-PBD-4, REQ-PBD-6, REQ-PBD-7, REQ-PBD-12, REQ-PBD-14

Follow the tone and structure of existing skills (implement, prep-plan) for parallel sections like When to Use / When to Skip.

Create the SKILL.md with these sections:

**Frontmatter**: `name: plan-breakdown`, description triggering on "break down this plan", "decompose this plan", "create tasks from this plan", "plan-breakdown".

**When to Use / When to Skip**: Use after `/prep-plan`, before `/implement`. Skip when the plan is simple enough that implement can work from steps directly (plan-breakdown is optional per spec constraints).

**Input**: Path to a plan artifact (`.lore/plans/*.md`). Read the plan. If the plan has a spec reference, load the spec too (for requirement IDs in the Why section).

**Rejection gate** (REQ-PBD-14): Before decomposing, check that the plan has at least 2 concrete steps with file references or actionable verbs. If not, reject with specific feedback on which steps are vague and what's missing.

**Decomposition guidance** (REQ-PBD-1, 2, 3): Walk through plan steps. Each step that does one logical thing becomes one task. Split a step when it modifies files with different concerns, requires validation in distinct ways, or addresses multiple requirements. Don't over-split: if a step is already atomic, it stays as one task. Order tasks so task N can assume 1 through N-1 are complete. If dependencies are circular, ask the user.

**Task file output** (REQ-PBD-4, 5, 6, 7): Include the task file template inline (frontmatter with source/sequence/status, then What/Validation/Why/Files sections). Save to `.lore/tasks/<plan-name>/NNN-<task-name>.md`. Reference the frontmatter schema for field definitions.

The skill description for each section should convey intent, not mechanical steps. For example, the decomposition section describes what makes a good split and what makes a bad one, rather than listing "if condition A, split; if condition B, don't split."

**User review** (REQ-PBD-12): After generating all task files, present a summary: count, ordered list, and any steps that were split into multiple tasks. User can approve, edit task files directly, or re-run after modifying the plan.

### Step 3: Modify implement to consume task files

**Files**: `lore-development/skills/implement/SKILL.md` (modify)
**Addresses**: REQ-PBD-8, REQ-PBD-9, REQ-PBD-10, REQ-PBD-11, REQ-PBD-13

These changes are additions to the existing skill, not rewrites. The existing flow (plan without tasks, spec, design, notes) remains untouched. The task file path is a new branch in the phase detection logic.

Four modifications, each located by section heading:

**1. Input table** (under `## Input`, the table starting with `| Input Type |`):

Add a footnote or parenthetical to the Plan row's Behavior column. Change "Follow the plan's steps as phases" to "Follow the plan's steps as phases (but see Task File Detection below)".

**2. Initialize section** (under `### 1. Initialize`):

Insert a new subsection after the paragraph that begins "Read the input artifact. If it is a plan..." and before "If resuming from notes...". Title it **Task file detection.** Content:

When the input is a plan, check whether `.lore/tasks/<plan-name>/` exists (where `<plan-name>` matches the plan's filename without extension). If the directory exists and contains task files:

- **Staleness check** (REQ-PBD-13): Compare the plan's modification timestamp against the oldest task file's timestamp. The oldest task is the right comparison point because all tasks are generated in one `/plan-breakdown` run, so the oldest represents when the decomposition happened. If the plan is newer than the oldest task, warn the user via AskUserQuestion with three options: re-run `/plan-breakdown`, use existing tasks, or abort.
- **Phase list**: Read task files sorted by their `sequence` frontmatter field. These become the phases. Each phase corresponds to one task file.

If no task directory exists, derive phases from the plan's steps as usual.

**3. Execute Phases section** (under `### 2. Execute Phases`):

Insert a new paragraph after "For each phase:" and before step "a. Dispatch implementation." Content:

**When phases come from task files:** The implementation agent prompt includes the task's What, Validation, Why, and Files sections. It does not receive the full plan, other task files, or the task's sequence number. After a task passes the implement/test/review cycle, update the task file's frontmatter `status` to `complete`. If the implementation agent reports the work is already done, or the user explicitly requests skipping via AskUserQuestion, mark the task `skipped`. The orchestrator does not skip tasks on its own judgment.

**4. Resume behavior** (under `### 1. Initialize`, the paragraph starting "If resuming from notes..."):

Extend the existing resume paragraph. After "Skip completed phases." add: "When the source is a plan with task files, also read task file statuses. Tasks marked `complete` or `skipped` are not re-run, regardless of what the notes progress tracker shows. Task file status is authoritative for task-based phases."

### Step 4: Validate against spec

Use the Task tool with `subagent_type: general-purpose`. Prompt the agent to read the spec at `.lore/specs/lore-development/plan-breakdown.md` and review all three modified/created files:
- `lore-development/shared/frontmatter-schema.md`
- `lore-development/skills/plan-breakdown/SKILL.md`
- `lore-development/skills/implement/SKILL.md`

The agent should check each requirement (REQ-PBD-1 through REQ-PBD-14) against the implementation and report only requirements that are missing or incorrectly addressed. Capture findings in the implementation notes. If critical requirements are unmet, halt and escalate to user.

Additionally, run the `skill-reviewer` agent on both skill files (plan-breakdown and implement). It catches structural and consistency issues that spec-compliance validation misses. This step is not optional.

## Delegation Guide

No specialized expertise needed. All three steps are prompt writing (skill files) and documentation edits. The implementation agent should be `general-purpose` or the default implementation agent from the registry.

## Open Questions

- The spec says task files need frontmatter with status tracking. The implement skill currently records progress in the notes file. With task files, progress is tracked in two places (task file status + notes progress tracker). This is intentional per the spec (task status enables resume, notes enable retro), but worth confirming the dual tracking doesn't create confusion.
