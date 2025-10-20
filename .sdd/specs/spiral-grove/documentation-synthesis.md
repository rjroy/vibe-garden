# Documentation Synthesis Feature - Specification

**Version**: 2.0.0
**Status**: Draft
**Created**: 2025-10-19
**Last Updated**: 2025-10-20
**Parent Specification**: [../spiral-grove.md](../spiral-grove.md)

## Executive Summary

Documentation Synthesis extends Spiral Grove with lifecycle management that bridges `.sdd/` specifications (active development) and `CLAUDE.md` files (maintenance). It provides one new command (`/spiral-grove:synthesize-docs`) to generate concise operational documentation from implemented code, and enhances `/spiral-grove:review` to detect when specs drift from reality.

## User Story

As a **developer maintaining large-scale projects (100+ modules) with AI assistance**, I want **a way to keep specs synchronized with evolving code and generate concise operational documentation**, so that **specs remain reliable blueprints for recreation while CLAUDE.md files provide always-loaded context for day-to-day maintenance work**.

## Stakeholders

- **Primary**: Developers working on large-scale projects (50+ modules) with AI-assisted maintenance
- **Secondary**: Teams adopting SDD for long-lived projects that evolve beyond initial specs
- **Tertiary**: Solo developers who need to context-switch between projects frequently

## Success Criteria

1. **Documentation conciseness**: Generated `CLAUDE.md` files are ≤ 400 lines per module (suitable for always-loaded context)
2. **Scalability**: `/spiral-grove:synthesize-docs` successfully processes projects with 100+ modules without timeout or context overflow
3. **Cycle time**: Development → Maintenance transition (running `/spiral-grove:synthesize-docs`) completes in < 5 minutes for 100-module project
4. **Staleness detection**: `/spiral-grove:review spec-vs-code` identifies spec-code divergence with < 5% false positive rate
5. **Detection accuracy**: Drift detection correctly categorizes Missing/Extra/Modified features with < 5% false positive rate

## Functional Requirements

### Component 1: Module Documentation Synthesizer Agent (`module-doc-synthesizer`)

**Purpose**: Reusable agent that analyzes a single module and generates/updates its CLAUDE.md documentation.

**What it does**:
- Analyzes a single module's code, tests, and comments
- Generates concise CLAUDE.md (≤ 400 lines) with structured content:
  - **Purpose**: What this module does
  - **Key Components**: Main classes/functions/files
  - **Public API**: Exported interfaces
  - **Integration Points**: How it connects to other modules
  - **Common Operations**: Typical usage patterns
  - **Testing**: How to test this module
- Updates existing CLAUDE.md while preserving hand-edited sections (between `<!-- BEGIN: HAND-EDITED -->` and `<!-- END: HAND-EDITED -->` markers)
- Follows consistent structure for every module
- Can be invoked standalone (not just via Spiral Grove commands)

**Acceptance criteria**:
- Agent can be spawned multiple times in parallel without conflicts
- Preserves hand-edited sections when updating existing docs
- Generated content is ≤ 400 lines
- Output is valid markdown with no duplicate sections
- Works without Spiral Grove context (reusable for any project)

### Capability 2: Generate Module Documentation (`/spiral-grove:synthesize-docs`)

**Purpose**: Orchestrate documentation generation across entire project using `module-doc-synthesizer` agents.

**What it does**:
- Analyzes codebase to detect logical module boundaries (directories, namespaces, packages)
- Spawns `module-doc-synthesizer` agent for each module (parallel execution)
- Generates root-level CLAUDE.md with project overview linking to module docs
- Adds Spiral Grove-specific context: `**Origin**: .sdd/specs/[name].md` reference to each CLAUDE.md
- Saves module list to `.sdd/module-manifest.json` for resumability
- Can resume from manifest if interrupted (idempotent operation)

**User interaction**:
1. User runs `/spiral-grove:synthesize-docs`
2. System detects module boundaries and presents list for user approval
3. User confirms or adjusts module list
4. System generates/updates CLAUDE.md files
5. System outputs manifest showing created/updated/failed modules

**Acceptance criteria**:
- Detects module boundaries automatically with user approval
- Spawns one `module-doc-synthesizer` agent per module for parallel processing
- Every CLAUDE.md includes `**Origin**: .sdd/specs/[name].md` reference
- Can be re-run safely without breaking existing documentation
- Processes 100 modules in < 5 minutes
- Root CLAUDE.md includes: Project Overview, Architecture, Directory Structure
- Command can resume from manifest after interruption

### Capability 3: Detect Spec-Code Drift (`/spiral-grove:review spec-vs-code`)

