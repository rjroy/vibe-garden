# Documentation Synthesis Feature - Specification

**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-19
**Last Updated**: 2025-10-19
**Parent Specification**: [../spiral-grove.md](../spiral-grove.md)

## Executive Summary

Documentation Synthesis extends Spiral Grove with lifecycle management capabilities that bridge the gap between `.sdd/` specifications and actual code. It introduces a two-phase documentation system: `.sdd/` for active development (with decision rationale), and `CLAUDE.md` for maintenance (concise operational docs). Two new commands (`/retrofit-spec`, `/synthesize-docs`) and an enhancement to the existing `/review` command enable developers to retrofit specs to match reality, synthesize operational documentation from implementation, and detect when specs become stale.

## User Story

As a **developer maintaining large-scale projects (100+ modules) with AI assistance**, I want **a way to keep specs synchronized with evolving code and generate concise operational documentation**, so that **specs remain reliable blueprints for recreation while CLAUDE.md files provide always-loaded context for day-to-day maintenance work**.

## Stakeholders

- **Primary**: Developers working on large-scale projects (50+ modules) with AI-assisted maintenance
- **Secondary**: Teams adopting SDD for long-lived projects that evolve beyond initial specs
- **Tertiary**: Solo developers who need to context-switch between projects frequently

## Success Criteria

1. **Spec fidelity**: `/retrofit-spec` produces specs that accurately reflect implementation reality in 90%+ of cases (validated by spec-vs-code review)
2. **Documentation conciseness**: Generated `CLAUDE.md` files are ≤ 400 lines per module (suitable for always-loaded context)
3. **Scalability**: `/synthesize-docs` successfully processes projects with 100+ modules using agent parallelization without timeout or context overflow
4. **Cycle time**: Development → Maintenance transition (running `/synthesize-docs`) completes in < 5 minutes for 100-module project
5. **Recreation fidelity**: Project recreated from retrofitted spec matches original implementation in 85%+ of functional tests
6. **Staleness detection**: `/review spec-vs-code` identifies spec-code divergence with < 5% false positive rate

## Functional Requirements

### Command 1: Retrofit Specification (`/retrofit-spec`)

**Capabilities:**
- Analyze current implementation to identify deviations from existing spec
- Update specification to accurately reflect "as-built" implementation
- Preserve original decision rationale where still applicable
- Document evolution from original spec to current reality
- Generate "Spec Evolution" section showing what changed and why
- Validate that retrofitted spec could recreate the current implementation
- Support both parent and child specs in hierarchical projects

**Acceptance Criteria:**
- Compares existing spec acceptance criteria against actual implementation tests
- Identifies functional requirements that were added, modified, or removed
- Updates technical context to reflect actual technologies used
- Preserves success criteria that are still relevant
- Adds "Spec Evolution" section documenting changes from original version
- Outputs updated spec with version incremented (e.g., 1.0.0 → 1.1.0)
- Does not lose historical decision rationale from original spec
- Prompts user to approve changes before writing updated spec

### Command 2: Synthesize Documentation (`/synthesize-docs`)

**Capabilities:**
- Generate hierarchical `CLAUDE.md` files from implementation + specs
- Detect logical module boundaries in codebase (directories, namespaces, packages)
- Spawn one agent per module for parallel analysis (for projects with 50+ modules)
- Extract WHAT/HOW from code, tests, and originating specs
- Create both root-level and module-level `CLAUDE.md` files
- Link each `CLAUDE.md` to its originating spec for decision rationale
- Preserve hand-edited sections marked with `<!-- BEGIN: HAND-EDITED -->` tags
- Support progressive refinement (update existing CLAUDE.md files without losing hand-edits)

**Acceptance Criteria:**
- Detects module boundaries automatically (with user approval of module list)
- For projects ≥ 50 modules: spawns agent per module to preserve context efficiency
- Each module's `CLAUDE.md` includes: Purpose, Key Components, Public API, Integration Points, Common Operations, Testing
- Root `CLAUDE.md` includes: Project Overview, Architecture, Key Design Patterns, Directory Structure
- Every `CLAUDE.md` includes `**Origin**: Implemented from .sdd/specs/[name].md` reference
- Generated files are ≤ 400 lines per module (concise enough for always-loaded context)
- Preserves content between `<!-- BEGIN: HAND-EDITED -->` and `<!-- END: HAND-EDITED -->` markers
- Outputs file manifest showing which CLAUDE.md files were created/updated

