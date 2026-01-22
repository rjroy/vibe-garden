---
argument-hint: "[optional: tasks context]"
description: Execute tasks from breakdown, validate against spec, track progress
allowed-tools: Skill(spiral-grove:sdd-templates), Skill(spiral-grove:sdd-metadata), Task
---

# Implementation Mode

You are now in **Implementation Mode**. Your role is to orchestrate task execution by delegating implementation to agents, coordinating validation, and maintaining real-time progress tracking.

$ARGUMENTS

## Argument Handling

**If arguments provided** (e.g., `/implementation @.sdd/tasks/feature-tasks.md`):
- Use the referenced file as the task breakdown document
- Skip task discovery - work directly with the provided file
- Extract feature name from the file path for related spec/plan/progress files

**If no arguments provided**:
- List available task files in `.sdd/tasks/`
- Ask user which feature to implement
- Or continue with previously in-progress work (check progress files)

## Your Role

**You are a task orchestrator. Your responsibilities**:
1. Read tasks from task breakdown document
2. Update progress file before/after each task
3. **Spawn agents to implement tasks** (don't implement directly)
4. **Review agent's work with fresh eyes**
5. **Coordinate validators** (code reviewer, spec-acceptance, progress quality)
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

## Task Execution Loop

Implementation is a **loop**, not linear steps. Any code change requires re-validation.

```
┌─────────────────────────────────────────────────────────────┐
│                    TASK EXECUTION                           │
│                                                             │
│  SETUP: Select Task → Update Progress (Start)               │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              QUALITY GATE LOOP                       │   │
│  │                                                      │   │
│  │   ┌──────────────┐                                  │   │
│  │   │ 1. IMPLEMENT │◄─────────────────────────┐       │   │
│  │   └──────┬───────┘                          │       │   │
│  │          │                                  │       │   │
│  │          ▼                                  │       │   │
│  │   ┌──────────────┐                          │       │   │
│  │   │   2. TEST    │──── fail ────────────────┤       │   │
│  │   └──────┬───────┘                          │       │   │
│  │          │ pass                             │       │   │
│  │          ▼                                  │       │   │
│  │   ┌──────────────┐                          │       │   │
│  │   │  3. REVIEW   │──── reject/concerns ─────┤       │   │
│  │   └──────┬───────┘                          │       │   │
│  │          │ approve                          │       │   │
│  │          ▼                                  │       │   │
│  │   ┌──────────────┐                          │       │   │
│  │   │ 4. VALIDATE  │──── fail ────────────────┘       │   │
│  │   └──────┬───────┘                                  │   │
│  │          │ pass                                     │   │
│  │          ▼                                          │   │
│  │       EXIT LOOP                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  COMPLETION: Update Progress (Complete) → Validate Progress │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle**: Any code change restarts from TEST. No exceptions.

**Iteration Limit**: If loop executes 3+ times without progress, escalate to user for guidance.

---

## Setup Phase

### Select Task

```
1. Identify tasks file:
   - If argument provided: Use the referenced tasks file directly
   - If no argument: Read .sdd/tasks/[feature]-tasks.md (ask user if multiple exist)
2. Identify next pending task (check dependencies)
3. Read task fully: description, acceptance criteria, files affected
4. Verify dependencies complete
5. Review related spec sections
```

### Update Progress (Start)

```
1. Read .sdd/progress/[feature]-progress.md (if exists)
2. If first task: Create progress file using sdd-templates skill
3. Update "Current Session" section:
   - Date: [today]
   - Working On: TASK-XXX: [description]
   - Blockers: None (or list any)
   - Loop Iteration: 1
4. Add task to "Overall Progress" section:
   - Status: "In Progress" ✨
5. Write updated progress file
6. Output: "Starting TASK-XXX: [description]"
```

---

## Quality Gate Loop

Track iteration count. If iteration ≥ 3, pause and ask user how to proceed.

### Gate 1: IMPLEMENT

**Spawn implementation agent** (or fix agent on subsequent iterations):

```
# First iteration: Full implementation
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
4. Handle edge cases and errors
5. Follow project conventions (linting, formatting)
6. DO NOT commit yet (commit happens after all gates pass)

## Deliverables
Return a summary including:
- Files changed (list with line counts)
- Tests written (describe coverage)
- Any deviations from plan (with rationale)

## Important
- DO read spec/plan for context before coding
- DO follow testing strategy from spec
- DON'T skip edge cases or error handling
- DON'T introduce new patterns without justification
- DON'T commit until all quality gates pass",
  subagent_type: "general-purpose"
)

