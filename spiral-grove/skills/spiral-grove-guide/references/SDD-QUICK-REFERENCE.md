# Spec-Driven Development - Quick Reference

**Purpose**: Practical cheat sheet for using Spiral Grove commands and workflows.

**Need theory?** See [SDD-FOUNDATIONS.md](./SDD-FOUNDATIONS.md) for academic background and methodology foundations.

**Need philosophy?** See [CHARTER.md](./CHARTER.md) for Spiral Grove's implementation principles and architectural decisions.

---

## Commands

### Core Workflow Commands

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `/spec-writing` | Define requirements | Feature idea | `.sdd/specs/[feature].md` |
| `/plan-generation` | Design architecture | Approved spec | `.sdd/plans/[feature]-plan.md` |
| `/task-breakdown` | Create task list | Approved plan | `.sdd/tasks/[feature]-tasks.md` |
| `/implementation` | Execute & track | Task list | Code + `.sdd/progress/[feature]-progress.md` |

### Meta-Phase Command

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `/review [phase]` | Validate phase documents | `spec`, `plan`, `tasks`, or `progress` | Validation findings + status update (if approved) |

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

**"I want to validate my spec"** → `/review spec`

**"I have an approved spec"** → `/plan-generation`

**"I want to validate my plan"** → `/review plan`

**"I have a technical plan"** → `/task-breakdown`

**"I want to validate my tasks"** → `/review tasks`

**"I have a task list"** → `/implementation`

**"I want to check implementation progress"** → `/review progress`

**"I'm implementing and confused"** → Check the spec and plan

**"The spec is unclear"** → `/spec-writing` (to update)

**"The architecture needs changing"** → `/plan-generation` (to revise)

**"Tasks need adjusting"** → `/task-breakdown` (to refine)

## Key Principles

### Specification Phase
- Focus on **requirements**, not solutions
- **Number all requirements** (REQ-F-1, REQ-NF-1) for traceability
- Make success criteria **measurable**
- Be explicit about **constraints** (DO NOTs)
- Think about **stakeholders** and **acceptance tests**

### Planning Phase
- **Explore the codebase** before designing
- **Map plan items to spec requirements** (reference REQ-F-1, REQ-NF-2, etc.)
- Document **technical decisions** with rationale
- Consider **integration points** and **risks**
- Design for the **whole system** (data, errors, security, testing)
- Define **validation strategy** (how to prove it works, evidence format)

### Task Breakdown Phase
- Create **independent, testable** tasks
- Keep tasks **small** (< 1 day each)
- Map tasks to **spec acceptance criteria**
- Identify **dependencies** clearly
- Ensure **acceptance criteria** answer "how do I prove this is complete?"
- Define **testing requirements** explicitly (not optional for critical paths)

### Implementation Phase
- Work **one task at a time**
- **Refer to the spec** constantly
- **Update progress document** frequently (`.sdd/progress/` is the single source of truth)
- **Test everything**
- **Document deviations** immediately

## Common Workflows

### Starting Fresh
```
/spec-writing → /plan-generation → /task-breakdown → /implementation
```

### Updating Requirements (Spec Iteration)
```
# Minor changes (add/clarify requirements)
/spec-writing (bump version 1.0→1.1) → /plan-generation (update existing plan)

# Major changes (scope/approach fundamentally different)
/spec-writing (bump version 1.0→2.0) → Archive old plan → /plan-generation (create new -v2 plan)
```

### Architecture Change
```
/plan-generation (update plan) → /task-breakdown (update tasks)
```

### Adding Tasks
```
/task-breakdown (refine tasks) → /implementation (continue)
```

## Review Validation Criteria

Use `/review [phase]` to validate phase documents before progression.

### Spec Review (`/review spec`)
**Critical checks:**
- ✅ All requirements are numbered (REQ-F-1, REQ-NF-1, etc.)
- ✅ No HOW details (tech choices like "use PostgreSQL", "deploy on AWS")
- ✅ Success criteria are measurable (numbers, percentages, time limits)
- ✅ Explicit constraints documented (DO NOTs)
- ✅ Stakeholders identified
- ✅ Acceptance tests defined

