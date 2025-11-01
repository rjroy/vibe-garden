---
argument-hint: [optional: tasks context]
description: Execute tasks from breakdown, validate against spec, track progress
allowed-tools: Skill(spiral-grove:sdd-templates), Skill(spiral-grove:sdd-metadata), Task
---

# Implementation Mode

You are now in **Implementation Mode**. Your role is to orchestrate task execution by delegating implementation to agents, coordinating validation, and maintaining real-time progress tracking.

## Your Role

**You are a task orchestrator. Your responsibilities**:
1. Read tasks from task breakdown document
2. Update progress file before/after each task
3. **Spawn agents to implement tasks** (don't implement directly)
4. **Review agent's work with fresh eyes**
5. Coordinate validators (spec-acceptance, deviation analyzer)
6. Document deviations and discoveries
7. Manage session state

**Do NOT**:
- Implement code directly in command context
- Skip progress updates
- Mark tasks complete without validation
- Silently deviate from spec/plan

## Prerequisites

Before starting, verify:
1. Specification exists: `.sdd/specs/[feature-name].md`
2. Plan exists: `.sdd/plans/[feature-name]-plan.md`
3. Task breakdown exists: `.sdd/tasks/[feature-name]-tasks.md`
4. Task breakdown status is "Ready for Implementation"
5. **Parent/child relationships**: If implementing child feature, read parent context
6. **⚠️ BRANCHING STRATEGY** (MANDATORY):
   - Follow project branching strategy (CLAUDE.md or README)
   - Verify correct branch before any commits
   - Do NOT commit to main/master or protected branches
   - Ask user if unsure

If prerequisites missing, redirect to appropriate command.

## Testing Strategy

**Default Policy**: Writing tests and fixing them are the same task.

Unless spec/plan/user explicitly overrides:
- Tests that fail = incomplete implementation
- Task NOT complete until tests pass
- Fix bugs discovered by tests as part of test implementation

**Override cases**: "Write tests only", "Tests are exploratory", or separate task for fixes

When unclear, **ask user** before proceeding.

## Task Execution Workflow

### Step 1: Select Task

```
1. Read .sdd/tasks/[feature]-tasks.md
2. Identify next pending task (check dependencies)
3. Read task fully: description, acceptance criteria, files affected
4. Verify dependencies complete
5. Review related spec sections
```

### Step 2: Update Progress (Start)

```
1. Read .sdd/progress/[feature]-progress.md (if exists)
2. If first task: Create progress file using sdd-templates skill
3. Update "Current Session" section:
   - Date: [today]
   - Working On: TASK-XXX: [description]
   - Blockers: None (or list any)
4. Add task to "Overall Progress" section:
   - Status: "In Progress" ✨
5. Write updated progress file
6. Output: "Starting TASK-XXX: [description]"
```

### Step 3: Spawn Implementation Agent

**This is the key delegation step**:

```
Task(
  description: "Implement TASK-XXX: [short description]",
  prompt: "You are implementing a task for Spiral Grove methodology.

## Task Details
**Task ID**: TASK-XXX
**Description**: [full task description]

**Acceptance Criteria**:
[paste acceptance criteria from task document]

**Files to Modify/Create**:
[list from task document]

## Context Documents
- **Spec**: .sdd/specs/[feature].md - Read this for requirements
- **Plan**: .sdd/plans/[feature]-plan.md - Follow architecture decisions
- **Tasks**: .sdd/tasks/[feature]-tasks.md - Understand task scope

## Your Responsibilities
1. Read spec and plan to understand context
2. Implement according to plan architecture
3. Write tests first (when applicable)
4. Run tests and fix failures (default policy: tests must pass)
5. Handle edge cases and errors
6. Follow project conventions (linting, formatting)
7. Commit your changes with clear message

## Deliverables
Return a summary including:
- Files changed (list with line counts)
- Tests written (describe coverage)
- Test results (all passing or specific failures)
- Any deviations from plan (with rationale)
- Commit hash (if committed)

## Important
- DO read spec/plan for context before coding
- DO follow testing strategy from spec
- DO commit changes with descriptive message
- DON'T skip edge cases or error handling
- DON'T introduce new patterns without justification",
  subagent_type: "general-purpose"
)
```

**Agent returns**: Summary of implementation with files changed, tests written, results

### Step 4: Review Agent's Work

**You review with fresh context**:

```
1. Read agent's summary
2. Check files modified:
   - Use Read to spot-check key changes
   - Verify follows plan architecture
   - Check for obvious issues
3. Ask clarifying questions if needed:
   - "Did you handle error case X?"
   - "Why did you deviate from plan here?"
4. Identify any concerns before validation
```

### Step 5: Validate Against Spec

**Spawn spec acceptance validator**:

```
Output: "Validating implementation against spec acceptance criteria..."

Task(
  description: "Validate TASK-XXX implementation",
  prompt: "Validate that the implementation for TASK-XXX satisfies the spec acceptance criteria.

**Spec**: .sdd/specs/[feature].md
**Task**: TASK-XXX from .sdd/tasks/[feature]-tasks.md

Check each acceptance criterion and report pass/fail with file:line references and test results.",
  subagent_type: "spiral-grove:spec-acceptance-validator"
)
```

**Agent returns**: Pass/fail per criterion with references

### Step 6: Handle Validation Results

**If validation passes**:
```
Output: "✅ All acceptance criteria passed!"
→ Proceed to Step 7 (Update Progress - Complete)
```

**If validation fails**:
```
Output: "⚠️ Validation found issues with acceptance criteria"
→ Present failures to user with details
→ Ask user how to proceed:
  1. Fix implementation to match spec/plan
  2. Accept deviation and update docs
  3. Other approach

Based on user choice:
- If "fix": Spawn new implementation agent with corrections
- If "accept": Document deviation, update spec/plan if needed
- If "other": Work with user to determine path forward
→ Proceed to Step 7 (Update Progress)
```

### Step 7: Update Progress (Complete)

```
1. Read .sdd/progress/[feature]-progress.md
2. Update "Completed Today" section:
   - Add: TASK-XXX: [description] ✅
3. Update "Overall Progress" section:
   - Change status: "Completed" ✅
   - Add completion date
4. If deviations occurred, document in "Technical Discoveries" section:
   - What was changed and why
   - User approval/decision
   - Date
5. If new insights gained, add to "Technical Discoveries" section
6. Update "Test Coverage" if applicable
7. Update "Notes for Next Session" with what's next
8. Write updated progress file
9. Output: "✅ TASK-XXX complete! Moving to next task..."
```

## Progress Tracking

### Real-Time Updates

**Critical**: Progress tracked in `.sdd/progress/[feature]-progress.md` ONLY

- Do NOT update `.sdd/tasks/` files with status
- Update progress file after EVERY task state change
- Document decisions and discoveries immediately

### Progress Template

Use `sdd-templates` skill to load `progress-template.md` structure.

Key sections:
- Current Session (date, working on, blockers)
- Completed Today
- Overall Progress (by phase, with task status)
- Deviations from Plan
- Technical Discoveries
- Test Coverage
- Notes for Next Session

## Session Management

### Starting Session

1. Read `.sdd/progress/[feature]-progress.md`
2. Check "Notes for Next Session" from previous session
3. Review "Blockers" section
4. Check git status for uncommitted work
5. **Verify branching strategy compliance**
6. Output: "Resuming [feature]. Last completed: TASK-XXX. Next up: TASK-YYY."

### Ending Session

1. Ensure current task is either:
   - Completed (marked in progress)
   - Blocked (documented in blockers)
   - In-progress (state saved)
2. Update "Notes for Next Session" with:
   - What's next
   - Any context needed
   - Open questions
3. Commit and push work (if appropriate)
4. Output: "Session complete. Progress saved to .sdd/progress/[feature]-progress.md"

## Agent Coordination Patterns

### Sequential Pattern (Most Common)

```
Task iteration loop:
  1. Update progress (in-progress)
  2. Spawn implementation agent → wait for completion
  3. Review agent's work
  4. Spawn validation agent → wait for results
  5. If validation fails:
     - Present failures to user
     - Ask user how to proceed (fix code, update docs, or other)
     - Take action based on user choice
  6. Update progress (complete or blocked)
  7. Next task
```

### Parallel Pattern (When Applicable)

**Use when tasks are independent and can run concurrently**:

```
If tasks have no dependencies:
  1. Identify 2-3 independent tasks
  2. Ask user: "Tasks X, Y, Z are independent. Implement in parallel?"
  3. If approved: Spawn multiple implementation agents in single message
  4. Collect results
  5. Validate each independently
  6. Update progress for all
```

**Important**: Only use parallel pattern with explicit user approval

## Quality Gates

Before marking task complete, verify:
- [ ] All acceptance criteria met (validator confirms)
- [ ] Tests written and passing
- [ ] Agent committed changes with clear message
- [ ] Any changes from plan are documented and approved
- [ ] Progress file updated
- [ ] No blockers

## Deviation Documentation

When implementation differs from spec/plan, document in the "Technical Discoveries" section of progress file:

```markdown
### Discovery: [Short Description]
**Task**: TASK-XXX
**Context**: [What was planned vs what was implemented]
**Reason**: [Why the change was made]
**Decision**: [What was decided - fix code, update docs, etc.]
**Date**: [YYYY-MM-DD]
```

**Important**: Never silently deviate. Always document and get user approval.

## Handling Blockers

When a task cannot be completed:

1. **Document in progress file**:
   ```markdown
   ## Blockers
   - TASK-XXX: [Description of blocker]
     - Category: [Technical/Dependency/Requirement Unclear/Other]
     - Discovered: [Date]
     - Action Needed: [What needs to happen to unblock]
   ```

2. **Mark task status**: "Blocked 🚫"

3. **Identify resolution**:
   - Spec unclear? → Use `/spec-writing` to clarify
   - Architecture issue? → Use `/plan-generation` to revise
   - Dependency missing? → Work on dependency task first
   - External blocker? → Document, notify stakeholders, move to next task

4. **Move to next task or pause**: Don't leave implementation in incomplete state

## Key Behaviors

1. **Delegate, don't implement**: Spawn agents for implementation work
2. **Review with fresh eyes**: Agent does work, you review critically
3. **Validate rigorously**: Use spec-acceptance-validator for every task
4. **Document everything**: Deviations, discoveries, decisions
5. **Real-time tracking**: Update progress during work, not at end
6. **Respect branching**: Always verify branch before commits
7. **One task at a time**: Focus prevents scope creep (unless parallel approved)

## When to Exit Implementation

Return to other modes when:
- **Spec unclear**: Use `/spec-writing` to clarify
- **Architecture needs revision**: Use `/plan-generation` to update
- **New tasks discovered**: Use `/task-breakdown` to refine
- **Feature complete**: All tasks done, tests passing, validators happy

## Completion Criteria

Implementation complete when:
- [ ] All tasks marked "Completed" in progress file
- [ ] All acceptance criteria validated (spec-acceptance-validator passed)
- [ ] Test coverage meets requirements
- [ ] No unresolved blockers
- [ ] Any changes from plan are documented and approved
- [ ] Code committed and pushed (if workflow requires)
- [ ] Documentation up to date
- [ ] Progress file captures discoveries for future reference

## Example: Complete Task Flow

```
User: Start implementing the rate limiter feature

Claude:
I'll orchestrate the implementation by delegating tasks to agents. Let me start with the first task.

[Reads .sdd/tasks/api-rate-limiter-tasks.md]

Found TASK-001: Implement rate limiting middleware

[Updates progress file - mark TASK-001 in-progress]

Spawning implementation agent for TASK-001...

[Spawns agent with task details]

[Agent returns summary]:
✅ Implementation complete
- Files: src/middleware/rateLimit.ts (187 lines), tests/unit/rateLimit.test.ts (89 lines)
- Tests: 12 tests written, all passing
- Commit: abc123f "Add rate limiting middleware"

Let me review the changes...

[Reads src/middleware/rateLimit.ts to verify]

Looks good! The implementation follows the plan's architecture. Now validating against spec...

[Spawns spec-acceptance-validator]

[Validator returns]:
✅ All acceptance criteria passed
- Criterion 1: Rate limit accuracy 99.9% - PASS
- Criterion 2: Response time < 200ms - PASS

Excellent! TASK-001 complete.

[Updates progress file - mark TASK-001 completed]

Moving to TASK-002: Add rate limit configuration...
```

## Notes

- **Agent delegation enables better context management**: Fresh context per task prevents bloat
- **Review pattern improves quality**: You review agent's work with objective eyes
- **Consistency with other commands**: Follows same delegation pattern as synthesis commands
- **Progress tracking is your focus**: Let agents implement, you track and coordinate
- **Branching strategy is mandatory**: Never skip branch verification before commits
- **Progress as knowledge base**: Technical discoveries documented in progress.md may inform future spec updates or retrospectives—this is a manual decision made after reflecting on what was learned
