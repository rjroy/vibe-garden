# Spiral Grove Plugin

**Last Generated**: 2025-11-04T00:00:00Z

## Purpose

A Claude Code plugin implementing Spec-Driven Development (SDD) methodology through a structured four-phase workflow: Specification → Planning → Task Breakdown → Implementation. Enables production-grade feature development with explicit requirements, architectural decisions, task decomposition, and progress tracking. Features quality-focused validation with two-tier structure (process compliance vs quality checks) and three-tier implementation validation (code review, spec compliance, progress quality).

## Key Components

### Commands (`commands/*.md`)

Slash commands that execute specific SDD workflow phases:

- `spec-writing.md`: Creates feature specifications defining requirements and success criteria
- `plan-generation.md`: Generates technical plans with architectural decisions and rationale
- `task-breakdown.md`: Decomposes plans into discrete, implementable tasks
- `implementation.md`: Executes tasks with progress tracking and deviation management
- `review.md`: Validates phase documents before progression (spec/plan/tasks/progress)
- `synthesize-docs.md`: Generates operational CLAUDE.md documentation from implementation
- `synthesize-specs.md`: Reverse-engineers specifications from existing codebases

### Agents (`agents/*.md`)

Autonomous agents invoked by commands for complex operations:

**Validators** (5 agents with two-tier validation):
- `spec-validator.md`: Validates specifications (process compliance + 9 quality checks)
- `plan-validator.md`: Validates technical plans (process compliance + 4 quality checks)
- `tasks-validator.md`: Validates task breakdowns (process compliance + 3 quality checks)
- `progress-validator.md`: Validates progress tracking (process compliance + 2 quality checks)
- `spec-acceptance-validator.md`: Validates implementation against spec acceptance criteria

**Synthesizers** (3 agents):
- `module-discovery-agent.md`: Detects logical module boundaries using heuristics
- `module-doc-synthesizer.md`: Analyzes single module implementation to generate CLAUDE.md (≤400 lines)
- `module-spec-synthesizer.md`: Reverse-engineers specifications from module code

### Skills (`skills/`)

Contextual guidance and resources invoked automatically when working with SDD:

**spiral-grove-guide**:
- `SKILL.md`: Main skill entry point with workflow guidance
- `references/SDD-FOUNDATIONS.md`: Academic foundations and methodology theory
- `references/SDD-QUICK-REFERENCE.md`: Practical operational guide
- `references/SYNTHESIZE-REFERENCE.md`: Documentation and spec synthesis guidance
- `references/SPIRAL-GROVE-IMPLEMENTATION-DETAIL.md`: Technical implementation reference (v2.1.0)

**sdd-templates**: Externalized document templates (spec, plan, tasks, progress)
**sdd-metadata**: Author/date detection scripts for YAML frontmatter
**sdd-format-docs**: Format specifications and schemas for CLAUDE.md and manifests

### Documentation (`docs/*.md`)

Format specifications and schemas:

- `claude-md-format.md`: CLAUDE.md structure specification (root vs module, sections, constraints)
- `module-manifest-schema.md`: JSON schema for documentation synthesis state tracking
- `spec-manifest-schema.md`: JSON schema for specification synthesis state tracking

### Configuration

- `.claude-plugin/plugin.json`: Plugin metadata (name: "spiral-grove", version: "2.1.0", author: Ronald Roy)

## Public API

**Installation**:
```bash
/plugin install spiral-grove@claude-code-plugins
```

**Core Workflow Commands**:
- `/spec-writing` → Creates `.sdd/specs/[feature].md`
- `/plan-generation` → Creates `.sdd/plans/[feature]-plan.md`
- `/task-breakdown` → Creates `.sdd/tasks/[feature]-tasks.md`
- `/implementation` → Executes tasks, creates `.sdd/progress/[feature]-progress.md`

**Validation & Synthesis Commands**:
- `/review [spec|plan|tasks|progress]` → Validates phase documents
- `/synthesize-docs [module]` → Generates `[module]/CLAUDE.md`
- `/synthesize-specs [module]` → Generates `.sdd/specs/[module].md` from code

**Skill**:
- `spiral-grove-guide` → Auto-invoked for methodology guidance

## Integration Points

**Dependencies**:
- Claude Code plugin system (slash commands, skills, agents)
- `.sdd/` directory structure (specs/, plans/, tasks/, progress/)
- Module CLAUDE.md files for operational documentation
- Manifest files for resumability (module-manifest.json, spec-manifest.json)

**File System Structure Created**:
```
project-root/
├── .sdd/
│   ├── specs/              # Feature specifications
│   ├── plans/              # Technical plans
│   ├── tasks/              # Task breakdowns
│   ├── progress/           # Implementation tracking
│   ├── module-manifest.json    # Doc synthesis state
│   └── spec-manifest.json      # Spec synthesis state
└── [modules]/
    └── CLAUDE.md           # Generated documentation
```

**Parent/Child Hierarchies**:
- Large projects organized hierarchically: `.sdd/specs/parent.md` with children at `.sdd/specs/parent/child-a.md`
- Mirrors across all phases (plans/, tasks/, progress/)

