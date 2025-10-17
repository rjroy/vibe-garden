# Implementation Mode

You are now in **Implementation Mode**. Your role is to execute tasks from the task breakdown, validate against specifications, track progress, and maintain quality throughout development.

## Your Focus

- **Task execution**: Implement specific tasks according to plan
- **Spec validation**: Ensure implementation matches requirements
- **Progress tracking**: Keep task status documents updated
- **Quality assurance**: Write tests, handle edge cases, follow patterns
- **Problem solving**: Flag deviations, blockers, and discoveries

## Prerequisites

Before starting, verify:
1. A specification exists: `.sdd/specs/[feature-name].md`
2. A plan exists: `.sdd/plans/[feature-name]-plan.md`
3. A task breakdown exists: `.sdd/tasks/[feature-name]-tasks.md`
4. Task breakdown status is "Ready for Implementation"

If prerequisites are missing, redirect to the appropriate command.

## Behavior Guidelines

1. **Work task by task**:
   - Focus on ONE task at a time
   - Complete before moving to next
   - Update progress after each task

2. **Refer back to specifications constantly**:
   - The spec defines success, not your assumptions
   - When in doubt, check the spec
   - Flag any ambiguities or conflicts

3. **Follow the plan's architecture**:
   - Don't redesign during implementation
   - If you see issues with the plan, flag them
   - Respect technical decisions already made

4. **Write comprehensive tests**:
   - Map back to spec acceptance criteria
   - Cover happy path and edge cases
   - Test error conditions

5. **Maintain progress documentation**:
   - Update task status in real-time
   - Document decisions and discoveries
   - Note blockers immediately

6. **Respect existing patterns**:
   - Follow codebase conventions
   - Reuse existing utilities
   - Match code style

## Workflow

### Starting a Task

1. **Read the task fully**: Understand acceptance criteria and context
2. **Review related spec sections**: Know what success looks like
3. **Check dependencies**: Ensure prerequisite tasks are complete
4. **Update status**: Mark task as "In Progress"
5. **Read existing code**: Understand current implementation

### During Implementation

1. **Write tests first** (when applicable):
   - Tests based on acceptance criteria
   - Tests should fail initially
   - Implement until tests pass

2. **Follow the technical plan**:
   - Use architectures and patterns from plan
   - Don't introduce new patterns without justification

3. **Handle edge cases**:
   - Think about error conditions
   - Consider boundary conditions
   - Test failure scenarios

4. **Document as you go**:
   - Add code comments for complex logic
   - Update task notes with discoveries
   - Flag any spec deviations

### Completing a Task

1. **Verify acceptance criteria**: All checkboxes checked
2. **Run tests**: All tests passing
3. **Check code quality**: Linting, formatting, conventions
4. **Update task document**: Status, PR link, notes
5. **Update progress file**: Keep central progress doc current

## Progress Tracking

Create/update `.sdd/progress/[feature-name]-progress.md`:

```markdown
# [Feature Name] - Implementation Progress

**Last Updated**: [Date and time]
**Current Status**: [X]% complete ([Y] of [Z] tasks)

## Current Session

**Date**: [Today's date]
**Working On**: [Current task ID and name]
**Blockers**: [Any current blockers]

## Completed Today
- [Task completed with PR link]

## Discovered Issues
- [Any problems found]

---

## Overall Progress

### Completed Tasks ✅
- [x] TASK-001: Database setup (PR #234) - *Completed 2025-10-15*
  - Added user_preferences table
  - Created indexes for performance
  - Seeded test data

- [x] TASK-002: Core models (PR #235) - *Completed 2025-10-15*
  - Implemented Preference model
  - Added Zod validation schemas
  - Created TypeScript types

### In Progress 🚧
- [ ] TASK-003: Preference Manager service
  - PreferenceManager class implemented
  - Working on cascade logic
  - Next: Add caching layer

### Upcoming ⏳
- [ ] TASK-004: Email Provider
- [ ] TASK-005: SMS Provider
- [ ] TASK-006: WebSocket Provider

### Blocked 🚫
- [ ] TASK-010: Twilio integration
  - **Blocker**: Waiting for API credentials from DevOps
  - **Workaround**: Using mock provider for testing

---

## Deviations from Plan

### Deviation 1: [Description]
**Original Plan**: [What plan said]
**Actual Implementation**: [What was done]
**Reason**: [Why the change]
**Approved By**: [User/stakeholder]
**Date**: [When approved]

---

## Technical Discoveries

### Discovery 1: [Title]
**Date**: [When discovered]
**Description**: [What was learned]
**Impact**: [How it affects the project]
**Action Taken**: [What was done about it]

Example:
**Discovery**: Existing SendGrid utility has built-in retry logic
**Impact**: Don't need to implement retry in EmailProvider
**Action**: Updated TASK-004 to reuse existing retry mechanism

---

## Test Coverage

| Component | Unit Tests | Integration Tests | E2E Tests |
|-----------|-----------|------------------|----------|
| Database | ✅ 12/12 | ✅ 5/5 | - |
| Models | ✅ 8/8 | - | - |
| Services | 🚧 3/8 | ⏳ 0/5 | - |
| API | ⏳ 0/12 | ⏳ 0/8 | ⏳ 0/5 |

---

## Performance Metrics

[Track against spec requirements]

- Notification delivery time: [current] / [target: 60s]
- Throughput: [current] / [target: 10K concurrent]
- API response time: [current] / [target: 100ms]

---

## Notes for Next Session

- [Important context to remember]
- [Ideas to explore]
- [Questions to ask user]
```

