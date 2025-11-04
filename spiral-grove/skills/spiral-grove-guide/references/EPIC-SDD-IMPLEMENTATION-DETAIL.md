# Spiral Grove Implementation Details

**Version**: 2.1.0
**Last Updated**: 2025-11-04
**Purpose**: Technical implementation reference for Spiral Grove plugin architecture and feature implementation

---

## Overview

This document provides detailed implementation information for the Spiral Grove plugin, mapping specification requirements to actual implementation components. Use this reference when you need to understand how Spiral Grove works internally, troubleshoot issues, or answer questions about specific features.

**Related Documents**:
- **CHARTER.md**: Philosophy and design principles
- **SDD-FOUNDATIONS.md**: Theoretical methodology background
- **SDD-QUICK-REFERENCE.md**: Practical operational guide
- **SYNTHESIZE-REFERENCE.md**: Retrofit command details

**Source Specification**: `.sdd/specs/spiral-grove.md` (v1.1.0)

---

## Architecture Overview

### Component Hierarchy

```
Spiral Grove Plugin
├── Commands (Orchestration Layer)
│   ├── /spec-writing
│   ├── /plan-generation
│   ├── /task-breakdown
│   ├── /implementation
│   ├── /review
│   ├── /synthesize-docs
│   └── /synthesize-specs
├── Skills (Resource Bundles)
│   ├── spiral-grove-guide (Methodology guidance)
│   ├── sdd-templates (Document templates)
│   ├── sdd-metadata (Metadata detection)
│   └── sdd-format-docs (Format specifications)
└── Agents (Autonomous Executors)
    ├── Validators
    │   ├── spec-validator
    │   ├── plan-validator
    │   ├── tasks-validator
    │   ├── progress-validator
    │   └── spec-acceptance-validator
    ├── Synthesis
    │   ├── module-discovery-agent
    │   ├── module-doc-synthesizer
    │   └── module-spec-synthesizer
    └── (Future: implementation agents)
```

### Design Pattern: Commands Orchestrate, Agents Execute, Skills Serve

**Commands** are conversation-level orchestrators that:
- Interact with users to gather context
- Load templates from skills
- Spawn agents for discrete work
- Present results and coordinate phase progression

**Agents** are autonomous workers that:
- Execute in fresh context (prevent bloat)
- Perform focused tasks (validation, synthesis, implementation)
- Return structured results to commands
- Are reusable across multiple commands

**Skills** are resource bundles that:
- Provide templates, schemas, and reference documentation
- Execute zero-token operations (metadata detection)
- Offer contextual guidance when user asks SDD questions
- Are invoked by commands/agents via Skill tool

---

## Requirement Implementation Mapping

### Specification Phase (REQ-F-1 to REQ-F-6)

**Command**: `/spec-writing`
**Location**: `spiral-grove/commands/spec-writing.md`

**Implementation Details**:
- **REQ-F-1**: Command guides user through structured specification creation with prompts for user story, stakeholders, requirements, constraints, acceptance tests
- **REQ-F-2**: Command enforces WHAT vs HOW separation through explicit instructions: "Focus on requirements and capabilities, NOT implementation details"
- **REQ-F-3**: Command requires numbered functional requirements using format `REQ-F-N` and non-functional requirements using `REQ-NF-N`
- **REQ-F-4**: Template includes dedicated sections for Primary/Secondary/Tertiary stakeholders, user stories (As a...I want...so that...), success criteria (measurable), and "Explicit Constraints (DO NOT)" section
- **REQ-F-5**: Uses `sdd-metadata` skill to auto-generate YAML frontmatter with version (default 1.0.0), status (Draft), created date (ISO 8601), last_updated, authored_by (Git/P4/ENV detection)
- **REQ-F-6**: Command supports revision workflow: user can update spec, system increments version (major for breaking changes, minor for additions), maintains changelog in frontmatter

**Agent Integration**:
- Automatically spawns `spec-validator` agent at end of specification generation
- Validator checks: WHAT vs HOW separation, numbered requirements, measurable success criteria, phase boundary violations
- User approves validation before marking spec as "Under Review" or "Approved"

**Template Source**: `sdd-templates` skill → `templates/spec-template.md`

### Planning Phase (REQ-F-7 to REQ-F-11)

**Command**: `/plan-generation`
**Location**: `spiral-grove/commands/plan-generation.md`

**Implementation Details**:
- **REQ-F-7**: Command creates technical plans with sections for Architecture Overview, Technical Decisions, Technology Choices, Implementation Approach, Integration Strategy
- **REQ-F-8**: Template requires "Technical Decisions" section with subsections per decision: Options Considered, Pros/Cons Analysis, Chosen Approach, Rationale
- **REQ-F-9**: Command instructs to reference spec requirements explicitly: "This decision addresses REQ-F-5 (file operations)" pattern throughout plan
- **REQ-F-10**: Command MANDATES codebase exploration: "BEFORE generating the plan, you MUST explore the codebase using Glob/Grep to understand existing patterns, services, and conventions"
- **REQ-F-11**: Template includes sections for: Integration Points (APIs, databases, external services), Data Models (schema design), Error Handling Strategy, Testing Approach (unit/integration/e2e)

**Agent Integration**:
- Automatically spawns `plan-validator` agent after plan draft
- Validator checks: codebase exploration evidence, technical decisions documented with rationale, all spec requirements addressed, integration points identified
- Validator detects if HOW details leaked back into referenced spec

**Template Source**: `sdd-templates` skill → `templates/plan-template.md`

### Task Breakdown Phase (REQ-F-12 to REQ-F-17)

**Command**: `/task-breakdown`
**Location**: `spiral-grove/commands/task-breakdown.md`

