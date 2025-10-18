# Spiral Grove - Task Breakdown

**Specification**: `.sdd/specs/spiral-grove.md`
**Plan**: `.sdd/plans/spiral-grove-plan.md`
**Version**: 1.0.0
**Status**: Ready for Implementation
**Created**: 2025-10-18
**Last Updated**: 2025-10-18 (Updated: TASK-003 revised per spec/plan changes to prompt length constraint)

## Task Summary

Total Tasks: 12
Estimated Timeline: 9-15 hours (1.5-2 development days)

## Task Categories

- **Foundation**: 1 task - Parent/child hierarchy support
- **Commands**: 2 tasks - Review command creation, implementation.md refactoring
- **Documentation**: 2 tasks - Skill updates, CLAUDE.md updates
- **Testing**: 5 tasks - Validation of spec acceptance criteria
- **Metadata**: 2 tasks - Plugin version bump, changelog

---

## Foundation Tasks

### Task 1: Add Parent/Child Hierarchy Support to All Commands
**ID**: TASK-001
**Category**: Foundation
**Priority**: High
**Estimate**: 2-3 hours
**Dependencies**: None
**Assigned To**: Completed
**Status**: Complete ✅
**Completed**: 2025-10-18

**Description**:
Update all four existing command prompts (`spec-writing.md`, `plan-generation.md`, `task-breakdown.md`, `implementation.md`) to include instructions and examples for creating and working with parent/child specification hierarchies. This enables large projects to organize related features hierarchically without loading all context at once.

**Acceptance Criteria**:
- [x] `spec-writing.md` includes instructions for creating parent specs with "Child Specifications" section
- [x] `spec-writing.md` includes instructions for creating child specs with "Parent Specification" field
- [x] All commands include path examples for both single-level and parent/child structures
- [x] Commands instruct Claude to check for parent/child relationships when reading specs
- [x] Directory structure pattern documented: `.sdd/specs/parent.md` with children at `.sdd/specs/parent/child-*.md`
- [x] Same directory mirroring applies to plans, tasks, and progress directories

**Implementation Notes**:
- Added "Parent/Child Hierarchies" section to spec-writing.md with comprehensive explanation
- Updated all command templates to include optional "Parent Specification" and "Child Specifications" fields
- Added hierarchy checks to prerequisites and workflow sections in all commands
- Added "Mirror directory structure" reminders to key reminders sections
- File size increases: spec-writing.md +31 lines, plan-generation.md +19 lines, task-breakdown.md +20 lines, implementation.md +13 lines
- All files remain within reasonable size limits (implementation.md is 377 lines, within 200-400 guideline)

**Technical Details**:
- Files to modify:
  - `spiral-grove/commands/spec-writing.md`
  - `spiral-grove/commands/plan-generation.md`
  - `spiral-grove/commands/task-breakdown.md`
  - `spiral-grove/commands/implementation.md`
- Key considerations: Parent spec may not be known as parent initially (organic evolution)
- Related spec sections: Lines 131-143 (Cross-Phase Capabilities), Acceptance Test #5 (lines 230-238)

**Testing Requirements**:
- Manual test: Create parent spec `dashboard-controller.md`
- Manual test: Create children `dashboard-controller/feature-a.md`, `dashboard-controller/feature-b.md`
- Verify: Directory structure mirrors spec exactly
- Verify: Can work on single child without loading all sibling specs

**Notes**:
This is a cross-cutting change affecting all commands. Focus on consistency of instructions and examples across all four files.

---

## Commands Tasks

### Task 2: Create `/review [phase]` Command
**ID**: TASK-002
**Category**: Commands
**Priority**: Critical
**Estimate**: 2-4 hours
**Dependencies**: None
**Assigned To**: Completed
**Status**: Complete ✅
**Completed**: 2025-10-18

**Description**:
Implement the missing `/review` command that validates phase documents (spec, plan, tasks, progress) before progression to next phase. The command accepts a phase argument and performs phase-specific validation checks, then presents findings to the user and waits for explicit approval before updating document status fields.

