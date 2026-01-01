# GitHub API Scripts Skill

## Overview

This skill provides Python scripts for reliable GitHub Project API operations. It replaces embedded GraphQL guidance in command markdown files with tested, reusable abstractions.

## Configuration

Operations require a configuration file at `.compass-rose/config.json`:

```json
{
  "project": {
    "owner": "<org-or-username>",
    "owner_type": "user",
    "number": <project-number>
  }
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `owner` | string | GitHub username or organization name |
| `owner_type` | string | Either `"user"` or `"organization"` |
| `number` | integer | Project number (from project URL) |

### Owner Type

- Use `"user"` for personal projects: `github.com/users/<name>/projects/<n>`
- Use `"organization"` for org projects: `github.com/orgs/<name>/projects/<n>`

## Operations

### list-issues

List all open issues in the configured project with automatic pagination.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh list-issues
```

**Example Output**:
```json
{
  "success": true,
  "data": {
    "issues": [
      {
        "number": 42,
        "title": "Fix login timeout",
        "body": "Users experiencing timeouts after 30 seconds...",
        "url": "https://github.com/my-org/my-repo/issues/42",
        "state": "OPEN",
        "labels": ["bug", "priority-high"],
        "status": "Ready",
        "priority": "P0",
        "size": "S"
      },
      {
        "number": 58,
        "title": "Add user preferences panel",
        "body": "Feature request for user settings...",
        "url": "https://github.com/my-org/my-repo/issues/58",
        "state": "OPEN",
        "labels": ["feature"],
        "status": "To Do",
        "priority": "P1",
        "size": "M"
      }
    ],
    "count": 2
  }
}
```

**Notes**:
- Automatically paginates through projects with >100 items
- Only returns issues in OPEN state
- Field values (status, priority, size) are extracted from project custom fields

### get-issue

Get a single issue by number with full project field values.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh get-issue <number>
```

**Example**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh get-issue 42
```

**Example Output**:
```json
{
  "success": true,
  "data": {
    "issue": {
      "number": 42,
      "title": "Fix login timeout",
      "body": "Users experiencing timeouts after 30 seconds...",
      "url": "https://github.com/my-org/my-repo/issues/42",
      "state": "OPEN",
      "labels": ["bug", "priority-high"],
      "status": "Ready",
      "priority": "P0",
      "size": "S"
    }
  }
}
```

**Error Cases**:
- `ISSUE_NOT_FOUND` - Issue number doesn't exist in the repository
- `ISSUE_NOT_IN_PROJECT` - Issue exists but isn't linked to the configured project

### set-status

Update the Status field of an issue in the project.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh set-status <number> "<status>"
```

**Example**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh set-status 42 "In Progress"
```

**Example Output**:
```json
{
  "success": true,
  "data": {
    "issue_number": 42,
    "previous_status": "Ready",
    "new_status": "In Progress"
  }
}
```

**Notes**:
- Status value must match one of the project's configured status options (case-sensitive)
- Common status values: `"Ready"`, `"In Progress"`, `"Done"`, `"To Do"`

**Error Cases**:
- `STATUS_INVALID` - Provided status value doesn't match project options
- `FIELD_NOT_FOUND` - Project doesn't have a Status field configured

### add-to-project

Add an existing repository issue to the configured project.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh add-to-project <number>
```

**Example**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh add-to-project 156
```

**Example Output**:
```json
{
  "success": true,
  "data": {
    "issue_number": 156,
    "item_id": "PVTI_lADOBQ..."
  }
}
```

**Notes**:
- Issue must exist in the repository before adding to project
- The returned `item_id` can be used for subsequent field updates

**Error Cases**:
- `ISSUE_NOT_FOUND` - Issue number doesn't exist in the repository

### set-priority

Update the Priority field of an issue in the project.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh set-priority <number> "<priority>"
```

**Example**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh set-priority 42 "P1"
```

