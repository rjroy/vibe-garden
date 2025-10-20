# Documentation Synthesis - Task Breakdown

**Specification**: [../../specs/spiral-grove/documentation-synthesis.md](../../specs/spiral-grove/documentation-synthesis.md)
**Plan**: [../../plans/spiral-grove/documentation-synthesis-plan.md](../../plans/spiral-grove/documentation-synthesis-plan.md)
**Parent Tasks**: [../spiral-grove-tasks.md](../spiral-grove-tasks.md)
**Version**: 2.0.0
**Status**: In Progress
**Created**: 2025-10-20
**Last Updated**: 2025-10-20

## Summary

**Total Tasks**: 18 (reduced from 23 via consolidation)
**Completed**: 11/18 (61%)
**Estimated Remaining**: 8-12 hours

**Categories**:
- Foundation (2) - Format specs
- Agent (3) - Module doc synthesizer
- Command (6) - Orchestration + review extension
- Testing (6) - Acceptance validation
- Release (1) - Version bump

---

## Foundation

### TASK-001: CLAUDE.md Format Spec
**Status**: Complete | **Estimate**: 2h | **Dependencies**: None

Document CLAUDE.md structure for agent and manual editing.

**Deliverables**:
- `spiral-grove/docs/claude-md-format.md` with required sections, hand-edit markers, templates, constraints
- Examples of valid module and root CLAUDE.md files

**Acceptance**: Format defines ≤400 line constraint, marker syntax, all required sections

**Commit**: 05b2da3

### TASK-002: Module Manifest Schema
**Status**: Complete | **Estimate**: 1h | **Dependencies**: None

Document `.sdd/module-manifest.json` schema for resumability.

**Deliverables**:
- Schema in `spiral-grove/docs/module-manifest-schema.md` or inline in synthesize-docs command
- Example manifest with all status types (pending/completed/failed)

**Acceptance**: Schema defines generated_at, project_root, modules array with path/status/claude_md_path/error fields

**Commit**: 05b2da3

## Agent

### TASK-003: Module Doc Synthesizer Agent
**Status**: Complete | **Estimate**: 8-10h | **Dependencies**: TASK-001

Create `module-doc-synthesizer` agent (framework-agnostic, parallel-safe, idempotent).

**Deliverables**:
- `spiral-grove/agents/module-doc-synthesizer.md` with YAML frontmatter and 7-step routine
- Hand-edited section preservation via `<!-- BEGIN/END: HAND-EDITED -->` markers
- 400-line validation with condensing retry
- Documentation: invocation guide, code analysis guidelines, examples

