# Documentation Synthesis Feature - Task Breakdown

**Specification**: [../../specs/spiral-grove/documentation-synthesis.md](../../specs/spiral-grove/documentation-synthesis.md)
**Plan**: [../../plans/spiral-grove/documentation-synthesis-plan.md](../../plans/spiral-grove/documentation-synthesis-plan.md)
**Parent Tasks**: [../spiral-grove-tasks.md](../spiral-grove-tasks.md)
**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-20
**Last Updated**: 2025-10-20

## Task Summary

Total Tasks: 23
Estimated Timeline: 19-27 hours (2.5-3.5 development days)

## Task Categories

- **Foundation**: 2 tasks - Documentation and project setup
- **Agent Implementation**: 5 tasks - Module documentation synthesizer agent
- **Command Implementation**: 8 tasks - Synthesize-docs command and review extension
- **Integration**: 3 tasks - SDD integration and manifest handling
- **Testing**: 4 tasks - Test suites for acceptance criteria
- **Release**: 1 task - Version bump and changelog

---

## Foundation Tasks

### Task 1: Create CLAUDE.md Format Specification
**ID**: TASK-001
**Category**: Foundation
**Priority**: Critical
**Estimate**: 2-3 hours
**Dependencies**: None
**Assigned To**: Unassigned

**Description**:
Create comprehensive documentation for the CLAUDE.md format specification that will be used by the module-doc-synthesizer agent and users who want to manually edit CLAUDE.md files.

**Acceptance Criteria**:
- [ ] File created at `spiral-grove/docs/claude-md-format.md`
- [ ] Documents required sections (Purpose, Key Components, Public API, Integration Points, Common Operations, Testing)
- [ ] Documents hand-edited section markers (`<!-- BEGIN/END: HAND-EDITED -->`)
- [ ] Includes module CLAUDE.md template (≤400 lines constraint)
- [ ] Includes root CLAUDE.md template
- [ ] Documents Origin field format for SDD integration
- [ ] Provides examples of well-formed CLAUDE.md files
- [ ] Documents constraints (line limits, valid markdown, marker rules)

**Technical Details**:
- Files to create: `spiral-grove/docs/claude-md-format.md`
- Reference: Plan section "CLAUDE.md Files" (lines 259-362)
- Key considerations: This is referenced by agent and commands, must be complete before agent implementation

**Testing Requirements**:
- Manual review: Specification is clear and complete
- Validation: All examples are valid markdown

**Notes**:
This task must be completed first as it defines the contract that the agent will implement.

---

### Task 2: Create Module Manifest Schema Documentation
**ID**: TASK-002
**Category**: Foundation
**Priority**: Critical
**Estimate**: 1 hour
**Dependencies**: None
**Assigned To**: Unassigned

**Description**:
Document the `.sdd/module-manifest.json` schema that will be used for stateful resumability during documentation synthesis.

**Acceptance Criteria**:
- [ ] JSON schema documented in plan or separate schema file
- [ ] Schema includes: generated_at, project_root, modules array
- [ ] ModuleEntry schema includes: path, status, claude_md_path, optional error
- [ ] Status enum values defined: pending, completed, failed
- [ ] Example manifest provided with all three status types
- [ ] Schema validation rules documented (e.g., unique paths)

**Technical Details**:
- Location: Can be in `spiral-grove/docs/module-manifest-schema.md` or inline in synthesize-docs command
- Reference: Plan section "Module Manifest" (lines 229-256)
- Schema is defined in plan lines 554-597

**Testing Requirements**:
- Create example manifest file for reference
- Validate JSON structure is parseable

**Notes**:
This defines the data structure for resumability. Complete early to guide command implementation.

---

## Agent Implementation Tasks

### Task 3: Create Module Documentation Synthesizer Agent - Core Structure
**ID**: TASK-003
**Category**: Agent Implementation
**Priority**: Critical
**Estimate**: 2 hours
**Dependencies**: TASK-001 (CLAUDE.md format spec)
**Assigned To**: Unassigned

**Description**:
Create the agent file with YAML frontmatter and core structure. This agent will analyze a single module and generate/update its CLAUDE.md documentation.

**Acceptance Criteria**:
- [ ] File created at `spiral-grove/agents/module-doc-synthesizer.md`
- [ ] YAML frontmatter includes description field
- [ ] YAML frontmatter includes capabilities array: module-documentation, claude-md-generation, hand-edit-preservation
- [ ] Agent prompt starts with role definition ("This agent analyzes a single module...")
- [ ] "When to use this agent" section present
- [ ] "Capabilities" section lists key features
- [ ] Agent is framework-agnostic (no SDD-specific logic)

**Technical Details**:
- Files to create: `spiral-grove/agents/module-doc-synthesizer.md`
- Reference: Plan lines 61-105, Spec lines 46-73
- Follow existing agent patterns in Claude Code ecosystem

**Testing Requirements**:
- Validate YAML frontmatter is parseable
- Verify agent can be discovered by Claude Code

**Notes**:
Focus on structure only in this task. Routine implementation comes in TASK-004.

---

### Task 4: Implement Agent Routine - Analysis and Generation
**ID**: TASK-004
**Category**: Agent Implementation
**Priority**: Critical
**Estimate**: 3-4 hours
**Dependencies**: TASK-003
**Assigned To**: Unassigned

**Description**:
Implement the 7-step agent routine that executes every time the agent is invoked. This includes code analysis and CLAUDE.md content generation.

