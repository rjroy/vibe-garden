# GitHub Project Reference Skill

## Overview

This skill provides reference documentation for working with GitHub Projects via the `gh` CLI. It covers configuration loading, field discovery, item management, and error handling patterns used throughout Compass Rose.

## Configuration Loading

### Schema

Configuration is stored in `.compass-rose/config.json` at the repository root:

```json
{
  "project": {
    "owner": "<org-or-username>",
    "number": <project-number>
  },
  "preferences": {
    "promptForLargeItems": true,
    "largeSizeThreshold": ["L", "XL"],
    "validateIssuesBeforeWork": true,
    "validationTimeoutSeconds": 30
  }
}
```

### Required Fields

- `project.owner`: GitHub organization or username that owns the project
- `project.number`: Project number (visible in project URL)

### Optional Fields

- `preferences.promptForLargeItems`: Whether to prompt before starting L-sized items (default: `true`)
- `preferences.largeSizeThreshold`: Array of size values that trigger spec-writing prompts (default: `["L", "XL"]`)
- `preferences.validateIssuesBeforeWork`: Whether to validate issue relevance before starting work (default: `true`)
- `preferences.validationTimeoutSeconds`: Maximum time for issue validation checks (default: `30`)

### Configuration Loading Pattern

```bash
# Check if config exists
if [ ! -f .compass-rose/config.json ]; then
  echo "Error: Configuration file not found."
  echo ""
  echo "Please create .compass-rose/config.json with your project details:"
  echo ""
  echo '{'
  echo '  "project": {'
  echo '    "owner": "<org-or-username>",'
  echo '    "number": <project-number>'
  echo '  }'
  echo '}'
  exit 1
fi

# Parse config (using jq or similar)
OWNER=$(jq -r '.project.owner' .compass-rose/config.json)
NUMBER=$(jq -r '.project.number' .compass-rose/config.json)

# Validate required fields
if [ "$OWNER" = "null" ] || [ "$NUMBER" = "null" ]; then
  echo "Error: Invalid configuration."
  echo ""
  echo "Both 'project.owner' and 'project.number' are required."
  echo ""
  echo "Example:"
  echo '{'
  echo '  "project": {'
  echo '    "owner": "my-org",'
  echo '    "number": 123'
  echo '  }'
  echo '}'
  exit 1
fi
```

### Error Messages

**Missing Configuration File**:
```
Error: Configuration file not found.

Please create .compass-rose/config.json with your project details:

{
  "project": {
    "owner": "<org-or-username>",
    "number": <project-number>
  }
}

Find your project number in the project URL:
https://github.com/orgs/<owner>/projects/<number>
```

**Invalid Configuration**:
```
Error: Invalid configuration.

Both 'project.owner' and 'project.number' are required.

Example:
{
  "project": {
    "owner": "my-org",
    "number": 123
  }
}
```

**Project Not Found**:
```
Error: Project not found.

Verify that:
1. Project owner is correct: <owner>
2. Project number is correct: <number>
3. You have access to the project
4. You are authenticated: gh auth status
```

## Field Discovery

GitHub Projects support custom fields with user-defined names. Compass Rose discovers fields at runtime rather than assuming specific names.

### Discovering Fields

```bash
# List all fields in the project
gh project field-list $NUMBER --owner $OWNER --format json

# Returns array of field objects:
# [
#   {
#     "id": "PVTSSF_lADOABCDEF...",
#     "name": "Status",
#     "type": "SINGLE_SELECT",
#     "options": [
#       {"id": "...", "name": "To Do"},
#       {"id": "...", "name": "In Progress"},
#       {"id": "...", "name": "Done"}
#     ]
#   },
#   {
#     "id": "PVTSSF_lAGHIJKL...",
#     "name": "Priority",
#     "type": "SINGLE_SELECT",
#     "options": [
#       {"id": "...", "name": "P0"},
#       {"id": "...", "name": "P1"},
#       {"id": "...", "name": "P2"},
#       {"id": "...", "name": "P3"}
#     ]
#   }
# ]
```

### Field Matching Patterns

When looking for specific field types, use case-insensitive pattern matching:

| Semantic Field | Matching Patterns |
|----------------|-------------------|
| **Status** | "status", "state", "column" |
| **Priority** | "priority", "p0-p3", "severity", "importance" |
| **Size** | "size", "estimate", "points", "effort" |
| **Iteration** | "iteration", "sprint", "cycle", "milestone" |

### Handling Missing Fields

Always provide graceful degradation when expected fields are missing:

```
Warning: Priority field not found in project. All items will be treated as equal priority.

Available fields: Status, Size, Iteration

To enable priority-based sorting, add a "Priority" field to your project with values like P0, P1, P2, P3.
```

## Item Management

### Listing Items

```bash
# Get all items in the project
gh project item-list $NUMBER --owner $OWNER --format json --limit 100

# Filter by field value (using jq after fetching)
gh project item-list $NUMBER --owner $OWNER --format json | \
  jq '[.items[] | select(.status == "Ready")]'
```