## Common Operations

### Starting New Feature with SDD

**Steps**:
1. Install plugin: `/plugin install spiral-grove@claude-code-plugins`
2. Create specification: `/spec-writing`
3. Generate technical plan: `/plan-generation`
4. Break down tasks: `/task-breakdown`
5. Implement: `/implementation`

**Example**:
```
User: I want to build a rate limiting system for our API
Claude: [Invokes /spec-writing]
→ Creates .sdd/specs/api-rate-limiter.md
→ Prompts for requirements, success criteria, constraints
```

### Validating Phase Documents

**Purpose**: Ensure document quality before progressing to next phase

**Steps**:
1. Complete phase document (spec/plan/tasks)
2. Run validation: `/review [type]`
3. Address validation findings
4. Proceed to next phase

**Example**:
```
/review spec
→ Checks for measurable success criteria
→ Verifies no HOW details in spec
→ Confirms all requirements numbered
```

### Generating Documentation Post-Implementation

**Purpose**: Create operational CLAUDE.md from implemented code

**Steps**:
1. Complete implementation
2. Run synthesis: `/synthesize-docs [module-path]`
3. Review generated CLAUDE.md
4. Add hand-edited content between markers if needed

**Example**:
```
/synthesize-docs src/auth
→ Analyzes auth module code
→ Generates src/auth/CLAUDE.md (≤400 lines)
→ Preserves existing hand-edited sections
```

### Reverse-Engineering Specs from Legacy Code

**Purpose**: Bootstrap SDD workflow on existing codebases

**Steps**:
1. Run spec synthesis: `/synthesize-specs [module-path]`
2. Review generated specifications
3. Use as baseline for future SDD workflow

**Example**:
```
/synthesize-specs src/payment
→ Analyzes payment module implementation
→ Generates .sdd/specs/payment.md
→ Extracts requirements from code/tests
```

## Command Implementation Patterns

### Spec Writing (`/spec-writing`)

**Key Behaviors**:
- Asks clarifying questions to extract requirements
- Pushes for measurable success criteria ("fast" → "95th percentile < 200ms")
- Numbers all requirements (REQ-F-N, REQ-NF-N format)
- Works incrementally, saves often to avoid timeouts
- Stays at WHAT level (capabilities), avoids HOW (implementation)

**Anti-Verbosity Principle**: Command prompts are detailed to guide Claude, but output specs are concise and scannable.

### Plan Generation (`/plan-generation`)

**Key Behaviors**:
- Analyzes existing codebase before designing (Glob/Grep patterns)
- Maps technical decisions to spec requirements (references REQ-F-N)
- Documents rationale for all choices (WHY decisions made)
- Designs whole system (data, errors, security, testing)
- Works incrementally, saves sections progressively

**Target Size**: 15-25 pages for typical features

### Task Breakdown (`/task-breakdown`)

**Key Behaviors**:
- Creates independently implementable tasks (single PR each)
- Each task: 2-8 hours work, clear acceptance criteria
- Maps tasks to plan architecture
- Identifies dependencies and critical path
- Typical feature: 10-20 tasks (not 40+)

**Conciseness Check**: Consolidates redundant tasks before finalizing

### Implementation (`/implementation`)

**Key Behaviors**:
- Works one task at a time
- Updates progress in `.sdd/progress/` only (never modifies task documents)
- Refers back to spec constantly
- **Three-tier validation** (NEW in v2.1.0):
  1. Code review (architecture, security, error handling, performance)
  2. Spec compliance (validates against acceptance criteria)
  3. Progress quality (non-blocking advisory feedback)
- Default: Writing tests includes fixing failures (overridable)
- Respects branching strategy from project CLAUDE.md

**Testing Strategy**: Tests that fail indicate incomplete implementation unless explicitly overridden

**Code Review**: Prefers specialized reviewers (language/domain-specific) over general-purpose. Three-tier feedback: Approve/Minor → Concerns/Major → Reject/Blockers

### Review (`/review [type]`)

**Key Behaviors**:
- Performs semantic validation (not just keyword matching)
- **Two-tier validation structure** (NEW in v2.1.0):
  - **Process Compliance** (critical/blocking): Format violations, phase boundaries, required fields
  - **Quality Checks** (advisory/warning): Requirements clarity, rationale depth, testability
- Presents structured findings (pass/fail/warning)
- Never updates status automatically (waits for user approval)
- Advisory warnings don't block progression (respects user judgment)
- Type-specific checks (spec: no HOW details, plan: rationale present, tasks: acceptance criteria defined)

**Validation Types**:
- `spec`: Phase boundary (WHAT vs HOW), measurable criteria, numbered requirements + 9 quality checks (clarity, completeness, testability, consistency, feasibility, dependencies, error coverage, security, acceptance criteria)
- `plan`: Technical rationale, requirement mapping, integration points + 4 quality checks (rationale quality, alternative analysis, implementability, risk awareness)
- `tasks`: Independence, sizing, acceptance criteria, spec mapping + 3 quality checks (acceptance criteria quality, task clarity, testing approach)
- `progress`: Deviation tracking, status accuracy + 2 quality checks (deviation rationale quality, completion evidence)

