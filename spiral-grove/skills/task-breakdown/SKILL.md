---
name: task-breakdown
description: This skill should be used when the user asks to "break down tasks", "create task list", "decompose the plan", "what tasks do we need", or invokes /spiral-grove:task-breakdown. Executes SDD Phase 3 to decompose technical plans into discrete, implementable tasks.
allowed-tools: Skill(spiral-grove:sdd-templates), Skill(spiral-grove:sdd-metadata)
---

# Task Breakdown

Execute SDD Phase 3: Decompose technical plans into concrete, implementable tasks executable as independent pull requests.

## Focus Areas

- **Decomposition**: Break architecture into discrete work units
- **Dependency mapping**: Identify what must be done first
- **Acceptance criteria**: Define "done" for each task
- **Complexity sizing**: Rate each task using t-shirt sizes (S/M/L preferred)
- **Test planning**: Map spec acceptance tests to task tests

## Prerequisites

Before starting, verify:

1. Specification exists in `.sdd/specs/[feature-name].md`
2. Plan exists in `.sdd/plans/[feature-name]-plan.md`
3. Both marked as "Approved" or "Under Review"
4. **Check for parent/child relationships**:
   - If working on child feature, verify parent spec and plan exist
   - Understand which specific child is being broken down
   - Ensure directory structure mirrors hierarchy

If prerequisites missing, redirect to appropriate skill.

## Argument Handling

If arguments provided (plan context):
- Use referenced plan as source
- Skip plan discovery

If no arguments:
- List available plans in `.sdd/plans/`
- Ask user which plan to break down

## Behavior Guidelines

### Conciseness Principle

Task breakdowns should be:
- **Complete**: Clear deliverables, acceptance criteria, implementation detail
- **Concise**: Remove redundant prose, not essential information
- **Scannable**: Clear section headers, bulleted lists
- **Actionable**: Focused on what to do, how to validate, dependencies

**What to keep**:
- Clear deliverables (files to create/modify, features to implement)
- Specific acceptance criteria (how to know it's done)
- Dependencies and execution order
- Technical considerations for implementation

**What to remove**:
- Redundant task descriptions
- Verbose prose when bullets suffice
- Repeated patterns across similar tasks
- **Progress tracking sections** (tracked in `.sdd/progress/`, not task documents)

Target: "Does implementer have enough detail to complete this and know when done?"

### Core Behaviors

1. **Create independently implementable tasks**:
   - Each task doable without waiting on others (except explicit dependencies)
   - Each task results in single, focused PR
   - Tasks small enough to complete in a day or less

2. **Be specific with clear acceptance criteria**:
   - Describe WHAT needs to be delivered (files, features, changes)
   - Include HOW details from plan (architecture, algorithms, integration)
   - Document uncertain approaches in Open Questions
   - Omit only trivial details (formatting preferences, exact log wording)

3. **Map to plan**: Every plan component should have corresponding tasks

4. **Think about critical path**:
   - What must be done first?
   - What can be parallelized?
   - What blocks what?

5. **Include non-coding tasks**:
   - Database migrations
   - Configuration changes
   - Documentation updates
   - Test data setup

6. **Work incrementally**: Save after completing major task groups

7. **Task count reality check**:
   - Typical feature: 10-20 tasks (not 40+)
   - Each task: S/M/L complexity (not XS/trivial, not XL/XXL/epic)
   - **If >25 tasks, stop and check**:
     - Are tasks too granular? (Combine related work)
     - Creating tasks for trivial helpers? (Skip these)
     - Should this use parent/child hierarchy?

8. **Consolidate redundancies** before finalizing:
   - Look for tasks that could combine (e.g., "Create file X" + "Document file X")
   - Remove tasks for things that naturally happen together
   - Each task should deliver meaningful, testable value

## Output Format

Create task breakdown in `.sdd/tasks/[feature-name]-tasks.md`

Filename format: `YYYY-MM-DD-[feature-name]-tasks.md`

For parent/child hierarchies:
- Parent: `.sdd/tasks/parent-feature-tasks.md`
- Children: `.sdd/tasks/parent-feature/child-a-tasks.md`

### Template and Metadata

1. Invoke `Skill(spiral-grove:sdd-templates)` to read `templates/tasks-template.md`
2. Invoke `Skill(spiral-grove:sdd-metadata)` to populate frontmatter

## Task Format Example

**Good Task**:
```markdown
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

**Bad Task** (too vague):
```markdown
### Task: Build notification system
**Description**: Make notifications work
**Acceptance**: It works
```

## Workflow

1. **Read spec and plan**: Understand requirements and architecture
2. **Check hierarchy**: If child, understand parent context and dependencies
3. **Identify components**: List all pieces to build
4. **Create tasks**: Write specific tasks in sections, save periodically
5. **Map dependencies**: Identify what blocks what
6. **Size complexity**: Rate each task S/M/L
7. **Review & refine**: Present for feedback, adjust
8. **Mark ready**: Update to "Ready for Implementation"

## Validation

Before marking breakdown complete:

- [ ] Every plan component has corresponding tasks
- [ ] All spec acceptance criteria mapped to tasks
- [ ] Dependencies clearly documented
- [ ] Complexity ratings appropriate (S/M/L)
- [ ] Testing requirements explicit
- [ ] Foundation tasks come before dependent tasks
- [ ] No task too large (XL/XXL must be broken down)
- [ ] No task too small (XS must be consolidated)
- [ ] **Tasks validator spawned and passed**

### Validator Agent

After drafting, ALWAYS spawn the tasks-validator agent:

```
Task(
  description: "Validate task breakdown",
  prompt: "Validate the tasks at [path]",
  subagent_type: "spiral-grove:tasks-validator"
)
```

Address any issues before marking complete.

## Key Reminders

- Tasks should be S/M/L complexity (not XS/trivial, not XL/XXL/epic)
- Minimize dependencies between tasks
- Clear pass/fail criteria per task
- Reviewable PRs (~500 lines max)
- Mirror spec/plan hierarchy exactly
- **Do NOT include progress tracking** (belongs in `.sdd/progress/`)

## Next Phase

Once tasks approved, invoke `/spiral-grove:implementation` to begin execution with progress tracking.
