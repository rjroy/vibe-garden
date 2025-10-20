# Documentation Synthesis Feature - Specification

**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-19
**Last Updated**: 2025-10-19
**Parent Specification**: [../spiral-grove.md](../spiral-grove.md)

## Executive Summary

Documentation Synthesis extends Spiral Grove with lifecycle management capabilities that bridge the gap between `.sdd/` specifications and actual code. It introduces a two-phase documentation system: `.sdd/` for active development (with decision rationale), and `CLAUDE.md` for maintenance (concise operational docs). One new command (`/spiral-grove:synthesize-docs`) and an enhancement to the existing `/spiral-grove:review` command enable developers to synthesize operational documentation from implementation and detect when specs become stale (requiring manual update via `/spiral-grove:spec-writing`).

## User Story

As a **developer maintaining large-scale projects (100+ modules) with AI assistance**, I want **a way to keep specs synchronized with evolving code and generate concise operational documentation**, so that **specs remain reliable blueprints for recreation while CLAUDE.md files provide always-loaded context for day-to-day maintenance work**.

## Stakeholders

- **Primary**: Developers working on large-scale projects (50+ modules) with AI-assisted maintenance
- **Secondary**: Teams adopting SDD for long-lived projects that evolve beyond initial specs
- **Tertiary**: Solo developers who need to context-switch between projects frequently

## Success Criteria

1. **Documentation conciseness**: Generated `CLAUDE.md` files are ≤ 400 lines per module (suitable for always-loaded context)
2. **Scalability**: `/spiral-grove:synthesize-docs` successfully processes projects with 100+ modules using agent parallelization without timeout or context overflow
3. **Cycle time**: Development → Maintenance transition (running `/spiral-grove:synthesize-docs`) completes in < 5 minutes for 100-module project
4. **Staleness detection**: `/spiral-grove:review spec-vs-code` identifies spec-code divergence with < 5% false positive rate
5. **Detection accuracy**: Drift detection correctly categorizes Missing/Extra/Modified features with < 5% false positive rate

## Functional Requirements

### Component 1: Module Documentation Synthesizer Agent (`module-doc-synthesizer`)

**Purpose:** Standalone agent that analyzes a single module and generates/updates its CLAUDE.md documentation.

**Capabilities:**
- Analyze a single module's code, tests, and comments
- Generate concise CLAUDE.md (≤ 400 lines) with structured content
- Update existing CLAUDE.md while preserving hand-edited sections
- Follow a consistent routine for every module analysis
- Extract operational knowledge (WHAT/HOW) from implementation
- Identify key components, APIs, integration points, and common operations
- Preserve content between `<!-- BEGIN: HAND-EDITED -->` and `<!-- END: HAND-EDITED -->` markers

**Agent File Structure** (`agents/module-doc-synthesizer.md`):
```markdown
---
description: Analyzes a single module and generates/updates its CLAUDE.md documentation
capabilities: ["module-documentation", "claude-md-generation", "hand-edit-preservation"]
---

# Module Documentation Synthesizer

This agent analyzes a single module and generates concise CLAUDE.md documentation.

## Capabilities

- Generate CLAUDE.md files ≤ 400 lines
- Preserve hand-edited sections marked with HTML comments
- Extract operational knowledge from code and tests
- Follow consistent documentation structure

## When to use this agent

- When generating documentation for a single module
- When updating existing module documentation after changes
- When part of larger documentation synthesis orchestration

## Agent Routine (executed every time)

[Detailed step-by-step routine as specified in acceptance criteria]
```

**Agent Routine (executed every time):**
1. Check if CLAUDE.md exists for this module
2. If exists: Read and identify hand-edited sections
3. Analyze module implementation (code + tests)
4. Generate structured CLAUDE.md content:
   - **Purpose**: What this module does
   - **Key Components**: Main classes/functions/files
   - **Public API**: Exported interfaces
   - **Integration Points**: How it connects to other modules
   - **Common Operations**: Typical usage patterns
   - **Testing**: How to test this module
5. If updating: Merge new content with preserved hand-edited sections
6. Validate output ≤ 400 lines
7. Write CLAUDE.md to disk