**Acceptance Criteria**:
- [ ] Step 1: Check if CLAUDE.md exists for module (documented)
- [ ] Step 2: If exists, read and identify hand-edited sections (documented)
- [ ] Step 3: Analyze module implementation using Read, Glob, Grep tools
- [ ] Step 4: Generate structured CLAUDE.md content with all required sections
- [ ] Step 5: If updating, merge new content with preserved hand-edits
- [ ] Step 6: Validate output ≤400 lines (with retry logic)
- [ ] Step 7: Return markdown content (command writes to disk)
- [ ] Agent prompt includes specific instructions for each step
- [ ] Includes guidance on code analysis (what to look for)
- [ ] Includes CLAUDE.md template to follow

**Technical Details**:
- Files to modify: `spiral-grove/agents/module-doc-synthesizer.md`
- Reference: Plan routine (lines 88-101), Spec routine (lines 76-88)
- Tools to use: Read (file content), Glob (find files), Grep (search code)

**Testing Requirements**:
- Unit test: Invoke agent on simple module with 3 files
- Validation: Generated CLAUDE.md has all required sections
- Validation: Line count ≤400 lines

**Notes**:
This is the core implementation. Focus on generating accurate, concise documentation.

---

### Task 5: Implement Hand-Edited Section Preservation
**ID**: TASK-005
**Category**: Agent Implementation
**Priority**: High
**Estimate**: 2 hours
**Dependencies**: TASK-004
**Assigned To**: Unassigned

**Description**:
Implement logic to preserve user-edited content between `<!-- BEGIN: HAND-EDITED -->` and `<!-- END: HAND-EDITED -->` markers when regenerating CLAUDE.md files.

**Acceptance Criteria**:
- [ ] Agent reads existing CLAUDE.md before generation
- [ ] Extracts content between markers using regex pattern
- [ ] Validates markers are well-formed (one pair, on own lines)
- [ ] Stores extracted sections
- [ ] Inserts preserved sections at same location in new content
- [ ] Handles missing markers gracefully (no markers = regenerate fully)
- [ ] Errors on malformed markers (nested, unpaired)
- [ ] Documented in agent prompt with examples

**Technical Details**:
- Files to modify: `spiral-grove/agents/module-doc-synthesizer.md`
- Reference: Plan lines 809-834, Spec acceptance test #2 (lines 282-298)
- Regex pattern: `<!-- BEGIN: HAND-EDITED -->.*?<!-- END: HAND-EDITED -->`

**Testing Requirements**:
- Test case: Existing CLAUDE.md with hand-edited section
- Validation: Hand-edited content preserved verbatim after regeneration
- Test case: Malformed markers (should error)

**Notes**:
Critical for user trust. Users must be confident their manual edits won't be lost.

---

### Task 6: Implement 400-Line Validation with Condensing
**ID**: TASK-006
**Category**: Agent Implementation
**Priority**: High
**Estimate**: 2-3 hours
**Dependencies**: TASK-004
**Assigned To**: Unassigned

**Description**:
Implement validation step that ensures generated CLAUDE.md is ≤400 lines. If over, agent applies condensing strategies and retries once.

**Acceptance Criteria**:
- [ ] Agent counts lines in generated content
- [ ] If ≤400: Proceed to return content
- [ ] If >400: Apply condensing strategies
- [ ] Condensing: Remove redundant examples (keep 1-2 most representative)
- [ ] Condensing: Shorten component descriptions to 1 sentence
- [ ] Condensing: Collapse similar sections
- [ ] Condensing: Move extensive code snippets to hand-edited section prompt
- [ ] After condensing: Retry validation once
- [ ] If still >400: Return with warning message to user
- [ ] Warning explains module is complex, suggests splitting

**Technical Details**:
- Files to modify: `spiral-grove/agents/module-doc-synthesizer.md`
- Reference: Plan Decision 5 (lines 466-495), Spec success criterion #1 (line 23)
- Context budget: ≤5% (400 lines ≈ 2K tokens)

**Testing Requirements**:
- Test case: Complex module that generates 420 lines initially
- Validation: Agent condenses to ≤400 or returns warning
- Test case: Normal module (200 lines), should not trigger condensing

**Notes**:
This ensures context efficiency. Performance target is critical.

---

### Task 7: Agent Documentation and Examples
**ID**: TASK-007
**Category**: Agent Implementation
**Priority**: Medium
**Estimate**: 1 hour
**Dependencies**: TASK-003, TASK-004, TASK-005, TASK-006
**Assigned To**: Unassigned

**Description**:
Add comprehensive documentation to the agent prompt including usage examples, guidelines, and output format specifications.

**Acceptance Criteria**:
- [ ] "How to invoke this agent" section with Task tool example
- [ ] Guidelines for code analysis (what to extract, what to ignore)
- [ ] Output format specification (references CLAUDE.md format doc)
- [ ] Examples of good vs. bad CLAUDE.md content
- [ ] Error handling guidance (no source files, over 400 lines, etc.)
- [ ] References to CLAUDE.md format specification (TASK-001)
- [ ] Agent prompt is clear and actionable

**Technical Details**:
- Files to modify: `spiral-grove/agents/module-doc-synthesizer.md`
- Reference: Plan API design (lines 659-682)
- Keep agent prompt concise (~200-400 lines guideline)

**Testing Requirements**:
- Manual review: Agent prompt is clear and complete
- Validate: No references to SDD/Spiral Grove (framework-agnostic)

**Notes**:
Agent should be usable standalone without Spiral Grove context.

---

