---
specification: [.sdd/specs/2025-12-24-compass-rose-gh-api-scripts.md](./../specs/2025-12-24-compass-rose-gh-api-scripts.md)
plan: [.sdd/plans/2025-12-24-compass-rose-gh-api-scripts-plan.md](./../plans/2025-12-24-compass-rose-gh-api-scripts-plan.md)
status: Ready for Implementation
version: 1.0.0
created: 2025-12-25
last_updated: 2025-12-25
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Compass Rose GitHub API Scripts - Task Breakdown

## Task Summary
Total: 14 tasks | Complexity Distribution: 5×S, 7×M, 2×L

## Foundation

### TASK-001: Project Structure and Config Loader
**Priority**: Critical | **Complexity**: M | **Dependencies**: None

**Description**: Create skill directory structure and implement config loading with validation for owner_type field.

**Acceptance Criteria**:
- [ ] Directory created: `compass-rose/skills/gh-api-scripts/scripts/`
- [ ] `gh_project.py` exists with argparse CLI structure (subcommands stubbed)
- [ ] Config loader reads `.compass-rose/config.json`
- [ ] Validates required fields: `project.owner`, `project.owner_type`, `project.number`
- [ ] Returns `CONFIG_MISSING` error with remediation when file absent
- [ ] Returns `CONFIG_INVALID` error when `owner_type` not "user" or "organization"

**Files**:
- Create: `compass-rose/skills/gh-api-scripts/scripts/gh_project.py`
- Create: `compass-rose/skills/gh-api-scripts/SKILL.md`

**Testing**: Unit tests for config loading (valid, missing, malformed, invalid owner_type)

---

### TASK-002: Subprocess Wrapper and Error Handling
**Priority**: Critical | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Implement subprocess execution wrapper for `gh api graphql` with retry logic, timeout handling, and error code taxonomy.

**Acceptance Criteria**:
- [ ] `_execute_with_retry()` function with exponential backoff (1s, 2s, 4s)
- [ ] 30s timeout per attempt, max 3 attempts
- [ ] Differentiates retryable (502, 503, timeout) vs non-retryable (404, 401, 400) errors
- [ ] `AUTH_REQUIRED` error detected from `gh` auth failure with `gh auth login` guidance
- [ ] `AUTH_SCOPE_MISSING` error detected with `gh auth refresh -s project` guidance
- [ ] `RATE_LIMITED` error detected with retry-after from 429 response
- [ ] `API_ERROR` fallback for other failures includes raw message

**Files**:
- Modify: `compass-rose/skills/gh-api-scripts/scripts/gh_project.py`

**Testing**: Unit tests for each error code with mocked subprocess responses

---

### TASK-003: JSON Output Envelope
**Priority**: High | **Complexity**: S | **Dependencies**: TASK-001

**Description**: Implement consistent JSON output format for all operations (success and error envelopes).

**Acceptance Criteria**:
- [ ] Success: `{"success": true, "data": {...}}`
- [ ] Error: `{"success": false, "error": {"code": "...", "message": "...", "details": "..."}}`
- [ ] All output goes to stdout
- [ ] Exit code 0 for success, 1 for any error
- [ ] Helper functions for formatting both envelopes

**Files**:
- Modify: `compass-rose/skills/gh-api-scripts/scripts/gh_project.py`

**Testing**: Verify envelope structure in all operation tests

---

## Core Operations

### TASK-004: List Issues Operation with Pagination
**Priority**: Critical | **Complexity**: L | **Dependencies**: TASK-002, TASK-003

**Description**: Implement `list-issues` operation that fetches all open issues from configured project with automatic pagination.

**Acceptance Criteria**:
- [ ] CLI: `python3 gh_project.py list-issues`
- [ ] Uses correct GraphQL query root based on owner_type (user vs organization)
- [ ] Paginates automatically using cursor until `hasNextPage` is false
- [ ] Returns all issues with: number, title, body, url, state, labels, status, priority, size
- [ ] Handles projects with >100 items correctly
- [ ] Returns `FIELD_NOT_FOUND` if Status field missing from project