**Acceptance**:
- Generates CLAUDE.md ≤400 lines with all required sections
- Preserves hand-edits verbatim on update
- Works standalone (no SDD dependencies)
- Parallel-safe (multiple instances don't conflict)

**Commit**: a01a09c (core), befadee (docs)

## Command

### TASK-004: Synthesize-Docs Command Structure
**Status**: Complete | **Estimate**: 1h | **Dependencies**: TASK-001, TASK-002

Create `/spiral-grove:synthesize-docs` command with 3-phase workflow.

**Deliverables**:
- `spiral-grove/commands/synthesize-docs.md` with YAML frontmatter, role definition, prerequisites, workflow structure

**Acceptance**: Command discoverable, YAML valid, documents 3 phases (discovery → generation → SDD integration)

**Commit**: fe97e22

### TASK-005: Phase 1 - Module Discovery
**Status**: Complete | **Estimate**: 3h | **Dependencies**: TASK-004

Implement module boundary detection with user approval.

**Deliverables**:
- Glob-based heuristics: package files, 3+ source files + tests, standard dirs (src/, lib/)
- Exclusions: node_modules/, vendor/, .git/, dist/, build/
- User approval prompt before proceeding
- Manifest save to `.sdd/module-manifest.json`

**Acceptance**: Language-agnostic detection, editable manifest, handles 0 modules gracefully

**Commit**: b0a3c1d

### TASK-006: Phase 2 - Parallel Generation
**Status**: Complete | **Estimate**: 4-5h | **Dependencies**: TASK-003, TASK-005

Spawn agents in parallel, write CLAUDE.md files, generate root doc.

**Deliverables**:
- Parallel Task tool invocation (single message with multiple calls)
- Status tracking: pending → completed/failed with error messages
- Root CLAUDE.md generation with project overview, directory structure, module index
- Progress indicators and graceful failure handling

**Acceptance**: 100 modules in <5 min, all files written, manifest updated, failures don't block other modules

**Commit**: 5f2bdcc

### TASK-007: Phase 3 - SDD Integration
**Status**: Complete | **Estimate**: 2-3h | **Dependencies**: TASK-006

Add `**Origin**` references linking CLAUDE.md to specs.

**Deliverables**:
- Fuzzy matching: module path → spec file (exact, shortened, directory name)
- Origin field insertion after title
- Parent/child spec hierarchy support
- Warnings for unmatched modules (utility code without specs)

**Acceptance**: Matched modules get Origin field, unmatched modules warn, hand-edits preserved during re-write

**Commit**: 910a52e

### TASK-008: Resumability + Reporting
**Status**: Not Started | **Estimate**: 3h | **Dependencies**: TASK-006, TASK-007

Implement idempotent re-runs and comprehensive output reporting.

**Implementation approach**:

1. **On command start**, check if `.sdd/module-manifest.json` exists:
   - If not: Start fresh (proceed to Phase 1)
   - If yes: Read and parse manifest, count statuses

2. **Status assessment**:
   - Count modules by status: completed, failed, pending
   - If all completed: Prompt "All modules complete. Re-run to regenerate all? [y/n]"
   - If partial: Prompt "Found X pending/failed modules. Continue from where we left off? [y/n]"
   - If user declines: Exit gracefully

3. **Resume logic**:
   - Filter manifest to only pending/failed modules
   - Skip Phase 1 (module discovery) - use existing manifest
   - Run Phase 2 only on filtered list
   - Run Phase 3 on all modules (in case new specs added)
   - Update manifest timestamps

4. **Output reporting** (final summary):
   - Total count: "Generated X CLAUDE.md files (Y root + Z modules)"
   - Status breakdown: "Completed: X, Failed: Y"
   - Linked modules: "Modules with Origin field: X"
   - Unlinked modules: "Modules without specs: X (list names)"
   - Failed modules: "Failed: module-name (error message)" with retry guidance
   - Total time: "Completed in X seconds"
   - Manifest location: "Progress saved to .sdd/module-manifest.json"

5. **Edge cases**:
   - 0 modules detected: "No modules found. Try manual manifest or specific directory."
   - All failed: List all errors, suggest reviewing heuristics
   - Interrupted mid-run: Next run picks up seamlessly

**Deliverables**:
- Resumption logic in synthesize-docs.md command
- User prompts with clear options
- Comprehensive final report with counts and guidance
- Timestamp updates in manifest

**Acceptance**:
- Re-running interrupted session completes only remaining modules
- All edge cases handled with helpful messages
- Report shows counts, failures, and next steps

### TASK-009: Review Extension - Spec-vs-Code Mode
**Status**: Not Started | **Estimate**: 6-8h | **Dependencies**: None (extends review.md)

Add drift detection mode to `/spiral-grove:review` for detecting spec-code divergence.

**Implementation approach**:

1. **Command structure**:
   - Add `spec-vs-code` to argument-hint in review.md frontmatter
   - New mode section after existing review modes
   - Usage: `/spiral-grove:review spec-vs-code [feature-name]`

2. **Spec criteria extraction**:
   - Read `.sdd/specs/[feature-name].md`
   - Parse "Acceptance Criteria" or "Acceptance Tests" section
   - Extract each criterion (bullet points, numbered lists, checklist items)
   - Store as array of criterion objects: {text, keywords}

3. **Test suite discovery**:
   - Use Glob to find test files: `**/*test*.{js,ts,py,go}`, `**/test_*.py`, etc.
   - Filter to likely feature tests (filename contains feature name or subdirectory match)
   - Read test files with Read tool

4. **Semantic matching algorithm**:
   - For each spec criterion:
     - Tokenize: extract keywords (nouns, verbs), remove stop words
     - Search test files using Grep for keyword combinations
     - Score matches: 3/4 keywords = 75% confidence, 4/4 = 100%
     - Accept matches ≥70% confidence
   - For each test found:
     - Check if it maps to any spec criterion
     - If no mapping and confidence <70%, mark as "Extra" (not in spec)

5. **Drift categorization**:
   - **Missing**: Spec criteria with no matching tests (confidence <70%)
   - **Extra**: Tests with no matching spec criteria
   - **Modified**: Tests that partially match but with low confidence (suggest behavior changed)
   - Calculate: `drift% = (missing + extra + modified) / total_spec_criteria * 100`

6. **Report generation**:
   - Header: Feature name, spec path, drift percentage
   - Section: Missing (in spec, not in tests) - list criteria
   - Section: Extra (in tests, not in spec) - list test names
   - Section: Modified (possible behavior changes) - list with confidence scores
   - Recommendations based on drift%:
     - <10%: "Minor drift. No action needed."
     - 10-20%: "Moderate drift. Consider running `/spiral-grove:spec-writing` to update spec."
     - >20%: "Significant drift detected. Run `/spiral-grove:spec-writing` to synchronize spec with implementation."
   - Warning: "This is advisory only. No automatic changes made to spec."

7. **False positive mitigation**:
   - Use flexible keyword matching (synonyms: "create"/"add"/"new")
   - Present uncertain matches (60-70% confidence) with "Possible match?" prompt
   - Let user confirm/reject uncertain matches
   - Target: <5% false positive rate

**Deliverables**:
- New `spec-vs-code` mode in `spiral-grove/commands/review.md`
- Spec criteria extraction logic
- Semantic matching algorithm with confidence scoring
- Drift categorization (Missing/Extra/Modified)
- Report format with recommendations
- Advisory-only approach (no auto-updates)

**Acceptance**:
- Correctly categorizes drift in all three categories
- <5% false positive rate on test features
- Completes in <1 min for typical feature (5-20 files)
- No automatic spec modifications

**Open Questions**:
- Should semantic matching use LLM-based similarity instead of keyword tokenization for better accuracy?
- What confidence threshold is optimal (currently 70%)?

## Testing

### TASK-010: Agent Standalone Test (Acceptance #6)
**Status**: Not Started | **Estimate**: 1h | **Dependencies**: TASK-003

Validate framework-agnostic agent requirement.

**Test cases**:
- Invoke agent on 3 module types (API, CLI, library) without .sdd/ directory
- Verify CLAUDE.md ≤400 lines, all sections present, no SDD references

**Acceptance**: Agent works in non-Spiral Grove projects

---

### TASK-011: Full Project Synthesis (Acceptance #1)
**Status**: Not Started | **Estimate**: 2h | **Dependencies**: TASK-007, TASK-008

End-to-end workflow validation on 10-15 module project.

**Test cases**:
- Module detection → user approval → manifest save
- Parallel agent spawning → CLAUDE.md generation → Origin field addition
- Performance: <2 min for 10 modules (scales to <5 min for 100)

**Acceptance**: All phases complete, all files ≤400 lines, manifest shows "completed"

---

### TASK-012: Resumability Test (Acceptance #5)
**Status**: Not Started | **Estimate**: 1h | **Dependencies**: TASK-008, TASK-011

Validate interruption recovery.

**Test cases**:
- Interrupt after 5/10 modules, edit manifest, re-run
- Verify only pending modules processed, completed untouched
- Test various interruption points (25%, 50%, 75%)

**Acceptance**: Idempotent re-runs, manifest-driven resumption works

### TASK-013: Hand-Edit Preservation Test (Acceptance #2)
**Status**: Not Started | **Estimate**: 1h | **Dependencies**: TASK-003, TASK-011

Validate hand-edited content survives regeneration.

**Test cases**:
- Add `<!-- BEGIN: HAND-EDITED -->` section with custom "Common Gotchas"
- Regenerate via synthesize-docs
- Verify content byte-identical, no duplicates, markers intact

**Acceptance**: Hand-edits preserved verbatim across multiple regenerations

---

### TASK-014: Drift Detection Test (Acceptance #3)
**Status**: Not Started | **Estimate**: 2h | **Dependencies**: TASK-009

Validate spec-vs-code mode categorization.

**Test cases**:
- 0% drift (perfect alignment), 20% drift (2 extra features), 50%+ drift (major divergence)
- "Shopping cart" spec (8 criteria) + implementation (10 features including wishlist/save-for-later extras)

**Acceptance**: Correct Missing/Extra/Modified categorization, drift %, <5% false positives, no auto-updates

---

### TASK-015: Lifecycle Test (Acceptance #4)
**Status**: Not Started | **Estimate**: 2h | **Dependencies**: TASK-011, TASK-014

Validate Development → Maintenance → Development cycle.

**Test workflow**:
- Complete feature → synthesize docs → simulate 6mo evolution → detect drift → update spec → new feature
- "Payment processing" with bug fixes introducing 15% drift

**Acceptance**: CLAUDE.md useful for maintenance, drift detection accurate, specs updatable

---

### TASK-016: Performance Test (Acceptance #1, criteria #2-3)
**Status**: Not Started | **Estimate**: 2h | **Dependencies**: TASK-011

Validate scale targets.

**Test cases**:
- 50-100 module project (synthetic if needed)
- Measure total time: target 100 modules in <5 min
- Validate all CLAUDE.md ≤400 lines
- Context budget: 5 files × 400 lines = 10K tokens ≤ 5% of 200K

**Acceptance**: <5 min for 100 modules, no timeouts, all files within limits

## Release

### TASK-017: Version Bump and Changelog
**Status**: Not Started | **Estimate**: 1-2h | **Dependencies**: All previous tasks

Prepare plugin release.

**Deliverables**:
- Update `spiral-grove/.claude-plugin/plugin.json`: 0.2.0 → 0.3.0
- Changelog: new commands (`synthesize-docs`), agents (`module-doc-synthesizer`), modes (`spec-vs-code`)
- Example manifest for docs
- Git tag v0.3.0

**Acceptance**: Valid JSON, plugin discoverable, all functionality tested

---

### TASK-018: Documentation Completion
**Status**: Not Started | **Estimate**: 2-3h | **Dependencies**: All testing complete

Create comprehensive user-facing documentation for the Documentation Synthesis feature.

**Implementation approach**:

1. **README.md additions** (update existing Spiral Grove README):
   - Add Documentation Synthesis to feature list
   - Add `/synthesize-docs` and `/review spec-vs-code` to command reference
   - Quick example: "Generate docs for 100-module project in <5 min"

2. **USAGE.md** (create new file: `spiral-grove/docs/documentation-synthesis-usage.md`):
   - **Basic workflow**: Spec → Implementation → `/synthesize-docs` → Maintenance
   - **Command examples**:
     - Running synthesize-docs for first time
     - Resuming interrupted generation
     - Re-running to update after code changes
   - **Drift detection workflow**: Maintenance → `/review spec-vs-code` → Update spec
   - **Hand-editing CLAUDE.md**: How to use `<!-- BEGIN: HAND-EDITED -->` markers
   - **Troubleshooting**: Module not detected, 0 modules found, agent failures

3. **API.md additions** (update existing API reference):
   - **/synthesize-docs command**:
     - Arguments: `[scope]` (optional, future: target specific directory)
     - Output: Manifest location, counts, failures
     - Exit codes: 0 (success), 1 (partial failure), 2 (complete failure)
   - **/review spec-vs-code command**:
     - Arguments: `[feature-name]` (required)
     - Output: Drift report with categories and percentage
   - **Module manifest schema**: JSON structure documentation
   - **CLAUDE.md format**: Link to claude-md-format.md spec

4. **TROUBLESHOOTING.md** (create new or update existing):
   - **Common issues**:
     - "No modules detected" → Check heuristics, create manual manifest
     - "Agent spawn failed" → Check manifest for error, retry specific module
     - "CLAUDE.md over 400 lines" → Module too complex, consider splitting
     - "Drift detection has false positives" → Adjust confidence threshold
     - "Hand-edits were lost" → Check marker syntax, file Git history
   - **Performance issues**: 100 modules taking >5 min → Check parallel execution
   - **Debugging**: How to read manifest, check agent logs

5. **Cross-references**:
   - README → USAGE for detailed workflows
   - USAGE → API for command specs
   - USAGE → TROUBLESHOOTING for common issues
   - TROUBLESHOOTING → CLAUDE.md format spec for marker syntax

**Deliverables**:
- Updated `spiral-grove/README.md` with feature additions
- New `spiral-grove/docs/documentation-synthesis-usage.md`
- Updated API reference with command specs and schemas
- Troubleshooting guide with common issues and solutions
- All docs with copy-paste ready examples

**Acceptance**:
- All commands documented with usage examples
- Common workflows have step-by-step guides
- Troubleshooting covers 10+ common issues
- Cross-references work (no broken links)
- Examples can be copied and run successfully

## Dependencies

```
Foundation: 001, 002 (parallel)
  ↓
Agent: 003 (depends on 001)
  ↓
Command: 004→005→006→007 (sequential)
         009 (parallel to command, no dependencies)
  ↓
Testing: 010→011→012, 013, 014→015, 016 (010 gates most tests)
  ↓
Release: 017, 018 (after all tests)
```

**Critical path**: 001 → 003 → 004 → 005 → 006 → 007 → 008 → 011 → testing → release
**Estimated remaining**: 8-12 hours (7 tasks × 1-2h avg)

## Acceptance Mapping

| Spec Test | Tasks | Success Criteria |
|-----------|-------|------------------|
| #1: Scale (100 modules <5 min) | 005,006,007,011,016 | Parallel agents, ≤400 lines, Origin fields |
| #2: Hand-edit preservation | 003,013 | Verbatim preservation, no duplicates |
| #3: Drift detection | 009,014 | Missing/Extra/Modified, <5% false positives |
| #4: Dev→Maint→Dev cycle | 011,014,015 | CLAUDE.md useful, drift accurate, specs updatable |
| #5: Resumability | 008,012 | Manifest-driven, idempotent re-runs |
| #6: Standalone agent | 003,010 | No .sdd/ required, no SDD references |
| #7: Parent/child hierarchy | 007,011 | Child docs link to child specs |

---

## Progress

**Completed (7/18)**: 001, 002, 003, 004, 005, 006, 007

**Remaining (11/18)**:
- 008: Resumability + Reporting (3h) - Implementation approach documented
- 009: Review Extension (6-8h) - Semantic matching algorithm detailed
- 010-016: Testing (8h) - Test cases specified
- 017-018: Release + Docs (3-5h) - Documentation structure planned

**Total Remaining**: 20-24 hours

**Note**: Tasks 008, 009, and 018 now include detailed implementation approaches with step-by-step HOW guidance.

---

## Key Principles

1. **Agent-command separation**: Agent is framework-agnostic, command adds SDD orchestration
2. **Parallel execution**: Single message with multiple Task calls for performance
3. **Hand-edit preservation**: Critical for user trust
4. **≤400 lines**: Non-negotiable context efficiency target
5. **Resumability**: Manifest-driven for large projects
6. **Semantic matching**: <5% false positive rate required
7. **Idempotency**: Safe to re-run all commands

**Next**: Use `/spiral-grove:implementation` to execute remaining tasks starting with TASK-008
