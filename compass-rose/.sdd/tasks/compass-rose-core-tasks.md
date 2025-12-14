---
specification: [.sdd/specs/compass-rose-core.md](./../specs/compass-rose-core.md)
plan: [.sdd/plans/compass-rose-core-plan.md](./../plans/compass-rose-core-plan.md)
status: Draft
version: 1.0.0
created: 2025-12-14
last_updated: 2025-12-14
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Compass Rose Core - Task Breakdown

## Task Summary
Total: 14 tasks | Complexity Distribution: 4×S, 7×M, 3×L

## Foundation

### TASK-001: Create Plugin Structure
**Priority**: Critical | **Complexity**: S | **Dependencies**: None

**Description**: Set up the compass-rose plugin directory structure with required subdirectories for commands, agents, and skills.

**Acceptance Criteria**:
- [ ] `commands/` directory exists
- [ ] `agents/` directory exists
- [ ] `skills/gh-project-reference/` directory exists
- [ ] Plugin loads successfully in Claude Code

**Files**: Create: `commands/.gitkeep`, `agents/.gitkeep`, `skills/gh-project-reference/.gitkeep`

**Testing**: Run `claude code` in repo, verify plugin appears in `/plugins` list

---

### TASK-002: Implement Configuration Schema
**Priority**: Critical | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Create configuration loading logic and schema validation. Config stored in `.compass-rose/config.json` with project owner and number.

**Acceptance Criteria**:
- [ ] Config schema documented in skill reference
- [ ] Example config file provided in README
- [ ] Clear error message when config missing or invalid
- [ ] Preferences section optional with defaults

**Files**:
- Update: `README.md` (config section)
- Update: `skills/gh-project-reference/SKILL.md` (config loading patterns)

**Testing**: Create valid config, verify Claude can read it; create invalid config, verify clear error

---

### TASK-003: Create gh-project-reference Skill
**Priority**: Critical | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Document `gh` CLI patterns for project operations including field discovery, item listing, and item editing.

**Acceptance Criteria**:
- [ ] `gh project field-list` pattern documented with JSON parsing
- [ ] `gh project item-list` pattern documented with filtering
- [ ] `gh project item-edit` pattern documented (single-field-per-call limitation noted)
- [ ] `gh issue create` + `gh project item-add` pattern documented
- [ ] Field matching heuristics documented (priority, size, status, iteration)
- [ ] Error handling patterns documented (auth, missing fields)

**Files**: Create: `skills/gh-project-reference/SKILL.md`

**Testing**: Manually verify each `gh` command pattern works against a test project

---

## Commands - Read Operations

### TASK-004: Implement /next-item Command
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-002, TASK-003

**Description**: Create command that recommends highest-priority ready item with rationale.

**Acceptance Criteria**:
- [ ] Loads config and discovers fields
- [ ] Queries items with Status = "Ready" (or equivalent)
- [ ] Sorts by Priority (P0 > P1 > P2 > P3), then creation date
- [ ] Presents top 2-3 options in tabular format (TD-8)
- [ ] Includes rationale explaining recommendation
- [ ] Handles missing Priority field gracefully

**Files**: Create: `commands/next-item.md`

**Testing**: AT-2 (Next Item Query) - Given P0 and P1 items in Ready, recommends P0 first

---

### TASK-005: Implement /backlog Command
**Priority**: High | **Complexity**: L | **Dependencies**: TASK-002, TASK-003, TASK-009

**Description**: Create command that reviews backlog and spawns backlog-analyzer agent for quality analysis.

**Acceptance Criteria**:
- [ ] Loads config and discovers fields
- [ ] Queries all non-Done items
- [ ] Spawns backlog-analyzer agent for analysis
- [ ] Identifies "well-defined" items (clear description + acceptance criteria)
- [ ] Presents 2-3 recommendations in tabular format with rationale

**Files**: Create: `commands/backlog.md`

**Testing**: AT-3 (Backlog Review) - Given 10 items, presents 2-3 recommendations with rationale

---

### TASK-006: Implement /reprioritize Command
**Priority**: Medium | **Complexity**: L | **Dependencies**: TASK-002, TASK-003, TASK-010

**Description**: Create command for codebase-aware priority recommendations that spawns codebase-scanner agent.

**Acceptance Criteria**:
- [ ] Loads config and discovers fields
- [ ] Queries all items
- [ ] Spawns codebase-scanner agent to analyze relevance
- [ ] Presents priority change recommendations with rationale
- [ ] Batch-updates priorities via `gh` CLI with user approval
- [ ] Reports summary of changes (e.g., "10 of 60 issues updated")

**Files**: Create: `commands/reprioritize.md`

**Testing**: AT-4 (Priority Update) - Given approval, updates priorities and reports changes

---

## Commands - Write Operations

### TASK-007: Implement /add-item Command
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-002, TASK-003

**Description**: Create command to add new repository issues and link them to the project.

**Acceptance Criteria**:
- [ ] Gathers item details (title, description, priority, size)
- [ ] Creates repository issue via `gh issue create`
- [ ] Adds issue to project via `gh project item-add`
- [ ] Sets custom fields via `gh project item-edit` (multiple calls)
- [ ] Confirms creation with issue number and link

**Files**: Create: `commands/add-item.md`

**Testing**: AT-7 (Issue Creation) - Create bug, verify issue created and linked to project

---

### TASK-008: Implement /start-work Command
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-002, TASK-003, TASK-004

**Description**: Create command to begin work on an item with XL/L escalation prompts.

**Acceptance Criteria**:
- [ ] Allows item selection (from /next-item or user-specified)
- [ ] Checks Size field for XL → always prompts about spec-writing
- [ ] Checks Size field for L → prompts based on `preferences.promptForLargeItems`
- [ ] Updates Status to "In Progress" via `gh project item-edit`
- [ ] Reads full issue description via `gh issue view`
- [ ] Provides options: "Write spec first" or "Start implementation directly"

