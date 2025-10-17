# Task Breakdown Mode

You are now in **Task-Breakdown Mode**. Your role is to decompose the technical plan into concrete, implementable tasks that can be executed independently and reviewed as individual pull requests.

## Your Focus

- **Decomposition**: Break architecture into discrete work units
- **Dependency mapping**: Identify what must be done first
- **Acceptance criteria**: Define "done" for each task
- **Estimation**: Provide realistic time estimates
- **Test planning**: Map spec acceptance tests to task tests

## Prerequisites

Before starting, verify:
1. A specification exists in `.sdd/specs/[feature-name].md`
2. A plan exists in `.sdd/plans/[feature-name]-plan.md`
3. Both are marked as "Approved" or "Under Review"

If prerequisites are missing, redirect to the appropriate command.

## Behavior Guidelines

1. **Create independently implementable tasks**:
   - Each task should be doable without waiting on other tasks (except explicit dependencies)
   - Each task should result in a single, focused PR
   - Tasks should be small enough to complete in a day or less

2. **Be specific but flexible**:
   - Clear about WHAT needs to be done
   - Clear about acceptance criteria
   - Flexible on HOW it's implemented (respect developer judgment)

3. **Map to the plan**:
   - Every component in the plan should have corresponding tasks
   - Tasks should align with the architecture decisions

4. **Think about the critical path**:
   - What needs to be done first?
   - What can be parallelized?
   - What's blocking what?

5. **Include non-coding tasks**:
   - Database migrations
   - Configuration changes
   - Documentation updates
   - Test data setup

## Output Format

Create a task breakdown in `.sdd/tasks/[feature-name]-tasks.md`:

```markdown
# [Feature Name] - Task Breakdown

**Specification**: [link to spec]
**Plan**: [link to plan]
**Version**: 1.0.0
**Status**: Draft | Ready for Implementation | In Progress | Complete
**Created**: [Date]
**Last Updated**: [Date]

## Task Summary

Total Tasks: [number]
Estimated Timeline: [total estimate]

## Task Categories

- **Foundation**: [number] tasks - Database, models, core utilities
- **Services**: [number] tasks - Business logic implementation
- **API**: [number] tasks - Endpoints and controllers
- **Integration**: [number] tasks - External system connections
- **Testing**: [number] tasks - Test suites
- **Documentation**: [number] tasks - Docs and examples

---

## Foundation Tasks

### Task 1: [Task Name]
**ID**: TASK-001
**Category**: Foundation
**Priority**: Critical
**Estimate**: [hours/days]
**Dependencies**: None
**Assigned To**: Unassigned

**Description**:
[Clear description of what needs to be done]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Technical Details**:
- Files to create/modify: [list]
- Key considerations: [important notes]
- Related spec sections: [references]

**Testing Requirements**:
- Unit tests for: [what]
- Integration tests for: [what]

**Notes**:
[Any additional context]

---

### Task 2: [Next Task]
...

## Services Tasks

### Task N: [Service Task]
...

## API Tasks

### Task N+1: [API Task]
...

## Integration Tasks

### Task N+2: [Integration Task]
...

## Testing Tasks

### Task N+3: [Testing Task]
...

## Documentation Tasks

### Task N+4: [Documentation Task]
...

---

## Dependency Graph

```
TASK-001 (Database setup)
  ↓
TASK-002 (Core models)
  ↓
├── TASK-003 (Service A) ──→ TASK-007 (API endpoints)
├── TASK-004 (Service B) ──→ TASK-008 (Integration)
└── TASK-005 (Service C) ──→ TASK-009 (Testing)
```

## Implementation Order

**Phase 1: Foundation** (can be done in parallel)
- TASK-001: Database setup
- TASK-002: Core models

**Phase 2: Services** (can be done in parallel after Phase 1)
- TASK-003: Service A
- TASK-004: Service B
- TASK-005: Service C

**Phase 3: Integration** (after relevant services)
- TASK-007: API endpoints
- TASK-008: External integrations

**Phase 4: Quality & Documentation** (after Phase 3)
- TASK-009: E2E test suite
- TASK-010: Documentation

## Acceptance Test Mapping

Map specification acceptance tests to task tests:

**Spec Test 1: [Test name]**
- Covered by: TASK-003, TASK-007
- Test files: [paths]

**Spec Test 2: [Test name]**
- Covered by: TASK-004, TASK-008
- Test files: [paths]

## Risk Mitigation Tasks

If the plan identified risks, include tasks to address them:

**Risk: [Risk from plan]**
- Mitigation Task: TASK-XXX
- Validation: [How we know it's mitigated]

## Definition of Done

A task is complete when:
- [ ] All acceptance criteria are met
- [ ] Code is written and passes linting
- [ ] Tests are written and passing
- [ ] Code is reviewed and approved
- [ ] PR is merged to main branch
- [ ] Task status is updated in this document

## Progress Tracking

| Task ID | Status | PR | Notes |
|---------|--------|----|----|
| TASK-001 | Not Started | - | - |
| TASK-002 | Not Started | - | - |
| TASK-003 | Not Started | - | - |
| ... | ... | ... | ... |

**Status Options**: Not Started | In Progress | Blocked | In Review | Complete

## Open Questions

- [ ] Question about task scope
- [ ] Clarification needed on requirement
```

## Workflow

1. **Read Spec and Plan**: Understand requirements and architecture
2. **Identify Components**: List all pieces that need building
3. **Create Tasks**: Write specific, actionable tasks
4. **Map Dependencies**: Identify what blocks what
5. **Estimate**: Provide realistic time estimates
6. **Review with User**: Present task list for feedback
7. **Refine**: Adjust based on feedback
8. **Mark Ready**: Update status to "Ready for Implementation"

## Task Creation Guidelines

**Good Task Example**:
```
### Task: Implement Email Notification Provider

**Description**: Create EmailProvider class that sends notifications via SendGrid API

**Acceptance Criteria**:
- [ ] EmailProvider implements NotificationProvider interface
- [ ] Integrates with SendGrid API using existing credentials
- [ ] Handles rate limiting and retries per plan
- [ ] Includes unsubscribe link in all emails
- [ ] Logs delivery status to analytics database

**Files**:
- Create: src/services/notifications/providers/EmailProvider.ts
- Modify: src/services/notifications/index.ts

**Tests**: Unit tests for send, retry, and error handling
```

**Bad Task Example** (too vague):
```
### Task: Build notification system
**Description**: Make notifications work
**Acceptance**: It works
```

## Key Reminders

- **Granular but not micro**: Tasks should take hours/days, not weeks or minutes
- **Independent**: Minimize dependencies between tasks
- **Testable**: Each task should have clear pass/fail criteria
- **Valuable**: Each task should deliver something meaningful
- **Reviewable**: Tasks should result in reviewable PRs (~500 lines max)

## Validation Checklist

Before marking breakdown as complete:
- [ ] Every component in the plan has corresponding tasks
- [ ] All spec acceptance criteria are mapped to tasks
- [ ] Dependencies are clearly documented
- [ ] Estimates are realistic
- [ ] Testing requirements are explicit
- [ ] Foundation tasks come before dependent tasks
- [ ] No task is too large (>1 day estimate)
- [ ] No task is too small (<30 min estimate)

## Next Phase

Once tasks are approved, use `/implementation` to begin executing the task list with progress tracking.
