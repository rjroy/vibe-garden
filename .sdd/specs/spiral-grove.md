# Spiral Grove: Spec-Driven Development Plugin - Specification

**Version**: 1.1.0
**Status**: Approved
**Created**: 2025-10-18
**Last Updated**: 2025-10-20 (Refactored to focus on WHAT capabilities/constraints rather than HOW implementation details)
**Child Specifications**:
- [documentation-synthesis.md](./spiral-grove/documentation-synthesis.md) - Lifecycle management with spec-code drift detection and CLAUDE.md generation

## Executive Summary

Spiral Grove enables developers to maintain strategic control over AI-assisted development by providing a structured workflow that separates "what to build" decisions from "how to build it" execution. The system prevents AI drift across long development sessions by enforcing phase boundaries, enabling session resumability, and validating implementation against user-approved requirements.

## User Story

As a **developer working with AI coding assistants**, I want **a structured methodology that keeps AI aligned with my intent across long development sessions**, so that **I can focus on defining requirements and architecture while delegating implementation details to AI with high confidence**.

## Stakeholders

- **Primary**: Solo developers and small teams using AI-assisted development (Claude Code)
- **Secondary**: Organizations adopting AI-driven development practices
- **Tertiary**: Open-source maintainers, development teams establishing SDD standards

## Success Criteria

1. **High-confidence automation**: Implementation phases complete successfully in one iteration 80%+ of the time when given quality requirements and plans
2. **Phase boundary enforcement**: Requirements documents contain zero implementation decisions (technology/vendor choices) in 95%+ of cases
3. **Zero-context resumability**: Developers can resume work after multi-day interruptions without re-explaining context to AI
4. **Scale flexibility**: System supports both single-feature projects (5-10 tasks) and large multi-component systems (100+ tasks across subsystems)
5. **Drift detection**: Implementation deviations from approved requirements are automatically detected and require explicit user approval
6. **Effort front-loading**: 70%+ of user decision-making effort occurs during requirements and planning phases, with minimal intervention during execution

## Functional Requirements

### Requirements Definition

**Must enable:**
- Structured requirements gathering that separates user-owned decisions (WHAT) from AI-delegated execution (HOW)
- Detection and prevention of premature technical decisions during requirements phase
- Measurable success criteria definition with specific, testable thresholds
- Stakeholder identification and explicit scope constraints
- Version tracking across requirement lifecycle (Draft → Approved → Superseded)

**Must prevent:**
- Implementation technology choices in requirements documents (unless justified by specific capabilities needed)
- Vague or unmeasurable success criteria
- Scope creep through missing "DO NOT" constraints

### Technical Planning

**Must enable:**
- Codebase-aware architecture design that respects existing patterns and conventions
- Explicit documentation of technical decision rationale (WHY choices were made)
- Comprehensive system design covering data, APIs, error handling, security, testing, and deployment
- Integration point identification with existing systems
- Risk surfacing with mitigation strategies

**Must enforce:**
- All technical decisions include alternatives considered and selection rationale
- Plans remain within approved specification scope (no feature additions)
- Integration points with existing systems are explicitly identified
- Architectural consistency with project conventions

### Work Decomposition

**Must enable:**
- Plan decomposition into independent, testable units of work
- Task-to-requirement traceability (every requirement maps to at least one task)
- Dependency identification and critical path analysis
- Progress tracking across task lifecycle

**Must enforce:**
- Task sizing appropriate for single pull request scope
- Every task has clear, testable acceptance criteria
- Tasks are executable with minimal blocking dependencies
- All requirement acceptance criteria map to implementation tasks

### Implementation Execution & Validation

**Must enable:**
- Sequential task execution with real-time progress visibility
- Automated validation of implementation against approved requirements
- Session resumability after interruptions (hours to days)
- Test-driven development workflow (tests before implementation)
- Deviation detection and approval workflow

**Must enforce:**
- Requirement deviations trigger user approval before proceeding
- Test coverage maps to requirement acceptance criteria
- Implementation respects approved architectural decisions
- Progress tracking updates immediately after task completion
- All code changes traceable to specific tasks and requirements

### Phase Validation & Quality Assurance

**Must enable:**
- Pre-progression validation before moving between workflow phases
- Consistency checking between related phase documents
- Open question identification and resolution tracking
- User-driven approval checkpoints (no automatic progression)

**Must validate per phase:**
- **Requirements**: No HOW details present, success criteria are measurable, DO NOT constraints exist
- **Plans**: Requirements reference exists, technical decisions have rationale, integration points documented
- **Tasks**: All requirement acceptance criteria mapped, dependency graph exists, appropriate task sizing
- **Progress**: Tasks tracked, deviations documented with approval, test coverage mapped to requirements

**Must enforce:**
- Structured findings presentation to user
- Explicit user approval required before status changes
- Phase document existence verification before validation

### Workflow Flexibility

**Must support:**
- Bidirectional phase navigation (return to requirements when conflicts arise during implementation)
- Downstream artifact updates when upstream documents change
- Iterative refinement across all phases (living documents)

**Must enable for large projects:**
- Hierarchical organization of related requirements (parent/child relationships)
- Focused work on subsystems without loading entire project context
- Consistent cross-referencing between parent and child artifacts
- Scalability from single features (5-10 tasks) to multi-subsystem projects (100+ tasks)