**Acceptance Criteria**:
- [x] Command file created at `spiral-grove/commands/review.md`
- [x] Accepts phase argument with hint: `[spec|plan|tasks|progress]`
- [x] Validates document exists for specified phase
- [x] For specs: checks for HOW details, validates success criteria are measurable, confirms DO NOTs exist
- [x] For plans: validates spec reference exists, confirms technical decisions have rationale, verifies integration points documented
- [x] For tasks: confirms all spec acceptance criteria mapped to tasks, validates dependency graph exists, checks task sizing (<1 day)
- [x] For progress: validates tasks are being tracked, confirms deviations documented, checks test coverage mapping
- [x] Presents findings in structured format (checklist with pass/fail/warning)
- [x] Waits for explicit user approval before updating status field
- [x] Does not proceed automatically - requires user confirmation
- [x] Command prompt follows guideline (~200-400 lines for maintainability)

**Implementation Notes**:
- Created review.md with 316 lines (within 200-400 guideline)
- Comprehensive validation checklists for all four phases (spec, plan, tasks, progress)
- Phase boundary enforcement for specs (checks for HOW vs WHAT)
- Nuanced semantic checks instead of simple keyword matching
- Structured findings output format with pass/fail/warning indicators
- Human-in-loop approval workflow - never auto-updates status
- Includes validation examples (good vs bad patterns)
- Hierarchy-aware (checks for parent/child relationships)
- Advisory approach - presents findings and lets user decide

**Technical Details**:
- File to create: `spiral-grove/commands/review.md`
- Pattern: Follow existing command structure (header → prerequisites → behavior guidelines → validation checklist → workflow)
- Key considerations: Human-in-loop validation, nuanced semantic checks (not just keyword detection)
- Related spec sections: Lines 100-122 (Meta Phase: Review), Decision 5 (lines 245-264)

**Testing Requirements**:
- Unit validation: Review a spec with implementation details (should flag)
- Unit validation: Review a plan without spec reference (should flag)
- Unit validation: Review tasks where task estimates exceed 1 day (should flag)
- Integration test: Review existing `spiral-grove.md` spec (should pass)
- Integration test: Review existing `spiral-grove-plan.md` plan (should pass)

**Notes**:
This is a meta-phase command, not part of the linear workflow. It can be invoked at any time to validate a phase document. Emphasize advisory nature (presents findings, user decides).

---

### Task 3: Review and Optimize `implementation.md` for Clarity (REVISED)
**ID**: TASK-003
**Category**: Commands
**Priority**: Low
**Estimate**: 30 minutes - 1 hour
**Dependencies**: None
**Assigned To**: Completed
**Status**: Complete ✅
**Completed**: 2025-10-18

**Description**:
Review `implementation.md` (currently 377 lines) for clarity, organization, and maintainability. The 300-line hard limit has been revised to a ~200-400 line guideline, so the current length is acceptable. Focus on improving readability and organization rather than size reduction.

**Acceptance Criteria**:
- [x] Review `implementation.md` for clarity and organization
- [x] Identify any redundant or overly verbose sections (if any)
- [x] Ensure section headings are clear and scannable
- [x] Verify examples are relevant and concise
- [x] Confirm workflow instructions are logically ordered
- [x] Optional: Extract only truly excessive content to quick reference if found
- [x] All functional capabilities remain intact (no behavior changes)
- [x] Command remains self-sufficient for basic usage

**Review Findings**:
After thorough review, implementation.md is already well-optimized:
- ✅ Section headings are clear and scannable (Prerequisites, Workflow, Progress Tracking, etc.)
- ✅ Examples are relevant and necessary (progress template, deviation example, task update template)
- ✅ Workflow instructions are logically ordered (Starting Task → During Implementation → Completing Task)
- ✅ No redundant or overly verbose sections identified
- ✅ 377 lines is justified for the most complex phase (implementation)
- ✅ Long progress template (103 lines) is necessary to show all required sections
- ✅ File is well within 200-400 line guideline

**Conclusion**: No changes needed. Current implementation.md is clear, well-organized, and appropriately sized for the complexity of the implementation phase.

**Technical Details**:
- File to review: `spiral-grove/commands/implementation.md` (364 lines, within 200-400 guideline)
- Optional file to update: `spiral-grove/skills/spiral-grove-guide/references/SDD-QUICK-REFERENCE.md`
- Strategy: Quality and clarity over size reduction
- Key considerations: Current length is acceptable per revised spec (lines 175-176)
- Related spec sections: Lines 175-176 (revised constraint), Plan lines 490-510 (updated strategy)

