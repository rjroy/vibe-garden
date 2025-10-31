---
name: spiral-grove-guide
description: Guide for Spec-Driven Development (SDD) methodology. This skill should be used when working with the Spiral Grove commands (/spec-writing, /plan-generation, /task-breakdown, /implementation, /review, /synthesize-docs, /synthesize-specs), when deciding whether to use SDD for a feature, when stuck during SDD workflow, when retrofitting legacy codebases, or when needing clarification about SDD phases and principles.
---

# Spiral Grove Guide

## Overview

Spiral Grove is a Spec-Driven Development (SDD) methodology implementation that transforms how AI coding agents and developers work together. SDD treats AI agents as literal-minded but highly capable pair programmers who excel when given explicit, detailed instructions through a four-phase workflow: Specification → Planning → Task Breakdown → Implementation.

This skill provides guidance on when and how to use SDD, explains the methodology's principles, and helps navigate the workflow phases.

**Version:** 2.0.0 introduces template externalization, metadata automation, and agent delegation for improved modularity and maintainability.

**Project Charter:** For Spiral Grove's foundational philosophy, mission, and design principles, see **references/CHARTER.md**. The charter defines what Spiral Grove is, why it exists, and provides decision-making guidance grounded in v2.0.0 implementation experience.

## When to Use SDD vs. Quick Prompts

### Use SDD for:
- Production features requiring multiple files or components
- Long-running development work spanning multiple sessions
- Team projects requiring consistency and documentation
- Features with compliance, security, or strict requirements
- Complex integrations with existing systems
- Mission-critical applications

### Use quick prompts for:
- Bug fixes with clear, isolated solutions
- Simple utility functions or scripts
- UI tweaks and minor styling changes
- Prototypes and experiments
- One-off scripts or automation
- Learning and exploration tasks

**Decision rule:** If a task requires 3+ distinct steps, involves multiple files, or needs to maintain consistency with existing patterns, use SDD. If it's a single, straightforward change, use quick prompts.

## The Four-Phase SDD Workflow

### Phase 1: Specification (`/spec-writing`)

**Purpose:** Define WHAT to build in user terms, not technical jargon.

**When to use:** Starting a new feature or when requirements are unclear.

**Key principles:**
- Focus on requirements, not solutions
- Make success criteria measurable and testable
- Be explicit about constraints (DO NOTs)
- Define stakeholders and acceptance tests
- Avoid technical implementation details

**Command:** `/spec-writing`

**Output:** `.sdd/specs/[feature-name].md`

**What makes a good spec:**
- Another developer could implement without clarification
- Success criteria are measurable (e.g., "95% of requests complete in <60s")
- Explicit constraints prevent scope creep
- Integration points with existing systems are identified
- Acceptance tests are concrete and testable

### Phase 2: Planning (`/plan-generation`)

**Purpose:** Design HOW to build, considering the entire system architecture.

**When to use:** After spec is approved and before writing any code.

**Key principles:**
- Explore the codebase before designing
- Document technical decisions with rationale
- Consider integration points and risks
- Design for the whole system (data, errors, security, testing)
- Respect existing patterns and conventions

**Command:** `/plan-generation`

**Input:** Approved specification

**Output:** `.sdd/plans/[feature-name]-plan.md`

**What makes a good plan:**
- Considers existing codebase patterns and services
- Identifies all integration points
- Documents architectural decisions and tradeoffs
- Includes database schema, API design, and error handling
- Addresses non-functional requirements (performance, security)

### Phase 3: Task Breakdown (`/task-breakdown`)

**Purpose:** Break the plan into discrete, testable STEPS.

**When to use:** After plan is approved and before implementation begins.

**Key principles:**
- Create independent, testable tasks
- Keep tasks small (< 1 day each)
- Map tasks to spec acceptance criteria
- Identify dependencies clearly
- Each task should be PR-able

**Command:** `/task-breakdown`

**Input:** Approved plan

**Output:** `.sdd/tasks/[feature-name]-tasks.md`

**What makes a good task breakdown:**
- Each task is independently implementable
- Tasks have clear acceptance criteria
- Dependencies are explicit and minimal
- Each task corresponds to a single PR
- Tasks map back to specification requirements