**Files**:
- Modify: `compass-rose/skills/gh-api-scripts/scripts/gh_project.py`

**Testing**: Unit tests with mocked multi-page responses, edge case for 0 issues

---

### TASK-005: Get Issue Operation
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-002, TASK-003

**Description**: Implement `get-issue` operation that retrieves a single issue by number with full project field values.

**Acceptance Criteria**:
- [ ] CLI: `python3 gh_project.py get-issue <number>`
- [ ] Validates issue number is positive integer
- [ ] Returns issue with: number, title, body, url, state, labels, status, priority, size
- [ ] Returns `ISSUE_NOT_FOUND` if issue doesn't exist
- [ ] Returns `ISSUE_NOT_IN_PROJECT` if issue exists but not linked to project

**Files**:
- Modify: `compass-rose/skills/gh-api-scripts/scripts/gh_project.py`

**Testing**: Unit tests for valid issue, not found, not in project

---

### TASK-006: Set Status Operation
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-002, TASK-003

**Description**: Implement `set-status` operation that updates the Status field of an issue in the project.

**Acceptance Criteria**:
- [ ] CLI: `python3 gh_project.py set-status <number> "<status>"`
- [ ] Looks up project's Status field ID and validates status value exists
- [ ] Updates issue status via GraphQL mutation
- [ ] Returns previous and new status in success response
- [ ] Returns `STATUS_INVALID` if status value not in project's field options
- [ ] Returns `FIELD_NOT_FOUND` if Status field doesn't exist in project

**Files**:
- Modify: `compass-rose/skills/gh-api-scripts/scripts/gh_project.py`

**Testing**: Unit tests for valid update, invalid status, field not found

---

### TASK-007: Add to Project Operation
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-002, TASK-003

**Description**: Implement `add-to-project` operation that adds an existing repository issue to the configured project.

**Acceptance Criteria**:
- [ ] CLI: `python3 gh_project.py add-to-project <number>`
- [ ] Looks up issue's node ID from repository
- [ ] Adds issue to project via GraphQL mutation
- [ ] Returns success with issue number and project item ID
- [ ] Returns `ISSUE_NOT_FOUND` if issue doesn't exist in repository

**Files**:
- Modify: `compass-rose/skills/gh-api-scripts/scripts/gh_project.py`

**Testing**: Unit tests for successful add, issue not found

---

## Testing

### TASK-008: Unit Test Suite
**Priority**: High | **Complexity**: L | **Dependencies**: TASK-004, TASK-005, TASK-006, TASK-007

**Description**: Create comprehensive unit test suite with mocked subprocess for all operations and error conditions.

**Acceptance Criteria**:
- [ ] Test file: `tests/test_gh_project.py`
- [ ] Config loading tests (valid, missing, malformed, invalid fields)
- [ ] All error codes tested with appropriate mocked responses
- [ ] Query generation tests for user vs organization owner_type
- [ ] Pagination simulation with multi-page responses
- [ ] Retry logic tested with transient failures
- [ ] All 10 acceptance tests from spec covered

**Files**:
- Create: `compass-rose/skills/gh-api-scripts/tests/test_gh_project.py`
- Create: `compass-rose/skills/gh-api-scripts/tests/__init__.py`

**Testing**: `python3 -m pytest compass-rose/skills/gh-api-scripts/tests/`

---

## Integration

### TASK-009: Update backlog.md Command
**Priority**: Medium | **Complexity**: S | **Dependencies**: TASK-004

**Description**: Update backlog.md to invoke gh-api-scripts skill instead of embedded GraphQL guidance.

**Acceptance Criteria**:
- [ ] Replace GraphQL query guidance with script invocation
- [ ] Document JSON output parsing
- [ ] Remove cursor management instructions (handled by script)

**Files**:
- Modify: `compass-rose/commands/backlog.md`

**Testing**: Manual verification that /backlog command works with new script

---

