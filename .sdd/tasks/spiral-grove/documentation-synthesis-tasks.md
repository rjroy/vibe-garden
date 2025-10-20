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

Idempotent re-runs and comprehensive output.

**Deliverables**:
- Manifest-based resumption: skip completed, process pending/failed
- User prompts: "Continue from X remaining?" or "Re-run to regenerate all?"
- Output report: count summary, linked vs. unlinked modules, failures with guidance, total time
- Edge case handling: 0 modules, all failed, interruption recovery

**Acceptance**: Re-run after interruption completes only remaining modules, helpful error messages

### TASK-009: Review Extension - Spec-vs-Code Mode
**Status**: Not Started | **Estimate**: 6-8h | **Dependencies**: None (extends review.md)

Add drift detection mode to `/spiral-grove:review`.

**Deliverables**:
- New mode: `/review spec-vs-code [feature-name]`
- Spec acceptance criteria extraction
- Test suite comparison via Glob + Grep
- Semantic matching: tokenize criteria, flexible keyword search, confidence scores
- Drift categorization: Missing/Extra/Modified with percentage
- Recommendations: <10% no action, 10-20% consider update, >20% run /spec-writing
- Advisory only (no auto-updates)

**Acceptance**: <5% false positive rate, correct categorization, completes in <1 min per feature

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

Create comprehensive user-facing documentation.

**Deliverables**:
- README.md: Project overview, quick start, tool descriptions
- USAGE.md: Detailed workflows, examples, tips
- API.md: Command specs, schemas, error codes
- TROUBLESHOOTING.md: Common issues, diagnostics, FAQ
- CONTRIBUTING.md: Dev setup, testing, PR process

**Acceptance**: All docs cross-referenced, copy-paste ready examples, comprehensive coverage

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
- 008: Resumability + Reporting (3h)
- 009: Review Extension (6-8h)
- 010-016: Testing (8h)
- 017-018: Release + Docs (3-5h)

**Total Remaining**: 20-24 hours

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