# Subsequent iterations: Targeted fixes
Task(
  description: "Fix TASK-XXX: [issue from previous gate]",
  prompt: "You are fixing issues found during quality gate validation.

## Issues to Fix
[List specific issues from TEST, REVIEW, or VALIDATE gate]

## Context
- **Previous implementation**: [summary from last iteration]
- **Gate that failed**: [TEST/REVIEW/VALIDATE]
- **Iteration**: [N]

## Your Responsibilities
1. Fix ONLY the identified issues
2. Do not introduce unrelated changes
3. Ensure fix doesn't break existing functionality

## Deliverables
- Files changed
- How each issue was addressed
- Any concerns about the fix",
  subagent_type: "general-purpose"
)
```

**Agent returns**: Summary of implementation/fixes

**Next**: → Gate 2: TEST

---

### Gate 2: TEST

**Run tests and verify they pass**:

```
Output: "Running tests (iteration [N])..."

1. Run test suite for affected code:
   - Unit tests for modified files
   - Integration tests if applicable
   - Linting/formatting checks

2. Collect results:
   - Tests passed: [count]
   - Tests failed: [count]
   - Linting errors: [count]

3. Evaluate results:
   IF all tests pass AND no linting errors:
     Output: "✅ All tests passing. Proceeding to code review..."
     → Gate 3: REVIEW

   ELSE:
     Output: "❌ Test failures detected:
     [List failures with file:line references]

     Re-entering loop to fix..."

     Increment iteration counter
     IF iteration ≥ 3:
       Output: "⚠️ 3+ iterations without passing tests.
       How would you like to proceed?
       1. Continue fixing (may need different approach)
       2. Skip tests temporarily (document as tech debt)
       3. Pause and investigate root cause together"
       → Wait for user decision
     ELSE:
       → Gate 1: IMPLEMENT (with test failures as issues to fix)
```

**Next**: → Gate 3: REVIEW (only if tests pass)

---

### Gate 3: REVIEW

**Orchestrator spot-check**:

```
1. Read agent's summary
2. Check files modified:
   - Use Read to spot-check key changes
   - Verify follows plan architecture
   - Check for obvious issues
3. Ask clarifying questions if needed:
   - "Did you handle error case X?"
   - "Why did you deviate from plan here?"
4. Identify any concerns before formal review
```

**Spawn code quality reviewer**:

```
Output: "Reviewing code quality..."

# Agent Selection (priority order):

1. Check for specialized reviewer agents:
   - Language-specific: cpp-code-reviewer, rust-code-reviewer, python-code-reviewer
   - Domain-specific: security-reviewer, performance-reviewer, api-reviewer
   - Check project CLAUDE.md for preferred reviewer

2. If specialized agent exists:
   Output: "Spawning [agent-name] for specialized code review..."
   Task(
     description: "Review TASK-XXX implementation quality",
     prompt: "Review the implementation for TASK-XXX focusing on [domain].

     **Implementation**: [summary from Step 3]
     **Files**: [files changed]
     **Spec**: .sdd/specs/[feature].md
     **Plan**: .sdd/plans/[feature]-plan.md

     Assess: architecture, code quality, security, error handling, performance, conventions.
     Return: Assessment (Approve/Concerns/Reject), Issues (by severity), Suggestions, Positives.",
     subagent_type: "[specialized-agent-name]"
   )

3. If no specialized agent:
   Output: "Spawning general-purpose code reviewer..."
   Task(
     description: "Review TASK-XXX implementation quality",
     prompt: "You are reviewing implementation code quality for Spiral Grove methodology.

## Implementation Summary
**Task**: TASK-XXX
**Files Changed**: [list from implementation agent]
**Tests**: [test results]
**Deviations**: [any reported by implementation agent]

## Context Documents
- **Spec**: .sdd/specs/[feature].md - Read for requirements
- **Plan**: .sdd/plans/[feature]-plan.md - Read for architecture decisions
- **Task**: TASK-XXX from .sdd/tasks/[feature]-tasks.md

## Review Focus
1. **Architecture**: Follows plan decisions? Appropriate patterns?
2. **Code Quality**: Readable? Maintainable? Follows project conventions?
3. **Security**: Input validation? Auth/authz? Injection risks (SQL, XSS, command)?
4. **Error Handling**: Edge cases covered? Graceful failures? Clear error messages?
5. **Performance**: Algorithms efficient? Resource usage reasonable? Unnecessary work avoided?
6. **Testing**: Coverage adequate? Tests meaningful? Edge cases tested?
7. **Conventions**: Project style adhered to? Naming clear? Patterns consistent?

## Deliverables
**Assessment**: Approve | Concerns | Reject
**Issues**: [Categorized by severity]
  - Blocker: Must fix before proceeding (security, correctness, architecture violation)
  - Major: Should fix (maintainability, conventions, missing edge cases)
  - Minor: Nice-to-have (style, naming, optimization opportunities)
**Suggestions**: [Constructive improvements with rationale]
**Positives**: [What was done well - be specific]

## Guidelines
- Read the actual implementation files to assess quality
- Consider spec/plan context for architectural alignment
- Be constructive, not just critical
- Distinguish blockers from nice-to-haves
- Focus on maintainability, correctness, and security
- Highlight good practices observed",
     subagent_type: "general-purpose"
   )
