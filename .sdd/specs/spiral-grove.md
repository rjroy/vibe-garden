# Spiral Grove: Spec-Driven Development Plugin - Specification

**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-18
**Last Updated**: 2025-10-18

## Executive Summary

Spiral Grove is a Claude Code plugin that implements Spec-Driven Development (SDD) methodology to enable repeatable, controlled AI-assisted software development. It provides a four-phase workflow (Specification → Planning → Task Breakdown → Implementation) that prevents AI drift by establishing clear checkpoints and separating user strategic decisions from AI tactical execution.

## User Story

As a **developer working with AI coding assistants**, I want **a structured methodology that keeps AI aligned with my intent across long development sessions**, so that **I can focus on defining requirements and architecture while delegating implementation details to AI with high confidence**.

## Stakeholders

- **Primary**: Solo developers and small teams using AI-assisted development (Claude Code)
- **Secondary**: Organizations adopting AI-driven development practices
- **Tertiary**: Open-source maintainers, development teams establishing SDD standards

## Success Criteria

1. **High-confidence automation**: `/implementation` and `/task-breakdown` phases complete successfully in one iteration 80%+ of the time when given quality specs and plans
2. **Phase adherence**: `/spec-writing` produces specifications with no implementation details (HOW) in 95%+ of cases
3. **Resumability**: Developers can resume work after interruptions by reading `.sdd/` artifacts without re-explaining context
4. **Scale flexibility**: Supports single-feature projects and large multi-component systems (via parent/child spec references)
5. **AI drift prevention**: Implementation deviations from approved specs are detected and flagged before merging
6. **User effort concentration**: 70%+ of user cognitive effort occurs during `/spec-writing` and `/plan-generation` phases, with minimal intervention during `/task-breakdown` and `/implementation`

## Functional Requirements

### Phase 1: Specification Writing (`/spec-writing`)

**Capabilities:**
- Guide users through requirements gathering with structured prompts
- Distinguish between capabilities/constraints (WHAT) and implementation choices (HOW)
- Generate specification documents with measurable success criteria
- Identify stakeholders, acceptance tests, and explicit constraints
- Detect and prevent premature technical decisions (e.g., "use PostgreSQL" vs. "need relational data model")
- Support versioning and status tracking (Draft → Under Review → Approved → Superseded)

**Acceptance Criteria:**
- Spec documents contain zero implementation technology choices (unless capability-driven)
- All success criteria are measurable with specific thresholds
- Explicit "DO NOT" constraints prevent scope creep
- Acceptance tests map to testable outcomes

### Phase 2: Plan Generation (`/plan-generation`)

**Capabilities:**
- Analyze existing codebase patterns before designing new architecture
- Document technical decisions with explicit rationale (WHY, not just WHAT)
- Design for complete system concerns: data model, API design, error handling, security, testing, deployment
- Identify integration points with existing systems
- Surface technical risks with mitigation strategies
- Maintain architectural consistency with project conventions

**Acceptance Criteria:**
- Plans reference at least 3 existing codebase patterns/utilities
- All technical decisions include "Options Considered" and "Rationale" sections
- Integration points with existing systems are explicitly documented
- Risks are identified with likelihood, impact, and mitigation
- Plans respect specification constraints (no feature additions)

### Phase 3: Task Breakdown (`/task-breakdown`)

**Capabilities:**
- Decompose plans into independent, testable tasks
- Map tasks to specification acceptance criteria
- Identify task dependencies and critical path
- Ensure tasks are appropriately sized (< 1 day, single PR scope)
- Generate task acceptance criteria linked to spec requirements
- Support progress tracking tables

**Acceptance Criteria:**
- Each task has clear acceptance criteria with checkboxes
- Task dependency graph shows execution order
- No task exceeds 1-day estimate
- All spec acceptance criteria map to at least one task
- Tasks can be worked independently (minimal blocking dependencies)

### Phase 4: Implementation (`/implementation`)