**Acceptance Criteria:**
- Agent can be invoked standalone (not just via Spiral Grove command)
- Follows same routine every time (consistency across modules)
- Preserves hand-edited sections when updating
- Generated content is concise (≤ 400 lines)
- Output is valid markdown with no duplicate sections
- Can be spawned multiple times in parallel without conflicts

---

### Command 1: Synthesize Documentation (`/spiral-grove:synthesize-docs`)

**Purpose:** Orchestrate documentation generation across entire project using module-doc-synthesizer agents.

**Capabilities:**
- Detect logical module boundaries in codebase (directories, namespaces, packages)
- Save module list to file for resumability
- Spawn module-doc-synthesizer agent for each module
- Add Spiral Grove-specific context (link to .sdd/specs)
- Generate root-level CLAUDE.md with project overview
- Support hierarchical documentation structures

**Workflow:**
1. **Module Discovery Phase:**
   - Scan codebase to detect module boundaries
   - Present module list to user for approval
   - Save approved list to `.sdd/module-manifest.json` (for resumability)

2. **Documentation Generation Phase:**
   - For each module in manifest:
     - Spawn `module-doc-synthesizer` agent with module path
     - Agent generates/updates module's CLAUDE.md
   - Generate root CLAUDE.md with project overview

3. **Spiral Grove Integration Phase:**
   - For each CLAUDE.md file:
     - Spawn `module-doc-synthesizer` to add `**Origin**` reference
     - Analyze .sdd/specs to find appropriate spec for this module
     - Update CLAUDE.md with: `**Origin**: Implemented from .sdd/specs/[name].md`

4. **Completion:**
   - Output file manifest showing all CLAUDE.md files created/updated
   - Report any modules that failed (for manual retry)

**Acceptance Criteria:**
- Detects module boundaries automatically (with user approval)
- Saves module list to `.sdd/module-manifest.json` before starting generation
- Can resume from manifest if interrupted (idempotent)
- Spawns one module-doc-synthesizer per module (parallel execution)
- Every CLAUDE.md includes `**Origin**: .sdd/specs/[name].md` reference
- Root CLAUDE.md includes: Project Overview, Architecture, Directory Structure
- Outputs manifest showing created/updated/failed modules
- Command can be re-run safely (updates existing docs without breaking them)

### Command 2: Add Spec-Code Comparison Mode to `/spiral-grove:review`

**Capabilities:**
- Extend existing `/spiral-grove:review [spec|plan|tasks|progress]` command with new `spec-vs-code` mode
- Compare specification acceptance criteria against actual implementation tests
- Detect when specs have become stale (implementation diverged without spec update)
- Identify features implemented that are not in spec (scope creep)
- Identify spec requirements that are not implemented (incomplete work)
- Suggest running `/spiral-grove:spec-writing` to update spec when significant drift detected
- Quantify drift percentage (% of spec criteria not matching implementation)

**Acceptance Criteria:**
- Accepts `spec-vs-code` as argument: `/spiral-grove:review spec-vs-code [feature-name]`
- Reads spec from `.sdd/specs/[feature-name].md`
- Analyzes implementation code and tests for the feature
- Compares spec acceptance tests against actual test suite
- Reports drift in three categories: Missing (in spec, not in code), Extra (in code, not in spec), Modified (behavior changed)
- Calculates drift percentage: (missing + extra + modified) / total spec criteria
- If drift > 20%: recommends running `/spiral-grove:spec-writing` to update the spec
- Presents findings in structured format with specific examples
- Does not auto-update specs (advisory only, user must manually update via spec-writing)

### Cross-Command Integration

**Two-phase documentation workflow:**
- **Development → Maintenance**: After implementation completes, run `/spiral-grove:synthesize-docs` to generate CLAUDE.md files
- **Maintenance → Development**: Before starting new development, run `/spiral-grove:review spec-vs-code` to detect drift, then use `/spiral-grove:spec-writing` to sync specs with reality

**Agent-Command Separation:**
- `module-doc-synthesizer` agent can be used standalone (not just via Spiral Grove)
- `/spiral-grove:synthesize-docs` uses the agent for orchestration
- Agent is reusable across any project (not Spiral Grove specific)
- Command adds SDD-specific logic (spec linking) on top of agent

