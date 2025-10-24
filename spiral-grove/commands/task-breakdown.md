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
4. **Check for parent/child relationships**:
   - If working on a child feature, verify parent spec and plan exist
   - Understand which specific child you're breaking down tasks for
   - Ensure directory structure mirrors the hierarchy

If prerequisites are missing, redirect to the appropriate command.

## Behavior Guidelines

**Conciseness Principle**:
This command prompt is intentionally detailed to guide you. **Do NOT mirror this verbosity in your output**. Your task breakdown should be:
- **Complete**: Clear deliverables, acceptance criteria, and enough detail to implement
- **Concise**: Remove redundant prose, not essential information
- **Scannable**: Clear section headers, bulleted lists over paragraphs
- **Actionable**: Focused on what to do, how to validate, and dependencies

**What to keep**:
- ✅ Clear deliverables (files to create/modify, features to implement)
- ✅ Specific acceptance criteria (how to know it's done)
- ✅ Dependencies and execution order
- ✅ Technical considerations for implementation

**What to remove**:
- ❌ Redundant task descriptions
- ❌ Verbose prose when bullets suffice
- ❌ Repeated patterns across similar tasks
- ❌ Implementation details better left to developer judgment
- ❌ **Progress tracking sections** - Progress is tracked in `.sdd/progress/` documents, not in task documents

Think: "Does an implementer have enough detail to complete this task and know when it's done?"

1. **Create independently implementable tasks**:
   - Each task should be doable without waiting on other tasks (except explicit dependencies)
   - Each task should result in a single, focused PR
   - Tasks should be small enough to complete in a day or less

2. **Be specific with clear acceptance criteria**:
   - Describe WHAT needs to be delivered (files, features, changes)
   - Include HOW details from the plan (architecture, algorithms, integration approach)
   - If uncertain about an approach, document it in Open Questions for review
   - Omit only trivial details (formatting preferences, exact wording of log messages)
   - Always include clear acceptance criteria (how to know the task is complete)

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

6. **Work incrementally and save often**:
   - Create the task breakdown in sections rather than all at once
   - Save after completing major sections (e.g., after Foundation Tasks, after Services Tasks, etc.)
   - This avoids API timeouts and allows for refinement as you identify dependencies
   - You can always edit and improve earlier sections as you work through later ones

7. **Task count reality check**:
   - Typical feature: 10-20 tasks (not 40+)
   - Each task: 2-8 hours of work (not 30 minutes, not 3 days)
   - **If you have >25 tasks, stop and check**:
     - Are tasks too granular? (Combine related work into single PRs)
     - Are you creating tasks for trivial helpers? (Skip these)
     - Should this use parent/child hierarchy instead?

8. **Final step - Consolidate redundancies**:
   - Review your task list before finalizing
   - Look for tasks that could be combined (e.g., "Create file X" + "Document file X" = one task)
   - Remove tasks for things that naturally happen together
   - Each task should deliver meaningful, testable value

## Output Format

Create a task breakdown in `.sdd/tasks/[feature-name]-tasks.md`.

**For parent/child hierarchies**: Mirror the spec directory structure:
- Parent tasks: `.sdd/tasks/parent-feature-tasks.md`
- Child tasks: `.sdd/tasks/parent-feature/child-a-tasks.md`, `.sdd/tasks/parent-feature/child-b-tasks.md`

**Template**:

```markdown
# [Feature Name] - Task Breakdown

**Specification**: [link to spec]
**Plan**: [link to plan]
**Status**: Draft | Ready for Implementation

## Task Summary
Total: [number] tasks, Estimated: [total hours/days]

## Tasks (organized by category as needed: Foundation, Services, API, Integration, Testing, Documentation)

### TASK-001: [Task Name]
**Category**: [category]
**Priority**: Critical | High | Medium | Low
**Estimate**: [hours]
**Dependencies**: [TASK-IDs or None]

**Description**: What needs to be done (1-2 sentences)

**Acceptance Criteria**:
- [ ] Specific, testable outcome 1
- [ ] Specific, testable outcome 2

**Files**: Create/modify [list]
**Testing**: [What to test]

---

[Repeat for each task]

## Dependency Graph (if helpful for complex features)
```
TASK-001 → TASK-002 → TASK-003
         └→ TASK-004
```

## Implementation Order
**Phase 1**: TASK-001, TASK-002 (can do in parallel)
**Phase 2**: TASK-003, TASK-004 (after Phase 1)

```

## Workflow

1. **Read spec and plan**: Understand requirements and architecture
2. **Check hierarchy**: If child, understand parent context and dependencies
3. **Identify components**: List all pieces to build
4. **Create tasks**: Write specific tasks in sections, save periodically
5. **Map dependencies**: Identify what blocks what
6. **Estimate**: Realistic time per task
7. **Review & refine**: Present for feedback, adjust
8. **Mark ready**: Update to "Ready for Implementation"

## Task Creation Guidelines

**Good Task Example**:
```
### TASK-005: Implement Email Notification Provider

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

**Testing**: Unit tests for send, retry, and error handling
```

**Bad Task Example** (too vague):
```
### Task: Build notification system
**Description**: Make notifications work
**Acceptance**: It works
```

## Key Reminders

- Tasks take hours/days (not weeks or minutes)
- Minimize dependencies between tasks
- Clear pass/fail criteria per task
- Reviewable PRs (~500 lines max)
- Mirror spec/plan hierarchy exactly
- **Do NOT include progress tracking** - That belongs in `.sdd/progress/` documents

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