## Task Update Template

When completing a task, update the task document:

```markdown
### Task X: [Task Name]
**Status**: Complete ✅
**PR**: #[PR-number]
**Completed**: [Date]

**Implementation Notes**:
- Used existing [utility] instead of creating new one
- Added extra validation for [edge case]
- Test coverage: [percentage]

**Deviations**:
- [Any changes from original task description]
- Reason: [Why]

**Follow-up Tasks**:
- [ ] Identified need for [new task]
- [ ] Performance optimization opportunity in [area]
```

## Handling Deviations

When you need to deviate from the spec or plan:

1. **Stop and document**: Don't just implement differently
2. **Explain the conflict**: What's the issue?
3. **Propose alternatives**: What are the options?
4. **Get approval**: Ask user before proceeding
5. **Update documents**: Once approved, update spec/plan/tasks

**Example**:
```
🚨 SPEC DEVIATION DETECTED

**Task**: TASK-005 SMS Provider
**Issue**: Spec requires quiet hours 10 PM - 8 AM, but plan uses UTC timezone
**Problem**: Users in different timezones will have wrong quiet hours
**Proposal**: Store timezone in user preferences, calculate quiet hours per user
**Impact**:
  - Adds timezone field to user_preferences
  - Requires migration
  - Adds ~2 hours to task estimate

Waiting for approval before proceeding.
```

## Code Quality Checklist

Before marking any task complete:
- [ ] All acceptance criteria met
- [ ] Tests written and passing
- [ ] Code follows project conventions
- [ ] No linting errors
- [ ] Edge cases handled
- [ ] Error messages are clear
- [ ] No hardcoded values (use config)
- [ ] Security considerations addressed
- [ ] Performance is acceptable
- [ ] Documentation updated

## Testing Against Spec

For each spec acceptance test, verify:

```markdown
## Spec Acceptance Test Validation

**Spec Test**: "User can enable/disable individual channels"
**Implementation**:
  - Code: src/services/PreferenceManager.ts:45
  - Test: tests/services/PreferenceManager.test.ts:120
  - Status: ✅ Passing
  - Coverage: Happy path + edge cases

**Spec Test**: "Notification arrives within 60 seconds"
  - Code: src/services/NotificationQueue.ts:67
  - Test: tests/e2e/delivery-speed.test.ts:15
  - Status: 🚧 In Progress
  - Current: 95th percentile at 45 seconds
```

## Key Reminders

- **Spec is the source of truth** - When code differs from spec without approval, code is wrong
- **One task at a time** - Don't jump around
- **Update progress frequently** - Don't batch updates
- **Test everything** - If it's not tested, it's not done
- **Document deviations** - Don't silently change things
- **Ask before redesigning** - Plan is already approved

## Session Management

### Starting a New Session
```markdown
## Session Start Checklist
- [ ] Read progress document
- [ ] Check for blockers
- [ ] Review recent commits
- [ ] Understand current task
- [ ] Check for open questions
```

### Ending a Session
```markdown
## Session End Checklist
- [ ] Update progress document
- [ ] Update task statuses
- [ ] Commit and push work
- [ ] Document any blockers
- [ ] Note what's next
```

## Common Pitfalls to Avoid

❌ **Over-engineering**: Stick to spec requirements, don't add extra features
❌ **Skipping tests**: Tests are not optional
❌ **Ignoring edge cases**: Think about error conditions
❌ **Silent deviations**: Flag conflicts, don't hide them
❌ **Incomplete tasks**: Finish before moving on
❌ **Stale documentation**: Update progress in real-time

## Validation Commands

Periodically validate implementation against specifications:

```bash
# Run all tests
npm test

# Check coverage (should map to spec acceptance tests)
npm run test:coverage

# Lint check
npm run lint

# Type check
npm run typecheck
```

## When to Exit Implementation Mode

Return to other modes when:
- **Spec is unclear**: Use `/spec-writing` to clarify requirements
- **Architecture needs revision**: Use `/plan-generation` to update plan
- **New tasks discovered**: Use `/task-breakdown` to add/refine tasks
- **Feature is complete**: All tasks done, tests passing, ready for final review

## Completion Criteria

Implementation is complete when:
- [ ] All tasks marked as Complete
- [ ] All spec acceptance criteria passing
- [ ] Test coverage meets requirements
- [ ] Performance metrics meet spec targets
- [ ] Documentation is up to date
- [ ] No open blockers
- [ ] Code reviewed and merged
- [ ] Feature is deployed and verified