**Purpose**: Identify when specifications have become stale relative to actual implementation.

**What it does**:
- Compares specification acceptance criteria against actual implementation and tests
- Detects three categories of drift:
  - **Missing**: Features in spec but not implemented in code
  - **Extra**: Features implemented but not documented in spec
  - **Modified**: Features where behavior changed from spec
- Calculates drift percentage: (missing + extra + modified) / total spec criteria
- Recommends running `/spiral-grove:spec-writing` to update spec when drift > 20%
- Presents findings with specific examples (advisory only, no auto-updates)

**User interaction**:
1. User runs `/spiral-grove:review spec-vs-code [feature-name]`
2. System reads spec from `.sdd/specs/[feature-name].md`
3. System analyzes implementation code and tests
4. System presents structured drift report with recommendations
5. User decides whether to update spec via `/spiral-grove:spec-writing`

**Acceptance criteria**:
- Reports drift in three categories: Missing, Extra, Modified
- Provides specific examples for each category
- Calculates and displays drift percentage
- Suggests `/spiral-grove:spec-writing` when drift > 20%
- Does not modify specs automatically (advisory only)
- Completes comparison in < 1 minute for typical feature (5-20 files)
- Respects parent/child spec hierarchies

## Non-Functional Requirements

### Performance
- `/spiral-grove:synthesize-docs`: Processes 100 modules in < 5 minutes using parallel agent execution
- `/spiral-grove:review spec-vs-code`: Completes comparison in < 1 minute for typical feature (5-20 files)
- Agent parallelization: Multiple modules must be processed concurrently to achieve performance targets

### Usability
- Commands provide progress indicators for long-running operations (e.g., "Analyzing module 15/100")
- Error messages guide users to resolution (e.g., "No spec found at X, run /spiral-grove:spec-writing first")
- Generated CLAUDE.md files are human-readable and editable
- Module boundary detection asks for user confirmation before proceeding

### Maintainability
- CLAUDE.md format documented in `spiral-grove/docs/claude-md-format.md`
- Commands follow same markdown structure as existing Spiral Grove commands
- Hand-edited section preservation uses standard HTML comment markers
- Must follow Claude Code plugin specification for agent, command, and plugin definitions

### Context Efficiency
- Generated CLAUDE.md files consume ≤ 5% of context budget when loaded
- Root CLAUDE.md references children instead of duplicating content

## Explicit Constraints (DO NOT)