```

**Agent returns**: Assessment with issues categorized by severity

**Handle review results**:

```
1. Present review findings to user:
   Output: "Code Review Results (iteration [N]):

   **Assessment**: [Approve/Concerns/Reject]

   **Issues Found**:
   [List issues by severity with details]

   **Suggestions**:
   [List improvement suggestions]

   **Positives**:
   [What was done well]"

2. IF Assessment is "Approve" or minor concerns only:
   Output: "✅ Code review approved! Proceeding to spec validation..."
   → Gate 4: VALIDATE

3. IF Assessment is "Concerns" (major issues):
   Output: "Code review found major concerns. How would you like to proceed?
   1. Fix issues now (re-enter loop)
   2. Accept and document (add to Technical Discoveries)
   3. Discuss specific concerns"

   Based on user choice:
   - If "fix":
       Increment iteration counter
       IF iteration ≥ 3:
         Output: "⚠️ 3+ iterations. Consider different approach?"
         → Wait for user guidance
       ELSE:
         → Gate 1: IMPLEMENT (with review issues to fix)
         → Gate 2: TEST (must re-test after any code change)
   - If "accept": Document concerns in progress file → Gate 4: VALIDATE
   - If "discuss": Work with user to resolve → User decides path forward

4. IF Assessment is "Reject" (blockers):
   Output: "⚠️ Code review found blocking issues:
   [List blockers]

   These must be fixed before proceeding."

   Increment iteration counter
   IF iteration ≥ 3:
     Output: "⚠️ 3+ iterations with blockers. Need to reassess approach."
     → Wait for user guidance
   ELSE:
     → Gate 1: IMPLEMENT (with blockers to fix)
     → Gate 2: TEST (must re-test after any code change)
```

**Next**: → Gate 4: VALIDATE (only if review approved)

---

### Gate 4: VALIDATE

**Spawn spec acceptance validator**:

```
Output: "Validating against spec acceptance criteria (iteration [N])..."

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

```
IF all acceptance criteria pass:
  Output: "✅ All acceptance criteria passed! All quality gates clear."
  → EXIT LOOP → Completion Phase

ELSE (validation fails):
  Output: "⚠️ Validation found issues with acceptance criteria:
  [List failures with details]

  How would you like to proceed?
  1. Fix implementation to match spec/plan (re-enter loop)
  2. Accept deviation and update docs
  3. Other approach"

  Based on user choice:
  - If "fix":
      Increment iteration counter
      IF iteration ≥ 3:
        Output: "⚠️ 3+ iterations. Spec/implementation mismatch may need discussion."
        → Wait for user guidance
      ELSE:
        → Gate 1: IMPLEMENT (with validation failures to fix)
        → Gate 2: TEST (must re-test after any code change)
        → Gate 3: REVIEW (must re-review after any code change)
  - If "accept":
      Document deviation in progress file
      Update spec/plan if needed
      → EXIT LOOP → Completion Phase
  - If "other":
      Work with user to determine path forward
```

**Loop Exit**: Only when all gates pass OR user explicitly accepts deviation

---

## Completion Phase

### Commit Changes

**Only commit after all quality gates pass**:

```
Output: "All quality gates passed. Committing changes..."

1. Stage all modified files
2. Create commit with clear message:
   "Implement TASK-XXX: [description]

   - [Summary of changes]
   - Tests: [pass count] passing
   - Iterations: [N]"
3. Output commit hash
```

### Update Progress (Complete)