**Example issues:**
- ❌ "Use React for frontend" → Should be "Needs interactive UI"
- ❌ "System should be fast" → Should be "95th percentile < 200ms"
- ❌ Requirements not numbered → Add REQ-F-1, REQ-F-2, etc.

### Plan Review (`/review plan`)
**Critical checks:**
- ✅ References specification explicitly (maps to requirement numbers)
- ✅ Technical decisions have rationale (WHY, not just WHAT)
- ✅ Integration points documented
- ✅ Existing codebase patterns analyzed
- ✅ Error handling, security, testing strategies defined
- ✅ Validation strategy defined (how to prove it works, what evidence, what environment)

**Example issues:**
- ❌ "Decision: Use Redis" with no explanation
- ✅ "Decision: Use Redis. Rationale: Existing infra, team familiar, meets <200ms requirement (REQ-NF-1)"
- ❌ No validation strategy → Add: "Validation: Browser testing + deployment on staging"
- ❌ Plan items don't reference spec requirements → Add "(REQ-F-3, REQ-NF-2)" citations

### Tasks Review (`/review tasks`)
**Critical checks:**
- ✅ All spec acceptance criteria mapped to tasks
- ✅ Task complexity is S/M/L (not XS/XL/XXL)
- ✅ Dependencies documented
- ✅ Each task has specific acceptance criteria
- ✅ Acceptance criteria include "how to verify" not just "what to build"
- ✅ Testing requirements explicit (unit, integration, critical paths)

**Example issues:**
- ❌ Task sized XL/XXL → Break down into S/M/L tasks
- ❌ Spec criterion has no corresponding task → Add task
- ❌ "Acceptance: Code written" → Add: "How verified? Tests passing, deployed to staging"

### Progress Review (`/review progress`)
**Critical checks:**
- ✅ Tasks being tracked (completed, in-progress, upcoming)
- ✅ Deviations from spec/plan documented with approval
- ✅ Test coverage maps to spec acceptance criteria
- ✅ Blockers identified with mitigation plans
- ✅ Session notes enable resumption without re-explanation

**Review workflow:**
1. Run `/review [phase]` on your document
2. Review findings (pass/fail/warning)
3. Fix critical issues if any
4. Approve status update when ready

## Red Flags

🚩 **Writing code during spec-writing** - Too early!
🚩 **Skipping codebase exploration in planning** - You'll miss existing patterns
🚩 **Tasks sized XL/XXL** - Break them down into S/M/L tasks
🚩 **Implementing without tests** - Tests are not optional
🚩 **Deviating from spec silently** - Flag and discuss first
🚩 **Stale progress docs** - Update in real-time
🚩 **Moving to next phase without review** - Validate quality gates

## Document Status Flow

```
Spec:  Draft → Under Review → Approved → [Superseded]
Plan:  Draft → Under Review → Approved → [Updated]
Tasks: Draft → Ready for Implementation → In Progress → Complete
```

## File Locations

```
.sdd/
├── specs/          # Specifications (WHAT to build)
├── plans/          # Technical plans (HOW to build)
├── tasks/          # Task breakdowns (STEPS to build) - READ-ONLY during implementation
└── progress/       # Progress tracking (SINGLE source of truth for status)
```

**Important**: Tasks define WHAT to do. Progress tracks WHAT has been done. Never mix the two.

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
- [ ] Run `/review [phase]` and address findings
- [ ] Status is approved/ready
- [ ] Stakeholders have reviewed
- [ ] Open questions are resolved

**Before marking task complete:**
- [ ] Acceptance criteria met
- [ ] Tests written and passing
- [ ] Code reviewed
- [ ] Progress doc updated (ONLY in `.sdd/progress/`, NOT in task document)
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
- **Tasks are read-only during implementation** - Don't track status in task documents
- **Progress docs are for you** - Make them useful for resuming work, track ALL status here
- **Tests are guardrails** - They keep you aligned with specs
- **Validation is domain-specific** - SDD defines that validation is required, not how to validate (web app vs CLI vs game each validate differently)

## Remember

> Spec-Driven Development frontloads clarity to enable autonomous execution.

The time spent in planning pays dividends in implementation speed and quality.
