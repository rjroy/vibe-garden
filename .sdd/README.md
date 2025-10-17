# Spec-Driven Development (SDD) Directory

This directory contains all artifacts for features developed using the Spec-Driven Development methodology.

## Directory Structure

```
.sdd/
├── specs/          # Feature specifications (the "what")
├── plans/          # Technical plans (the "how")
├── tasks/          # Task breakdowns (the "steps")
├── progress/       # Implementation progress tracking
└── README.md       # This file
```

## The SDD Workflow

Spec-Driven Development follows a four-phase approach:

### 1. Specification Phase
**Command**: `/spec-writing`
**Output**: `.sdd/specs/[feature-name].md`

Define WHAT to build:
- User stories and stakeholders
- Success criteria (measurable)
- Functional and non-functional requirements
- Explicit constraints (what NOT to build)
- Acceptance tests

### 2. Planning Phase
**Command**: `/plan-generation`
**Output**: `.sdd/plans/[feature-name]-plan.md`

Define HOW to build it:
- Architecture and component design
- Technical decisions with rationale
- Integration points
- Data models and API contracts
- Risk assessment

### 3. Task Breakdown Phase
**Command**: `/task-breakdown`
**Output**: `.sdd/tasks/[feature-name]-tasks.md`

Break down into STEPS:
- Discrete, independent tasks
- Dependencies and order
- Acceptance criteria per task
- Time estimates
- Test requirements

### 4. Implementation Phase
**Command**: `/implementation`
**Output**: Code + `.sdd/progress/[feature-name]-progress.md`

Execute and track:
- Implement tasks one by one
- Validate against specs
- Track progress and discoveries
- Document deviations
- Maintain test coverage

## Document Lifecycle

### Specification
- **Draft**: Initial creation, under discussion
- **Under Review**: Awaiting stakeholder approval
- **Approved**: Ready for planning
- **Superseded**: Replaced by newer version

### Plan
- **Draft**: Initial architecture, under discussion
- **Under Review**: Awaiting technical approval
- **Approved**: Ready for task breakdown
- **Updated**: Modified based on implementation discoveries

### Tasks
- **Draft**: Initial breakdown, needs refinement
- **Ready for Implementation**: Approved, ready to work
- **In Progress**: Being actively implemented
- **Complete**: All tasks done

### Progress
- **Updated continuously** during implementation
- Archive when feature is complete

## File Naming Convention

- **Specs**: `[feature-name].md` (e.g., `notification-system.md`)
- **Plans**: `[feature-name]-plan.md` (e.g., `notification-system-plan.md`)
- **Tasks**: `[feature-name]-tasks.md` (e.g., `notification-system-tasks.md`)
- **Progress**: `[feature-name]-progress.md` (e.g., `notification-system-progress.md`)

Use kebab-case for consistency.

## Getting Started

### For a New Feature

1. Start with `/spec-writing`:
   ```
   /spec-writing
   ```
   Describe the feature you want to build. Claude will help you create a comprehensive specification.

2. Once spec is approved, move to `/plan-generation`:
   ```
   /plan-generation
   ```
   Claude will explore your codebase and design the technical architecture.

3. When plan is approved, use `/task-breakdown`:
   ```
   /task-breakdown
   ```
   Claude will create an ordered list of implementable tasks.

4. Finally, begin `/implementation`:
   ```
   /implementation
   ```
   Claude will execute tasks and track progress.

### For an Existing Feature

If you have existing specifications or plans, you can jump into any phase:

```
# Continue working on tasks
/implementation

# Refine the task breakdown
/task-breakdown

# Revise the technical plan
/plan-generation

# Update the specification
/spec-writing
```

## Best Practices

### Do
- ✅ Keep specs focused on requirements, not implementation
- ✅ Document technical decisions with rationale in plans
- ✅ Make tasks small and independent
- ✅ Update progress documents frequently
- ✅ Map tests to spec acceptance criteria
- ✅ Version your specifications when they change

### Don't
- ❌ Skip phases (each builds on the previous)
- ❌ Make silent deviations from specs
- ❌ Create tasks without a plan
- ❌ Start implementation without clear acceptance criteria
- ❌ Let progress documents get stale

## Document Templates

Templates for each phase are embedded in the slash commands:
- `/spec-writing` - Specification template
- `/plan-generation` - Plan template
- `/task-breakdown` - Task breakdown template
- `/implementation` - Progress tracking template

## Integration with Claude Code

These commands are designed to work seamlessly with Claude Code's features:
- **Repo Grokking**: Claude explores your codebase during planning
- **Multi-file editing**: Claude implements tasks across multiple files
- **Test execution**: Validates implementation against specs
- **Git integration**: Creates focused PRs per task

## Cross-Referencing

Documents should reference each other:

**Specs** ← referenced by → **Plans**
**Plans** ← referenced by → **Tasks**
**Tasks** ← referenced by → **Progress**

Example:
```markdown
# Feature Plan

**Specification**: [notification-system.md](../specs/notification-system.md)
```

This creates a traceable path from requirements → architecture → implementation.

## Tips for Success

1. **Be thorough in the spec**: Time spent here saves implementation time
2. **Explore the codebase**: Let Claude analyze existing patterns during planning
3. **Review before proceeding**: Get feedback on specs and plans before breaking down tasks
4. **Track deviations**: Document why implementation differs from plan
5. **Keep specs alive**: Update them as you learn during implementation

## Examples

See the guide document for a complete walkthrough:
- `A Practical Guide to Spec-Driven Development.md`

This guide includes a full example of building a notification system using SDD.

## Questions?

Each slash command includes detailed guidance and templates. Just invoke the command and Claude will guide you through the process.

For general help with Claude Code:
```
/help
```
