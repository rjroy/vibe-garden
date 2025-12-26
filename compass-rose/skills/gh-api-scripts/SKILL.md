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
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py list-issues
```

**Output**: Array of issues with number, title, body, url, state, labels, status, priority, size.

### get-issue

Get a single issue by number with full project field values.

```bash
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py get-issue <number>
```

### set-status

Update the Status field of an issue in the project.

```bash
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py set-status <number> "<status>"
```

### add-to-project

Add an existing repository issue to the configured project.

```bash
python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py add-to-project <number>
```

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

## Related Documentation

- Spec: `.sdd/specs/2025-12-24-compass-rose-gh-api-scripts.md`
- Plan: `.sdd/plans/2025-12-24-compass-rose-gh-api-scripts-plan.md`