## Command Implementation Tasks

### Task 8: Create Synthesize-Docs Command - Core Structure
**ID**: TASK-008
**Category**: Command Implementation
**Priority**: Critical
**Estimate**: 1 hour
**Dependencies**: TASK-001, TASK-002
**Assigned To**: Unassigned

**Description**:
Create the command file with YAML frontmatter and core structure for the `/spiral-grove:synthesize-docs` command.

**Acceptance Criteria**:
- [ ] File created at `spiral-grove/commands/synthesize-docs.md`
- [ ] YAML frontmatter includes argument-hint: [scope]
- [ ] YAML frontmatter includes description field
- [ ] Command prompt starts with role definition ("You are now in Documentation Synthesis Mode...")
- [ ] "Your Focus" section with bullet points
- [ ] "Prerequisites" section checking for .sdd/ directory
- [ ] "Behavior Guidelines" section
- [ ] Structure for three-phase workflow documented

**Technical Details**:
- Files to create: `spiral-grove/commands/synthesize-docs.md`
- Reference: Plan lines 106-170, existing command patterns (review.md, implementation.md)
- Follow Spiral Grove command conventions

**Testing Requirements**:
- Validate YAML frontmatter is parseable
- Verify command is discoverable as `/spiral-grove:synthesize-docs`

**Notes**:
Focus on structure only. Phase implementations come in subsequent tasks.

---

### Task 9: Implement Phase 1 - Module Discovery
**ID**: TASK-009
**Category**: Command Implementation
**Priority**: Critical
**Estimate**: 3-4 hours
**Dependencies**: TASK-008
**Assigned To**: Unassigned

**Description**:
Implement Phase 1 of the synthesize-docs command: detecting logical module boundaries in the codebase and saving to manifest.

**Acceptance Criteria**:
- [ ] Uses Glob tool to scan codebase
- [ ] Applies heuristics: directories with package files (package.json, setup.py, go.mod, Cargo.toml)
- [ ] Applies heuristics: directories with 3+ source files + test directory
- [ ] Applies heuristics: subdirectories of src/, lib/, modules/, packages/
- [ ] Excludes: node_modules/, vendor/, .git/, dist/, build/
- [ ] Presents detected module list to user for approval/modification
- [ ] Saves approved list to `.sdd/module-manifest.json`
- [ ] Manifest includes: generated_at, project_root, modules array
- [ ] Each module entry has: path, status="pending", claude_md_path

**Technical Details**:
- Files to modify: `spiral-grove/commands/synthesize-docs.md`
- Reference: Plan Decision 2 (lines 386-415), Plan Phase 1 (lines 122-140)
- Manifest schema: Plan lines 554-597

**Testing Requirements**:
- Test on diverse project structures (monorepo, microservices, single app)
- Validate manifest JSON is well-formed
- Test edge case: 0 modules detected (should guide user)

**Notes**:
Mandatory user approval before generation starts. Module detection must be language-agnostic.

---

### Task 10: Implement Phase 2 - Parallel Documentation Generation
**ID**: TASK-010
**Category**: Command Implementation
**Priority**: Critical
**Estimate**: 4-5 hours
**Dependencies**: TASK-009, TASK-007 (agent complete)
**Assigned To**: Unassigned

**Description**:
Implement Phase 2: spawn module-doc-synthesizer agents in parallel for all modules, track status, and generate root CLAUDE.md.

**Acceptance Criteria**:
- [ ] Reads module list from `.sdd/module-manifest.json`
- [ ] For each module with status="pending": spawn module-doc-synthesizer agent via Task tool
- [ ] Uses single message with multiple Task tool calls (parallel execution)
- [ ] Each agent receives: module path, existing CLAUDE.md path (if any)
- [ ] Writes agent-returned content to [module]/CLAUDE.md
- [ ] Updates manifest status: "pending" → "completed" or "failed"
- [ ] Saves error message to manifest.error field on failure
- [ ] Generates root CLAUDE.md with project overview, directory structure, module index
- [ ] Provides progress indicators during generation
- [ ] Handles agent spawn failures gracefully (continues with other modules)

**Technical Details**:
- Files to modify: `spiral-grove/commands/synthesize-docs.md`
- Reference: Plan Phase 2 (lines 142-153), Plan Decision 3 (lines 416-441)
- Agent invocation: Task tool with subagent_type="module-doc-synthesizer"

**Testing Requirements**:
- Test with 10 modules (validate parallel spawning)
- Test with failing module (validate error handling continues)
- Validate all CLAUDE.md files created with valid content
- Performance: Ensure faster than serial processing

**Notes**:
This is the core performance-critical implementation. Must achieve <5 min for 100 modules.

---

### Task 11: Implement Phase 3 - SDD Integration
**ID**: TASK-011
**Category**: Command Implementation
**Priority**: High
**Estimate**: 2-3 hours
**Dependencies**: TASK-010
**Assigned To**: Unassigned

**Description**:
Implement Phase 3: add `**Origin**: .sdd/specs/[name].md` references to generated CLAUDE.md files by analyzing module paths against spec hierarchy.

**Acceptance Criteria**:
- [ ] For each completed CLAUDE.md: analyze module path
- [ ] Match module path to spec file (e.g., src/auth → .sdd/specs/authentication.md)
- [ ] Fuzzy matching: tries exact name, shortened name, directory name
- [ ] If match found: insert `**Origin**: Implemented from .sdd/specs/[name].md` after title
- [ ] If no match: skip Origin field, warn user (module may not need spec)
- [ ] Handles parent/child spec structures (child modules link to child specs)
- [ ] Re-writes CLAUDE.md file with Origin field added
- [ ] Reports modules with/without matching specs