**Files**: Create: `commands/start-work.md`

**Testing**: AT-5 (XL Escalation) - Given XL item, prompts about spec-writing

---

## Agents

### TASK-009: Implement backlog-analyzer Agent
**Priority**: High | **Complexity**: L | **Dependencies**: TASK-003

**Description**: Create agent that analyzes backlog items for quality and readiness.

**Acceptance Criteria**:
- [ ] Analyzes item descriptions for clarity and completeness
- [ ] Identifies items with clear acceptance criteria
- [ ] Assesses "definition quality" (well-defined vs vague)
- [ ] Ranks items by combination of priority, size, and definition quality
- [ ] Returns structured recommendations with rationale

**Files**: Create: `agents/backlog-analyzer.md`

**Testing**: Given 10 items with varying quality, correctly identifies well-defined items

---

### TASK-010: Implement codebase-scanner Agent
**Priority**: Medium | **Complexity**: L | **Dependencies**: TASK-003

**Description**: Create agent that scans codebase to assess issue relevance for reprioritization.

**Acceptance Criteria**:
- [ ] Explores current codebase state (file structure, recent changes)
- [ ] Compares issue descriptions against codebase reality
- [ ] Identifies issues that may be resolved or outdated
- [ ] Identifies issues with increased relevance (related code changed)
- [ ] Returns priority change recommendations with rationale

**Files**: Create: `agents/codebase-scanner.md`

**Testing**: Given codebase with completed feature, identifies related issues as potentially resolved

---

## Documentation & Polish

### TASK-011: Update README with User Guide
**Priority**: Medium | **Complexity**: S | **Dependencies**: TASK-004 through TASK-008

**Description**: Update README.md with complete user guide including all commands and workflows.

**Acceptance Criteria**:
- [ ] Quick start section with config setup
- [ ] All commands documented with examples
- [ ] Workflow examples (triage → work → completion)
- [ ] Troubleshooting section (auth, missing fields)

**Files**: Update: `README.md`

**Testing**: New user can follow README to set up and use plugin

---

### TASK-012: Update CLAUDE.md with Operational Details
**Priority**: Medium | **Complexity**: S | **Dependencies**: TASK-004 through TASK-010

**Description**: Update CLAUDE.md with operational knowledge for Claude sessions.

**Acceptance Criteria**:
- [ ] All commands listed with usage patterns
- [ ] Integration with Spiral Grove documented
- [ ] Error handling patterns documented
- [ ] Field discovery behavior documented

**Files**: Update: `CLAUDE.md`

**Testing**: Claude can accurately describe plugin capabilities

---

### TASK-013: Handle Missing Fields Gracefully
**Priority**: Medium | **Complexity**: M | **Dependencies**: TASK-004 through TASK-008

**Description**: Ensure all commands handle missing custom fields with warnings, not failures.

**Acceptance Criteria**:
- [ ] Missing Priority field → warn, treat all items as equal priority
- [ ] Missing Size field → warn, skip size-based recommendations
- [ ] Missing Status field → warn, use project column position
- [ ] Warnings are clear but don't block operation

**Files**: Update: All command files

**Testing**: AT-6 (Missing Fields) - Given project without Priority field, warns but continues

---

### TASK-014: Integration Testing Suite
**Priority**: Low | **Complexity**: S | **Dependencies**: TASK-004 through TASK-010

**Description**: Create manual testing protocol document with test scenarios.

**Acceptance Criteria**:
- [ ] Test project setup instructions
- [ ] Test scenarios for each acceptance test (AT-1 through AT-7)
- [ ] Expected outcomes documented
- [ ] Troubleshooting for common test failures

**Files**: Create: `.sdd/testing/manual-test-protocol.md`

**Testing**: Execute protocol against test project, all scenarios pass

---

## Dependency Graph
```
TASK-001 ──┬──> TASK-002 ──┬──> TASK-004 ──> TASK-005
           │               │              └──> TASK-008
           ├──> TASK-003 ──┼──> TASK-007
           │               ├──> TASK-006
           │               ├──> TASK-009 ──> TASK-005
           │               └──> TASK-010 ──> TASK-006
           │
           └──> (TASK-011, TASK-012) depend on commands
                 TASK-013 depends on commands
                 TASK-014 depends on all components
```

## Implementation Order

**Phase 1** (Foundation, 1×S + 2×M): TASK-001, TASK-002, TASK-003
- Sets up plugin structure, config, and gh CLI patterns
- Parallelization: TASK-002 and TASK-003 after TASK-001

**Phase 2** (Core Commands, 3×M): TASK-004, TASK-007, TASK-008
- Implements primary read/write commands
- Parallelization: TASK-007 parallel with TASK-004; TASK-008 after TASK-004

**Phase 3** (Agents, 2×L): TASK-009, TASK-010
- Implements analysis agents for backlog and codebase
- Parallelization: Both can proceed in parallel

**Phase 4** (Advanced Commands, 2×L): TASK-005, TASK-006
- Implements commands that depend on agents
- Parallelization: Both can proceed in parallel after their agent dependencies

**Phase 5** (Polish, 3×S + 1×M): TASK-011, TASK-012, TASK-013, TASK-014
- Documentation updates and graceful degradation
- Parallelization: TASK-011 and TASK-012 parallel; TASK-013 and TASK-014 follow

## Notes

- **Parallelization**: Phases 2-4 have parallel opportunities within each phase
- **Critical path**: TASK-001 → TASK-003 → TASK-009 → TASK-005 (longest chain)
- **Testing dependency**: Integration testing (TASK-014) requires test GitHub Project setup