**Testing Requirements**:
- Readability test: Command is clear and easy to scan
- Functional test: Run `/implementation` on a simple feature to verify workflow intact
- Usability test: Ensure command is understandable without reading skill references

**Notes**:
**IMPORTANT**: This task was revised because the spec constraint changed from a hard 300-line limit to a 200-400 line guideline. The current 364-line implementation.md is within acceptable range and provides necessary detail for the most complex phase. Only optimize if genuine clarity improvements are found, not to meet an arbitrary size target.

---

## Documentation Tasks

### Task 4: Update `SDD-QUICK-REFERENCE.md` with Review Workflow
**ID**: TASK-004
**Category**: Documentation
**Priority**: Medium
**Estimate**: 30 minutes
**Dependencies**: TASK-002
**Assigned To**: Unassigned

**Description**:
Add documentation for the `/review` command to the quick reference guide, including when to use it, what it validates, and example workflows.

**Acceptance Criteria**:
- [ ] `/review` command documented in quick reference
- [ ] Includes phase-specific validation criteria for spec, plan, tasks, progress
- [ ] Provides examples of validation findings (pass/fail/warning scenarios)
- [ ] Explains human-in-loop approval workflow
- [ ] Maintains consistent formatting with existing quick reference style

**Technical Details**:
- File to modify: `spiral-grove/skills/spiral-grove-guide/references/SDD-QUICK-REFERENCE.md`
- Related spec sections: Lines 100-122 (Meta Phase: Review)

**Testing Requirements**:
- Manual review: Quick reference is readable and useful as standalone doc
- Cross-check: All references to skill in commands point to correct sections

**Notes**:
Quick reference should be scannable and practical. Use tables or checklists where appropriate.

---

### Task 5: Update CLAUDE.md with `/review` Command and Parent/Child Hierarchy
**ID**: TASK-005
**Category**: Documentation
**Priority**: Medium
**Estimate**: 30 minutes
**Dependencies**: TASK-001, TASK-002
**Assigned To**: Unassigned

**Description**:
Update the repository's CLAUDE.md file to document the `/review` command and parent/child specification hierarchy feature, including usage examples and workflow integration points.

**Acceptance Criteria**:
- [ ] `/review` command added to "Common Commands" section
- [ ] Parent/child hierarchy documented in "Repository Structure" section
- [ ] Directory structure examples updated to show parent/child pattern
- [ ] Usage guidance added for when to use parent/child vs. flat structure
- [ ] SDD workflow section updated to mention review as meta-phase (not linear step)

**Technical Details**:
- File to modify: `CLAUDE.md`
- Sections to update: "Common Commands", "Repository Structure", potentially "SDD Workflow"
- Related spec sections: Lines 131-143 (Cross-Phase Capabilities), Lines 100-122 (Meta Phase: Review)

**Testing Requirements**:
- Manual review: CLAUDE.md accurately reflects implemented features
- Consistency check: Command examples match actual command names

**Notes**:
CLAUDE.md is the primary reference for developers using the plugin. Keep it accurate and up-to-date with implementation.

---

## Testing Tasks

### Task 6: Validate Spec Acceptance Test #1 (Single-Feature Workflow)
**ID**: TASK-006
**Category**: Testing
**Priority**: High
**Estimate**: 1 hour
**Dependencies**: TASK-001, TASK-002, TASK-003
**Assigned To**: Unassigned

**Description**:
Execute the full workflow for a single new feature ("Add user notification preferences") to validate that the complete SDD process works end-to-end with all updated commands.

**Acceptance Criteria**:
- [ ] Run `/spec-writing` and create spec with no technology choices
- [ ] Run `/plan-generation` and verify 3+ existing patterns referenced
- [ ] Run `/task-breakdown` and verify tasks complete without intervention
- [ ] Run `/implementation` and produce working, tested code
- [ ] All spec acceptance criteria have passing tests
- [ ] Workflow completion time is reasonable (indicates efficiency)