### TASK-010: Update start-work.md Command
**Priority**: Medium | **Complexity**: S | **Dependencies**: TASK-005, TASK-006

**Description**: Update start-work.md to invoke gh-api-scripts skill for issue retrieval and status updates.

**Acceptance Criteria**:
- [ ] Replace GraphQL query guidance with get-issue and set-status invocations
- [ ] Document JSON output parsing
- [ ] Simplify status update instructions

**Files**:
- Modify: `compass-rose/commands/start-work.md`

**Testing**: Manual verification that /start-work command works with new scripts

---

### TASK-011: Update add-item.md Command
**Priority**: Medium | **Complexity**: S | **Dependencies**: TASK-007

**Description**: Update add-item.md to invoke gh-api-scripts skill for adding issues to project.

**Acceptance Criteria**:
- [ ] Replace GraphQL mutation guidance with add-to-project invocation
- [ ] Document JSON output parsing

**Files**:
- Modify: `compass-rose/commands/add-item.md`

**Testing**: Manual verification that /add-item command works with new script

---

### TASK-012: Update reprioritize.md Command
**Priority**: Medium | **Complexity**: S | **Dependencies**: TASK-004

**Description**: Update reprioritize.md to invoke gh-api-scripts skill for listing project items.

**Acceptance Criteria**:
- [ ] Replace GraphQL query guidance with list-issues invocation
- [ ] Document JSON output parsing
- [ ] Remove pagination instructions (handled by script)

**Files**:
- Modify: `compass-rose/commands/reprioritize.md`

**Testing**: Manual verification that /reprioritize command works with new script

---

## Documentation

### TASK-013: Config Migration Documentation
**Priority**: Medium | **Complexity**: S | **Dependencies**: TASK-001

**Description**: Document migration path for existing configs to add owner_type field.

**Acceptance Criteria**:
- [ ] Update compass-rose README with new config schema
- [ ] Include example config with owner_type
- [ ] Note that existing configs need owner_type added

**Files**:
- Modify: `compass-rose/README.md` or `compass-rose/CLAUDE.md`

**Testing**: Documentation review

---

### TASK-014: Skill Documentation
**Priority**: Low | **Complexity**: S | **Dependencies**: TASK-004, TASK-005, TASK-006, TASK-007

**Description**: Complete SKILL.md with full usage documentation for the gh-api-scripts skill.

**Acceptance Criteria**:
- [ ] Document all four operations with examples
- [ ] Include error code reference table
- [ ] Document config requirements

**Files**:
- Modify: `compass-rose/skills/gh-api-scripts/SKILL.md`

**Testing**: Documentation review

---

## Dependency Graph
```
TASK-001 ──┬─> TASK-002 ──┬─> TASK-004 ──┬─> TASK-008 ──> TASK-009, TASK-012
           │              │              │
           │              └─> TASK-005 ──┼─> TASK-010
           │              │              │
           │              └─> TASK-006 ──┤
           │              │              │
           │              └─> TASK-007 ──┼─> TASK-011
           │                             │
           └─> TASK-003 ─────────────────┘
           │
           └─> TASK-013

TASK-004 ──┬─> TASK-014
TASK-005 ──┤
TASK-006 ──┤
TASK-007 ──┘
```

## Implementation Order
**Phase 1** (Foundation, M×2 + S×1): TASK-001, TASK-002, TASK-003
**Phase 2** (Core Operations, L×1 + M×3): TASK-004, TASK-005, TASK-006, TASK-007
**Phase 3** (Testing, L×1): TASK-008
**Phase 4** (Integration, S×4): TASK-009, TASK-010, TASK-011, TASK-012
**Phase 5** (Documentation, S×2): TASK-013, TASK-014

## Notes
- **Parallelization**: TASK-002 and TASK-003 can run in parallel after TASK-001. TASK-009/010/011/012 can run in parallel after their dependencies. TASK-013 can start after TASK-001.
- **Critical path**: TASK-001 → TASK-002 → TASK-004 → TASK-008 → TASK-009
