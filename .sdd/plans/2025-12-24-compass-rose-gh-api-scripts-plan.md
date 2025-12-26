---
specification: [.sdd/specs/2025-12-24-compass-rose-gh-api-scripts.md](./../specs/2025-12-24-compass-rose-gh-api-scripts.md)
status: Draft
version: 1.0.0
created: 2025-12-24
last_updated: 2025-12-24
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Compass Rose GitHub API Scripts - Technical Plan

## Overview

This plan implements a Python-based skill within the compass-rose plugin that provides reliable, tested abstractions for GitHub Project API operations. The scripts replace embedded GraphQL guidance in command markdown files, reducing token usage and eliminating interpretation errors.

The implementation uses Python 3.12+ with stdlib only, invoking `gh api graphql` via subprocess for authentication handling. Scripts will be organized as a single-file skill with clear function boundaries and consistent JSON output.

## Architecture

### System Context

The gh-api-scripts skill sits between Compass Rose commands and the GitHub API:

```
┌─────────────────────────────────────────────────────────────┐
│                   Compass Rose Commands                     │
│  (start-work.md, backlog.md, add-item.md, reprioritize.md) │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Invokes via Bash tool
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    gh-api-scripts Skill                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────┐  │
│  │list-issues│ │get-issue  │ │set-status │ │add-to-proj │  │
│  └───────────┘ └───────────┘ └───────────┘ └────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ subprocess: gh api graphql
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     gh CLI + GitHub API                     │
│              (authentication, rate limiting)                │
└─────────────────────────────────────────────────────────────┘
```

### Components

- **`scripts/gh_project.py`**: Single Python module with all operations (REQ-F-1 through REQ-F-4)
- **`SKILL.md`**: Skill definition documenting command-line invocation patterns
- **Config loader**: Reads `.compass-rose/config.json` with owner_type validation (REQ-F-8, REQ-F-9, REQ-F-10)

### Script Operations

| Script Entry Point | Purpose | Spec Requirement |
|-------------------|---------|------------------|
| `list_issues` | List all open issues in project with pagination | REQ-F-1 |
| `get_issue` | Retrieve single issue by number | REQ-F-2 |
| `set_status` | Update Status field of an issue | REQ-F-3 |
| `add_to_project` | Add existing repo issue to project | REQ-F-4 |

## Technical Decisions

### TD-1: Single Python Module Design

**Choice**: Implement all operations in a single `gh_project.py` file with CLI entry points via argparse.

**Requirements**: REQ-F-1, REQ-F-2, REQ-F-3, REQ-F-4, REQ-NF-4

**Rationale**:
- Python's argparse provides robust CLI parsing with subcommands
- Single file reduces complexity and makes the skill easier to maintain
- No package installation needed - can be invoked directly with `python3 scripts/gh_project.py <operation>`
- All shared utilities (config loading, error handling, subprocess management) stay colocated
- Matches existing skill patterns in the plugin ecosystem

**Invocation Pattern**:
```bash
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py list-issues
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py get-issue 42
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py set-status 42 "In Progress"
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py add-to-project 42
```

### TD-2: Owner Type Configuration

**Choice**: Add explicit `owner_type` field to config with values "user" or "organization".

**Requirements**: REQ-F-9, REQ-F-10

**Rationale**:
- GitHub GraphQL API requires different root queries: `user(login: $owner)` vs `organization(login: $owner)`
- The current config has `project.owner` but no way to determine if it's a user or org
- Explicit config is more reliable than runtime detection (which would require additional API calls)
- Simple validation: reject any value other than "user" or "organization"

**Config Schema Update**:
```json
{
  "project": {
    "owner": "rjroy",
    "owner_type": "user",
    "number": 8
  }
}
```

### TD-3: Subprocess Invocation via `gh api graphql`

**Choice**: Execute `gh api graphql` via subprocess.run() for all API operations.

**Requirements**: REQ-F-11, REQ-NF-4

