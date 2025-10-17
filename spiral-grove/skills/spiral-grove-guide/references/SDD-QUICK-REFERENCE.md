# Spec-Driven Development - Quick Reference

## Commands

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `/spec-writing` | Define requirements | Feature idea | `.sdd/specs/[feature].md` |
| `/plan-generation` | Design architecture | Approved spec | `.sdd/plans/[feature]-plan.md` |
| `/task-breakdown` | Create task list | Approved plan | `.sdd/tasks/[feature]-tasks.md` |
| `/implementation` | Execute & track | Task list | Code + `.sdd/progress/[feature]-progress.md` |

## Phase Flow

```
┌─────────────────┐
│  /spec-writing  │  Define WHAT to build
└────────┬────────┘
         │ Spec approved
         ↓
┌─────────────────┐
│ /plan-generation│  Design HOW to build
└────────┬────────┘
         │ Plan approved
         ↓
┌─────────────────┐
│ /task-breakdown │  Break into STEPS
└────────┬────────┘
         │ Tasks ready
         ↓
┌─────────────────┐
│ /implementation │  BUILD and TRACK
└─────────────────┘
```

## Quick Decision Tree

**"I have a feature idea"** → `/spec-writing`

**"I have an approved spec"** → `/plan-generation`

**"I have a technical plan"** → `/task-breakdown`

**"I have a task list"** → `/implementation`

**"I'm implementing and confused"** → Check the spec and plan

**"The spec is unclear"** → `/spec-writing` (to update)

**"The architecture needs changing"** → `/plan-generation` (to revise)

**"Tasks need adjusting"** → `/task-breakdown` (to refine)

## Key Principles

### Specification Phase
- Focus on **requirements**, not solutions
- Make success criteria **measurable**
- Be explicit about **constraints** (DO NOTs)
- Think about **stakeholders** and **acceptance tests**

### Planning Phase
- **Explore the codebase** before designing
- Document **technical decisions** with rationale
- Consider **integration points** and **risks**
- Design for the **whole system** (data, errors, security, testing)

### Task Breakdown Phase
- Create **independent, testable** tasks
- Keep tasks **small** (< 1 day each)
- Map tasks to **spec acceptance criteria**
- Identify **dependencies** clearly

### Implementation Phase
- Work **one task at a time**
- **Refer to the spec** constantly
- **Update progress** frequently
- **Test everything**
- **Document deviations** immediately

## Common Workflows

### Starting Fresh
```
/spec-writing → /plan-generation → /task-breakdown → /implementation
```

### Updating Requirements
```
/spec-writing (update spec) → /plan-generation (revise plan)
```

### Architecture Change
```
/plan-generation (update plan) → /task-breakdown (update tasks)
```

### Adding Tasks
```
/task-breakdown (refine tasks) → /implementation (continue)
```

## Red Flags

🚩 **Writing code during spec-writing** - Too early!
🚩 **Skipping codebase exploration in planning** - You'll miss existing patterns
🚩 **Tasks taking > 1 day** - Break them down further
🚩 **Implementing without tests** - Tests are not optional
🚩 **Deviating from spec silently** - Flag and discuss first
🚩 **Stale progress docs** - Update in real-time

## Document Status Flow

```
Spec:  Draft → Under Review → Approved → [Superseded]
Plan:  Draft → Under Review → Approved → [Updated]
Tasks: Draft → Ready for Implementation → In Progress → Complete
```

## File Locations

```
.sdd/
├── specs/          # Specifications
├── plans/          # Technical plans
├── tasks/          # Task breakdowns
└── progress/       # Progress tracking
```

## When to Use SDD vs. Quick Prompts

### Use SDD for:
- Production features
- Multi-file implementations
- Team projects
- Long-running work
- Compliance-sensitive code

### Use quick prompts for:
- Bug fixes
- Simple utilities
- UI tweaks
- Prototypes
- One-off scripts

## Checklist for Quality

**Before moving to next phase:**
- [ ] Current document is complete
- [ ] Status is approved/ready
- [ ] Stakeholders have reviewed
- [ ] Open questions are resolved

**Before marking task complete:**
- [ ] Acceptance criteria met
- [ ] Tests written and passing
- [ ] Code reviewed
- [ ] Progress doc updated
- [ ] No blockers remaining

## Emergency Procedures

**"I'm stuck on implementation"**
1. Check the spec - what does success look like?
2. Check the plan - what's the architecture?
3. Check the task - what's the acceptance criteria?
4. Ask for clarification

**"The spec and code conflict"**
1. Stop implementing
2. Document the conflict
3. Propose a solution
4. Get approval
5. Update spec/plan/tasks
6. Continue

**"I found a major architecture issue"**
1. Stop and document the problem
2. Return to `/plan-generation`
3. Revise the plan
4. Update affected tasks
5. Continue implementation

## Tips

- **Specs are living documents** - Update them as you learn
- **Plans can be revised** - Architecture isn't set in stone
- **Tasks can be added** - Discovery is part of the process
- **Progress docs are for you** - Make them useful for resuming work
- **Tests are guardrails** - They keep you aligned with specs

## Remember

> Spec-Driven Development frontloads clarity to enable autonomous execution.

The time spent in planning pays dividends in implementation speed and quality.