### Phase 4: Implementation (`/implementation`)

**Purpose:** Execute tasks and track progress with continuous validation.

**When to use:** After tasks are ready for implementation.

**Key principles:**
- Work one task at a time
- Refer to the spec constantly
- Update progress frequently
- Test everything against acceptance criteria
- Document deviations immediately

**Command:** `/implementation`

**Input:** Task list

**Output:** Code + `.sdd/progress/[feature-name]-progress.md`

**What makes good implementation:**
- Each task completed with tests
- Progress document updated in real-time
- Deviations from spec are flagged and discussed
- Tests validate against spec acceptance criteria
- Code follows existing patterns from the plan

## Workflow Decision Tree

**Starting point questions:**

- "I have a feature idea" → `/spec-writing`
- "I have an approved spec" → `/plan-generation`
- "I have a technical plan" → `/task-breakdown`
- "I have a task list" → `/implementation`

**Problem-solving questions:**

- "I'm implementing and confused" → Check the spec and plan
- "The spec is unclear" → `/spec-writing` (to update)
- "The architecture needs changing" → `/plan-generation` (to revise)
- "Tasks need adjusting" → `/task-breakdown` (to refine)
- "I found a major issue during implementation" → Stop, document, return to appropriate phase

**Emergency procedures:**

- **Stuck on implementation:** Check spec (what is success?), check plan (what's the architecture?), check task (what's the acceptance criteria?)
- **Spec and code conflict:** Stop implementing, document conflict, propose solution, get approval, update docs, continue
- **Major architecture issue:** Stop, document problem, return to `/plan-generation`, revise plan, update tasks, continue

## SDD Principles

### Specification Phase Principles
- Requirements, not solutions (stay at WHAT not HOW)
- Measurable success criteria (numbers, percentages, specific behaviors)
- Explicit constraints (DO NOT items prevent scope creep)
- Stakeholder-focused (who benefits and how?)
- Test-driven (acceptance criteria become tests)

### Planning Phase Principles
- Codebase exploration first (understand before designing)
- Technical decisions with rationale (document the "why")
- System-wide thinking (data, errors, security, testing, performance)
- Integration awareness (how does this fit with existing systems?)
- Risk identification (what could go wrong?)