**Rationale**:
- `gh` CLI handles OAuth token refresh, SSO, and credential storage
- No need to manage tokens or implement authentication logic
- Works immediately for any user with `gh auth login` completed
- Captures stdout/stderr separately for clean error handling
- `subprocess.run()` with `capture_output=True` and `text=True` provides clean interface

**Implementation Pattern**:
```python
result = subprocess.run(
    ["gh", "api", "graphql", "-f", f"query={query}", ...],
    capture_output=True,
    text=True,
    timeout=30
)
if result.returncode != 0:
    # Parse stderr for error details
```

### TD-4: Consistent JSON Output Format

**Choice**: All operations return JSON with a consistent envelope structure.

**Requirements**: REQ-F-5, REQ-F-6, REQ-F-7

**Rationale**:
- Commands can parse output reliably without special-casing
- Errors include actionable information for LLM to surface to user
- Success responses have predictable shape regardless of operation

**Success Envelope**:
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Envelope**:
```json
{
  "success": false,
  "error": {
    "code": "CONFIG_MISSING",
    "message": "Configuration file not found",
    "details": "Expected config at .compass-rose/config.json"
  }
}
```

### TD-5: Pagination Handling

**Choice**: Automatically paginate in `list_issues` using cursor-based pagination.

**Requirements**: REQ-F-1

**Rationale**:
- GitHub Projects can have >100 items
- Current commands embed pagination guidance that LLM must interpret
- Encapsulating pagination in the script eliminates a common error source
- Loop until `hasNextPage` is false, accumulating nodes

**Implementation**:
```python
def list_issues() -> list:
    all_items = []
    cursor = None
    while True:
        response = _execute_query(LIST_QUERY, cursor=cursor)
        items = response["data"]["user"]["projectV2"]["items"]
        all_items.extend(items["nodes"])
        if not items["pageInfo"]["hasNextPage"]:
            break
        cursor = items["pageInfo"]["endCursor"]
    return all_items
```

### TD-6: Error Code Taxonomy

**Choice**: Define specific error codes for all failure modes.

**Requirements**: REQ-F-12, REQ-F-13, REQ-F-14

**Rationale**:
- LLM can pattern-match on error codes to provide appropriate guidance
- Human-readable messages provide context
- Details field enables specific remediation steps

**Error Codes**:

| Code | When | Remediation Guidance |
|------|------|---------------------|
| `CONFIG_MISSING` | Config file not found | Create .compass-rose/config.json |
| `CONFIG_INVALID` | Required fields missing or invalid owner_type | Check owner, owner_type, number fields |
| `AUTH_REQUIRED` | gh CLI not authenticated | Run `gh auth login` |
| `AUTH_SCOPE_MISSING` | project scope not authorized | Run `gh auth refresh -s project` |
| `ISSUE_NOT_FOUND` | Issue number doesn't exist | Verify issue number with `gh issue view` |
| `ISSUE_NOT_IN_PROJECT` | Issue exists but not linked to project | Add issue to project first |
| `STATUS_INVALID` | Status value not in project's field options | List valid status values |
| `FIELD_NOT_FOUND` | Status field doesn't exist in project | Add Status field to project |
| `RATE_LIMITED` | GitHub API rate limit exceeded | Retry after X seconds |
| `API_ERROR` | Other GitHub API errors | Include raw error message |

### TD-7: GraphQL Query Templates

**Choice**: Embed GraphQL queries as Python constants with parameterization.

**Requirements**: REQ-F-1, REQ-F-2, REQ-F-3, REQ-F-4

**Rationale**:
- Queries are complex and error-prone to construct dynamically
- Constants are testable and reviewable
- Variable substitution via `gh api graphql -f` or `-F` flags
- Different query roots for user vs organization (see TD-2)