**Must provide:**
- Methodology guidance and quick reference materials
- Extensibility for project-specific tooling integration
- Framework-agnostic workflow (works with any tech stack)

## Non-Functional Requirements

### Performance
- **Context efficiency**: Workflow commands must operate within typical LLM context windows without truncation
- **Workflow efficiency**: System design must concentrate user decision-making upfront (70%+ during requirements/planning) to minimize rework

### Usability
- **Phase clarity**: Users can identify which workflow phase to use for their current need
- **Error guidance**: System guides users to correct workflow phase when prerequisites missing
- **Artifact readability**: All output artifacts human-readable without specialized tools
- **Navigation support**: Users can determine workflow state and next steps from artifact inspection

### Maintainability
- **Separation of concerns**: Operational logic separated from reference/guidance materials
- **Minimal code footprint**: System relies on prompts and structured artifacts, not executable code (except validation)
- **Extensibility**: System adapts to project-specific tooling without core modification

### Compatibility
- **Language agnostic**: Works with any programming language or tech stack
- **Integration neutral**: Respects existing project tooling (git, CI/CD, issue trackers) without requiring specific tools
- **Convention respecting**: Adapts to project-specific coding standards and testing frameworks

## Explicit Constraints (DO NOT)

- **Do NOT** provide project management features (issue tracking, sprint planning, team coordination)
- **Do NOT** generate code during requirements, planning, or decomposition phases (only during implementation)
- **Do NOT** require integration with specific external tools (git, Jira, etc.) - must work with or without them
- **Do NOT** enforce specific development methodologies (Agile, Waterfall) - remain methodology-agnostic
- **Do NOT** allow implementation technology choices during requirements phase (databases, frameworks, vendors)
- **Do NOT** replace developer judgment - provide structure and validation, not prescriptive solutions
- **Do NOT** assume one-size-fits-all - must support customization via project-specific conventions
- **Do NOT** create hard dependencies on specific file formats, directory structures, or naming conventions (these are implementation choices for planning phase)

## Technical Context

- **Target platform**: Claude Code (Anthropic's CLI for AI-assisted development)
- **Plugin capabilities available**:
  - Command system for workflow phase execution
  - Skill system for methodology guidance
  - Agent system for complex implementation delegation
- **Artifact persistence required**: System must maintain structured artifacts across sessions for resumability
- **Integration opportunities**:
  - Version control systems (git, etc.)
  - Project-specific tooling via Model Context Protocol (MCP)
  - Existing CI/CD and testing infrastructure

## Acceptance Tests

### Test 1: Single-feature development workflow
**Given**: A new feature request ("Add user notification preferences")
**When**: User completes full workflow (requirements → planning → decomposition → implementation)
**Then**:
- Requirements document contains zero technology choices (only capabilities and constraints)
- Plan references existing codebase patterns and documents decision rationale
- Implementation completes in one iteration (80%+ success rate for quality inputs)
- All code changes map back to requirements acceptance criteria
- Automated tests validate requirements fulfillment

### Test 2: Requirements-to-code alignment
**Given**: Approved requirements with 5 acceptance criteria
**When**: Implementation phase completes
**Then**:
- All 5 acceptance criteria have passing automated tests
- No features implemented beyond approved requirements scope
- All deviations documented with explicit user approval records

### Test 3: Session resumption
**Given**: Implementation interrupted mid-way through task execution
**When**: Developer returns 2+ days later and reviews progress artifacts
**Then**:
- Developer and AI understand current state without user re-explanation
- Work continues from exact stopping point
- Zero context loss across multi-day interruption

### Test 4: Phase boundary enforcement
**Given**: User in requirements definition phase
**When**: System attempts to make technology selection decisions (databases, frameworks, vendors)
**Then**:
- System detects and prevents premature HOW decisions
- Validation flags technology choices in requirements document
- User receives guidance to defer implementation decisions to planning phase

### Test 5: Hierarchical project organization
**Given**: Large project with 5 related subsystems
**When**: User organizes requirements hierarchically (parent + 5 children)
**Then**:
- Parent requirements include references to all child requirements
- Each child references parent for context
- Related artifacts (plans, tasks, progress) maintain consistent hierarchy
- Developer can work on single subsystem without loading all sibling context
- System scales from simple (5 tasks) to complex (100+ tasks) projects

### Test 6: Tool integration flexibility
**Given**: Project has custom tooling (issue tracker, specific CI/CD, etc.)
**When**: User integrates workflow with project-specific tools
**Then**:
- System adapts without core modification
- Workflow integrity maintained regardless of tool choices
- No hardcoded tool dependencies required

## Open Questions

- [x] How should conflicts between multiple specs be handled in large projects (e.g., overlapping requirements)? Escalate to the user.
- [x] Should the plugin provide templates for different project types (web app, CLI tool, library), or remain generic? NO

## Out of Scope

- **Code generation frameworks**: Spiral Grove structures workflow, not code scaffolding
- **Team collaboration features**: Real-time editing, comments, assignments (use project's existing tools)
- **Deployment automation**: CI/CD pipeline management (SDD documents inform these, but don't replace)
- **Time tracking**: Estimates are for planning, not billing/reporting
- **Compliance frameworks**: SDD can support compliance workflows, but doesn't implement HIPAA/SOC2 directly
- **Multi-language support**: Commands are English-only (projects can be any language)
- **Offline mode**: Requires Claude Code connection (artifacts are local markdown)