**Example Output**:
```json
{
  "success": true,
  "data": {
    "number": 42,
    "previous_priority": null,
    "new_priority": "P1"
  }
}
```

**Notes**:
- Priority value must match one of the project's configured priority options (case-sensitive)
- Common priority values: `"P0"`, `"P1"`, `"P2"`, `"P3"`

**Error Cases**:
- `STATUS_INVALID` - Provided priority value doesn't match project options
- `FIELD_NOT_FOUND` - Project doesn't have a Priority field configured
- `ISSUE_NOT_IN_PROJECT` - Issue is not linked to the configured project

### set-size

Update the Size field of an issue in the project.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh set-size <number> "<size>"
```

**Example**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh set-size 42 "M"
```

**Example Output**:
```json
{
  "success": true,
  "data": {
    "number": 42,
    "previous_size": null,
    "new_size": "M"
  }
}
```

**Notes**:
- Size value must match one of the project's configured size options (case-sensitive)
- Common size values: `"S"`, `"M"`, `"L"`, `"XL"`

**Error Cases**:
- `STATUS_INVALID` - Provided size value doesn't match project options
- `FIELD_NOT_FOUND` - Project doesn't have a Size field configured
- `ISSUE_NOT_IN_PROJECT` - Issue is not linked to the configured project

## Output Format

All operations return JSON with a consistent envelope:

**Success**:
```json
{
  "success": true,
  "data": { ... }
}
```

**Error**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": "Actionable remediation guidance"
  }
}
```

## Error Codes

| Code | When | Remediation |
|------|------|-------------|
| `CONFIG_MISSING` | Config file not found | Create `.compass-rose/config.json` |
| `CONFIG_INVALID` | Required fields missing or invalid | Check owner, owner_type, number fields |
| `AUTH_REQUIRED` | gh CLI not authenticated | Run `gh auth login` |
| `AUTH_SCOPE_MISSING` | project scope not authorized | Run `gh auth refresh -s project` |
| `ISSUE_NOT_FOUND` | Issue number doesn't exist | Verify issue number |
| `ISSUE_NOT_IN_PROJECT` | Issue not linked to project | Add issue to project first |
| `STATUS_INVALID` | Status value not valid | Check project's status options |
| `FIELD_NOT_FOUND` | Status field not in project | Add Status field to project |
| `RATE_LIMITED` | API rate limit exceeded | Wait and retry |
| `API_ERROR` | Other API errors | Check error details |

## Requirements

- Python 3.12+ (stdlib only, no pip dependencies)
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)

## Usage in Commands

This skill is used by Compass Rose commands to interact with GitHub Projects:

| Command | Operations Used |
|---------|----------------|
| `/backlog` | `list-issues` |
| `/next-item` | `list-issues` |
| `/start-work` | `get-issue`, `set-status` |
| `/add-item` | `add-to-project`, `set-status`, `set-priority`, `set-size` |
| `/reprioritize` | `list-issues`, `set-priority`, `set-status` |

### Common Patterns

**Check for errors before processing:**
```bash
RESPONSE=$(${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh list-issues)

if echo "$RESPONSE" | jq -e '.success == false' > /dev/null; then
  echo "$RESPONSE" | jq -r '.error.details'
  exit 1
fi

# Process successful response
echo "$RESPONSE" | jq '.data.issues'
```

**Filter by status:**
```bash
# Get only "Ready" items
echo "$RESPONSE" | jq '[.data.issues[] | select(.status == "Ready")]'
```

**Sort by priority:**
```bash
# Sort by priority (P0 first)
echo "$RESPONSE" | jq '.data.issues | sort_by(.priority)'
```

## Related Documentation

- Spec: `.sdd/specs/2025-12-24-compass-rose-gh-api-scripts.md`
- Plan: `.sdd/plans/2025-12-24-compass-rose-gh-api-scripts-plan.md`
- Tasks: `.sdd/tasks/2025-12-25-compass-rose-gh-api-scripts-tasks.md`