### Enhancement: Add Spec-Code Comparison Mode to `/review`

**Capabilities:**
- Extend existing `/review [spec|plan|tasks|progress]` command with new `spec-vs-code` mode
- Compare specification acceptance criteria against actual implementation tests
- Detect when specs have become stale (implementation diverged without spec update)
- Identify features implemented that are not in spec (scope creep)
- Identify spec requirements that are not implemented (incomplete work)
- Suggest running `/retrofit-spec` when significant drift detected
- Quantify drift percentage (% of spec criteria not matching implementation)

**Acceptance Criteria:**
- Accepts `spec-vs-code` as argument: `/review spec-vs-code [feature-name]`
- Reads spec from `.sdd/specs/[feature-name].md`
- Analyzes implementation code and tests for the feature
- Compares spec acceptance tests against actual test suite
- Reports drift in three categories: Missing (in spec, not in code), Extra (in code, not in spec), Modified (behavior changed)
- Calculates drift percentage: (missing + extra + modified) / total spec criteria
- If drift > 20%: recommends running `/retrofit-spec`
- Presents findings in structured format with specific examples
- Does not auto-update specs (advisory only)

### Cross-Command Integration

**Two-phase documentation workflow:**
- **Development → Maintenance**: After implementation completes, run `/synthesize-docs` to generate CLAUDE.md files
- **Maintenance → Development**: Before starting new development, run `/retrofit-spec` to sync specs with reality, then begin new spec cycle

**Hierarchy awareness:**
- All commands respect parent/child spec structures
- `/retrofit-spec` can update parent or child specs independently
- `/synthesize-docs` generates CLAUDE.md hierarchy mirroring code structure (not necessarily spec structure)
- `/review spec-vs-code` compares child specs to their code sections

## Non-Functional Requirements

### Performance
- `/retrofit-spec`: Completes analysis in < 2 minutes for medium projects (10-50 files)
- `/synthesize-docs`: Processes 100 modules in < 5 minutes using agent parallelization
- `/review spec-vs-code`: Completes comparison in < 1 minute for typical feature (5-20 files)
- Agent spawning: Each agent operates independently with isolated context (no cross-agent dependencies)

### Usability
- Commands provide progress indicators for long-running operations (e.g., "Analyzing module 15/100")
- Error messages guide users to resolution (e.g., "No spec found at X, run /spec-writing first")
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