**Implementation Details**:
- **REQ-F-12**: Command decomposes plan into discrete tasks with structure: Task ID, Description, Complexity, Dependencies, Acceptance Criteria, Spec Mapping
- **REQ-F-13**: Uses t-shirt sizing: XS (1 pt), S (2 pts), M (3 pts), L (5 pts), XL (8 pts), XXL (13 pts) with complexity ratings based on time estimation and risk
- **REQ-F-14**: Template requires "Acceptance Criteria" subsection per task with clear pass/fail conditions: "Task complete when: [checkboxes with testable statements]"
- **REQ-F-15**: Template includes "Dependencies" field per task with explicit references to prerequisite task IDs, generates critical path analysis at end
- **REQ-F-16**: Template includes "Maps to Spec Criteria" field referencing acceptance test IDs from specification (AT-1, AT-2, etc.)
- **REQ-F-17**: Command warns: "Tasks rated XL or XXL are too large and must be broken down further. Tasks rated XS should be consolidated with related work to avoid overhead."

**Agent Integration**:
- Automatically spawns `tasks-validator` agent after task breakdown
- Validator checks: task sizing appropriate (no XL/XXL), clear acceptance criteria, dependencies well-formed, spec mapping present, independent implementability
- Validator flags XS tasks with recommendation to consolidate

**Template Source**: `sdd-templates` skill → `templates/tasks-template.md`

### Implementation Phase (REQ-F-18 to REQ-F-23)

**Command**: `/implementation`
**Location**: `spiral-grove/commands/implementation.md`

**Implementation Details**:
- **REQ-F-18**: Command creates/updates progress document with task status table: Task ID | Description | Status (Pending/In Progress/Completed/Blocked) | Completion Date | Notes
- **REQ-F-19**: Command delegates each task to specialized implementation agent with fresh context: "Spawn Task tool with subagent_type=general-purpose, provide task context (spec excerpt, plan excerpt, task acceptance criteria)"
- **REQ-F-20**: After task completion, command automatically spawns `spec-acceptance-validator` agent with task ID, spec acceptance criteria, and file changes to validate implementation matches requirements
- **REQ-F-21**: Command instructs: "If implementation must deviate from spec/plan, IMMEDIATELY document in Deviations section with: What changed, Why it changed, Impact, User approval timestamp"
- **REQ-F-22**: Progress document includes "Technical Discoveries" section to capture: New constraints discovered, Patterns learned, Libraries/APIs used differently than planned
- **REQ-F-23**: Progress document tracks: Tests Written (count), Tests Passing (count), Performance Metrics (if applicable), Completion Velocity (tasks per session)

**Three-Tier Validation Integration** (NEW in v2.1):
- **Step 1 - Code Review**: After task implementation, command spawns code review agent to validate code quality (architecture, security, error handling, performance, conventions)
  - Prefers specialized reviewers when available (language-specific, domain-specific)
  - Falls back to general-purpose reviewer if no specialized agent exists
  - Returns three-tier feedback: Approve/Minor, Concerns/Major, Reject/Blockers
  - User decides on remediation: fix issues, accept risk with documentation, or discuss further
- **Step 2 - Spec Compliance**: After code review approval, command spawns `spec-acceptance-validator` agent to check implementation against spec acceptance criteria
- **Step 3 - Progress Quality**: After task marked complete, command spawns `progress-validator` in silent mode for non-blocking advisory feedback on progress documentation quality

**Agent Integration**:
- Implementation agents (general-purpose subagent) execute tasks autonomously
- Code review agents validate implementation quality before spec validation
- `spec-acceptance-validator` agent validates each completed task against spec criteria
- `progress-validator` agent checks progress document for deviation tracking, status accuracy

**Template Source**: `sdd-templates` skill → `templates/progress-template.md`

### Validation and Review (REQ-F-24 to REQ-F-35)

**Command**: `/review [spec|plan|tasks|progress]`
**Location**: `spiral-grove/commands/review.md`

**Implementation Details**:
- **REQ-F-24**: Command accepts phase document type as argument, routes to appropriate validator agent
- **REQ-F-25**: Command spawns:
  - `spec-validator` for specifications
  - `plan-validator` for plans
  - `tasks-validator` for task breakdowns
  - `progress-validator` for progress documents
- **REQ-F-26**: Two-tier validation structure (NEW in v2.1):
  - **Process Compliance Checks** (critical/blocking): Format compliance, phase boundaries, required fields
  - **Quality Checks** (advisory/warning): Requirements clarity, decision rationale depth, task implementability
- **REQ-F-27**: Quality-focused validation beyond format compliance (NEW in v2.1):
  - Spec: Requirements clarity, completeness, testability, consistency, feasibility, dependency clarity, error coverage, security awareness, acceptance criteria quality
  - Plan: Rationale quality, alternative analysis depth, decision implementability, risk awareness
  - Tasks: Acceptance criteria quality, task clarity, testing approach adequacy
  - Progress: Deviation rationale quality, completion evidence