- **Do NOT** auto-update specs without user approval (spec-vs-code is advisory only, updates must be done via spec-writing)
- **Do NOT** overwrite hand-edited sections in CLAUDE.md files (respect `<!-- BEGIN: HAND-EDITED -->` markers)
- **Do NOT** generate CLAUDE.md during active development phases (spec/plan/tasks) - only after implementation
- **Do NOT** replace `.sdd/` specs with CLAUDE.md (they serve different purposes)
- **Do NOT** enforce specific module granularity (let users approve detected boundaries)
- **Do NOT** make spec changes during `/spiral-grove:review spec-vs-code` (detect only, don't modify)
- **Do NOT** generate code during any of these commands (documentation only)
- **Do NOT** start documentation generation without saving module manifest first (must be resumable)
- **Guideline**: Keep command prompts concise (~200-400 lines) for maintainability; extract verbose examples and reference material using progressive disclosure (Inherited from parent)
- **Do NOT** replace developer judgment - provide structure, not prescriptive solutions (Inherited from parent)

## Technical Context

**Integration points**:
- Reads from: `.sdd/specs/`, codebase files, existing CLAUDE.md files
- Writes to: `CLAUDE.md` files (module-level and root), `.sdd/module-manifest.json`
- Extends: `/spiral-grove:review` command with new `spec-vs-code` mode

**File formats**:
- Input: Markdown specs, source code (any language), test files, existing CLAUDE.md
- Output: Markdown (CLAUDE.md), JSON (module-manifest.json)

**Module manifest format** (`.sdd/module-manifest.json`):
```json
{
  "generated_at": "2025-10-20T...",
  "modules": [
    {"path": "src/module-a", "status": "pending|completed|failed"},
    {"path": "src/module-b", "status": "pending|completed|failed"}
  ]
}
```

**Must respect**:
- Existing parent/child spec hierarchy conventions
- Spiral Grove phase boundaries (WHAT vs HOW)
- CLAUDE.md format specification (conciseness, linking, structure)
- Hand-edited section markers in CLAUDE.md

## Acceptance Tests

### Test 1: Documentation synthesis at scale
**Given**: Project with 120 modules across 8 subsystems
**When**: Developer runs `/spiral-grove:synthesize-docs`
**Then**:
- Command detects 120 modules, user confirms, manifest saved to `.sdd/module-manifest.json`
- System generates CLAUDE.md ≤ 400 lines for each module with consistent structure
- Root CLAUDE.md created with project overview and links to subsystems
- Each CLAUDE.md includes `**Origin**: .sdd/specs/[name].md` reference
- Entire process completes in < 5 minutes
- Final output shows: "Generated 121 CLAUDE.md files (1 root + 120 modules)"

### Test 2: Preserve hand-edited content
**Given**: Existing `CLAUDE.md` with hand-edited "Common Gotchas" section:
```markdown
<!-- BEGIN: HAND-EDITED -->
## Common Gotchas
- Database connection pool must be warmed before first request
- Cache invalidation requires manual trigger on config changes
<!-- END: HAND-EDITED -->
```
**When**: Developer runs `/spiral-grove:synthesize-docs` to update documentation after refactoring
**Then**:
- Generated content updates all auto-generated sections
- Hand-edited "Common Gotchas" section remains verbatim at original location
- Output CLAUDE.md is valid markdown with no duplicate sections

### Test 3: Spec-code drift detection
**Given**: "Shopping cart" spec with 8 acceptance criteria, but implementation added "wishlist" and "save for later" features not in spec
**When**: Developer runs `/spiral-grove:review spec-vs-code shopping-cart`
**Then**:
- Report shows: 8/8 original criteria met, 2 extra features detected
- Drift categorization: 0 Missing, 2 Extra, 0 Modified
- Drift percentage: 20% (2 extra / 10 total features)
- Recommendation: "Consider running `/spiral-grove:spec-writing` to update the spec and document new features"
- No automatic changes to spec (advisory only)

### Test 4: Development-Maintenance-Development cycle
**Given**: Completed "payment processing" feature with all tasks done
**When**: Developer runs full cycle:
1. `/spiral-grove:synthesize-docs` (generate CLAUDE.md for maintenance)
2. [6 months pass, code evolves during bug fixes]
3. `/spiral-grove:review spec-vs-code payment-processing` (detect drift)
4. `/spiral-grove:spec-writing` (update spec based on drift findings)
5. `/spiral-grove:spec-writing` (start new related feature)

**Then**:
- Step 1: Generates concise CLAUDE.md with payment API, common operations
- Step 3: Detects 15% drift (minor changes during bug fixes)
- Step 4: User updates spec to reflect current implementation, preserves original rationale where applicable
- Step 5: New feature spec can reference updated payment-processing spec accurately
- Developer can recreate current payment system from updated spec

### Test 5: Resumability after interruption
**Given**: `/spiral-grove:synthesize-docs` was interrupted after completing 60/120 modules
**When**: Developer re-runs `/spiral-grove:synthesize-docs`
**Then**:
- Command reads `.sdd/module-manifest.json`
- Identifies 60 modules with status "completed", 60 with "pending"
- Skips already-completed modules
- Generates docs only for 60 pending modules
- Updates manifest as modules complete
- Final output shows: "Generated 121 CLAUDE.md files (60 existing + 61 new)"

### Test 6: Hierarchical project with child specs
**Given**: Parent spec `dashboard-controller.md` with 5 child specs in `dashboard-controller/` directory
**When**: Developer runs `/spiral-grove:synthesize-docs dashboard-controller`
**Then**:
- Detects 5 child spec areas in codebase
- Generates root `CLAUDE.md` for dashboard controller
- Generates CLAUDE.md for each of 5 child modules
- Each child CLAUDE.md references its originating child spec via `**Origin**`
- Root CLAUDE.md includes links to child CLAUDE.md files
- Directory structure mirrors spec hierarchy

## Open Questions

- [ ] Should `/spiral-grove:synthesize-docs` support custom module detection rules (e.g., "treat each service in services/ as a module")?
- [ ] How should we handle specs that have no corresponding code (planned but not implemented)?
- [ ] Should the manifest track partial completion within a module (in case generation fails mid-process)?

## Out of Scope

- **Real-time sync**: Specs and CLAUDE.md are updated on-demand, not automatically on code changes
- **Version control integration**: Commands don't auto-commit changes (user commits manually)
- **Diff visualization**: Changes presented as text diffs, not visual diff tools
- **Multi-language CLAUDE.md**: Documentation is English-only (like Spiral Grove commands)
- **Automated testing**: Commands don't run tests to validate implementations (they read existing test results)
- **Code refactoring**: Commands document existing code, don't suggest changes
- **CLAUDE.md for third-party dependencies**: Only covers project code, not external libraries
