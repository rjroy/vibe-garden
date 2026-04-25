---
title: "Implementation notes: plan-breakdown"
date: 2026-02-10
status: complete
tags: [implementation, notes]
source: .lore/work/plans/plan-breakdown.md
modules: [lore-development]
---

# Implementation Notes: Plan Breakdown Skill

## Progress
- [x] Phase 1: Add task type to frontmatter schema
- [x] Phase 2: Create plan-breakdown skill
- [x] Phase 3: Modify implement skill to consume task files
- [x] Phase 4: Validate against spec

## Log

### Phase 1: Add task type to frontmatter schema
- Dispatched: Add task row to status table, task-specific fields section, and task example to frontmatter-schema.md
- Result: Three targeted additions made cleanly. Task type with `pending`/`complete`/`skipped` statuses, `source` and `sequence` fields documented, example added.
- Review: Verified inline. Follows existing patterns (Notes-Specific Fields section, example format). No issues.

### Phase 2: Create plan-breakdown skill
- Dispatched: Create lore-development/skills/plan-breakdown/SKILL.md following prep-plan and implement as style references, plugin-dev skill development guidance for structure
- Result: Skill created with frontmatter (third-person description, trigger phrases), When to Use/Skip, Input, Rejection Gate, Decomposition, Output (inline task template), User Review, Relationship to Other Skills, What Plan-Breakdown Adds sections
- Review: Background review agent checked all 8 requirements (PBD-1,2,3,4,6,7,12,14). All covered. Found missing lore-researcher invocation (structural gap vs siblings). Fixed by adding lore-researcher step to Input section.
- Resolution: Added lore-researcher invocation after plan/spec loading.

### Phase 3: Modify implement skill to consume task files
- Dispatched: Four targeted additions to implement/SKILL.md (input table footnote, task file detection subsection, task file phase behavior, resume extension)
- Result: All four additions placed correctly. Existing content preserved. Task file detection with staleness check, phase list from sequence field, scope-restricted agent prompts, status updates, and authoritative task file status for resume.
- Review: Verified inline. Additions integrate cleanly at specified locations.

### Phase 4: Validate against spec
- Dispatched: Spec compliance agent (REQ-PBD-1 through 14) and skill-reviewer on both skills
- Spec compliance: All 14 requirements covered. All 10 success criteria addressed. No gaps.
- Skill review (plan-breakdown): Pass. Three fixes applied: (1) description changed to third person throughout, (2) lore-researcher usage made imperative instead of descriptive, (3) staleness check mention added to Relationship section.
- Skill review (implement): Two major findings fixed: (1) "work already done" skip path now requires user confirmation via AskUserQuestion, aligning with escalation rules and "does not skip without user confirmation" principle. (2) Skipped tasks now have defined progress tracker representation and log entry guidance.

## Summary

Built plan-breakdown skill (new) and modified implement skill (existing) across 3 files plus frontmatter schema. Four phases, all passed. Two review cycles caught structural issues: missing lore-researcher invocation in plan-breakdown, and skipped-task handling gaps in implement. Both addressed.