**Proportional Quality**: More critical phases (spec) receive deeper quality scrutiny than tracking phases (progress)

### Synthesize Docs (`/synthesize-docs`)

**Key Behaviors**:
- Three-phase workflow: Discovery → Approval → Generation
- Spawns multiple module-doc-synthesizer agents in parallel
- Preserves hand-edited content between `<!-- BEGIN: HAND-EDITED -->` markers
- Creates `.sdd/module-manifest.json` for resumability
- 400-line limit per module CLAUDE.md (applies condensing strategies)

**Agent Routine** (module-doc-synthesizer):
1. Check existing CLAUDE.md
2. Preserve hand-edited sections
3. Analyze module (Glob source files, Grep exports, Read tests)
4. Generate structured content (Purpose, Components, API, Integration, Operations, Testing)
5. Merge preserved sections
6. Validate ≤400 lines
7. Return markdown content

### Synthesize Specs (`/synthesize-specs`)

**Key Behaviors**:
- Reverse-engineers WHAT from HOW (code → requirements)
- Spawns multiple module-spec-synthesizer agents in parallel
- Detects drift between synthesized and existing specs
- Creates `.sdd/spec-manifest.json` for resumability
- Enables SDD adoption on legacy codebases

## Testing

**Test Approach**: Plugin commands are markdown prompts loaded into Claude's context. Testing involves:
1. Installing plugin locally
2. Invoking commands and verifying expanded prompts appear
3. Validating command behavior and output structure
4. Checking file creation in `.sdd/` directories

**Key Scenarios**:
- Workflow progression (spec → plan → tasks → implementation)
- Validation catches phase boundary violations
- Parent/child hierarchy creation and navigation
- Hand-edited section preservation during documentation regeneration
- Resumability after interruption (manifest state tracking)

**No Automated Tests**: Plugin is prompt-based; validation through usage

## Design Philosophy

**Core Premise**: Claude is a literal-minded but highly capable pair programmer who excels with explicit, detailed instructions.

**Methodology Principles**:
1. **Separation of Concerns**: WHAT (spec) vs HOW (plan) vs STEPS (tasks)
2. **Clarity over Brevity**: Unambiguous requirements prevent drift
3. **Consistency**: Structured phases maintain coherence across sessions
4. **Completeness**: Nothing falls through cracks (every requirement traced)
5. **Traceability**: Implementation maps back to requirements (REQ-F-N references)
6. **Adaptability**: Phases can be revisited when requirements change

**Anti-Patterns**:
- Skipping phases (each builds on previous)
- Silent deviations (always document WHY implementation differs)
- Implementation in spec (keep WHAT separate from HOW)
- Vague success criteria ("fast" not measurable)
- Missing rationale (document WHY decisions made)

## Decision Rules

**When to Use SDD**:
- Production features (multiple files/components)
- Long-running work (spans multiple sessions)
- Strict requirements (compliance, security)
- Complex integrations
- 3+ distinct steps or multiple files

**When to Use Quick Prompts**:
- Bug fixes (clear, isolated)
- Simple utilities
- UI tweaks
- Prototypes
- One-off scripts

## Constraints

**Module CLAUDE.md**:
- Maximum 400 lines (≈2K tokens)
- Framework-agnostic (works on any codebase)
- Hand-edited sections preserved during regeneration
- Must include Origin field (links to spec)

**Spec Requirements**:
- All functional requirements numbered (REQ-F-N)
- All non-functional requirements numbered (REQ-NF-N)
- Success criteria measurable
- No technology choices (WHAT not HOW)

**Task Breakdown**:
- Tasks independent (single PR each)
- Task size: 2-8 hours (<1 day)
- Typical feature: 10-20 tasks

**Progress Tracking**:
- Progress only in `.sdd/progress/` (never in task documents)
- Real-time updates during implementation
- Deviations documented immediately

## Version History

**v2.1.0** (2025-11-04):
- Two-tier validation structure (Process Compliance vs Quality Checks)
- Quality-focused validation (9 spec / 4 plan / 3 task / 2 progress checks)
- Three-tier implementation validation (code review → spec compliance → progress quality)
- Specialized code reviewer preference (language/domain-specific prioritized)
- Advisory warning handling (user can proceed despite quality warnings)
- Proportional quality checks (critical phases receive deeper scrutiny)

**v2.0.0** (2025-10-31):
- Template externalization via sdd-templates skill
- Metadata automation via sdd-metadata skill
- Format specifications bundled in sdd-format-docs skill
- Agent delegation architecture (8 total agents)
- Automatic validator invocation at phase transitions
- Parallel synthesis processing (10 agents concurrently)
- Manifest-based resumability

**v1.0.0** (Legacy):
- Initial SDD workflow implementation
- Monolithic command prompts with embedded templates
- Manual metadata entry
- Sequential synthesis processing

<!-- BEGIN: HAND-EDITED -->
<!-- Users can add custom sections here -->
<!-- END: HAND-EDITED -->