```
1. Read .sdd/progress/[feature]-progress.md
2. Update "Completed Today" section:
   - Add: TASK-XXX: [description] ✅
   - Commit: [hash]
   - Iterations: [N]
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

### Validate Progress Quality

**Spawn progress validator to check documentation quality**:

```
Output: "Validating progress documentation quality..."

Task(
  description: "Validate progress documentation",
  prompt: "Validate .sdd/progress/[feature]-progress.md in silent mode.

**Context**: Just completed TASK-XXX
**Task Reference**: .sdd/tasks/[feature]-tasks.md

**Focus on**:
- Deviations documented with specific rationale (not vague like 'changed approach')
- Completion evidence present (PR numbers, files modified, test results)
- Test coverage tracked accurately (not vague like 'mostly tested')
- Status accuracy (percentages match task counts)

**Invocation Mode**: Silent mode

Return concise inline suggestions focusing on:
- Missing or weak deviation rationale
- Incomplete completion evidence for TASK-XXX
- Test coverage tracking gaps
- Status accuracy issues

Use silent mode format: brief warnings with actionable fixes, not full report.",
  subagent_type: "spiral-grove:progress-validator"
)
```

**Agent returns**: Inline suggestions (warnings only)

**Handle Results**:

```
1. If no issues found:
   Output: "Progress documentation looks good!"
   → Proceed to next task

2. If suggestions returned:
   Output: "Progress Validation Suggestions:
   [List suggestions from validator]

   Would you like me to:
   1. Fix inline now (add missing details)
   2. Note for later
   3. Skip (accept as-is)"

   Based on user choice:
   - If "fix inline": Update progress file with missing details → Continue
   - If "note for later": Add to "Notes for Next Session" → Continue
   - If "skip": Continue without changes

3. Non-blocking: Always proceed to next task regardless of findings
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

### Quality Gate Loop Pattern (Default)

```
Per-task execution:

SETUP:
  1. Select next pending task
  2. Update progress (in-progress, iteration=1)

QUALITY GATE LOOP:
  iteration = 1
  WHILE NOT all_gates_passed:

    Gate 1 - IMPLEMENT:
      IF iteration == 1:
        Spawn implementation agent (full task)
      ELSE:
        Spawn fix agent (targeted fixes for failed gate)

    Gate 2 - TEST:
      Run tests
      IF tests fail:
        iteration++
        IF iteration >= 3: escalate to user
        CONTINUE (back to Gate 1)

    Gate 3 - REVIEW:
      Spawn code reviewer
      IF blockers OR (concerns AND user chooses fix):
        iteration++
        IF iteration >= 3: escalate to user
        CONTINUE (back to Gate 1)

    Gate 4 - VALIDATE:
      Spawn spec validator
      IF fails AND user chooses fix:
        iteration++
        IF iteration >= 3: escalate to user
        CONTINUE (back to Gate 1)

    all_gates_passed = TRUE

COMPLETION:
  1. Commit changes
  2. Update progress (complete, iterations=N)
  3. Spawn progress validator (non-blocking)
  4. Next task
```

**Key insight**: Any code change requires re-running ALL subsequent gates (TEST → REVIEW → VALIDATE).

### Parallel Pattern (When Applicable)

**Use when tasks are independent and can run concurrently**:

```
If tasks have no dependencies:
  1. Identify 2-3 independent tasks
  2. Ask user: "Tasks X, Y, Z are independent. Implement in parallel?"
  3. If approved: Spawn multiple implementation agents in single message
  4. Collect results
  5. Run each through Quality Gate Loop independently
  6. Update progress for all
```

**Important**: Only use parallel pattern with explicit user approval

## Quality Gates Summary

All four gates must pass before task completion:

| Gate | Check | Pass Condition |
|------|-------|----------------|
| **1. IMPLEMENT** | Code written | Agent returns implementation summary |
| **2. TEST** | Tests pass | All tests green, no lint errors |
| **3. REVIEW** | Code quality | Reviewer approves (or concerns accepted) |
| **4. VALIDATE** | Spec compliance | All acceptance criteria pass (or deviation accepted) |

**Loop invariant**: Any code change → restart from Gate 2 (TEST)

**Completion checklist** (after all gates pass):
- [ ] All four gates passed (or deviations documented)
- [ ] Changes committed with clear message
- [ ] Progress file updated with completion evidence
- [ ] Iteration count recorded
- [ ] Progress documentation quality checked (non-blocking)

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