**Query Structure**:
```python
# Parameterized for owner_type
LIST_ISSUES_QUERY = """
query($owner: String!, $number: Int!, $cursor: String) {{
  {owner_type}(login: $owner) {{
    projectV2(number: $number) {{
      items(first: 100, after: $cursor) {{
        pageInfo {{ hasNextPage endCursor }}
        nodes {{
          id
          content {{
            ... on Issue {{
              number title body state url
              labels(first: 10) {{ nodes {{ name }} }}
            }}
          }}
          fieldValues(first: 10) {{
            nodes {{
              ... on ProjectV2ItemFieldSingleSelectValue {{
                name
                field {{ ... on ProjectV2SingleSelectField {{ name }} }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""
```

### TD-8: Transient Failure Handling

**Choice**: Implement automatic retry with exponential backoff for transient errors.

**Requirements**: REQ-NF-2

**Rationale**:
- Network timeouts and temporary API errors (502, 503) are common with external APIs
- Without retry logic, a single transient failure fails the entire operation
- Exponential backoff (1s, 2s, 4s) prevents hammering the API during outages
- Differentiate permanent errors (404, 401, 400) from retryable errors
- 3 attempts total (1 initial + 2 retries) balances reliability with responsiveness

**Retry Strategy**:
- **Retryable**: Network timeout, connection error, subprocess timeout, HTTP 502, 503
- **Non-retryable**: HTTP 404, 401, 400, rate limit 429 (handled specially with retry-after)
- **Backoff**: 1s → 2s → 4s (exponential)
- **Max attempts**: 3 total
- **Per-attempt timeout**: 30s

**Implementation**:
```python
def _execute_with_retry(cmd: list[str], max_attempts: int = 3) -> subprocess.CompletedProcess:
    delays = [1, 2, 4]  # exponential backoff
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result
            if not _is_retryable_error(result.stderr):
                return result  # permanent error, don't retry
        except subprocess.TimeoutExpired:
            pass  # retryable
        if attempt < max_attempts - 1:
            time.sleep(delays[attempt])
    return result  # return last failure
```

## Data Model

### Issue Data Structure (REQ-F-6)

All issue-returning operations normalize to this shape:

```python
@dataclass
class IssueData:
    number: int
    title: str
    body: str
    url: str
    state: str           # "OPEN" or "CLOSED"
    labels: list[str]
    status: str | None   # Project Status field value
    priority: str | None # Project Priority field value
    size: str | None     # Project Size field value
```

### Config Data Structure (REQ-F-8, REQ-F-9)

```python
@dataclass
class ProjectConfig:
    owner: str
    owner_type: str  # "user" or "organization"
    number: int
```

## API Design

### Command-Line Interface

```
gh_project.py <operation> [arguments]

Operations:
  list-issues           List all open issues in configured project
  get-issue <number>    Get single issue by number
  set-status <number> <status>  Update issue status
  add-to-project <number>       Add repo issue to project

All operations read config from .compass-rose/config.json
All output is JSON to stdout
Exit codes: 0 = success, 1 = error (details in JSON)
```

### Output Examples

**list-issues (success)**:
```json
{
  "success": true,
  "data": {
    "issues": [
      {
        "number": 42,
        "title": "Fix login timeout",
        "body": "Users are experiencing...",
        "url": "https://github.com/rjroy/vibe-garden/issues/42",
        "state": "OPEN",
        "labels": ["bug", "P0"],
        "status": "Ready",
        "priority": "P0",
        "size": "S"
      }
    ],
    "count": 1
  }
}
```

**get-issue (issue not found)**:
```json
{
  "success": false,
  "error": {
    "code": "ISSUE_NOT_FOUND",
    "message": "Issue #999 not found in repository",
    "details": "Verify issue number with: gh issue view 999"
  }
}
```

**set-status (success)**:
```json
{
  "success": true,
  "data": {
    "number": 42,
    "previous_status": "Ready",
    "new_status": "In Progress"
  }
}
```

## Integration Points

### Config File (`.compass-rose/config.json`)

