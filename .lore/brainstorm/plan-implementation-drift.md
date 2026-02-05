---
title: Plan-Implementation Drift
date: 2026-02-02
status: open
tags: [workflow, plan-mode, spec-drift, validation, context-management]
modules: [lore-development]
---

# Plan-Implementation Drift

## Problem

Plans drift ~10% from specs. Implementation happens at peak context load, compounding the drift. By the time "done" is declared, the result diverges from what the spec actually specified.

## Observed Failure Mode

1. Spec is written with clear requirements
2. `prep-plan` loads context, enters plan mode
3. Plan mode explores (Explore agent) and plans (Plan agent)
4. Plan gets it 90% right but introduces subtle drift
5. "Clear Context and implement" pastes plan into fresh context
6. Implementation follows the drifted plan, not the spec
7. At peak context load, quality degrades further
8. Result is "meh" - technically complete but missing the point

## Root Causes

**Spec reference without reading**: Plans include links to specs but don't instruct implementation to actually read them. "See spec at X" without "read the spec at X."

**Main context implementation**: Tasks execute in the main context window where accumulated work creates noise. Each task adds to the pile.

**No validation checkpoint**: Implementation ends when tasks are done, not when spec requirements are verified.

## Proposed Solution

Update `prep-plan` to instruct plan mode to include three mandatory elements:

### 1. Spec Reference (with read instruction)

Plans must include the spec path AND make reading it the first implementation step.

```markdown
## Spec Reference
Spec: `.lore/specs/feature-name.md`

**First step**: Read the spec file before beginning implementation.
```

### 2. Implementation Approach (sub-agents)

Plans must mandate sub-agent usage for implementation phases to conserve context.

```markdown
## Implementation Approach
Each phase should be implemented using a sub-agent with fresh context.
Sub-agents receive: relevant spec section + specific task description.
This prevents context accumulation from degrading quality.
```

### 3. Validation Step (explicit)

Plans must end with a validation task that re-reads the spec.

```markdown
## Final Task: Validation
Launch a fresh-context sub-agent to:
1. Read the spec file
2. Review the implementation
3. Compare against each requirement
4. Flag any gaps or drift before declaring complete
```

## Why This Works

- **Clear context benefit preserved**: "Clear Context and implement" still works, plan carries the instructions
- **Spec is source of truth**: Implementation reads the actual spec, not a summary of it
- **Fresh context per phase**: Sub-agents don't inherit accumulated noise
- **Validation catches drift**: Fresh-context sub-agent compares implementation to spec without accumulated bias

## Open Questions

- Will plan mode reliably include these sections if instructed?
- Is there value in the plan quoting key requirements verbatim as a checksum?

## Next Steps

If this holds up: update `prep-plan` skill to include these instructions when entering plan mode.