**Capabilities:**
- Execute tasks sequentially with real-time progress tracking
- Validate implementation against specification acceptance criteria
- Detect and flag deviations from spec/plan before code completion
- Maintain progress documentation for session resumption
- Support test-driven development (tests before implementation)
- Track technical discoveries and deviations with approval workflow

**Acceptance Criteria:**
- Progress document updates immediately after task completion (before moving to next task)
- Spec deviations trigger approval prompt before continuing
- Test coverage maps back to spec acceptance tests
- Implementation respects plan's architectural decisions
- Progress document enables resumption without user re-explanation

### Phase 5: Review (`/review [phase]`)

**Capabilities:**
- Validate phase documents before moving to next phase
- Check consistency between current phase and previous phase documents
- Identify open questions that need resolution
- Verify completion of validation checklists
- Facilitate approval discussion with user
- Support all phases: spec, plan, tasks, progress

**Acceptance Criteria:**
- Command accepts phase argument: `spec`, `plan`, `tasks`, or `progress`
- Validates document exists for specified phase
- For specs: checks for HOW details, validates success criteria are measurable, confirms DO NOTs exist
- For plans: validates spec reference exists, confirms technical decisions have rationale, verifies integration points documented
- For tasks: confirms all spec acceptance criteria mapped to tasks, validates dependency graph exists, checks task sizing (<1 day)
- For progress: validates tasks are being tracked, confirms deviations documented, checks test coverage mapping
- Presents findings to user in structured format
- Waits for explicit user approval before updating status field
- Does not proceed automatically - requires user confirmation

**Argument hint:** `[spec|plan|tasks|progress]`

### Cross-Phase Capabilities

**Bidirectional navigation:**
- Return to earlier phases when conflicts arise (e.g., `/spec-writing` to clarify requirements during `/implementation`)
- Update downstream artifacts when upstream documents change
- Support iterative refinement (living documents)

**Context management for large projects:**
- Support parent/child specification hierarchies using directory structure
- Parent specs stored at: `.sdd/specs/[parent-name].md`
- Child specs stored at: `.sdd/specs/[parent-name]/[child-name].md`
- Parent specs include "Child Specifications" section listing all children
- Child specs include "Parent Specification" field referencing parent
- Enable focused work on subsystems without loading entire project context
- Plans, tasks, and progress documents follow same directory structure as their specs

**Skill integration:**
- Provide `spiral-grove:spiral-grove-guide` skill for methodology guidance
- Supply quick reference and theoretical foundations documents
- Enable plugin extensibility (e.g., directing to project-specific MCP tools)

## Non-Functional Requirements

### Performance
- Context window efficiency: Each command prompt ≤ 300 lines (excluding reference materials)
- Workflow efficiency: Phases are designed to concentrate user effort upfront (spec/plan) to minimize rework during implementation

### Usability
- Phase boundaries are explicit (clear when to use each command)
- Error messages guide users to correct command (e.g., "No spec found, run `/spec-writing` first")
- Output artifacts are human-readable markdown with consistent formatting
- Decision trees help users navigate workflow states

### Maintainability
- All command prompts are markdown files in `commands/` directory
- Reference materials separated from operational prompts
- No executable code in plugin (except test/validation scripts)
- Extensible via Claude Code's skill and agent systems

### Compatibility
- Works with any programming language or project type
- Integrates with existing project structures (git, CI/CD, issue trackers via direction)
- Respects project-specific conventions (coding standards, testing frameworks)
- Does not require specific MCPs but can be directed to use them

## Explicit Constraints (DO NOT)

- **Do NOT** provide project management features (issue tracking, sprint planning, team coordination beyond docs)
- **Do NOT** generate code during `/spec-writing`, `/plan-generation`, or `/task-breakdown` phases
- **Do NOT** integrate directly with external tools (git, Jira, etc.) - allow direction but don't enforce
- **Do NOT** enforce specific development methodologies (Agile, Waterfall) - SDD is methodology-agnostic
- **Do NOT** make implementation decisions during specification phase (e.g., selecting databases, frameworks)
- **Do NOT** exceed 300 lines for any command, skill, or agent prompt (reference materials exempt)
- **Do NOT** replace developer judgment - provide structure, not prescriptive solutions
- **Do NOT** assume one-size-fits-all - support customization via project-specific skills/conventions