- **Do NOT** auto-update specs without user approval (retrofit is advisory, not automatic)
- **Do NOT** overwrite hand-edited sections in CLAUDE.md files (respect `<!-- BEGIN: HAND-EDITED -->` markers)
- **Do NOT** generate CLAUDE.md during active development phases (spec/plan/tasks) - only after implementation
- **Do NOT** replace `.sdd/` specs with CLAUDE.md (they serve different purposes)
- **Do NOT** enforce specific module granularity (let users approve detected boundaries)
- **Do NOT** spawn agents for small projects (< 50 modules) - overhead not justified
- **Do NOT** make spec changes during `/review spec-vs-code` (detect only, don't modify)
- **Do NOT** generate code during any of these three commands (documentation only)

## Technical Context

- **Existing system**: Spiral Grove plugin with four-phase SDD workflow
- **Integration points**:
  - Reads from: `.sdd/specs/`, `.sdd/plans/`, `.sdd/progress/`, codebase files
  - Writes to: `.sdd/specs/` (retrofit), `CLAUDE.md` files (synthesize)
  - Uses: Claude Code agent spawning (Task tool with subagent_type)
  - Extends: `/review` command with new mode
- **File formats**:
  - Input: Markdown specs, source code (any language), test files
  - Output: Markdown (specs and CLAUDE.md)
- **Agent architecture**:
  - Each spawned agent receives: module path, originating spec path, plan path
  - Each agent outputs: CLAUDE.md content for its module
  - Orchestrator collects outputs and writes files
- **Must respect**:
  - Existing parent/child spec hierarchy conventions
  - Spiral Grove phase boundaries (WHAT vs HOW)
  - CLAUDE.md format specification (conciseness, linking, structure)

## Acceptance Tests

### Test 1: Retrofit workflow
**Given**: Implementation of "user notifications" feature that added email templates not in original spec
**When**: Developer runs `/retrofit-spec user-notifications`
**Then**:
- Command identifies 3 new functional requirements (email templates, scheduling, retry logic)
- Presents diff showing spec additions
- User approves changes
- Updated spec version increments to 1.1.0
- "Spec Evolution" section documents additions with rationale
- Original decision rationale for notification system is preserved

### Test 2: Documentation synthesis at scale
**Given**: Project with 120 modules across 8 subsystems
**When**: Developer runs `/synthesize-docs`
**Then**:
- Command detects 120 modules organized by directory structure
- User confirms module boundaries
- System spawns 120 agents (one per module)
- Each agent generates CLAUDE.md ≤ 400 lines
- Root CLAUDE.md created with project overview and links to subsystems
- All CLAUDE.md files include `**Origin**` reference to originating spec
- Entire process completes in < 5 minutes
- File manifest shows 121 files created (1 root + 120 modules)

### Test 3: Preserve hand-edited content
**Given**: Existing `CLAUDE.md` with hand-edited "Common Gotchas" section:
```markdown
<!-- BEGIN: HAND-EDITED -->
## Common Gotchas
- Database connection pool must be warmed before first request
- Cache invalidation requires manual trigger on config changes
<!-- END: HAND-EDITED -->
```
**When**: Developer runs `/synthesize-docs` to update documentation after refactoring
**Then**:
- Generated CLAUDE.md includes updated components and APIs
- "Common Gotchas" section is preserved verbatim
- New sections are added around hand-edited content
- File is valid markdown with no duplicate sections

### Test 4: Spec-code drift detection
**Given**: "Shopping cart" spec with 8 acceptance criteria, but implementation added "wishlist" and "save for later" features not in spec
**When**: Developer runs `/review spec-vs-code shopping-cart`
**Then**:
- Report shows: 8/8 original criteria met, 2 extra features detected
- Drift categorization: 0 Missing, 2 Extra, 0 Modified
- Drift percentage: 20% (2 extra / 10 total features)
- Recommendation: "Consider running `/retrofit-spec shopping-cart` to document new features"
- No automatic changes to spec (advisory only)

### Test 5: Development-Maintenance-Development cycle
**Given**: Completed "payment processing" feature with all tasks done
**When**: Developer runs full cycle:
1. `/synthesize-docs` (generate CLAUDE.md for maintenance)
2. [6 months pass, code evolves during bug fixes]
3. `/review spec-vs-code payment-processing` (detect drift)
4. `/retrofit-spec payment-processing` (sync spec to reality)
5. `/spec-writing` (start new related feature)

**Then**:
- Step 1: Generates concise CLAUDE.md with payment API, common operations
- Step 3: Detects 15% drift (minor changes during bug fixes)
- Step 4: Updates spec to reflect current implementation, preserves original rationale
- Step 5: New feature spec can reference updated payment-processing spec accurately
- Developer can recreate current payment system from retrofitted spec

### Test 6: Hierarchical project with child specs
**Given**: Parent spec `dashboard-controller.md` with 5 child specs in `dashboard-controller/` directory
**When**: Developer runs `/synthesize-docs dashboard-controller`
**Then**:
- Detects 5 child spec areas in codebase
- Generates root `CLAUDE.md` for dashboard controller
- Generates 5 module-level CLAUDE.md files for child features
- Each child CLAUDE.md references its originating child spec
- Root CLAUDE.md includes links to child CLAUDE.md files
- Directory structure mirrors spec hierarchy

## Open Questions

- [ ] Should `/synthesize-docs` support custom module detection rules (e.g., "treat each service in services/ as a module")?
- [ ] How should we handle specs that have no corresponding code (planned but not implemented)?
- [ ] Should `/retrofit-spec` create a backup of the original spec before updating?
- [ ] What's the right threshold for spawning agents (50 modules? 100? configurable)?

## Out of Scope

- **Real-time sync**: Specs and CLAUDE.md are updated on-demand, not automatically on code changes
- **Version control integration**: Commands don't auto-commit changes (user commits manually)
- **Diff visualization**: Changes presented as text diffs, not visual diff tools
- **Multi-language CLAUDE.md**: Documentation is English-only (like Spiral Grove commands)
- **Automated testing**: Commands don't run tests to validate implementations (they read existing test results)
- **Code refactoring**: Commands document existing code, don't suggest changes
- **CLAUDE.md for third-party dependencies**: Only covers project code, not external libraries