### Task Breakdown Principles
- Independence (tasks don't block each other when possible)
- Small scope (< 1 day, single PR)
- Testability (clear acceptance criteria)
- Spec alignment (map to acceptance criteria)
- Dependency clarity (explicit prerequisites)

### Implementation Principles
- One task at a time (focus and completion)
- Constant spec reference (stay aligned)
- Real-time progress updates (visibility)
- Test everything (validation against spec)
- Document deviations (transparency)

## Document Status Flow

**Specifications:**
- Draft → Under Review → Approved → [Superseded]

**Plans:**
- Draft → Under Review → Approved → [Updated]

**Tasks:**
- Draft → Ready for Implementation → In Progress → Complete

**Progress:**
- Continuously updated during implementation

## Common Workflows

### Starting fresh:
```
/spec-writing → /plan-generation → /task-breakdown → /implementation
```

### Updating requirements:
```
/spec-writing (update spec) → /plan-generation (revise plan)
```

### Architecture change:
```
/plan-generation (update plan) → /task-breakdown (update tasks)
```

### Adding tasks mid-implementation:
```
/task-breakdown (refine tasks) → /implementation (continue)
```

## Red Flags and Anti-Patterns

**Red flags to watch for:**
- Writing code during spec-writing (too early!)
- Skipping codebase exploration in planning (you'll miss patterns)
- Tasks taking > 1 day (break them down further)
- Implementing without tests (tests are not optional)
- Deviating from spec silently (flag and discuss first)
- Stale progress docs (update in real-time)
- Over-specifying implementation details (specify what, not how)
- Under-specifying edge cases (think through errors)
- Ignoring existing patterns (respect codebase conventions)

**Common pitfalls:**
- Treating specs as one-time documents (they're living documents)
- Skipping phases (each builds on the previous)
- Weak success criteria (be measurable and specific)
- Forgetting non-functional requirements (performance, security, compliance)
- Not updating docs when learning (capture discoveries)

## Quality Checklists

### Before moving to next phase:
- Current document is complete
- Status is approved/ready
- Stakeholders have reviewed
- Open questions are resolved

### Before marking task complete:
- Acceptance criteria met
- Tests written and passing
- Code reviewed
- Progress doc updated
- No blockers remaining

## File Structure

```
.sdd/
├── specs/          # Feature specifications (WHAT to build)
├── plans/          # Technical plans (HOW to build)
├── tasks/          # Task breakdowns (STEPS)
└── progress/       # Implementation tracking
```

## v2.0.0 Architecture

Spiral Grove v2.0.0 introduces a modular architecture with external templates, automated metadata, and agent delegation:

### Skills for Resource Bundling

**sdd-templates skill:** Bundles document structure templates (spec, plan, tasks, progress)
- Commands/agents invoke skill to access templates
- Enables template updates without modifying command prompts
- Location: `spiral-grove/skills/sdd-templates/templates/`

**sdd-metadata skill:** Provides zero-token metadata detection
- Auto-detects author (Git → P4 → ENV → Unknown)
- Auto-generates dates (ISO 8601 format)
- Populates frontmatter YAML automatically
- Location: `spiral-grove/skills/sdd-metadata/scripts/`

**sdd-format-docs skill:** Bundles format specifications and schemas
- CLAUDE.md format specification
- Manifest schemas (module, spec)
- Used by synthesis commands and agents
- Location: `spiral-grove/skills/sdd-format-docs/docs/`

### Agent Delegation Pattern

Commands orchestrate workflows by delegating to specialized agents:

**Validator Agents:**
- `spec-validator` - Phase boundary compliance (WHAT vs HOW)
- `plan-validator` - Requirements coverage, rationale presence
- `tasks-validator` - Task sizing, dependencies, acceptance criteria
- `progress-validator` - Status accuracy, deviation tracking

**Implementation Agents:**
- `spec-acceptance-validator` - Validates implementation against spec criteria
- `module-discovery-agent` - Detects module boundaries for synthesis

**Synthesis Agents:**
- `module-doc-synthesizer` - Generates CLAUDE.md for single module
- `module-spec-synthesizer` - Reverse-engineers spec from module code

### Benefits of v2.0.0 Architecture

- **Modularity:** Templates, metadata, and validation logic externalized
- **Maintainability:** Update templates/agents without changing commands
- **Composability:** Agents reusable across multiple commands
- **Consistency:** Centralized templates ensure uniform document structure
- **Performance:** Parallel agent execution for faster synthesis
- **Zero-token operations:** Metadata detection happens outside context window

## Additional Commands

### Review Command (`/review`)

**Purpose:** Validate phase documents before progression using specialized validator agents.

**When to use:**
- Before moving from one phase to the next
- Want to verify spec/plan/task quality
- Need confidence that documents are ready

**What it checks (via agents):**
- Specs: WHAT vs HOW separation, measurable success criteria (spec-validator agent)
- Plans: Technical rationale, codebase exploration evidence (plan-validator agent)
- Tasks: Mapping to spec acceptance criteria, proper dependencies (tasks-validator agent)
- Progress: Deviation tracking and documentation (progress-validator agent)

**Command:** `/review [spec|plan|tasks|progress]`

**Agent Delegation (v2.0.0):** Command spawns specialized validator agents to perform comprehensive checks and present structured reports to user.

**Key benefit:** Catches issues before they cascade through later phases.

### Retrofit Commands (`/synthesize-docs`, `/synthesize-specs`)

**Purpose:** Enable SDD adoption on legacy codebases by reverse-engineering documentation and specifications from implementation.

**When to use:**
- Inheriting legacy codebase without documentation
- Want to adopt SDD on existing project
- Need compliance/audit documentation
- Onboarding team members to large codebase
- Detecting drift between specs and implementation

**Commands:**
- `/synthesize-docs` - Generate CLAUDE.md files (HOW - operational knowledge)
- `/synthesize-specs` - Generate specifications (WHAT - requirements)

**Key features:**
- Automatic module discovery
- Parallel processing (100 modules in ~10-45 minutes)
- Drift detection (specs vs implementation)
- Cross-command integration (reuse manifests)
- Resumable if interrupted

**See:** SYNTHESIZE-REFERENCE.md for comprehensive guide

## Resources

This skill includes comprehensive reference documentation:

### references/CHARTER.md
**Purpose:** Project charter defining Spiral Grove's mission, core pillars, and design philosophy

**Contains:**
- Mission statement (why Spiral Grove exists)
- 5 core pillars (foundational principles)
- 8 design philosophy principles (decision-making rules)
- Boundaries (what Spiral Grove is NOT)
- Key differentiators (what makes us unique)
- Practical usage guidance (how to apply the charter)

**When to use:**
- Need to understand Spiral Grove's foundational philosophy
- Making architectural decisions (check against pillars and principles)
- Onboarding contributors to project vision
- Evaluating feature proposals for alignment
- Understanding design rationale behind v2.0.0 refactor
- Explaining Spiral Grove's unique approach vs other implementations

### references/SDD-QUICK-REFERENCE.md
**Purpose:** Practical operational guide for day-to-day SDD usage

**Contains:**
- Command summary table
- Phase flow diagram
- Quick decision tree
- Key principles checklist
- Common workflows
- Red flags
- Emergency procedures

**When to use:**
- Need quick lookup of command syntax
- Want reminder of workflow phases
- Looking for practical checklists
- Need immediate decision tree guidance
- Troubleshooting during active development

### references/SDD-FOUNDATIONS.md
**Purpose:** Deep theoretical reference for understanding SDD methodology

**Contains:**
- Academic foundations (Ostroff et al. 2004, Design by Contract, Formal Methods)
- Industry implementations (GitHub Spec Kit, Kiro IDE)
- Historical context and timeline
- Core principles with philosophical grounding
- Detailed phase explanations with validation criteria
- Comparisons to other methodologies (Waterfall, Agile, TDD, BDD, DbC)
- "Why SDD for AI?" rationale and problem analysis
- Spiral Grove's unique innovations and extensions
- Benefits, trade-offs, and critical analysis
- Full academic and industry citations

**When to use:**
- Need to understand WHY SDD works this way
- Want academic backing or legitimacy validation
- Explaining SDD to stakeholders or team members
- Making methodology decisions (when to use SDD vs alternatives)
- Understanding relationship to other methodologies
- Need theoretical grounding for SDD principles
- Researching trade-offs and costs
- Writing documentation about SDD
- Justifying SDD adoption to organization

### references/SYNTHESIZE-REFERENCE.md
**Purpose:** Comprehensive guide for retrofitting legacy codebases with SDD documentation and specifications

**Contains:**
- When to use synthesize commands
- Detailed command workflows for /synthesize-docs and /synthesize-specs
- Cross-command integration strategies
- Practical workflows (onboarding, drift detection, compliance)
- Performance optimization for large codebases
- Troubleshooting guide
- Common scenarios and solutions

**When to use:**
- Adopting SDD on legacy codebase
- Need to generate documentation for undocumented code
- Want to detect drift between specs and implementation
- Onboarding team to large project
- Compliance/audit documentation needed
- Reverse-engineering requirements from code

**Usage guideline:** Use QUICK-REFERENCE for "how to use SDD" and FOUNDATIONS for "why SDD exists and how it works." Use SYNTHESIZE-REFERENCE for "how to adopt SDD on existing code."

## Tips for Success

- **Specs are living documents** - Update them as understanding evolves
- **Plans can be revised** - Architecture isn't set in stone
- **Tasks can be added** - Discovery is part of the process
- **Progress docs are for resuming work** - Make them useful for context restoration
- **Tests are guardrails** - They keep implementation aligned with specs

## Remember

> Spec-Driven Development frontloads clarity to enable autonomous execution.

The time invested in specification and planning pays dividends in implementation speed, quality, and maintainability. SDD transforms AI agents from code generators into reliable pair programmers who understand context and deliver consistent results.