- **REQ-F-28**: Validator agents return structured reports with:
  - Executive Summary (pass/fail/warning overall status)
  - Process Compliance Checks (critical tier - must pass)
  - Quality Checks (advisory tier - warn but don't block)
  - Detailed Checks (per-check pass/fail with examples)
  - Recommendations (actionable next steps)
  - Severity Ratings (critical/warning/info)
- **REQ-F-29**: Command presents validation report, then asks: "Would you like me to update the document status field based on these results? (yes/no)" - only updates on user approval
- **REQ-F-30**: Validators detect phase boundary violations:
  - `spec-validator`: Flags code examples, technology choices, architecture details in spec
  - `plan-validator`: Flags missing technical rationale, missing codebase exploration evidence
- **REQ-F-31**: Advisory quality warnings without blocking (NEW in v2.1):
  - User can proceed despite quality warnings (respects user judgment)
  - Only process compliance failures are blocking
  - Quality checks provide constructive feedback and suggestions
- **REQ-F-32-35**: Code review integration (NEW in v2.1):
  - Three-tier feedback handling: Approve/Minor, Concerns/Major, Reject/Blockers
  - Specialized reviewer preference (language-specific, domain-specific)
  - Progress quality validation after task completion

**Agent Details**:
- **spec-validator** (spiral-grove:spec-validator): Checks phase boundary compliance, requirement numbering, measurable success criteria, stakeholder presence + 9 quality checks
- **plan-validator** (spiral-grove:plan-validator): Checks spec alignment, decision rationale presence, architecture completeness + 4 quality checks
- **tasks-validator** (spiral-grove:tasks-validator): Checks sizing correctness, independence, acceptance criteria clarity + 3 quality checks
- **progress-validator** (spiral-grove:progress-validator): Checks task status accuracy, deviation documentation, test coverage tracking + 2 quality checks

**Proportional Quality Check Distribution** (NEW in v2.1):
- Spec validators: 9 quality checks (most critical, foundational phase)
- Plan validators: 4 quality checks (architectural decisions)
- Tasks validators: 3 quality checks (execution planning)
- Progress validators: 2 quality checks (tracking/documentation)

**Locations**: `spiral-grove/agents/` directory

### Documentation Synthesis (REQ-F-36 to REQ-F-43)

**Commands**: `/synthesize-docs`, `/synthesize-specs`
**Locations**:
- `spiral-grove/commands/synthesize-docs.md`
- `spiral-grove/commands/synthesize-specs.md`

**Implementation Details**:
- **REQ-F-36**: `/synthesize-docs` reverse-engineers CLAUDE.md files from implemented modules by analyzing code structure, exports, dependencies, tests
- **REQ-F-37**: `/synthesize-specs` reverse-engineers specifications from existing codebases by extracting requirements from code behavior, tests, documentation, then comparing to existing specs if present (drift detection)
- **REQ-F-38**: Both commands invoke `module-discovery-agent` for automatic module detection using heuristics:
  - Package boundaries (package.json, Cargo.toml, go.mod)
  - Entry points (index.ts, main.py, main.go)
  - Directory naming patterns (src/, lib/, modules/)
  - Language-specific conventions
- **REQ-F-39**: `module-doc-synthesizer` agent generates CLAUDE.md with 400-line limit:
  - Condensing strategy: Prioritize Purpose, Key Components, Public Interface sections
  - Omit verbose implementation details if over limit
  - Include code examples only for critical APIs
- **REQ-F-40**: `module-doc-synthesizer` preserves hand-edited content:
  - Searches for `<!-- BEGIN: HAND-EDITED -->` and `<!-- END: HAND-EDITED -->` markers
  - Extracts content between markers before regeneration
  - Merges preserved content back into new documentation at same markers
  - Validates marker well-formedness (warns if unclosed)
- **REQ-F-41**: Commands process modules in parallel:
  - Spawns 10 `module-doc-synthesizer` or `module-spec-synthesizer` agents concurrently
  - Waits for batch completion before spawning next batch
  - Provides progress updates: "Processing batch 1/5 (10 modules)..."
- **REQ-F-42**: Commands track synthesis state in manifest files:
  - `.sdd/module-manifest.json` for `/synthesize-docs`
  - `.sdd/spec-manifest.json` for `/synthesize-specs`
  - Manifest schema: `{ version, lastUpdated, modules: [{ name, path, status, lastSynthesized }] }`
  - If interrupted, command resumes from manifest state (skips already-completed modules)
- **REQ-F-43**: `module-doc-synthesizer` links generated CLAUDE.md to originating specs:
  - Checks for corresponding spec at `.sdd/specs/[module-name].md`
  - If exists, adds frontmatter field: `related_spec: .sdd/specs/[module-name].md`
  - Adds section at end of CLAUDE.md: "## Specification: [link to spec]"

**Agent Details**:
- **module-discovery-agent** (spiral-grove:module-discovery-agent): Bash, Glob, Grep, Read tools for heuristic detection
- **module-doc-synthesizer** (spiral-grove:module-doc-synthesizer): Read, Glob, Grep, Write, SlashCommand tools for CLAUDE.md generation
- **module-spec-synthesizer** (spiral-grove:module-spec-synthesizer): Read, Glob, Grep, Write, Task tools for spec reverse-engineering

**Format Specification**: `sdd-format-docs` skill → `docs/claude-md-format.md`, `docs/manifest-schema.json`

### Agent Architecture (REQ-F-44 to REQ-F-47)

**Skills Architecture**:
- **REQ-F-44**: `sdd-templates` skill externalizes all document structure templates
  - Location: `spiral-grove/skills/sdd-templates/templates/`
  - Files: `spec-template.md`, `plan-template.md`, `tasks-template.md`, `progress-template.md`
  - Commands invoke skill: `Skill tool with command="spiral-grove:sdd-templates"`
  - Commands read template files from skill resources
  - Benefit: Update templates without modifying command prompts

- **REQ-F-45**: `sdd-metadata` skill provides metadata auto-detection via bash scripts
  - Location: `spiral-grove/skills/sdd-metadata/scripts/`
  - Scripts: `detect-author.sh`, `generate-date.sh`
  - Author detection priority: Git config → P4 user → ENV variables → "Unknown"
  - Date format: ISO 8601 (YYYY-MM-DD)
  - Zero-token operation: Runs outside Claude context via bash execution
  - Commands invoke: `Bash tool executing skill scripts, capture output, populate YAML frontmatter`

- **REQ-F-46**: `sdd-format-docs` skill bundles format specifications
  - Location: `spiral-grove/skills/sdd-format-docs/docs/`
  - Files: `claude-md-format.md` (CLAUDE.md structure), `manifest-schema.json` (module/spec manifest JSON schema)
  - Agents invoke skill to access format specifications during synthesis
  - Ensures consistency across all generated documentation

- **REQ-F-47**: Commands automatically spawn validator agents at phase completion
  - `/spec-writing` → spawns `spec-validator` after spec draft complete
  - `/plan-generation` → spawns `plan-validator` after plan draft complete
  - `/task-breakdown` → spawns `tasks-validator` after tasks draft complete
  - `/implementation` → spawns code review agent, then `spec-acceptance-validator` after each task complete, then `progress-validator` at end (three-tier validation, NEW in v2.1)
  - Mandatory quality gates: User must address critical issues or explicitly approve proceeding despite warnings

### Parent/Child Hierarchies (REQ-F-48 to REQ-F-51)

**Implementation Details**:
- **REQ-F-48**: All phase commands detect when project scope suggests parent/child organization:
  - Trigger: User mentions 3+ related sub-features, specification exceeds 20 pages, or user requests hierarchical organization
  - Command suggests: "This feature has multiple sub-components. Would you like to organize as parent/child hierarchy?"

- **REQ-F-49**: Parent/child file structure pattern:
  - Parent spec: `.sdd/specs/parent-feature.md`
  - Child specs: `.sdd/specs/parent-feature/child-a.md`, `.sdd/specs/parent-feature/child-b.md`
  - Naming convention: Parent uses noun (e.g., "authentication"), children use verb-noun (e.g., "implement-oauth", "add-2fa")

- **REQ-F-50**: Commands mirror hierarchy across all phases:
  - Specs: `.sdd/specs/parent/child-a.md`
  - Plans: `.sdd/plans/parent/child-a-plan.md`
  - Tasks: `.sdd/tasks/parent/child-a-tasks.md`
  - Progress: `.sdd/progress/parent/child-a-progress.md`
  - Maintains 1:1 correspondence between phases for each child feature

- **REQ-F-51**: Child specs inherit parent constraints:
  - Parent spec includes "Global Constraints" section
  - Child specs reference: "**Inherited from parent**: [list constraint with (Inherited) notation]"
  - Example: `- **DO NOT** use external auth providers (Inherited)`
  - Child specs can add additional constraints specific to their scope

---

## Non-Functional Requirements Implementation

### Performance (REQ-NF-1 to REQ-NF-4)

- **REQ-NF-1**: `module-discovery-agent` uses optimized heuristics:
  - Glob patterns before Grep (faster file enumeration)
  - Parallel file reads (batch of 10 files)
  - Early termination when pattern matches (don't read entire file)
  - Target: <2 minutes for 1000-file codebases

- **REQ-NF-2**: Synthesis commands use parallel batch processing:
  - 10 agents concurrently (configurable via command parameter)
  - Progress tracking with estimated time remaining
  - Target: 100 modules in 45 minutes (average 27 seconds per module)

- **REQ-NF-3**: Validator agents optimized for speed:
  - Read only necessary document sections (targeted regex search)
  - Use Grep instead of full file read where possible
  - Return findings immediately when critical issue detected (fail-fast)
  - Target: <30 seconds per document validation

- **REQ-NF-4**: Phase commands use incremental saves:
  - Specification generation: Save after each major section (Requirements, Constraints, Acceptance Tests)
  - Plan generation: Save after Architecture, Technical Decisions, Integration Strategy
  - Task breakdown: Save after each task defined (incremental append)
  - Prevents API timeout on large documents, enables resumability

### Usability (REQ-NF-5 to REQ-NF-8)

- **REQ-NF-5**: Natural slash command syntax via Claude Code plugin system:
  - Commands defined in `spiral-grove/commands/*.md`
  - SlashCommand tool invocation: `/spiral-grove:command-name [args]`
  - Short aliases registered in plugin.json: `/spec-writing`, `/plan-generation`

- **REQ-NF-6**: Validator reports use structured markdown:
  ```markdown
  ## Validation Report: [Document Type]

  **Status**: ✅ PASS / ⚠️ WARNING / ❌ FAIL

  ### Checks
  - ✅ Check Name: Passed (details)
  - ⚠️ Check Name: Warning (details, recommendation)
  - ❌ Check Name: Failed (details, required action)

  ### Recommendations
  1. [Actionable step]
  2. [Actionable step]

  ### Summary
  [Overall assessment]
  ```

- **REQ-NF-7**: Error messages include resolution steps:
  - Example: "❌ Specification contains implementation details (HOW). **Resolution**: Move technical details to planning phase. Remove code examples and architecture descriptions from Requirements section."
  - Error format: Problem statement + Specific location + Actionable resolution

- **REQ-NF-8**: `spiral-grove-guide` skill auto-invoked when user asks SDD questions:
  - Trigger phrases: "how to use SDD", "what is spec-driven development", "when to use /spec-writing"
  - Skill loads methodology guidance with phase-specific instructions
  - Provides decision trees and quick reference checklists

### Maintainability (REQ-NF-9 to REQ-NF-12)

- **REQ-NF-9**: Template externalization architecture:
  - Commands load templates dynamically via Skill tool invocation
  - Template updates propagate to all commands immediately (no command changes needed)
  - Version tracking in template frontmatter for compatibility checks

- **REQ-NF-10**: Agent reusability across commands:
  - `spec-validator` used by `/spec-writing`, `/review spec`, `/synthesize-specs` (post-synthesis validation)
  - `module-discovery-agent` used by `/synthesize-docs`, `/synthesize-specs`
  - Agent definitions in shared `spiral-grove/agents/` directory
  - Commands reference agents by subagent_type parameter

- **REQ-NF-11**: Metadata detection zero-token implementation:
  - Bash scripts execute outside Claude context
  - Output captured via Bash tool result
  - No prompt tokens consumed for author/date detection
  - Scripts cached for performance (15-minute TTL)

- **REQ-NF-12**: Consistent YAML frontmatter schema:
  ```yaml
  version: X.Y.Z        # Semver
  status: Draft|Under Review|Approved|Ready for Implementation
  created: YYYY-MM-DD   # ISO 8601
  last_updated: YYYY-MM-DD
  authored_by:
    - Name (via Git/P4/ENV detection)
  ```
  - All phase documents use identical frontmatter structure
  - Parsing logic centralized in `sdd-metadata` skill

### Consistency (REQ-NF-13 to REQ-NF-16)

- **REQ-NF-13**: Requirement numbering format enforced by templates:
  - Functional: `REQ-F-1`, `REQ-F-2`, ... `REQ-F-N`
  - Non-functional: `REQ-NF-1`, `REQ-NF-2`, ... `REQ-NF-N`
  - Validator regex checks format compliance: `REQ-(F|NF)-\d+`

- **REQ-NF-14**: Status lifecycle enforcement:
  - Specs: Draft → Under Review → Approved (terminal state, or Superseded if updated)
  - Plans: Draft → Under Review → Approved (terminal state, or Updated if revised)
  - Tasks: Draft → Ready for Implementation → In Progress → Complete
  - Progress: Continuously updated (no discrete states)
  - Validators check status field is valid for document type

- **REQ-NF-15**: CLAUDE.md section structure standardized in `sdd-format-docs`:
  - Required sections: Purpose, Key Components, Public Interface, Integration Points, Common Operations, Testing
  - Optional sections: Performance Considerations, Security, Troubleshooting
  - Validators check section presence and ordering

- **REQ-NF-16**: Validation report structure consistent across all validators:
  - Header: Document type, overall status
  - Two-tier structure: Process Compliance (critical) + Quality Checks (advisory) (NEW in v2.1)
  - Checks: Pass/fail/warning per check with details
  - Examples: Code snippets showing issues (if applicable)
  - Recommendations: Actionable next steps
  - Summary: Overall assessment paragraph

- **REQ-NF-17**: Proportional quality check distribution (NEW in v2.1):
  - Spec validators: 9 quality checks (foundational, most critical phase)
  - Plan validators: 4 quality checks (architectural decisions phase)
  - Tasks validators: 3 quality checks (execution planning phase)
  - Progress validators: 2 quality checks (tracking/documentation phase)
  - Rationale: More critical documents receive deeper quality scrutiny

### Reliability (REQ-NF-18 to REQ-NF-21)

- **REQ-NF-18**: Synthesis resumability via manifest state:
  - Manifest updated after each module completion (atomic write)
  - On command re-invocation, check manifest for completed modules
  - Skip completed modules, resume from first non-completed module
  - Manifest includes timestamp, status (pending/in-progress/completed/failed)

- **REQ-NF-19**: Validator graceful error handling:
  - Try-catch around document parsing (malformed YAML frontmatter)
  - If parse fails: Return warning report with message "Document malformed, could not validate. Please check YAML frontmatter syntax."
  - Continue validation of parseable sections (partial validation better than crash)

- **REQ-NF-20**: Module discovery resilience:
  - Check directory existence before Glob (avoid errors on missing paths)
  - Handle empty files gracefully (skip if no content to analyze)
  - Continue processing if individual module fails (log error, proceed to next)
  - Return partial results rather than failing entire discovery

- **REQ-NF-21**: Hand-edit preservation validation:
  - Check for unclosed markers: regex match `<!-- BEGIN: HAND-EDITED -->` count equals `<!-- END: HAND-EDITED -->` count
  - If mismatch: Warn user "Hand-edited markers are malformed. Skipping preservation to avoid data loss."
  - Validate marker placement (not inside code blocks)
  - Backup original file before regeneration (copy to `.bak` extension)

### Interoperability (REQ-NF-22 to REQ-NF-25)

- **REQ-NF-22**: Language-agnostic design:
  - No hardcoded language assumptions in commands/agents
  - Module discovery uses generic patterns (file structure, not syntax)
  - Documentation generation describes behavior (not language-specific constructs)
  - Tested with: TypeScript, Python, Go, Rust, Java, C++, Unreal Engine C++

- **REQ-NF-23**: Language-specific pattern detection in `module-discovery-agent`:
  - TypeScript/JavaScript: import/export statements, package.json
  - Python: import statements, __init__.py, setup.py
  - Go: import statements, go.mod
  - Rust: use statements, Cargo.toml
  - Java: import statements, pom.xml/build.gradle
  - C++: #include directives, CMakeLists.txt

- **REQ-NF-24**: Framework-agnostic documentation:
  - No assumptions about project structure (src/ vs lib/ vs app/)
  - No assumptions about build tools (webpack vs vite vs rollup)
  - No assumptions about test frameworks (jest vs mocha vs pytest)
  - Documentation describes module purpose/interface, not framework integration

- **REQ-NF-25**: Manifest JSON standard format:
  - Follows JSON Schema Draft 7
  - Schema files in `sdd-format-docs/docs/manifest-schema.json`
  - Parseable by any JSON-compliant tool
  - Cross-command integration: `/synthesize-docs` manifest can be read by `/synthesize-specs`

---

## Explicit Constraints Implementation

Commands and agents enforce these constraints via validation checks and explicit instructions:

| Constraint | Implementation | Enforced By |
|------------|----------------|-------------|
| DO NOT include implementation code in specs | Spec template instructions, spec-validator checks for code blocks | `spec-validator` agent |
| DO NOT allow technology choices in spec phase | Spec template omits Technology section, validator flags tech mentions | `spec-validator` agent |
| DO NOT permit vague success criteria | Validator regex checks for measurable terms (numbers, percentages, "95%", "<100ms") | `spec-validator` agent |
| DO NOT allow XL/XXL tasks | Validator flags any task with complexity > L (5 points), recommends breakdown | `tasks-validator` agent |
| DO NOT update task documents with progress | Template instructs: "Progress tracked in `.sdd/progress/`, NOT in tasks document" | `/implementation` command |
| DO NOT modify hand-edited sections | Synthesizer extracts markers, regenerates around them, merges preserved content | `module-doc-synthesizer` agent |
| DO NOT exceed 400-line CLAUDE.md limit | Synthesizer word count check, condensing strategies if over limit | `module-doc-synthesizer` agent |
| DO NOT proceed without validation approval | Commands spawn validators before phase transition, require user approval | All phase commands |
| DO NOT implement multiple tasks in parallel | Command instructs: "Implement ONE task at a time, mark complete before proceeding" | `/implementation` command |
| DO NOT allow silent deviations | Progress template requires Deviations section, command checks for user approval | `/implementation` command |
| DO NOT block on advisory quality warnings (NEW v2.1) | Validators distinguish Process Compliance (blocking) from Quality Checks (advisory), user can proceed with warnings | All validator agents |
| DO NOT skip code review step (NEW v2.1) | Implementation command enforces three-tier validation workflow (code review → spec compliance → progress quality) | `/implementation` command |

---

## Technical Architecture Details

### File System Structure

```
.sdd/
├── specs/                          # Specification documents
│   ├── feature-a.md                # Single feature spec
│   ├── parent-feature.md           # Parent spec
│   └── parent-feature/             # Child specs
│       ├── child-a.md
│       └── child-b.md
├── plans/                          # Technical plans
│   ├── feature-a-plan.md
│   └── parent-feature/
│       ├── child-a-plan.md
│       └── child-b-plan.md
├── tasks/                          # Task breakdowns
│   ├── feature-a-tasks.md
│   └── parent-feature/
│       ├── child-a-tasks.md
│       └── child-b-tasks.md
├── progress/                       # Implementation tracking
│   ├── feature-a-progress.md
│   └── parent-feature/
│       ├── child-a-progress.md
│       └── child-b-progress.md
├── module-manifest.json            # Synthesis state for /synthesize-docs
└── spec-manifest.json              # Synthesis state for /synthesize-specs
```

### Data Flow: Specification to Implementation

```
User Input
    ↓
/spec-writing command
    ↓
Load sdd-templates skill (spec template)
Load sdd-metadata skill (author, date)
    ↓
Generate spec with user collaboration
Save to .sdd/specs/[feature].md
    ↓
Spawn spec-validator agent
    ↓
Present validation report to user
User approves or requests changes
    ↓
Update spec status: Draft → Under Review → Approved
    ↓
/plan-generation command
    ↓
Read approved spec
Explore codebase (Glob/Grep)
Load sdd-templates skill (plan template)
    ↓
Generate plan with architectural decisions
Save to .sdd/plans/[feature]-plan.md
    ↓
Spawn plan-validator agent
Validate spec alignment, rationale presence
    ↓
Update plan status: Approved
    ↓
/task-breakdown command
    ↓
Read approved plan
Load sdd-templates skill (tasks template)
    ↓
Generate task list with sizing, dependencies
Save to .sdd/tasks/[feature]-tasks.md
    ↓
Spawn tasks-validator agent
Check sizing, independence, acceptance criteria
    ↓
Update tasks status: Ready for Implementation
    ↓
/implementation command
    ↓
Read ready tasks
Load sdd-templates skill (progress template)
Create .sdd/progress/[feature]-progress.md
    ↓
FOR EACH task:
    Spawn implementation agent with task context
    Agent writes code, runs tests
    Spawn spec-acceptance-validator agent
    Validate implementation against spec criteria
    Update progress document: task status → Completed
    IF deviation required:
        Document in progress with rationale
        Get user approval
    END IF
END FOR
    ↓
Spawn progress-validator agent
Check deviation tracking, test coverage
    ↓
Final report: All tasks completed
```

### Agent Execution Pattern

**Delegation Flow**:
1. Command identifies work requiring fresh context (validation, synthesis, implementation)
2. Command invokes Task tool with:
   - `subagent_type`: Agent name (e.g., "spiral-grove:spec-validator")
   - `description`: Brief task summary
   - `prompt`: Detailed instructions with context
3. Claude Code spawns agent in fresh context (no history bloat)
4. Agent executes autonomously using available tools (Read, Glob, Grep, Write, Bash)
5. Agent returns structured result (report, generated file, validation findings)
6. Command receives agent result, presents to user, coordinates next step

**Benefits**:
- **Context isolation**: Each agent starts fresh (avoids bloated conversation history)
- **Reusability**: Same agent used by multiple commands
- **Parallelization**: Multiple agents can run concurrently (synthesis batches)
- **Specialization**: Each agent optimized for specific task type

### Metadata Detection Implementation

**Author Detection** (`sdd-metadata/scripts/detect-author.sh`):
```bash
#!/bin/bash
# Priority: Git → P4 → ENV → Unknown
if git config user.name &>/dev/null; then
    git config user.name
elif p4 info &>/dev/null; then
    p4 info | grep "User name:" | cut -d: -f2 | xargs
elif [ -n "$USER" ]; then
    echo "$USER"
else
    echo "Unknown"
fi
```

**Date Generation** (`sdd-metadata/scripts/generate-date.sh`):
```bash
#!/bin/bash
# ISO 8601 format: YYYY-MM-DD
date +"%Y-%m-%d"
```

**Invocation** (from command):
```markdown
Use Bash tool to execute: bash spiral-grove/skills/sdd-metadata/scripts/detect-author.sh
Capture output, use as authored_by in YAML frontmatter.
```

### Manifest Schema

**Module Manifest** (`.sdd/module-manifest.json`):
```json
{
  "version": "1.0.0",
  "lastUpdated": "2025-10-31T12:00:00Z",
  "modules": [
    {
      "name": "authentication-service",
      "path": "src/services/auth",
      "status": "completed",
      "lastSynthesized": "2025-10-31T11:45:00Z",
      "documentPath": "src/services/auth/CLAUDE.md"
    },
    {
      "name": "payment-gateway",
      "path": "src/services/payment",
      "status": "pending",
      "lastSynthesized": null,
      "documentPath": null
    }
  ]
}
```

**Spec Manifest** (`.sdd/spec-manifest.json`):
```json
{
  "version": "1.0.0",
  "lastUpdated": "2025-10-31T12:00:00Z",
  "modules": [
    {
      "name": "authentication-service",
      "path": "src/services/auth",
      "status": "completed",
      "lastSynthesized": "2025-10-31T11:50:00Z",
      "specPath": ".sdd/specs/authentication-service.md",
      "driftDetected": true,
      "driftSummary": "3 added requirements, 1 missing implementation"
    }
  ]
}
```

---

## Integration Points

### Claude Code Plugin System

**Registration**: `spiral-grove/.claude-plugin/plugin.json`
```json
{
  "name": "spiral-grove",
  "version": "1.0.0",
  "description": "Spec-Driven Development methodology for Claude Code",
  "author": { "name": "Epic Games", "email": "gsdwig@gmail.com" },
  "commands": ["spec-writing", "plan-generation", "task-breakdown", "implementation", "review", "synthesize-docs", "synthesize-specs"],
  "skills": ["spiral-grove-guide", "sdd-templates", "sdd-metadata", "sdd-format-docs"],
  "agents": ["spec-validator", "plan-validator", "tasks-validator", "progress-validator", "spec-acceptance-validator", "module-discovery-agent", "module-doc-synthesizer", "module-spec-synthesizer"]
}
```

**Installation**: User runs `/plugin install spiral-grove@claude-code-plugins` → Claude Code reads marketplace, downloads plugin, registers components

### Git Version Control

**Author Detection**: Commands invoke `git config user.name` via Bash tool to populate `authored_by` field in YAML frontmatter

**No Auto-Commits**: Plugin does NOT automatically commit SDD documents. User controls version control workflow.

### Perforce Version Control (Optional)

**Author Detection Fallback**: If Git unavailable, commands invoke `p4 info` to detect P4 username

**Integration with perforce-hooks**: If perforce-hooks plugin installed, SDD documents automatically opened for edit via `p4 edit` when modified

### Environment Variables

**Metadata Fallback**: If Git/P4 unavailable, author detected from `$USER` or `$USERNAME` environment variables

---

## Acceptance Test Implementation

### AT-1: Specification Generation with Validation

**Implementation**:
1. User invokes `/spec-writing` command
2. Command loads spec template from `sdd-templates` skill
3. Command guides user through structured prompts for each section
4. Command saves draft spec to `.sdd/specs/[feature].md`
5. Command automatically spawns `spec-validator` agent with Task tool
6. Validator reads spec, checks: WHAT vs HOW separation (regex for code blocks, tech terms), numbered requirements (REQ-F-N format), measurable success criteria (regex for numbers/percentages)
7. Validator returns structured report with pass/fail/warning per check
8. Command presents report to user: "Validation complete. [Summary]. Would you like to update spec status?"
9. User reviews findings, addresses critical issues or approves proceeding
10. Command updates spec status field: Draft → Under Review (if approved)

**Validation Example**:
```markdown
## Validation Report: Specification

**Status**: ⚠️ WARNING

### Checks
✅ Requirements Numbered: All requirements use REQ-F-N format
❌ Phase Boundary Violation: Specification contains implementation details
  - Line 45: "Use JWT tokens for authentication" (technology choice)
  - Line 67: Code example showing API endpoint structure
⚠️ Vague Success Criteria: "System should be fast" (Line 32)
  - Recommendation: Replace with measurable target (e.g., "95th percentile response time <200ms")

### Recommendations
1. Move technology choices (JWT) to planning phase
2. Remove code examples from specification
3. Make success criteria measurable

### Summary
Specification has good requirement structure but violates phase boundaries. Address critical issues before proceeding to planning.
```

### AT-4: Implementation with Deviation Tracking

**Implementation**:
1. User invokes `/implementation` command
2. Command reads ready tasks from `.sdd/tasks/[feature]-tasks.md`
3. Command loads progress template from `sdd-templates` skill
4. Command creates `.sdd/progress/[feature]-progress.md` with task status table
5. FOR first task:
   - Command spawns implementation agent via Task tool with subagent_type=general-purpose
   - Agent receives context: spec excerpt (relevant requirements), plan excerpt (architecture), task details (acceptance criteria)
   - Agent implements task (writes code, runs tests)
   - Agent returns: files changed, test results
6. Command spawns `spec-acceptance-validator` agent
   - Validator receives: task ID, spec acceptance criteria, list of changed files
   - Validator checks: Does implementation satisfy acceptance criteria?
   - Validator returns: pass/fail with rationale
7. IF validator passes:
   - Command updates progress document: task status → Completed
   - Command moves to next task
8. IF deviation required during implementation:
   - Agent reports: "Task cannot be completed as specified. Reason: [explanation]"
   - Command prompts user: "Implementation requires deviation from spec. Document deviation and proceed? (yes/no)"
   - IF user approves:
     - Command adds to progress document Deviations section: What changed, Why, Impact, User approval timestamp
     - Agent proceeds with adjusted implementation
9. Repeat until all tasks complete

**Deviation Example** (in progress document):
```markdown
## Deviations

### Deviation 1: Authentication Token Format
- **Task**: TASK-3 (Implement JWT authentication)
- **Original Spec**: Use JWT tokens with 1-hour expiration
- **Actual Implementation**: Use 15-minute expiration with refresh tokens
- **Rationale**: Security audit required shorter expiration. Spec updated to REQ-NF-5 (modified).
- **Impact**: Additional refresh token endpoint needed (TASK-8 added)
- **Approved By**: User (2025-10-31T14:30:00Z)
```

### AT-6: Documentation Synthesis with Module Discovery

**Implementation**:
1. User invokes `/synthesize-docs` (no scope argument)
2. Command spawns `module-discovery-agent` via Task tool
3. Agent performs heuristic analysis:
   - Glob for package manifests: `**/{package.json,Cargo.toml,go.mod,setup.py}`
   - Glob for entry points: `**/{index.ts,main.py,main.go,__init__.py}`
   - Analyze directory structure: src/, lib/, modules/ directories
   - Detect module boundaries: Each package.json = module, each top-level src/ subdirectory = module
4. Agent returns discovered module list: `[{ name, path, type }]`
5. Command presents list to user with count: "Discovered 15 modules. Review list? [Yes/No]"
6. User approves list (can edit to exclude/add modules)
7. Command creates `.sdd/module-manifest.json` with modules (status: pending)
8. Command processes modules in batches of 10:
   - Batch 1: Spawn 10 `module-doc-synthesizer` agents in parallel via Task tool (10 tool calls in single message)
   - Each agent receives: module name, module path
   - Each agent: Reads code, analyzes structure, generates CLAUDE.md, saves to `[module-path]/CLAUDE.md`
   - Each agent checks word count, applies condensing if >400 lines
   - Each agent returns: success/failure, file path
9. Command updates manifest after each agent completes: status → completed, timestamp
10. Command waits for batch completion, displays progress: "Batch 1/2 complete (10/15 modules)"
11. Repeat for remaining batches
12. Command presents summary: "Synthesis complete. 15 CLAUDE.md files generated. Manifest: .sdd/module-manifest.json"

**Module Discovery Example**:
```markdown
## Discovered Modules

1. **authentication-service** (src/services/auth) - Package
2. **payment-gateway** (src/services/payment) - Package
3. **user-management** (src/services/user) - Package
4. **api-gateway** (src/gateway) - Directory
5. **database-client** (src/db) - Directory
...

Total: 15 modules

Proceed with synthesis? [Yes/No]
```

---

## Common Questions & Troubleshooting

### Q: Why does spec-validator flag my architecture diagram?

**A**: Specifications should focus on WHAT to build (requirements, capabilities), not HOW to build (architecture, technology). Architecture diagrams belong in the planning phase. Move the diagram to your technical plan document.

### Q: Can I update a specification after implementation started?

**A**: Yes! Specifications are living documents. If requirements change during implementation:
1. Update the spec document (increment version number)
2. Document changes in changelog section
3. Re-run `/plan-generation` to update plan if needed
4. Add new tasks via `/task-breakdown` if scope increased
5. Document the spec update in progress document Deviations section

### Q: How do I resume synthesis if interrupted?

**A**: Manifest files track synthesis state:
- `.sdd/module-manifest.json` for `/synthesize-docs`
- `.sdd/spec-manifest.json` for `/synthesize-specs`

Re-run the same command with same arguments. Command reads manifest, skips completed modules, resumes from first pending module.

### Q: Why are my tasks flagged as XL/XXL?

**A**: Tasks larger than L complexity (>5 points, typically >1 day of work) are too large to implement independently. `tasks-validator` flags these for breakdown. Split into smaller tasks:
- XL task (8 points): Split into 2-3 M tasks
- XXL task (13 points): Split into 3-5 S/M tasks

Each subtask should be independently testable and PR-able.

### Q: Can I customize document templates?

**A**: Yes! Templates are externalized in `spiral-grove/skills/sdd-templates/templates/`:
- `spec-template.md`
- `plan-template.md`
- `tasks-template.md`
- `progress-template.md`

Edit templates directly. Changes apply to all subsequent command invocations (no command modification needed).

### Q: How does hand-edit preservation work?

**A**: When regenerating module CLAUDE.md via `/synthesize-docs`:
1. Agent searches for `<!-- BEGIN: HAND-EDITED -->` markers
2. Extracts content between BEGIN and END markers
3. Generates new documentation from current code
4. Merges preserved content back into new documentation at same marker locations
5. Hand-edited sections remain unchanged

**Usage**: Wrap custom sections in markers:
```markdown
<!-- BEGIN: HAND-EDITED -->
## Custom Implementation Notes
[Your custom content here - will be preserved during regeneration]
<!-- END: HAND-EDITED -->
```

### Q: What if validator finds critical issues?

**A**: Validation reports use two-tier structure (NEW in v2.1):
- **Process Compliance (Critical)**: Format violations, phase boundary issues, missing required fields - MUST be fixed to proceed
- **Quality Checks (Advisory)**: Requirements clarity, rationale depth, testability concerns - warns but doesn't block

**Severity ratings within each tier**:
- **Critical (❌)**: Process compliance failures - blocks progression
- **Warning (⚠️)**: Quality concerns - should be addressed but can proceed with user approval
- **Info (ℹ️)**: Best practices, optional improvements

Commands ask for user approval: "Critical issues found. Fix issues before proceeding? [Yes/No]"

If user chooses "No" for advisory warnings, command documents override in progress/review notes but allows proceeding (user takes responsibility). Process compliance failures MUST be resolved.

---

## Version History

### v2.1.0 (Current - 2025-11-04)
- **Two-tier validation structure**: Process Compliance (blocking) vs Quality Checks (advisory)
- **Quality-focused validation**: 9 spec checks, 4 plan checks, 3 task checks, 2 progress checks
- **Three-tier implementation validation**: Code review → Spec compliance → Progress quality
- **Specialized code reviewer preference**: Language/domain-specific reviewers prioritized
- **Advisory warning handling**: User can proceed despite quality warnings (respects judgment)
- **Proportional quality checks**: More critical phases receive deeper scrutiny

### v2.0.0 (2025-10-31)
- Template externalization via `sdd-templates` skill
- Metadata automation via `sdd-metadata` skill
- Format specifications bundled in `sdd-format-docs` skill
- Agent delegation architecture
- Automatic validator invocation at phase transitions
- Parallel synthesis processing
- Manifest-based resumability

### v1.0.0 (Legacy)
- Monolithic command prompts with embedded templates
- Manual metadata entry
- Sequential synthesis processing
- Manual validator invocation

---

## References

- **Specification**: `.sdd/specs/spiral-grove.md` (v1.1.0 - REQ-F-1 through REQ-F-51, REQ-NF-1 through REQ-NF-25, Acceptance Tests)
- **Charter**: `spiral-grove/skills/spiral-grove-guide/references/CHARTER.md` (Philosophy, Pillars, Principles)
- **Foundations**: `spiral-grove/skills/spiral-grove-guide/references/SDD-FOUNDATIONS.md` (Theoretical background)
- **Quick Reference**: `spiral-grove/skills/spiral-grove-guide/references/SDD-QUICK-REFERENCE.md` (Operational guide)
- **Synthesize Guide**: `spiral-grove/skills/spiral-grove-guide/references/SYNTHESIZE-REFERENCE.md` (Retrofit workflows)

---

**Last Updated**: 2025-11-04
**Maintained By**: Spiral Grove Plugin Team
**For Questions**: See spiral-grove-guide skill or CHARTER.md for project contact info