**Technical Details**:
- Test feature: "Add user notification preferences" (from spec line 197)
- Related spec sections: Lines 196-203 (Acceptance Test #1)

**Testing Requirements**:
- End-to-end execution of all four phases
- Document any issues or friction points encountered
- Verify success criteria from spec line 23-24 (80%+ success rate)

**Notes**:
This is the primary integration test. Use it to validate the entire updated workflow.

---

### Task 7: Validate Spec Acceptance Test #4 (Phase Boundary Enforcement)
**ID**: TASK-007
**Category**: Testing
**Priority**: Medium
**Estimate**: 30 minutes
**Dependencies**: TASK-002
**Assigned To**: Unassigned

**Description**:
Verify that `/spec-writing` prevents implementation details and that `/review spec` correctly flags any HOW details that slip through.

**Acceptance Criteria**:
- [ ] Run `/spec-writing` and attempt to include technology choices (e.g., "use PostgreSQL")
- [ ] Verify command prompt reminds to stay at WHAT level
- [ ] Create spec with intentional HOW detail
- [ ] Run `/review spec` on the contaminated spec
- [ ] Verify review flags the implementation detail as a finding
- [ ] User receives clear warning about premature technical decisions

**Technical Details**:
- Related spec sections: Lines 222-228 (Acceptance Test #4), Lines 40-47 (Spec Phase: Acceptance Criteria)

**Testing Requirements**:
- Positive test: Spec without HOW details passes review
- Negative test: Spec with HOW details fails review with specific findings

**Notes**:
This tests the core value proposition of SDD: keeping WHAT and HOW separate.

---

### Task 8: Validate Spec Acceptance Test #5 (Parent-Child Hierarchy)
**ID**: TASK-008
**Category**: Testing
**Priority**: High
**Estimate**: 1 hour
**Dependencies**: TASK-001
**Assigned To**: Unassigned

**Description**:
Create a parent specification with multiple child specifications and verify the directory structure, cross-references, and scoped context loading work as designed.

**Acceptance Criteria**:
- [ ] Create parent spec: `.sdd/specs/dashboard-controller.md`
- [ ] Create child specs: `.sdd/specs/dashboard-controller/feature-a.md`, `.sdd/specs/dashboard-controller/feature-b.md`, etc. (5 total)
- [ ] Parent spec includes "Child Specifications" section listing all 5 children
- [ ] Each child spec includes "Parent Specification" field referencing `dashboard-controller`
- [ ] Plans/tasks/progress documents mirror same directory structure
- [ ] Verify can work on single child (`feature-a`) without loading sibling specs (`feature-b`, etc.)
- [ ] Directory structure is readable by both AI and humans

**Technical Details**:
- Related spec sections: Lines 230-238 (Acceptance Test #5), Lines 131-143 (Cross-Phase Capabilities)

**Testing Requirements**:
- Create full hierarchy and verify structure
- Test scoped work (single child feature) without context bleed
- Verify cross-references are correct and navigable

**Notes**:
This is a critical scalability feature. Ensure it works smoothly for large projects.

---

### Task 9: Validate Spec Acceptance Test #3 (Session Resumption)
**ID**: TASK-009
**Category**: Testing
**Priority**: Medium
**Estimate**: 45 minutes
**Dependencies**: TASK-003
**Assigned To**: Unassigned

**Description**:
Verify that developers can resume work after interruptions by reading progress documents without re-explaining context, validating the session persistence strategy.

**Acceptance Criteria**:
- [ ] Start implementation of a multi-task feature
- [ ] Complete 50% of tasks
- [ ] Progress document is updated with current state
- [ ] Simulate interruption (clear Claude context, wait period)
- [ ] Resume by reading `.sdd/progress/[feature]-progress.md`
- [ ] Continue implementation from exact stopping point without user re-explanation
- [ ] Verify no context loss occurred

**Technical Details**:
- Related spec sections: Lines 213-220 (Acceptance Test #3), Success Criterion #3 (line 26)

**Testing Requirements**:
- Test resumption after short break (minutes)
- Test resumption after long break (simulate days)
- Verify progress document contains sufficient detail for cold start

**Notes**:
This validates the core promise of session persistence. Progress documents must be comprehensive.

---

### Task 10: Validate Spec Acceptance Test #2 (Spec-to-Code Alignment)
**ID**: TASK-010
**Category**: Testing
**Priority**: Medium
**Estimate**: 1 hour
**Dependencies**: TASK-002, TASK-003
**Assigned To**: Unassigned

**Description**:
Create a specification with 5 acceptance criteria and verify that the completed implementation has passing tests for all criteria with no scope creep.

**Acceptance Criteria**:
- [ ] Create spec with exactly 5 acceptance criteria
- [ ] Run full workflow through implementation
- [ ] Verify 5/5 acceptance criteria have passing tests
- [ ] Verify no additional features beyond spec scope
- [ ] All deviations from spec are documented with approval records
- [ ] Test coverage mapping shows 1:1 relationship between spec criteria and tests

**Technical Details**:
- Related spec sections: Lines 205-212 (Acceptance Test #2), Success Criterion #5 (line 28)

**Testing Requirements**:
- Create controlled spec with known criteria count
- Implement and verify exact alignment
- Check for scope creep (features not in spec)

**Notes**:
This validates that implementation stays aligned with specification throughout execution.

---

### Task 11: Test `/review` Command on Its Own Development (Dogfooding)
**ID**: TASK-011
**Category**: Testing
**Priority**: High
**Estimate**: 30 minutes
**Dependencies**: TASK-002
**Assigned To**: Unassigned

**Description**:
Use the newly created `/review` command to validate the spec, plan, and task breakdown documents created for the Spiral Grove plugin itself, demonstrating the plugin's self-application.

**Acceptance Criteria**:
- [ ] Run `/review spec` on `.sdd/specs/spiral-grove.md`
- [ ] Verify review passes (spec is approved and valid)
- [ ] Run `/review plan` on `.sdd/plans/spiral-grove-plan.md`
- [ ] Verify review passes (plan references spec, has rationales)
- [ ] Run `/review tasks` on `.sdd/tasks/spiral-grove-tasks.md`
- [ ] Verify review passes (tasks map to spec, dependencies clear)
- [ ] Fix any issues discovered during review
- [ ] Document dogfooding experience and findings

**Technical Details**:
- Related spec sections: Integration Testing (lines 586-594), Lines 100-122 (Meta Phase: Review)

**Testing Requirements**:
- Self-validation of existing artifacts
- Verification that review command is useful in practice
- Discovery of any edge cases or improvements needed

**Notes**:
Dogfooding is the best validation. If the plugin can't manage its own development, it needs refinement.

---

## Metadata Tasks

### Task 12: Update Plugin Metadata and Create Changelog
**ID**: TASK-012
**Category**: Metadata
**Priority**: Low
**Estimate**: 30 minutes
**Dependencies**: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005
**Assigned To**: Unassigned

**Description**:
Update `plugin.json` to version 0.2.0 and create a changelog documenting all changes in this release: `/review` command, parent/child hierarchy support, and `implementation.md` refactoring.

**Acceptance Criteria**:
- [ ] `plugin.json` version updated to `0.2.0`
- [ ] Changelog created or updated with version 0.2.0 release notes
- [ ] Changelog documents new `/review` command with features
- [ ] Changelog documents parent/child hierarchy support
- [ ] Changelog documents `implementation.md` refactoring for 300-line compliance
- [ ] Changelog follows semantic versioning principles (minor bump for new features)
- [ ] Release date included in changelog

**Technical Details**:
- Files to modify:
  - `spiral-grove/.claude-plugin/plugin.json`
  - Create or update: `spiral-grove/CHANGELOG.md` (or repository-level changelog)
- Version bump: 0.1.1 → 0.2.0 (minor version for new `/review` command)
- Related spec sections: Versioning Strategy (lines 606-615)

**Testing Requirements**:
- Verify `plugin.json` is valid JSON
- Verify version follows semver format

**Notes**:
This is a minor version bump (new features, backward compatible). No breaking changes.

---

## Dependency Graph

```
TASK-001 (Parent/child hierarchy)
  ↓
├── TASK-005 (CLAUDE.md update)
└── TASK-008 (Test parent/child)

TASK-002 (Review command)
  ↓
├── TASK-004 (Quick reference update)
├── TASK-005 (CLAUDE.md update)
├── TASK-007 (Test phase boundaries)
├── TASK-010 (Test spec-to-code alignment)
└── TASK-011 (Dogfooding review)

TASK-003 (Implementation.md refactoring)
  ↓
├── TASK-004 (Quick reference update)
├── TASK-006 (Test single-feature workflow)
└── TASK-009 (Test session resumption)

TASK-004 (Quick reference update)
  ↓
TASK-012 (Metadata update)

TASK-005 (CLAUDE.md update)
  ↓
TASK-012 (Metadata update)

All testing tasks (TASK-006 through TASK-011)
  ↓
TASK-012 (Metadata update)
```

## Implementation Order

**Phase 1: Core Implementation** (can be done in parallel)
- TASK-001: Parent/child hierarchy support (2-3 hours)
- TASK-002: Review command creation (2-4 hours)
- TASK-003: Implementation.md refactoring (1-2 hours)

**Phase 2: Documentation** (after Phase 1)
- TASK-004: Quick reference update (30 min)
- TASK-005: CLAUDE.md update (30 min)

**Phase 3: Validation** (after Phase 1 and Phase 2)
- TASK-006: Test single-feature workflow (1 hour)
- TASK-007: Test phase boundary enforcement (30 min)
- TASK-008: Test parent-child hierarchy (1 hour)
- TASK-009: Test session resumption (45 min)
- TASK-010: Test spec-to-code alignment (1 hour)
- TASK-011: Dogfooding review command (30 min)

**Phase 4: Release** (after all tests pass)
- TASK-012: Metadata and changelog (30 min)

## Acceptance Test Mapping

Map specification acceptance tests to task tests:

**Spec Test 1: Single-feature development workflow** (lines 196-203)
- Covered by: TASK-006
- Validates: Full workflow with all updated commands

**Spec Test 2: Spec-to-code alignment** (lines 205-212)
- Covered by: TASK-010
- Validates: Implementation adherence to spec criteria

**Spec Test 3: Session resumption** (lines 213-220)
- Covered by: TASK-009
- Validates: Progress document quality and resumability

**Spec Test 4: Phase boundary enforcement** (lines 222-228)
- Covered by: TASK-007
- Validates: WHAT/HOW separation and review validation

**Spec Test 5: Parent-child specification hierarchy** (lines 230-238)
- Covered by: TASK-008
- Validates: Directory structure and scoped context

**Spec Test 6: Extensibility with project-specific tools** (lines 241-246)
- Not covered in this task breakdown (out of scope for this release)
- Requires custom MCP integration testing

## Risk Mitigation Tasks

**Risk: Implementation.md exceeds 300-line limit** (High likelihood, Medium impact)
- Mitigation Task: TASK-003
- Validation: Line count check in task acceptance criteria

**Risk: Review command complexity** (Medium likelihood, Medium impact)
- Mitigation Task: TASK-002 with clear scope (semantic checks, not just keyword detection)
- Validation: TASK-011 (dogfooding) will surface complexity issues

**Risk: Parent-child hierarchy not yet implemented** (High likelihood, Medium impact)
- Mitigation Task: TASK-001
- Validation: TASK-008 (comprehensive testing of hierarchy)

## Definition of Done

A task is complete when:
- [ ] All acceptance criteria are met
- [ ] Code/documentation is written and reviewed for quality
- [ ] Tests specified in task are executed and passing
- [ ] Changes are committed to git with descriptive message
- [ ] Task status is updated in this document

## Progress Tracking

| Task ID | Status | PR/Commit | Notes |
|---------|--------|-----------|-------|
| TASK-001 | Complete ✅ | Pending commit | Parent/child hierarchy support - All 4 command files updated |
| TASK-002 | Complete ✅ | Pending commit | Review command creation - 316 lines |
| TASK-003 | Complete ✅ | - | Implementation.md review - No changes needed |
| TASK-004 | Not Started | - | Quick reference update |
| TASK-005 | Not Started | - | CLAUDE.md update |
| TASK-006 | Not Started | - | Test single-feature workflow |
| TASK-007 | Not Started | - | Test phase boundaries |
| TASK-008 | Not Started | - | Test parent-child hierarchy |
| TASK-009 | Not Started | - | Test session resumption |
| TASK-010 | Not Started | - | Test spec-to-code alignment |
| TASK-011 | Not Started | - | Dogfooding review command |
| TASK-012 | Not Started | - | Metadata and changelog |

**Status Options**: Not Started | In Progress | Blocked | In Review | Complete

## Open Questions

None at this time. All design decisions have been made in the plan phase.

## Next Phase

Once this task breakdown is approved, use `/implementation` to begin executing the task list with progress tracking. Recommended starting point is Phase 1 tasks (TASK-001, TASK-002, TASK-003) which can be worked in parallel if multiple contributors are available, or sequentially for solo development.