- **Read by**: All operations at startup
- **Required fields**: `project.owner`, `project.owner_type`, `project.number`
- **Validation**: Fail fast with specific error if missing or invalid

### `gh` CLI

- **Authentication**: Uses existing `gh auth` credentials
- **Required scope**: `project` (for GraphQL project queries)
- **Detection**: Check `gh auth status` before operations

### Compass Rose Commands

Commands will be updated to invoke scripts instead of embedding GraphQL:

**Before (embedded in command markdown)**:
```markdown
### 3. Query All Project Items

Use GraphQL to fetch items:
\`\`\`bash
gh api graphql -f query='
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    ...
'
\`\`\`
```

**After (script invocation)**:
```markdown
### 3. Query All Project Items

Use the gh-api-scripts skill to fetch items:
\`\`\`bash
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py list-issues
\`\`\`

Parse the JSON output and extract the issues array.
```

## Error Handling, Performance, Security

### Error Strategy

- **Fail fast**: Validate config and auth before making API calls
- **Specific codes**: Map all failure modes to error codes (TD-6)
- **Actionable details**: Every error includes remediation steps
- **Stderr isolation**: Subprocess stderr captured separately from stdout
- **Exit codes**: 0 for success, 1 for any error (JSON body has details)

### Performance Targets (REQ-NF-1)

| Operation | Target | Notes |
|-----------|--------|-------|
| Config load | <50ms | Local file read, JSON parse |
| Single-issue operations | <500ms | Single API call |
| list-issues (100 items) | <2s | 1-2 API calls with pagination |
| list-issues (500 items) | <5s | 5 API calls |

### Security Measures

- **No credential storage**: All auth via `gh` CLI
- **No token exposure**: Subprocess handles auth internally
- **Config validation**: Reject unexpected fields/values
- **Input sanitization**: Issue numbers validated as positive integers

## Testing Strategy

### Unit Tests (REQ-NF-3)

- **Config loading**: Valid, missing, malformed, missing fields
- **JSON output**: Verify envelope structure for all operations
- **Error codes**: Each error code has a test case
- **Query generation**: User vs organization query selection

### Integration Tests

- **Mock subprocess**: Capture `gh api graphql` calls, return canned responses
- **Pagination simulation**: Multi-page responses
- **Real API**: Optional tests with `COMPASS_ROSE_TEST_PROJECT` env var

### Test Commands

```bash
# Run all tests
python3 -m pytest compass-rose/skills/gh-api-scripts/tests/

# Run with coverage
python3 -m pytest --cov=compass-rose/skills/gh-api-scripts/scripts
```

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `gh` CLI not installed | M | H | Check at startup, clear error message with install instructions |
| Rate limiting on large projects | L | M | Detect 429 response, include retry-after in error (REQ-F-14) |
| GraphQL schema changes | L | H | Pin to stable API version, test with actual API regularly |
| User/org detection wrong | M | M | Explicit owner_type config (TD-2) eliminates guessing |
| Subprocess hang/timeout | L | M | 30s timeout per attempt, max 3 attempts with backoff (TD-8) |
| Transient network failures | M | L | Automatic retry with exponential backoff (TD-8), >99% success rate |

## Dependencies

### Technical

- **Python 3.12+**: stdlib only, no pip dependencies (REQ-NF-4)
- **`gh` CLI**: Must be installed and authenticated
- **`jq`**: Not required (Python handles JSON)

### Team

- **Config migration**: Existing users need to add `owner_type` field
- **Command updates**: All 5 commands need to switch from embedded GraphQL to script invocation

## Open Questions

- [x] Script location → Skill within compass-rose plugin (`compass-rose/skills/gh-api-scripts/`)
- [x] Org vs user projects → Explicit `owner_type` in config (TD-2)
- [x] API access method → Via `gh` CLI subprocess (TD-3)
- [ ] Backwards compatibility for config → Migration path for existing configs without `owner_type`