**Hierarchy awareness:**
- All commands respect parent/child spec structures
- `/spiral-grove:synthesize-docs` generates CLAUDE.md hierarchy mirroring code structure (not necessarily spec structure)
- `/spiral-grove:review spec-vs-code` compares child specs to their code sections

## Non-Functional Requirements

### Performance
- `/spiral-grove:synthesize-docs`: Processes 100 modules in < 5 minutes using agent parallelization
- `/spiral-grove:review spec-vs-code`: Completes comparison in < 1 minute for typical feature (5-20 files)
- Agent spawning: Each agent operates independently with isolated context (no cross-agent dependencies)

### Usability
- Commands provide progress indicators for long-running operations (e.g., "Analyzing module 15/100")
- Error messages guide users to resolution (e.g., "No spec found at X, run /spiral-grove:spec-writing first")
- Generated CLAUDE.md files are human-readable and editable
- Retrofit changes are presented as diffs before user approval
- Module boundary detection asks for user confirmation before proceeding

### Maintainability
- CLAUDE.md format documented in `spiral-grove/docs/claude-md-format.md`
- Commands follow same markdown structure as existing Spiral Grove commands
- Agent spawning logic is reusable across commands
- Hand-edited section preservation uses standard HTML comment markers

### Context Efficiency
- Generated CLAUDE.md files consume ≤ 5% of context budget when loaded
- Agent parallelization prevents context overflow on large projects
- Module detection algorithm prefers natural boundaries (directories, namespaces)
- Root CLAUDE.md references children instead of duplicating content

## Explicit Constraints (DO NOT)