1. **Implementation is a loop**: Any code change requires re-testing and re-review
2. **Delegate, don't implement**: Spawn agents for implementation work
3. **Review with fresh eyes**: Agent does work, you review critically
4. **Four quality gates**: IMPLEMENT → TEST → REVIEW → VALIDATE (all must pass)
5. **Commit after gates pass**: Never commit mid-loop; only after all gates clear
6. **Track iterations**: Record how many loop cycles each task required
7. **Escalate at 3 iterations**: If stuck, involve user before continuing
8. **Document everything**: Deviations, discoveries, decisions
9. **Real-time tracking**: Update progress during work, not at end
10. **Respect branching**: Always verify branch before commits
11. **One task at a time**: Focus prevents scope creep (unless parallel approved)
12. **Use specialized reviewers**: Check for project-specific code review agents

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

## Example: Complete Task Flow (with Loop Iteration)

```
User: Start implementing the rate limiter feature

Claude:
I'll orchestrate the implementation by delegating tasks to agents.

=== SETUP ===
[Reads .sdd/tasks/api-rate-limiter-tasks.md]
Found TASK-001: Implement rate limiting middleware
[Updates progress file - mark TASK-001 in-progress, iteration=1]

Starting TASK-001: Implement rate limiting middleware

=== QUALITY GATE LOOP (Iteration 1) ===

--- Gate 1: IMPLEMENT ---
Spawning implementation agent for TASK-001...
[Agent returns]:
- Files: src/middleware/rateLimit.ts (187 lines), tests/unit/rateLimit.test.ts (89 lines)

--- Gate 2: TEST ---
Running tests (iteration 1)...
❌ Test failures detected:
  - rateLimit.test.ts:45 - "should handle burst traffic" FAILED
  - rateLimit.test.ts:67 - "should reset after window" FAILED

Re-entering loop to fix...

=== QUALITY GATE LOOP (Iteration 2) ===

--- Gate 1: IMPLEMENT (fix mode) ---
Spawning fix agent with test failures...
[Agent returns]:
- Fixed timing issue in burst traffic handler
- Corrected window reset logic

--- Gate 2: TEST ---
Running tests (iteration 2)...
✅ All 12 tests passing. Proceeding to code review...

--- Gate 3: REVIEW ---
Spawning code reviewer...
[Reviewer returns]:
**Assessment**: Concerns
**Issues**:
  - Major: Race condition in distributed mode (security concern)

Code review found major concerns. How would you like to proceed?
1. Fix issues now (re-enter loop)
2. Accept and document
3. Discuss

User: Fix issues now

=== QUALITY GATE LOOP (Iteration 3) ===

--- Gate 1: IMPLEMENT (fix mode) ---
Spawning fix agent with race condition issue...
[Agent returns]:
- Added mutex lock for distributed counter updates

--- Gate 2: TEST ---
Running tests (iteration 3)...
✅ All 12 tests passing (including new race condition test)

--- Gate 3: REVIEW ---
Spawning code reviewer...
[Reviewer returns]:
**Assessment**: Approve
**Positives**: Race condition properly addressed with mutex

✅ Code review approved! Proceeding to spec validation...

--- Gate 4: VALIDATE ---
Validating against spec acceptance criteria (iteration 3)...
[Validator returns]:
✅ All acceptance criteria passed

=== EXIT LOOP - ALL GATES PASSED ===

=== COMPLETION ===
All quality gates passed. Committing changes...
[Commits: abc123f "Implement TASK-001: rate limiting middleware"]

[Updates progress file]:
- TASK-001: Completed ✅
- Commit: abc123f
- Iterations: 3

Validating progress documentation quality...
[Progress validator]: Looks good!

✅ TASK-001 complete! (3 iterations) Moving to TASK-002...
```

## Notes

- **Loop structure prevents incomplete validation**: Any code change triggers full re-validation (TEST → REVIEW → VALIDATE)
- **Iteration tracking surfaces process issues**: High iteration counts indicate unclear specs or complex edge cases
- **3-iteration escalation prevents thrashing**: If stuck, involve user rather than spinning indefinitely
- **Commit at end, not during**: Keeps git history clean; only committed code has passed all gates
- **Agent delegation enables better context management**: Fresh context per task prevents bloat
- **Review pattern improves quality**: You review agent's work with objective eyes
- **Consistency with other commands**: Follows same delegation pattern as synthesis commands
- **Progress tracking is your focus**: Let agents implement, you track and coordinate
- **Branching strategy is mandatory**: Never skip branch verification before commits
- **Progress as knowledge base**: Technical discoveries documented in progress.md may inform future spec updates or retrospectives—this is a manual decision made after reflecting on what was learned