**Technical Details**:
- Files to modify: `spiral-grove/commands/synthesize-docs.md`
- Reference: Plan Phase 3 (lines 155-163), Plan Decision 7 (lines 526-550)
- Must preserve hand-edited sections during re-write

**Testing Requirements**:
- Test with modules that have matching specs
- Test with utility modules (no spec)
- Test with parent/child spec hierarchy
- Validate Origin field placement is correct

**Notes**:
This separates SDD logic from agent (keeps agent reusable). Phase 3 is Spiral Grove-specific.

---

### Task 12: Implement Resumability Logic
**ID**: TASK-012
**Category**: Command Implementation
**Priority**: High
**Estimate**: 2 hours
**Dependencies**: TASK-010
**Assigned To**: Unassigned

**Description**:
Implement logic to resume documentation generation from an existing manifest when command is re-run (idempotent operation).

**Acceptance Criteria**:
- [ ] On command start: check if `.sdd/module-manifest.json` exists
- [ ] If exists: read and parse manifest
- [ ] Count completed, failed, and pending modules
- [ ] If all completed: ask user "All done, re-run to regenerate?"
- [ ] If partial: ask user "Continue from where we left off? (X modules remaining)"
- [ ] On user approval: process only "pending" and "failed" modules
- [ ] Update manifest timestamp on each run
- [ ] Regenerating completed module updates status and content safely

**Technical Details**:
- Files to modify: `spiral-grove/commands/synthesize-docs.md`
- Reference: Plan state management (lines 789-807), Spec acceptance test #5 (lines 324-333)
- Idempotency: Re-running on completed modules is safe (hand-edit preservation)

**Testing Requirements**:
- Test: Interrupt after 5/10 modules, re-run should complete remaining 5
- Test: Re-run on fully completed project (should ask confirmation)
- Validate: Manifest updated correctly each run

**Notes**:
Critical for large projects where generation may timeout or be interrupted.

---

### Task 13: Implement Output Reporting and Error Handling
**ID**: TASK-013
**Category**: Command Implementation
**Priority**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-010, TASK-011, TASK-012
**Assigned To**: Unassigned

**Description**:
Implement comprehensive output reporting showing generation results, failures, and next steps.

**Acceptance Criteria**:
- [ ] Final output shows: "Generated X CLAUDE.md files (Y root + Z modules)"
- [ ] Reports modules linked to specs vs. no matching spec
- [ ] Lists failed modules with error messages
- [ ] Provides guidance for failures (how to retry, manual fixes)
- [ ] Reports total time taken (for performance monitoring)
- [ ] Manifest location shown for reference
- [ ] Handles edge cases: 0 modules detected, all failed, etc.

**Technical Details**:
- Files to modify: `spiral-grove/commands/synthesize-docs.md`
- Reference: Plan API design (lines 729-741), Plan error handling (lines 835-935)

**Testing Requirements**:
- Test various scenarios: all success, partial failure, 0 modules
- Validate error messages are helpful

**Notes**:
Good error messages are critical for user experience.

---

### Task 14: Create Review Command Extension - Spec-vs-Code Mode
**ID**: TASK-014
**Category**: Command Implementation
**Priority**: High
**Estimate**: 4-5 hours
**Dependencies**: None (extends existing review.md)
**Assigned To**: Unassigned

**Description**:
Extend the existing `/spiral-grove:review` command with a new `spec-vs-code` mode for detecting drift between specifications and implementation.

**Acceptance Criteria**:
- [ ] Update argument-hint in frontmatter to include spec-vs-code
- [ ] Add new mode section to review.md command
- [ ] Reads spec from `.sdd/specs/[feature-name].md`
- [ ] Extracts acceptance criteria from spec
- [ ] Uses Glob to find feature's code files (heuristics based on spec name)
- [ ] Uses Grep to search test files for matching tests
- [ ] Compares spec criteria against test suite
- [ ] Categorizes drift: Missing (in spec, not in code), Extra (in code, not in spec), Modified (behavior changed)
- [ ] Calculates drift percentage: (missing + extra + modified) / total_spec_criteria * 100
- [ ] Generates drift report with specific examples
- [ ] Provides recommendations based on drift percentage (<10%: no action, 10-20%: consider update, >20%: run /spec-writing)
- [ ] Advisory only: does NOT modify specs automatically

**Technical Details**:
- Files to modify: `spiral-grove/commands/review.md`
- Reference: Plan component 3 (lines 171-228), Spec component 2 (lines 144-165)
- Semantic matching: Plan lines 520-525