### Creating Items (Two-Step Process)

Compass Rose always creates repository issues (not draft items):

```bash
# Step 1: Create repository issue
ISSUE_URL=$(gh issue create \
  --title "Fix login timeout" \
  --body "Users are experiencing timeouts after 30 seconds..." \
  --repo $REPO \
  --json url \
  --jq .url)

# Step 2: Add issue to project
ITEM_ID=$(gh project item-add $NUMBER \
  --owner $OWNER \
  --url $ISSUE_URL \
  --format json \
  --jq .id)

# Step 3: Set custom fields (one at a time)
# Note: gh CLI requires separate calls for each field

# Set Priority to P1
gh project item-edit \
  --id $ITEM_ID \
  --project-id $PROJECT_ID \
  --field-id $PRIORITY_FIELD_ID \
  --single-select-option-id $P1_OPTION_ID

# Set Size to M
gh project item-edit \
  --id $ITEM_ID \
  --project-id $PROJECT_ID \
  --field-id $SIZE_FIELD_ID \
  --single-select-option-id $M_OPTION_ID

# Set Status to Ready
gh project item-edit \
  --id $ITEM_ID \
  --project-id $PROJECT_ID \
  --field-id $STATUS_FIELD_ID \
  --single-select-option-id $READY_OPTION_ID
```

### Updating Item Fields

Each field requires a separate `gh project item-edit` call:

```bash
# Get field and option IDs from field-list output
PRIORITY_FIELD_ID="PVTSSF_..."
P0_OPTION_ID="..."

# Update priority
gh project item-edit \
  --id $ITEM_ID \
  --project-id $PROJECT_ID \
  --field-id $PRIORITY_FIELD_ID \
  --single-select-option-id $P0_OPTION_ID
```

## Authentication and Permissions

### Required Scopes

GitHub Projects require the `project` scope:

```bash
# Check current auth status
gh auth status

# Refresh authentication with project scope
gh auth refresh -s project
```

### Error Handling

**Not Authenticated**:
```
Error: GitHub CLI is not authenticated.

Run the following command to authenticate:
  gh auth login
```

**Missing Project Scope**:
```
Error: Missing required 'project' scope.

Run the following command to add the project scope:
  gh auth refresh -s project
```

## Performance Considerations

### Query Limits

Use `--limit` parameter to control result size:

```bash
# Typical backlog: limit to 100 items
gh project item-list $NUMBER --owner $OWNER --limit 100

# Large backlog: fetch in batches (gh handles pagination)
gh project item-list $NUMBER --owner $OWNER --limit 500
```

### Caching Strategy

**Do NOT cache project data between sessions** (per spec constraint). Always fetch fresh data on each command invocation to ensure accuracy.

### Performance Targets

- Config load: <100ms (local file read)
- Field discovery: <1s (single API call)
- Item listing: <2s (typical backlog of <100 items)
- Item creation: <3s (issue create + project add + field updates)

## Common Patterns

### Pattern: Safe Config Load

```bash
load_config() {
  local config_file=".compass-rose/config.json"

  if [ ! -f "$config_file" ]; then
    echo "Error: Configuration file not found."
    echo ""
    echo "Create $config_file with:"
    echo '{"project": {"owner": "<org>", "number": <num>}}'
    return 1
  fi

  OWNER=$(jq -r '.project.owner' "$config_file")
  NUMBER=$(jq -r '.project.number' "$config_file")

  if [ "$OWNER" = "null" ] || [ "$NUMBER" = "null" ]; then
    echo "Error: Invalid configuration. Both owner and number required."
    return 1
  fi

  return 0
}
```

### Pattern: Field Discovery with Fallback

```bash
discover_priority_field() {
  local fields=$(gh project field-list $NUMBER --owner $OWNER --format json)

  # Try to find priority-like field (case insensitive)
  local priority_field=$(echo "$fields" | jq -r '
    .fields[] |
    select(.name | test("priority|severity|importance"; "i")) |
    .id
  ' | head -1)

  if [ -z "$priority_field" ]; then
    echo "Warning: No priority field found. Using creation date for sorting."
    return 1
  fi

  echo "$priority_field"
  return 0
}
```

### Pattern: Item Filtering and Sorting

```bash
get_ready_items() {
  local items=$(gh project item-list $NUMBER --owner $OWNER --format json)

  # Filter by status and sort by priority
  echo "$items" | jq -r '
    [.items[] | select(.status == "Ready")] |
    sort_by(.priority) |
    .[]
  '
}
```

## References

- [gh project documentation](https://cli.github.com/manual/gh_project)
- GitHub Projects (new) API via `gh` CLI
- Spec: `compass-rose/.sdd/specs/compass-rose-core.md` (REQ-F-1 through REQ-F-3, REQ-NF-5)
- Plan: `compass-rose/.sdd/plans/compass-rose-core-plan.md` (TD-4: Configuration Schema)