- **Do NOT** auto-update specs without user approval (spec-vs-code is advisory only, updates must be done via spec-writing)
- **Do NOT** overwrite hand-edited sections in CLAUDE.md files (respect `<!-- BEGIN: HAND-EDITED -->` markers)
- **Do NOT** generate CLAUDE.md during active development phases (spec/plan/tasks) - only after implementation
- **Do NOT** replace `.sdd/` specs with CLAUDE.md (they serve different purposes)
- **Do NOT** enforce specific module granularity (let users approve detected boundaries)
- **Do NOT** make spec changes during `/spiral-grove:review spec-vs-code` (detect only, don't modify)
- **Do NOT** generate code during any of these commands (documentation only)
- **Do NOT** couple module-doc-synthesizer agent to Spiral Grove (keep it standalone/reusable)
- **Do NOT** start documentation generation without saving module manifest first (must be resumable)
- **Guideline**: Keep command and agent prompts concise (~200-400 lines) for maintainability; extract verbose examples and reference material using progressive disclosure (Inherited from parent)
- **Context efficiency note**: Agent prompts typically consume 3-5% of available context budget; prioritize clarity and completeness over arbitrary length limits (Inherited from parent)
- **Do NOT** replace developer judgment - provide structure, not prescriptive solutions (Inherited from parent)

## Technical Context

- **Existing system**: Spiral Grove plugin with four-phase SDD workflow
- **Integration points**:
  - Reads from: `.sdd/specs/`, codebase files, existing CLAUDE.md files
  - Writes to: `CLAUDE.md` files (module-level and root), `.sdd/module-manifest.json`
  - Uses: Claude Code agent spawning (Task tool with subagent_type)
  - Extends: `/spiral-grove:review` command with new mode
- **File formats**:
  - Input: Markdown specs, source code (any language), test files, existing CLAUDE.md
  - Output: Markdown (CLAUDE.md), JSON (module-manifest.json)
- **Agent architecture**:
  - **module-doc-synthesizer agent**: Standalone, reusable, single-module focused
    - Location: `agents/module-doc-synthesizer.md` in plugin root
    - File format: Markdown with frontmatter (as per Claude Code plugin spec)
    - Frontmatter fields:
      - `description`: "Analyzes a single module and generates/updates its CLAUDE.md documentation"
      - `capabilities`: ["module-documentation", "claude-md-generation", "hand-edit-preservation"]
    - Input: module path, optional existing CLAUDE.md
    - Output: CLAUDE.md content (≤ 400 lines)
    - Follows consistent routine every invocation
    - Preserves hand-edited sections
  - **Command orchestration**: `/spiral-grove:synthesize-docs`
    - Phase 1: Detect modules → save to manifest
    - Phase 2: Spawn module-doc-synthesizer per module (using Task tool with subagent_type)
    - Phase 3: Add SDD-specific context (spec links)
    - Uses manifest for resumability
- **Module manifest format** (`.sdd/module-manifest.json`):
  ```json
  {
    "generated_at": "2025-10-20T...",
    "modules": [
      {"path": "src/module-a", "status": "pending|completed|failed"},
      {"path": "src/module-b", "status": "pending|completed|failed"}
    ]
  }
  ```
- **Must respect**:
  - Existing parent/child spec hierarchy conventions
  - Spiral Grove phase boundaries (WHAT vs HOW)
  - CLAUDE.md format specification (conciseness, linking, structure)
  - Hand-edited section markers in CLAUDE.md

## Acceptance Tests

### Test 1: Documentation synthesis at scale
**Given**: Project with 120 modules across 8 subsystems
**When**: Developer runs `/spiral-grove:synthesize-docs`
**Then**:
- **Phase 1 (Discovery)**: Command detects 120 modules, user confirms, manifest saved to `.sdd/module-manifest.json`
- **Phase 2 (Generation)**: System spawns 120 `module-doc-synthesizer` agents (one per module in parallel)
- Each agent generates CLAUDE.md ≤ 400 lines with consistent structure
- Root CLAUDE.md created with project overview and links to subsystems
- **Phase 3 (SDD Integration)**: Command adds `**Origin**: .sdd/specs/[name].md` to each CLAUDE.md
- Entire process completes in < 5 minutes
- Manifest updated with status for each module (120 completed, 0 failed)
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
- `module-doc-synthesizer` agent reads existing CLAUDE.md
- Agent identifies hand-edited section markers
- Agent generates updated content (new components, APIs)
- Agent merges new content with preserved "Common Gotchas" section
- Output CLAUDE.md is valid markdown with no duplicate sections
- Hand-edited section remains verbatim at original location

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
- Spawns agents only for 60 pending modules
- Updates manifest as modules complete
- Final output shows: "Generated 121 CLAUDE.md files (60 existing + 61 new)"

### Test 6: Standalone agent usage
**Given**: Developer wants to document a single module without running full synthesis
**When**: Developer invokes `module-doc-synthesizer` agent directly with path to module
**Then**:
- Agent analyzes the single module
- Agent generates CLAUDE.md ≤ 400 lines
- CLAUDE.md includes all standard sections (Purpose, Components, API, etc.)
- Works without any Spiral Grove context (no .sdd/ directory needed)
- Output does not include `**Origin**` reference (only added by Spiral Grove command)

### Test 7: Hierarchical project with child specs
**Given**: Parent spec `dashboard-controller.md` with 5 child specs in `dashboard-controller/` directory
**When**: Developer runs `/spiral-grove:synthesize-docs dashboard-controller`
**Then**:
- Detects 5 child spec areas in codebase
- Generates root `CLAUDE.md` for dashboard controller
- Spawns `module-doc-synthesizer` for each of 5 child modules
- Each child CLAUDE.md references its originating child spec via `**Origin**`
- Root CLAUDE.md includes links to child CLAUDE.md files
- Directory structure mirrors spec hierarchy

## Open Questions

- [ ] Should `/spiral-grove:synthesize-docs` support custom module detection rules (e.g., "treat each service in services/ as a module")?
- [ ] How should we handle specs that have no corresponding code (planned but not implemented)?
- [ ] Should module-doc-synthesizer agent have configurable templates for different module types (API, CLI, library)?
- [ ] Should the manifest track partial completion within a module (in case agent fails mid-generation)?

## Out of Scope

- **Real-time sync**: Specs and CLAUDE.md are updated on-demand, not automatically on code changes
- **Version control integration**: Commands don't auto-commit changes (user commits manually)
- **Diff visualization**: Changes presented as text diffs, not visual diff tools
- **Multi-language CLAUDE.md**: Documentation is English-only (like Spiral Grove commands)
- **Automated testing**: Commands don't run tests to validate implementations (they read existing test results)
- **Code refactoring**: Commands document existing code, don't suggest changes
- **CLAUDE.md for third-party dependencies**: Only covers project code, not external libraries