**Testing Requirements**:
- Test on feature with 0% drift (all criteria match)
- Test on feature with 20% drift (2 extra features)
- Test on feature with 50% drift (significant changes)
- Validate <5% false positive rate (spec success criterion #4)

**Notes**:
This enables the Maintenance → Development cycle. Critical for keeping specs synchronized.

---

### Task 15: Implement Semantic Matching for Drift Detection
**ID**: TASK-015
**Category**: Command Implementation
**Priority**: High
**Estimate**: 2-3 hours
**Dependencies**: TASK-014
**Assigned To**: Unassigned

**Description**:
Implement semantic matching algorithm to compare spec acceptance criteria against test descriptions with flexible keyword matching (not exact string match).

**Acceptance Criteria**:
- [ ] Tokenizes spec criteria into keywords
- [ ] Searches test files for keyword combinations
- [ ] Accepts partial matches with confidence score
- [ ] Match score: 3/4 keywords = 75% confidence
- [ ] Presents uncertain matches with confidence to user
- [ ] Allows user to confirm/reject uncertain matches
- [ ] Achieves <5% false positive rate on testing

**Technical Details**:
- Files to modify: `spiral-grove/commands/review.md` (within spec-vs-code mode)
- Reference: Plan Decision 6 (lines 496-525), Plan error handling (lines 899-917)
- Avoid simple keyword search (too many false positives)

**Testing Requirements**:
- Test on 10 features with known matches
- Measure false positive rate: target <5%
- Test edge case: Test with different wording than spec (should still match)

**Notes**:
Accuracy is critical. Too many false positives = users ignore the tool.

---

## Integration Tasks

### Task 16: Test Agent Standalone (Framework-Agnostic)
**ID**: TASK-016
**Category**: Integration
**Priority**: High
**Estimate**: 1 hour
**Dependencies**: TASK-007 (agent complete)
**Assigned To**: Unassigned

**Description**:
Validate that the module-doc-synthesizer agent works standalone without any Spiral Grove or .sdd/ context, meeting the framework-agnostic requirement.

**Acceptance Criteria**:
- [ ] Create test project without .sdd/ directory
- [ ] Invoke agent directly on a module via Task tool
- [ ] Agent generates CLAUDE.md successfully
- [ ] Generated CLAUDE.md has all required sections
- [ ] Generated CLAUDE.md is ≤400 lines
- [ ] No references to Spiral Grove in agent output
- [ ] No requirement for .sdd/ directory
- [ ] Spec acceptance test #6 passes (lines 337-343)

**Technical Details**:
- Test environment: Simple project outside Spiral Grove context
- Reference: Spec line 216 ("Do NOT couple module-doc-synthesizer agent to Spiral Grove")
- Acceptance test: Spec lines 337-343

**Testing Requirements**:
- Invoke agent on 3 different module types (API, CLI, library)
- Validate each generates appropriate documentation
- Confirm no SDD-specific content appears

**Notes**:
This validates a critical spec requirement: agent must be reusable beyond Spiral Grove.

---

### Task 17: Test Full Project Synthesis (Acceptance Test #1)
**ID**: TASK-017
**Category**: Integration
**Priority**: Critical
**Estimate**: 2 hours
**Dependencies**: TASK-013 (synthesize-docs command complete)
**Assigned To**: Unassigned

**Description**:
Run full documentation synthesis on a real project with 10+ modules to validate the complete workflow from discovery to SDD integration.

**Acceptance Criteria**:
- [ ] Test on project with 10-15 modules
- [ ] Phase 1: Detects modules correctly, user approves, manifest saved
- [ ] Phase 2: Spawns agents in parallel, generates all CLAUDE.md files
- [ ] Phase 3: Adds Origin fields to modules with matching specs
- [ ] All generated CLAUDE.md files are ≤400 lines
- [ ] Root CLAUDE.md created with project overview
- [ ] Manifest shows all modules "completed"
- [ ] Process completes in <2 minutes (well under 5-min target for 10 modules)
- [ ] Spec acceptance test #1 passes (lines 268-278)

**Technical Details**:
- Test project: Could use vibe-garden repository itself (dogfooding)
- Reference: Spec acceptance test #1 (lines 268-278)
- Performance target: <5 minutes for 100 modules, so <1 min for 10 modules

**Testing Requirements**:
- Validate all CLAUDE.md files have correct structure
- Check manifest JSON is well-formed
- Verify parallel execution (agents run simultaneously)
- Measure total time for performance validation

**Notes**:
This is the primary integration test. Should cover the happy path end-to-end.

---

### Task 18: Test Resumability After Interruption (Acceptance Test #5)
**ID**: TASK-018
**Category**: Integration
**Priority**: High
**Estimate**: 1 hour
**Dependencies**: TASK-012 (resumability logic), TASK-017
**Assigned To**: Unassigned

**Description**:
Validate that documentation synthesis can be interrupted mid-process and successfully resumed from the manifest.

**Acceptance Criteria**:
- [ ] Run synthesize-docs on project with 10 modules
- [ ] Simulate interruption after 5 modules complete
- [ ] Manifest shows: 5 completed, 5 pending
- [ ] Re-run synthesize-docs command
- [ ] Command detects partial completion
- [ ] User prompted: "Continue from where we left off? (5 modules remaining)"
- [ ] On approval: Only 5 pending modules processed
- [ ] Final manifest shows: 10 completed, 0 pending
- [ ] Already-completed CLAUDE.md files unchanged
- [ ] Spec acceptance test #5 passes (lines 324-333)

**Technical Details**:
- Simulation: Edit manifest mid-process to have mixed statuses
- Reference: Spec acceptance test #5 (lines 324-333)
- Validate idempotency: Re-running doesn't break anything

**Testing Requirements**:
- Test interruption at various points (25%, 50%, 75% complete)
- Validate manifest reading/writing is reliable
- Test full re-run (all completed) scenario

**Notes**:
Critical for large projects where timeout or user cancellation is likely.

---

## Testing Tasks

### Task 19: Test Hand-Edited Section Preservation (Acceptance Test #2)
**ID**: TASK-019
**Category**: Testing
**Priority**: Critical
**Estimate**: 1 hour
**Dependencies**: TASK-005 (hand-edit preservation), TASK-017
**Assigned To**: Unassigned

**Description**:
Validate that user-edited content between markers is preserved when regenerating CLAUDE.md files.

**Acceptance Criteria**:
- [ ] Create CLAUDE.md with hand-edited section containing custom content
- [ ] Run synthesize-docs to regenerate (e.g., after code changes)
- [ ] Agent reads existing CLAUDE.md
- [ ] Hand-edited section content is identical before/after
- [ ] New content generated by agent appears in correct sections
- [ ] No duplicate sections in output
- [ ] Markers remain in place
- [ ] Spec acceptance test #2 passes (lines 282-298)

**Technical Details**:
- Setup: Manually add `<!-- BEGIN: HAND-EDITED -->` section to test CLAUDE.md
- Content to preserve: Custom "Common Gotchas" section
- Reference: Spec acceptance test #2 (lines 282-298)

**Testing Requirements**:
- Compare CLAUDE.md before/after regeneration
- Validate hand-edited content byte-for-byte identical
- Test edge case: Multiple regenerations (preservation should work repeatedly)

**Notes**:
User trust depends on this working correctly. Loss of hand-edited content is unacceptable.

---

### Task 20: Test Spec-Code Drift Detection (Acceptance Test #3)
**ID**: TASK-020
**Category**: Testing
**Priority**: High
**Estimate**: 2 hours
**Dependencies**: TASK-015 (drift detection with semantic matching)
**Assigned To**: Unassigned

**Description**:
Validate that the spec-vs-code review mode correctly detects and categorizes drift between specifications and implementation.

**Acceptance Criteria**:
- [ ] Create test spec with 8 acceptance criteria
- [ ] Implement 10 features (8 from spec + 2 extra not in spec)
- [ ] Run `/spiral-grove:review spec-vs-code [feature-name]`
- [ ] Report shows: 0 Missing, 2 Extra, 0 Modified
- [ ] Drift percentage: 20% (2/10)
- [ ] Recommendation: "Consider running `/spiral-grove:spec-writing`"
- [ ] No automatic spec changes made
- [ ] Spec acceptance test #3 passes (lines 298-305)

**Technical Details**:
- Test feature: "Shopping cart" with wishlist/save-for-later extras
- Reference: Spec acceptance test #3 (lines 298-305)
- Drift categories: Missing, Extra, Modified

**Testing Requirements**:
- Test 0% drift (perfect alignment)
- Test 20% drift (moderate changes)
- Test 50%+ drift (significant divergence)
- Validate categorization accuracy

**Notes**:
False positive rate must be <5% per spec success criterion #4.

---

### Task 21: Test Development-Maintenance-Development Cycle (Acceptance Test #4)
**ID**: TASK-021
**Category**: Testing
**Priority**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-017, TASK-020
**Assigned To**: Unassigned

**Description**:
Validate the complete lifecycle workflow: Development → Maintenance (synthesize) → Code Evolution → Drift Detection → Spec Update → New Development.

**Acceptance Criteria**:
- [ ] Step 1: Complete feature implementation with all tasks done
- [ ] Step 2: Run `/spiral-grove:synthesize-docs` → generates CLAUDE.md
- [ ] Step 3: Simulate 6 months of bug fixes (code evolves, spec unchanged)
- [ ] Step 4: Run `/spiral-grove:review spec-vs-code` → detects 15% drift
- [ ] Step 5: Run `/spiral-grove:spec-writing` → user updates spec to match reality
- [ ] Step 6: Start new related feature using updated spec
- [ ] CLAUDE.md provides accurate operational context throughout
- [ ] Developer can recreate current system from updated spec
- [ ] Spec acceptance test #4 passes (lines 310-321)

**Technical Details**:
- Test feature: "Payment processing" with evolution
- Reference: Spec acceptance test #4 (lines 310-321)
- Simulates real-world long-lived project

**Testing Requirements**:
- Validate CLAUDE.md is useful for maintenance work
- Validate drift detection identifies real changes
- Validate spec update process works smoothly

**Notes**:
This tests the core value proposition: keeping specs and code synchronized over time.

---

### Task 22: Performance and Scale Testing
**ID**: TASK-022
**Category**: Testing
**Priority**: Medium
**Estimate**: 2 hours
**Dependencies**: TASK-017
**Assigned To**: Unassigned

**Description**:
Validate performance targets: 100 modules in <5 minutes, CLAUDE.md files ≤400 lines consuming ≤5% context budget.

**Acceptance Criteria**:
- [ ] Test on project with 50-100 modules (or create synthetic test project)
- [ ] Measure total time from command start to completion
- [ ] Target: 100 modules in <5 minutes (300 seconds)
- [ ] Validate parallel agent spawning works at scale
- [ ] Measure CLAUDE.md line counts (all ≤400 lines)
- [ ] Calculate context budget: 5 CLAUDE.md files × 400 lines = 2K tokens × 5 = 10K tokens ≤ 5% of 200K budget
- [ ] No timeout errors during parallel execution
- [ ] Spec success criteria #2-3 validated (lines 24-26)

**Technical Details**:
- May need to create synthetic test project if real projects don't have 100 modules
- Reference: Plan performance section (lines 937-980)
- Performance targets: Spec lines 24-26

**Testing Requirements**:
- Measure time with high precision
- Monitor for resource issues (memory, timeout)
- Validate manifest handles large module counts

**Notes**:
If performance target not met, may need to implement batch spawning (50 at a time).

---

## Release Task

### Task 23: Plugin Metadata Update and Release
**ID**: TASK-023
**Category**: Release
**Priority**: Medium
**Estimate**: 1-2 hours
**Dependencies**: TASK-001 through TASK-022 (all tasks complete)
**Assigned To**: Unassigned

**Description**:
Update plugin metadata, write changelog, create example files, and prepare for release.

**Acceptance Criteria**:
- [ ] Update `spiral-grove/.claude-plugin/plugin.json` version: 0.2.0 → 0.3.0
- [ ] Write changelog in plugin.json or separate CHANGELOG.md
- [ ] Changelog documents: new commands, agents, modes added
- [ ] Changelog notes performance capabilities (100 modules <5 min)
- [ ] Create example `.sdd/module-manifest.json` for documentation
- [ ] Update parent Spiral Grove docs if needed
- [ ] Update skill guide with lifecycle workflows
- [ ] All files committed to git
- [ ] Git tag created: v0.3.0
- [ ] Release notes prepared

**Technical Details**:
- Files to modify: `spiral-grove/.claude-plugin/plugin.json`
- Reference: Plan deployment (lines 1076-1137)
- Version bump: Minor version (new features, backward compatible)

**Testing Requirements**:
- Validate plugin.json is valid JSON
- Verify version number format
- Test plugin discovery after update

**Notes**:
This is the final step. All functionality must be complete and tested before release.

---

## Dependency Graph

```
TASK-001 (CLAUDE.md format spec) ──┬──→ TASK-003 (Agent structure)
TASK-002 (Manifest schema)         │
                                    │
                                    ├──→ TASK-004 (Agent routine) ──┬──→ TASK-005 (Hand-edit preservation)
                                    │                                │
                                    │                                ├──→ TASK-006 (400-line validation)
                                    │                                │
                                    │                                └──→ TASK-007 (Agent docs) ──→ TASK-016 (Standalone test)
                                    │
                                    ├──→ TASK-008 (Command structure) ──→ TASK-009 (Phase 1: Discovery)
                                    │
                                    └──→ TASK-009 + TASK-007 ──→ TASK-010 (Phase 2: Generation)
                                                                     │
                                                                     ├──→ TASK-011 (Phase 3: SDD integration)
                                                                     │
                                                                     ├──→ TASK-012 (Resumability)
                                                                     │
                                                                     └──→ TASK-013 (Output reporting)

TASK-014 (Review extension) ──→ TASK-015 (Semantic matching)

TASK-013 + TASK-015 ──→ TASK-017 (Full project test) ──┬──→ TASK-018 (Resumability test)
                                                         │
                                                         ├──→ TASK-019 (Hand-edit test)
                                                         │
                                                         ├──→ TASK-020 (Drift detection test)
                                                         │
                                                         ├──→ TASK-021 (Lifecycle test)
                                                         │
                                                         └──→ TASK-022 (Performance test)

ALL TASKS COMPLETE ──→ TASK-023 (Release)
```

---

## Implementation Order

**Phase 1: Foundation** (3-4 hours)
- TASK-001: CLAUDE.md format specification
- TASK-002: Module manifest schema documentation

**Phase 2: Agent Development** (9-13 hours)
- TASK-003: Agent core structure
- TASK-004: Agent routine implementation
- TASK-005: Hand-edited section preservation
- TASK-006: 400-line validation with condensing
- TASK-007: Agent documentation and examples

**Phase 3: Command Development** (15-21 hours)
- TASK-008: Synthesize-docs command structure
- TASK-009: Phase 1 - Module discovery
- TASK-010: Phase 2 - Parallel generation
- TASK-011: Phase 3 - SDD integration
- TASK-012: Resumability logic
- TASK-013: Output reporting and error handling
- TASK-014: Review command extension (spec-vs-code mode)
- TASK-015: Semantic matching for drift detection

**Phase 4: Integration Testing** (6-8 hours)
- TASK-016: Test agent standalone
- TASK-017: Test full project synthesis
- TASK-018: Test resumability after interruption
- TASK-019: Test hand-edited preservation
- TASK-020: Test drift detection
- TASK-021: Test development-maintenance cycle
- TASK-022: Performance and scale testing

**Phase 5: Release** (1-2 hours)
- TASK-023: Plugin metadata update and release

**Total Timeline**: 34-48 hours distributed across phases (matches plan estimate of 19-27 hours for core implementation + testing)

---

## Acceptance Test Mapping

Map specification acceptance tests to implementation tasks:

**Spec Test 1: Documentation synthesis at scale** (spec lines 268-278)
- Covered by: TASK-009 (module discovery), TASK-010 (parallel generation), TASK-011 (SDD integration), TASK-017 (integration test)
- Test files: TASK-017 validates full workflow on 10-15 module project
- Success: 100 modules in <5 minutes, all ≤400 lines, proper Origin fields

**Spec Test 2: Preserve hand-edited content** (spec lines 282-298)
- Covered by: TASK-005 (hand-edit preservation implementation), TASK-019 (integration test)
- Test files: TASK-019 validates preservation across regeneration
- Success: Hand-edited sections preserved verbatim, no duplicate sections

**Spec Test 3: Spec-code drift detection** (spec lines 298-305)
- Covered by: TASK-014 (spec-vs-code mode), TASK-015 (semantic matching), TASK-020 (integration test)
- Test files: TASK-020 validates drift categorization (Missing/Extra/Modified)
- Success: Correct drift percentage, proper recommendations, <5% false positives

**Spec Test 4: Development-Maintenance-Development cycle** (spec lines 310-321)
- Covered by: TASK-017 (synthesize-docs), TASK-020 (drift detection), TASK-021 (full cycle test)
- Test files: TASK-021 validates complete lifecycle
- Success: CLAUDE.md useful for maintenance, drift detection accurate, spec updateable

**Spec Test 5: Resumability after interruption** (spec lines 324-333)
- Covered by: TASK-012 (resumability logic), TASK-018 (integration test)
- Test files: TASK-018 simulates interruption and resumption
- Success: Manifest tracks progress, resume skips completed, idempotent

**Spec Test 6: Standalone agent usage** (spec lines 337-343)
- Covered by: TASK-007 (agent framework-agnostic), TASK-016 (standalone test)
- Test files: TASK-016 validates agent without Spiral Grove context
- Success: Works without .sdd/, no SDD references, generates valid CLAUDE.md

**Spec Test 7: Hierarchical project with child specs** (spec lines 347-356)
- Covered by: TASK-011 (SDD integration with hierarchy), TASK-017 (test with hierarchy)
- Test files: TASK-017 includes parent/child spec testing
- Success: Child CLAUDE.md links to child specs, root links to parent spec

---

## Definition of Done

A task is complete when:
- [ ] All acceptance criteria are met
- [ ] Code (agent/command markdown) is written and follows existing patterns
- [ ] Referenced files exist and are accessible
- [ ] Task is manually tested with positive results
- [ ] Integration tests pass (where applicable)
- [ ] Task status is updated in this document
- [ ] Any discovered issues are documented

---

## Progress Tracking

| Task ID | Status | PR | Notes |
|---------|--------|----|----|
| TASK-001 | Complete | 05b2da3 | CLAUDE.md format spec (600+ lines) |
| TASK-002 | Complete | 05b2da3 | Module manifest schema (550+ lines) |
| TASK-003 | Complete | a01a09c | Agent core structure (600+ lines) |
| TASK-004 | Complete | a01a09c | Agent routine (part of TASK-003) |
| TASK-005 | Complete | a01a09c | Hand-edit preservation (part of TASK-003) |
| TASK-006 | Complete | a01a09c | 400-line validation (part of TASK-003) |
| TASK-007 | Complete | TBD | Added invocation guide + good/bad examples |
| TASK-008 | Not Started | - | - |
| TASK-009 | Not Started | - | - |
| TASK-010 | Not Started | - | - |
| TASK-011 | Not Started | - | - |
| TASK-012 | Not Started | - | - |
| TASK-013 | Not Started | - | - |
| TASK-014 | Not Started | - | - |
| TASK-015 | Not Started | - | - |
| TASK-016 | Not Started | - | - |
| TASK-017 | Not Started | - | - |
| TASK-018 | Not Started | - | - |
| TASK-019 | Not Started | - | - |
| TASK-020 | Not Started | - | - |
| TASK-021 | Not Started | - | - |
| TASK-022 | Not Started | - | - |
| TASK-023 | Not Started | - | - |

**Status Options**: Not Started | In Progress | Blocked | In Review | Complete

---

## Validation Checklist

Before marking task breakdown as complete:
- [x] Every component in the plan has corresponding tasks (agent, synthesize-docs command, review extension)
- [x] All spec acceptance criteria are mapped to tasks (7 acceptance tests covered)
- [x] Dependencies are clearly documented (dependency graph provided)
- [x] Estimates are realistic (34-48 hours total, aligns with plan estimate)
- [x] Testing requirements are explicit (7 integration/testing tasks)
- [x] Foundation tasks come before dependent tasks (TASK-001/002 first)
- [x] No task is too large (largest is 5 hours for Phase 2 generation)
- [x] No task is too small (smallest is 1 hour for documentation)

---

## Notes for Implementation

**Key Principles to Remember:**
1. **Agent-Command Separation**: Agent (TASK-003 to TASK-007) must be framework-agnostic; command (TASK-008 to TASK-013) adds SDD orchestration
2. **Parallel Execution**: TASK-010 must use single message with multiple Task tool calls for performance
3. **Hand-Edit Preservation**: TASK-005 is critical for user trust; test thoroughly in TASK-019
4. **Context Efficiency**: TASK-006 enforcement of ≤400 lines is non-negotiable (spec success criterion)
5. **Resumability**: TASK-012 manifest-based resumption enables large-scale projects
6. **Semantic Matching**: TASK-015 must achieve <5% false positive rate (test in TASK-020)
7. **Idempotency**: All commands must be safe to re-run (don't break on second execution)

**Implementation Tips:**
- Start with TASK-001 (CLAUDE.md format spec) - it defines the contract for everything else
- Complete agent (TASK-003 to TASK-007) before starting command implementation
- Test agent standalone (TASK-016) before integrating with command (validates separation)
- Use vibe-garden repository for dogfooding (TASK-017) to ensure real-world applicability
- Monitor performance during TASK-022; if <5 min target not met, implement batch spawning fallback

**Common Pitfalls to Avoid:**
- Don't add SDD logic to agent (violates framework-agnostic requirement)
- Don't skip user approval for module detection (spec explicitly requires it)
- Don't use exact string matching for drift detection (semantic matching required)
- Don't auto-update specs in review mode (advisory only, spec line 210)
- Don't assume modules have matching specs (handle missing specs gracefully)

---

## Next Phase

Once this task breakdown is approved, use `/spiral-grove:implementation` to begin executing tasks in order, starting with Phase 1 (Foundation Tasks).
