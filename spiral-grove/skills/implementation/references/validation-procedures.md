# Implementation Validation Procedures

Detailed procedures for the four quality gates in the implementation loop.

## Gate 1: IMPLEMENT - Agent Prompts

### First Iteration: Full Implementation

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
```

### Subsequent Iterations: Targeted Fixes

```
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

## Gate 2: TEST - Procedures

### Test Execution

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
     Output: "All tests passing. Proceeding to code review..."
     → Gate 3: REVIEW

   ELSE:
     Output: "Test failures detected:
     [List failures with file:line references]

     Re-entering loop to fix..."

     Increment iteration counter
     IF iteration >= 3:
       Output: "3+ iterations without passing tests.
       How would you like to proceed?
       1. Continue fixing (may need different approach)
       2. Skip tests temporarily (document as tech debt)
       3. Pause and investigate root cause together"
       → Wait for user decision
     ELSE:
       → Gate 1: IMPLEMENT (with test failures as issues to fix)
```

## Gate 3: REVIEW - Procedures

### Orchestrator Spot-Check

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

### Agent Selection Priority

```
1. Check for specialized reviewer agents:
   - Language-specific: cpp-code-reviewer, rust-code-reviewer, python-code-reviewer
   - Domain-specific: security-reviewer, performance-reviewer, api-reviewer
   - Check project CLAUDE.md for preferred reviewer

2. If specialized agent exists:
   Output: "Spawning [agent-name] for specialized code review..."
   Use specialized subagent_type

3. If no specialized agent:
   Output: "Spawning general-purpose code reviewer..."
   Use "general-purpose" subagent_type
```

### Code Review Agent Prompt

```
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
5. **Performance**: Algorithms efficient? Resource usage reasonable?
6. **Testing**: Coverage adequate? Tests meaningful? Edge cases tested?
7. **Conventions**: Project style adhered to? Naming clear?

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
  subagent_type: "[specialized-agent-name or general-purpose]"
)
```

### Review Results Handling

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
   Output: "Code review approved! Proceeding to spec validation..."
   → Gate 4: VALIDATE

3. IF Assessment is "Concerns" (major issues):
   Output: "Code review found major concerns. How would you like to proceed?
   1. Fix issues now (re-enter loop)
   2. Accept and document (add to Technical Discoveries)
   3. Discuss specific concerns"

   Based on user choice:
   - If "fix": Increment iteration, handle 3+ check, → Gate 1 → Gate 2
   - If "accept": Document concerns → Gate 4: VALIDATE
   - If "discuss": Work with user → User decides path forward

4. IF Assessment is "Reject" (blockers):
   Output: "Code review found blocking issues:
   [List blockers]

   These must be fixed before proceeding."

   Increment iteration, handle 3+ check, → Gate 1 → Gate 2
```

## Gate 4: VALIDATE - Procedures

### Spec Acceptance Validation

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

### Validation Results Handling

```
IF all acceptance criteria pass:
  Output: "All acceptance criteria passed! All quality gates clear."
  → EXIT LOOP → Completion Phase

ELSE (validation fails):
  Output: "Validation found issues with acceptance criteria:
  [List failures with details]

  How would you like to proceed?
  1. Fix implementation to match spec/plan (re-enter loop)
  2. Accept deviation and update docs
  3. Other approach"

  Based on user choice:
  - If "fix":
      Increment iteration, handle 3+ check
      → Gate 1: IMPLEMENT (with validation failures)
      → Gate 2: TEST
      → Gate 3: REVIEW
  - If "accept":
      Document deviation in progress file
      Update spec/plan if needed
      → EXIT LOOP → Completion Phase
  - If "other":
      Work with user to determine path forward
```

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

### Parallel Pattern (When Applicable)

**Use when tasks are independent and can run concurrently:**

```
If tasks have no dependencies:
  1. Identify 2-3 independent tasks
  2. Ask user: "Tasks X, Y, Z are independent. Implement in parallel?"
  3. If approved: Spawn multiple implementation agents in single message
  4. Collect results
  5. Run each through Quality Gate Loop independently
  6. Update progress for all
```

**Important**: Only use parallel pattern with explicit user approval.

## Quality Gates Summary

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

## Progress Validator Invocation

```
Output: "Validating progress documentation quality..."

Task(
  description: "Validate progress documentation",
  prompt: "Validate .sdd/progress/[feature]-progress.md in silent mode.

**Context**: Just completed TASK-XXX
**Task Reference**: .sdd/tasks/[feature]-tasks.md

**Focus on**:
- Deviations documented with specific rationale
- Completion evidence present (PR numbers, files modified, test results)
- Test coverage tracked accurately
- Status accuracy (percentages match task counts)

**Invocation Mode**: Silent mode

Return concise inline suggestions focusing on:
- Missing or weak deviation rationale
- Incomplete completion evidence for TASK-XXX
- Test coverage tracking gaps
- Status accuracy issues",
  subagent_type: "spiral-grove:progress-validator"
)
```

**Handle Results:**
- If no issues: "Progress documentation looks good!" → Proceed
- If suggestions: Present to user, offer to fix inline or note for later
- Non-blocking: Always proceed to next task regardless of findings

## Example: Complete Task Flow

```
User: Start implementing the rate limiter feature

Claude:
Orchestrating implementation by delegating tasks to agents.

=== SETUP ===
[Reads .sdd/tasks/api-rate-limiter-tasks.md]
Found TASK-001: Implement rate limiting middleware
[Updates progress file - TASK-001 in-progress, iteration=1]

Starting TASK-001: Implement rate limiting middleware

=== QUALITY GATE LOOP (Iteration 1) ===

--- Gate 1: IMPLEMENT ---
Spawning implementation agent for TASK-001...
[Agent returns]:
- Files: src/middleware/rateLimit.ts (187 lines)
- Tests: tests/unit/rateLimit.test.ts (89 lines)

--- Gate 2: TEST ---
Running tests (iteration 1)...
Test failures detected:
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
All 12 tests passing. Proceeding to code review...

--- Gate 3: REVIEW ---
Spawning code reviewer...
[Reviewer returns]:
**Assessment**: Concerns
**Issues**:
  - Major: Race condition in distributed mode

Code review found major concerns. Proceed?
1. Fix issues now
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
All 12 tests passing (including new race condition test)

--- Gate 3: REVIEW ---
Spawning code reviewer...
**Assessment**: Approve
**Positives**: Race condition properly addressed

Code review approved! Proceeding to spec validation...

--- Gate 4: VALIDATE ---
Validating against spec acceptance criteria (iteration 3)...
All acceptance criteria passed

=== EXIT LOOP - ALL GATES PASSED ===

=== COMPLETION ===
Committing changes...
[Commits: abc123f "Implement TASK-001: rate limiting middleware"]

[Updates progress file]:
- TASK-001: Completed
- Commit: abc123f
- Iterations: 3

Validating progress documentation quality...
[Progress validator]: Looks good!

TASK-001 complete! (3 iterations) Moving to TASK-002...
```