## Technical Context

- **Existing platform**: Claude Code (Anthropic's CLI tool for AI-assisted development)
- **Plugin system**: Uses Claude Code's `.claude-plugin/` directory structure
- **Artifact storage**: `.sdd/` directory with subdirectories for specs, plans, tasks, progress
  - Single-level: `.sdd/specs/feature-name.md`
  - Parent-child: `.sdd/specs/parent-name.md` with children at `.sdd/specs/parent-name/child-name.md`
  - Plans, tasks, and progress mirror the spec directory structure
- **Document format**: GitHub-flavored markdown with structured sections
- **Integration points**:
  - Claude Code skill system (for guidance and methodology support)
  - Claude Code agent system (for complex implementation tasks)
  - Claude Code command system (for phase execution)
  - Project-specific MCPs (via user direction, not hardcoded dependency)

## Acceptance Tests

### Test 1: Single-feature development workflow
**Given**: A new feature request ("Add user notification preferences")
**When**: User runs `/spec-writing` → `/plan-generation` → `/task-breakdown` → `/implementation`
**Then**:
- Specification contains no technology choices (only capabilities needed)
- Plan explores existing codebase and documents 3+ patterns to reuse
- Tasks complete in one iteration without user intervention
- Implementation produces working, tested code that passes spec acceptance criteria

### Test 2: Spec-to-code alignment
**Given**: An approved specification with 5 acceptance criteria
**When**: Implementation phase completes all tasks
**Then**:
- 5/5 acceptance criteria have passing tests
- No additional features beyond spec scope
- All deviations from spec are documented with approval records

### Test 3: Session resumption
**Given**: Implementation interrupted mid-way through task list
**When**: Developer returns 2 days later and reads `.sdd/progress/[feature]-progress.md`
**Then**:
- Developer understands current state without asking questions
- Can continue implementation from exact stopping point
- No context loss or re-explanation required

### Test 4: Phase boundary enforcement
**Given**: User runs `/spec-writing` command
**When**: AI begins writing implementation code or selecting technologies
**Then**:
- Command prompt reminds AI to stay at WHAT level
- Spec validation checklist flags HOW details
- User receives warning about premature technical decisions

### Test 5: Parent-child specification hierarchy
**Given**: Project with a dashboard controller that manages 5 features
**When**: User creates `.sdd/specs/dashboard-controller.md` with children at `.sdd/specs/dashboard-controller/feature-a.md`, `.sdd/specs/dashboard-controller/feature-b.md`, etc.
**Then**:
- Parent spec includes "Child Specifications" section listing all 5 children
- Each child spec includes "Parent Specification" field referencing dashboard-controller
- Plans/tasks/progress documents mirror the same directory structure
- Can work on single feature without loading all sibling specs
- Directory structure is readable by both AI and humans

### Test 6: Extensibility with project-specific tools
**Given**: Team provides custom MCP tool for issue tracking
**When**: User directs `/implementation` to use issue tracker for progress
**Then**:
- Spiral Grove adapts to use custom tool without plugin modification
- Core SDD workflow remains intact
- No hardcoded dependencies introduced

## Open Questions

- [ ] How should conflicts between multiple specs be handled in large projects (e.g., overlapping requirements)?
- [ ] Should the plugin provide templates for different project types (web app, CLI tool, library), or remain generic?

## Out of Scope

- **Code generation frameworks**: Spiral Grove structures workflow, not code scaffolding
- **Team collaboration features**: Real-time editing, comments, assignments (use project's existing tools)
- **Deployment automation**: CI/CD pipeline management (SDD documents inform these, but don't replace)
- **Time tracking**: Estimates are for planning, not billing/reporting
- **Compliance frameworks**: SDD can support compliance workflows, but doesn't implement HIPAA/SOC2 directly
- **Multi-language support**: Commands are English-only (projects can be any language)
- **Offline mode**: Requires Claude Code connection (artifacts are local markdown)
