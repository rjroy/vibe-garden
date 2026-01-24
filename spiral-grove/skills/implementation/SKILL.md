---
name: implementation
description: This skill should be used when the user asks to "implement tasks", "start coding", "execute the plan", "begin implementation", or invokes /spiral-grove:implementation. Executes SDD Phase 4 by orchestrating task execution through agent delegation, validation, and progress tracking.
allowed-tools: Skill(spiral-grove:sdd-templates), Skill(spiral-grove:sdd-metadata), Task
---

# Implementation

Execute SDD Phase 4: Orchestrate task execution by delegating implementation to agents, coordinating validation, and maintaining real-time progress tracking.

## Role

**You are a task orchestrator. Responsibilities:**
1. Read tasks from task breakdown document
2. Update progress file before/after each task
3. **Spawn agents to implement tasks** (don't implement directly)
4. **Review agent's work with fresh eyes**
5. **Coordinate validators** (code reviewer, spec-acceptance, progress quality)
6. Document deviations and discoveries
7. Manage session state

**Do NOT:**
- Implement code directly in skill context
- Skip progress updates
- Mark tasks complete without validation
- Silently deviate from spec/plan

## Argument Handling

**If arguments provided** (e.g., `@.sdd/tasks/feature-tasks.md`):
- Use referenced file as task breakdown document
- Skip task discovery
- Extract feature name from file path

**If no arguments:**
- List available task files in `.sdd/tasks/`
- Ask user which feature to implement
- Or continue with previously in-progress work (check progress files)

## Prerequisites

Before starting, verify:

1. Specification exists: `.sdd/specs/[feature-name].md`
2. Plan exists: `.sdd/plans/[feature-name]-plan.md`
3. Task breakdown exists: `.sdd/tasks/[feature-name]-tasks.md`
4. Task breakdown status is "Ready for Implementation"
5. **Parent/child relationships**: If implementing child, read parent context
6. **BRANCHING STRATEGY** (MANDATORY):
   - Follow project branching strategy (CLAUDE.md or README)
   - Verify correct branch before any commits
   - Do NOT commit to main/master or protected branches

If prerequisites missing, redirect to appropriate skill.

## Testing Strategy

**Default Policy**: Writing tests and fixing them are the same task.

Unless spec/plan/user explicitly overrides:
- Tests that fail = incomplete implementation
- Task NOT complete until tests pass
- Fix bugs discovered by tests as part of test implementation

When unclear, **ask user** before proceeding.

## Task Execution Loop

Implementation is a **loop**, not linear steps. Any code change requires re-validation.

```
TASK EXECUTION

SETUP: Select Task → Update Progress (Start)
                        │
                        ▼
    ┌─────────────────────────────────────────┐
    │           QUALITY GATE LOOP              │
    │                                          │
    │   ┌──────────────┐                      │
    │   │ 1. IMPLEMENT │◄─────────────┐       │
    │   └──────┬───────┘              │       │
    │          │                      │       │
    │          ▼                      │       │
    │   ┌──────────────┐              │       │
    │   │   2. TEST    │── fail ──────┤       │
    │   └──────┬───────┘              │       │
    │          │ pass                 │       │
    │          ▼                      │       │
    │   ┌──────────────┐              │       │
    │   │  3. REVIEW   │── reject ────┤       │
    │   └──────┬───────┘              │       │
    │          │ approve              │       │
    │          ▼                      │       │
    │   ┌──────────────┐              │       │
    │   │ 4. VALIDATE  │── fail ──────┘       │
    │   └──────┬───────┘                      │
    │          │ pass                         │
    │          ▼                              │
    │       EXIT LOOP                         │
    └─────────────────────────────────────────┘
                        │
                        ▼
COMPLETION: Update Progress → Validate Progress → Next Task
```

**Key Principle**: Any code change restarts from TEST. No exceptions.

**Iteration Limit**: If loop executes 3+ times without progress, escalate to user.

## Setup Phase

### Select Task

1. Identify tasks file (from argument or ask user)
2. Identify next pending task (check dependencies)
3. Read task fully: description, acceptance criteria, files
4. Verify dependencies complete
5. Review related spec sections

### Update Progress (Start)

1. Read/create `.sdd/progress/[feature]-progress.md`
2. Update "Current Session" section:
   - Date, Working On, Blockers, Loop Iteration: 1
3. Add task to "Overall Progress" section: Status "In Progress"
4. Write progress file
5. Output: "Starting TASK-XXX: [description]"

## Quality Gate Loop

Track iteration count. If iteration >= 3, pause and ask user.

For detailed gate implementation procedures, see **references/validation-procedures.md**.

### Gate 1: IMPLEMENT

Spawn implementation agent (or fix agent on subsequent iterations):

```
Task(
  description: "Implement TASK-XXX: [short description]",
  prompt: "[Full task context with spec/plan references]",
  subagent_type: "general-purpose"
)
```

Agent returns summary of implementation/fixes.

### Gate 2: TEST

Run tests for affected code:
- Unit tests for modified files
- Integration tests if applicable
- Linting/formatting checks

**If all pass**: Proceed to Gate 3
**If failures**: Increment iteration, return to Gate 1 with failures to fix

### Gate 3: REVIEW

First, spot-check key changes yourself. Then spawn code reviewer:

```
Task(
  description: "Review TASK-XXX implementation quality",
  prompt: "[Implementation summary with spec/plan context]",
  subagent_type: "[specialized-reviewer or general-purpose]"
)
```

Check for specialized reviewers first (language-specific, domain-specific).

**Assessment handling**:
- **Approve/Minor**: Proceed to Gate 4
- **Concerns/Major**: Ask user to fix or accept
- **Reject/Blockers**: Must fix, return to Gate 1

### Gate 4: VALIDATE

Spawn spec acceptance validator:

```
Task(
  description: "Validate TASK-XXX implementation",
  prompt: "Check acceptance criteria against implementation",
  subagent_type: "spiral-grove:spec-acceptance-validator"
)
```

**If all criteria pass**: Exit loop
**If failures**: Ask user to fix implementation or accept deviation

## Completion Phase

### Commit Changes

Only after all quality gates pass:

1. Stage all modified files
2. Commit with clear message including task ID and iteration count
3. Output commit hash

### Update Progress (Complete)

1. Update "Completed Today" section with task, commit hash, iterations
2. Update "Overall Progress" section: Status "Completed"
3. Document deviations in "Technical Discoveries" if any
4. Update "Test Coverage" if applicable
5. Update "Notes for Next Session"
6. Write progress file

### Validate Progress Quality

Spawn progress validator (non-blocking):

```
Task(
  description: "Validate progress documentation",
  prompt: "Check .sdd/progress/[feature]-progress.md for quality",
  subagent_type: "spiral-grove:progress-validator"
)
```

Address suggestions inline or note for later. Always proceed to next task.

## Progress Tracking

**Critical**: Track in `.sdd/progress/[feature]-progress.md` ONLY

- Do NOT update `.sdd/tasks/` files with status
- Update progress file after EVERY task state change
- Document decisions and discoveries immediately

Use `sdd-templates` skill for progress template structure.

## Session Management

### Starting Session

1. Read progress file
2. Check "Notes for Next Session"
3. Review "Blockers" section
4. Check git status for uncommitted work
5. Verify branching strategy compliance
6. Output: "Resuming [feature]. Last completed: TASK-XXX. Next: TASK-YYY."

### Ending Session

1. Ensure current task is completed, blocked, or state saved
2. Update "Notes for Next Session"
3. Commit and push if appropriate
4. Output: "Session complete. Progress saved."

## Deviation Documentation

When implementation differs from spec/plan:

```markdown
### Discovery: [Short Description]
**Task**: TASK-XXX
**Context**: [Planned vs implemented]
**Reason**: [Why the change]
**Decision**: [What was decided]
**Date**: [YYYY-MM-DD]
```

**Never silently deviate. Always document and get user approval.**

## Handling Blockers

When task cannot be completed:

1. Document in progress file with category and action needed
2. Mark task status: "Blocked"
3. Identify resolution path:
   - Spec unclear? → `/spiral-grove:spec-writing`
   - Architecture issue? → `/spiral-grove:plan-generation`
   - Dependency missing? → Work on dependency first
4. Move to next task or pause

## Key Behaviors

1. **Implementation is a loop**: Any code change requires re-testing and re-review
2. **Delegate, don't implement**: Spawn agents for implementation work
3. **Review with fresh eyes**: Agent does work, you review critically
4. **Four quality gates**: IMPLEMENT → TEST → REVIEW → VALIDATE
5. **Commit after gates pass**: Never commit mid-loop
6. **Track iterations**: Record loop cycles per task
7. **Escalate at 3 iterations**: Involve user before continuing
8. **Document everything**: Deviations, discoveries, decisions
9. **Real-time tracking**: Update progress during work
10. **Respect branching**: Always verify branch before commits
11. **One task at a time**: Focus prevents scope creep
12. **Use specialized reviewers**: Check for project-specific agents

## When to Exit Implementation

Return to other skills when:
- **Spec unclear**: `/spiral-grove:spec-writing`
- **Architecture revision needed**: `/spiral-grove:plan-generation`
- **New tasks discovered**: `/spiral-grove:task-breakdown`
- **Feature complete**: All tasks done, validators happy

## Completion Criteria

- [ ] All tasks marked "Completed" in progress file
- [ ] All acceptance criteria validated
- [ ] Test coverage meets requirements
- [ ] No unresolved blockers
- [ ] Deviations documented and approved
- [ ] Code committed and pushed
- [ ] Documentation up to date
- [ ] Progress file captures discoveries

## Additional Resources

For detailed gate implementation procedures and agent prompt templates, see **references/validation-procedures.md**.
