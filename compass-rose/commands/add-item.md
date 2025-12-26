---
argument-hint: []
description: Create a new repository issue and add it to the project with custom fields
allowed-tools: Bash, Read, Grep, Glob
---

# Add Item Mode

You are now in **Add Item Mode**. Your role is to interactively gather details about a new work item, create a repository issue, link it to the configured GitHub Project, and set appropriate custom fields.

## Your Focus

- **Field discovery**: Detect available custom fields (Priority, Size, Status, etc.)
- **Interactive gathering**: Ask user for title, description, priority, size, and status
- **Issue creation**: Create repository issue via `gh issue create`
- **Project linking**: Add issue to project via `gh-api-scripts add-to-project`
- **Field updates**: Set custom fields via multiple `gh project item-edit` calls

## Workflow

### 1. Load Configuration

The `gh-api-scripts` skill handles configuration loading and validation. Parse owner/number for field discovery:

```bash
# Parse config for field discovery (script handles validation)
if [ -f .compass-rose/config.json ]; then
  OWNER=$(jq -r '.project.owner' .compass-rose/config.json)
  NUMBER=$(jq -r '.project.number' .compass-rose/config.json)
else
  echo "Error: Configuration file not found."
  echo ""
  echo "Please create .compass-rose/config.json with your project details."
  exit 1
fi
```

Configuration validation is performed by the `add-to-project` operation - if config is missing or invalid, it returns structured error responses.

### 2. Discover Custom Fields

Use `gh project field-list` to detect available fields:

```bash
# Get project ID first (needed for item-edit later)
PROJECT_ID=$(gh project view $NUMBER --owner $OWNER --format json --jq .id)

# Discover fields
gh project field-list $NUMBER --owner $OWNER --format json
```

**Field Matching Patterns** (case-insensitive):
- **Priority**: Fields containing "priority", "p0-p3", "severity", "importance"
- **Size**: Fields containing "size", "estimate", "points", "effort"
- **Status**: Fields containing "status", "state", "column"
- **Iteration**: Fields containing "iteration", "sprint", "cycle", "milestone"

**Store Field Metadata**:
For each discovered field, extract:
- Field ID (required for `gh project item-edit`)
- Field name (for user-friendly prompts)
- Field options (for single-select fields like Priority, Size, Status)
- Option IDs (required for setting field values)

Example parsing:
```bash
# Extract Priority field and options
PRIORITY_FIELD_ID=$(echo "$fields" | jq -r '
  .fields[] |
  select(.name | test("priority"; "i")) |
  .id
')

PRIORITY_OPTIONS=$(echo "$fields" | jq -r '
  .fields[] |
  select(.name | test("priority"; "i")) |
  .options[] |
  "\(.name):\(.id)"
')
```

**Graceful Degradation**: If any field is missing:
```
Note: <Field> field not found in project. Skipping <field> selection.
```

Continue with available fields even if some are missing.

### 3. Gather Item Details

**Interactively prompt the user** for the following details. Present discovered field options to guide input:

#### 3.1. Title (Required)

```
What is the title of the new item?

Example: "Fix login timeout bug" or "Add dark mode support"
```

**Validation**:
- Must not be empty
- Keep concise (ideally <80 characters)

#### 3.2. Description (Optional)

```
Provide a description for this item (optional, press Enter to skip):

Include:
- What needs to be done
- Why it's important
- Any relevant context or links
- Acceptance criteria (for larger items)
```

**Default**: Empty string if user skips

#### 3.3. Priority (If available)

```
Select priority for this item:

Available options:
1. P0 - Critical
2. P1 - High
3. P2 - Medium
4. P3 - Low

Enter number (1-4) or press Enter for P2 (default):
```

**Default**: P2 (medium priority) if user skips
**Validation**: Must be one of the available options from field discovery

#### 3.4. Size (If available)

```
Select size estimate for this item:

Available options:
1. S - Small (< 4 hours)
2. M - Medium (1-2 days)
3. L - Large (3-5 days)
4. XL - Extra Large (> 1 week, consider spec)

Enter number (1-4) or press Enter for M (default):
```

**Default**: M (medium) if user skips
**Validation**: Must be one of the available options from field discovery

**XL Warning**: If user selects XL:
```
⚠️  XL items typically benefit from formal specification.

Consider using /spec-writing to create a detailed spec before implementation.
This ensures clear success criteria and reduces scope creep.

Continue with XL size? (y/n):
```

#### 3.5. Status (If available)

```
Select initial status for this item:

Available options:
1. Ready - Ready for implementation
2. To Do - Backlog (needs refinement)
3. Blocked - Cannot proceed yet

Enter number (1-3) or press Enter for "Ready" (default):
```

**Default**: "Ready" if user skips
**Validation**: Must be one of the available options from field discovery

### 4. Create Repository Issue

Use `gh issue create` to create the issue first:

```bash
# Get repository name from git remote
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)

# Create issue and capture URL
ISSUE_URL=$(gh issue create \
  --title "$TITLE" \
  --body "$DESCRIPTION" \
  --repo "$REPO" \
  --json url \
  --jq .url)

# Extract issue number from URL (for confirmation message)
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oP '\d+$')
```

**Error Handling**:
```
Error: Failed to create repository issue.

Verify that:
1. You have write access to the repository
2. You are authenticated: gh auth status
3. The repository exists: gh repo view
```

### 5. Add Issue to Project

Use the `gh-api-scripts` skill to link the issue to the project:

```bash
# Add issue to project using gh-api-scripts
RESPONSE=$(python3 compass-rose/skills/gh-api-scripts/scripts/gh_project.py add-to-project $ISSUE_NUMBER)

# Check result
if echo "$RESPONSE" | jq -e '.success == true' > /dev/null; then
  ITEM_ID=$(echo "$RESPONSE" | jq -r '.data.item_id')
  echo "✓ Added to project"
else
  ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message')
  ERROR_DETAILS=$(echo "$RESPONSE" | jq -r '.error.details')
  echo "Error: $ERROR_MSG"
  echo ""
  echo "$ERROR_DETAILS"
  exit 1
fi
```

**Note**: The config must include a `repository` field for add-to-project to work. The script returns structured errors for missing config or authentication issues.

### 6. Set Custom Fields

**IMPORTANT**: `gh project item-edit` can only update one field per invocation. Multiple fields require sequential calls.

```bash
# Set Priority (if available and user provided)
if [ -n "$PRIORITY_OPTION_ID" ]; then
  gh project item-edit \
    --id $ITEM_ID \
    --project-id $PROJECT_ID \
    --field-id $PRIORITY_FIELD_ID \
    --single-select-option-id $PRIORITY_OPTION_ID
fi

# Set Size (if available and user provided)
if [ -n "$SIZE_OPTION_ID" ]; then
  gh project item-edit \
    --id $ITEM_ID \
    --project-id $PROJECT_ID \
    --field-id $SIZE_FIELD_ID \
    --single-select-option-id $SIZE_OPTION_ID
fi

# Set Status (if available and user provided)
if [ -n "$STATUS_OPTION_ID" ]; then
  gh project item-edit \
    --id $ITEM_ID \
    --project-id $PROJECT_ID \
    --field-id $STATUS_FIELD_ID \
    --single-select-option-id $STATUS_OPTION_ID
fi
```

**Note**: Each `gh project item-edit` call is independent. If one fails, continue with the remaining fields and report which fields were successfully set.

**Error Handling**:
```
Warning: Failed to set <field> field.

The item was created successfully but some fields could not be set.
You can manually update these fields in the GitHub Projects web UI.
```

### 7. Confirm Creation

Display summary of created item:

```
✓ Item created successfully!

Issue: #<issue-number> - <title>
Link: <issue-url>

Fields set:
- Priority: <priority-value>
- Size: <size-value>
- Status: <status-value>

View in project: https://github.com/orgs/<owner>/projects/<number>
```

**If any fields failed to set**:
```
✓ Item created successfully!

Issue: #<issue-number> - <title>
Link: <issue-url>

Fields set:
- Priority: <priority-value>
- Size: <size-value>

⚠️  Could not set: Status (manual update required)

View in project: https://github.com/orgs/<owner>/projects/<number>
```

### 8. Handle Edge Cases

**No Custom Fields Available**:
```
Note: This project has no custom fields configured. Only title and description
will be set.

The item will be created as a basic repository issue linked to the project.
```

**Authentication Issues**:
```
Error: GitHub CLI is not authenticated.

Run the following command to authenticate:
  gh auth login

After authentication, you may need to add the 'project' scope:
  gh auth refresh -s project
```

**Repository Not Found**:
```
Error: Could not determine repository.

Verify that:
1. You are in a git repository: git status
2. Repository has a GitHub remote: git remote -v
3. You have access to the repository: gh repo view
```

**User Cancellation**:
If user enters "cancel" or "exit" at any prompt:
```
Item creation cancelled. No changes made.
```

## Requirements Mapping

This command implements the following specification requirements:

- **REQ-F-8**: Create new repository issues (not draft items)
- **REQ-F-9**: Update issue custom fields (Priority, Size, Iteration, Status)
- **REQ-F-10**: Link newly created issues to the configured project
- **REQ-F-7**: Handle projects with custom field configurations gracefully
- **REQ-NF-3**: Handle missing custom fields gracefully (warn, don't fail)
- **Explicit Constraint #1**: Do NOT create draft items (always create proper repository issues)

## Implementation Notes

**Performance Targets**:
- Config load: <100ms (local file read)
- Field discovery: <1s (single API call)
- Issue creation: <2s (gh issue create)
- Project linking: <1s (gh project item-add)
- Field updates: <1s per field (sequential gh project item-edit calls)
- Total operation: <5s end-to-end (for 3 fields)

**Data Flow**:
1. Load config → 2. Discover fields → 3. Gather input → 4. Create issue →
5. Link to project → 6. Set fields → 7. Confirm

**CLI Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)
- `jq` for JSON parsing
- `git` for repository context
- Python 3.12+ for `gh-api-scripts` skill

**Two-Step Creation Process**:
Following TD-5 from the plan, we ALWAYS create repository issues first, then link to project. This ensures:
- Issues have proper issue numbers for reference
- Issues appear in repository Issues tab
- Issues can be linked across multiple projects if needed
- Better visibility and integration with GitHub ecosystem

## Example Session

```
Loading project configuration...
✓ Config loaded: my-org/project-123

Discovering custom fields...
✓ Found fields: Status, Priority, Size

--- Create New Item ---

What is the title of the new item?
> Fix authentication timeout on mobile

Provide a description for this item (optional, press Enter to skip):
> Users on mobile devices are experiencing session timeouts after 30 seconds
> of inactivity. The web app timeout is configured for 30 minutes.
>
> Acceptance criteria:
> - Mobile timeout matches web (30 minutes)
> - Existing sessions are not affected
> - Timeout is configurable via environment variable

Select priority for this item:

Available options:
1. P0 - Critical
2. P1 - High
3. P2 - Medium
4. P3 - Low

Enter number (1-4) or press Enter for P2 (default):
> 1

Select size estimate for this item:

Available options:
1. S - Small (< 4 hours)
2. M - Medium (1-2 days)
3. L - Large (3-5 days)
4. XL - Extra Large (> 1 week, consider spec)

Enter number (1-4) or press Enter for M (default):
> 1

Select initial status for this item:

Available options:
1. Ready - Ready for implementation
2. To Do - Backlog (needs refinement)
3. Blocked - Cannot proceed yet

Enter number (1-3) or press Enter for "Ready" (default):
> 1

Creating repository issue...
✓ Issue created: #156

Linking to project...
✓ Added to project

Setting custom fields...
✓ Priority set to P0
✓ Size set to S
✓ Status set to Ready

✓ Item created successfully!

Issue: #156 - Fix authentication timeout on mobile
Link: https://github.com/my-org/my-repo/issues/156

Fields set:
- Priority: P0
- Size: S
- Status: Ready

View in project: https://github.com/orgs/my-org/projects/123
```

## Anti-Patterns to Avoid

- **Don't skip config validation**: Always verify config exists and is valid before proceeding
- **Don't assume field names**: Use discovery pattern, don't hardcode "Priority" or "Status"
- **Don't fail on missing fields**: Warn user and continue with available fields
- **Don't create draft items**: ALWAYS create repository issues (per spec constraint)
- **Don't batch field updates**: Use sequential `gh project item-edit` calls (gh CLI limitation)
- **Don't skip confirmation**: Always show summary of created item with link
- **Don't store credentials**: Rely on `gh` CLI authentication
- **Don't skip XL warning**: Always prompt user when they select XL size

## Related Commands

- `/next-item` - Find next work item to tackle
- `/backlog` - Review entire backlog
- `/start-work` - Begin implementation of item
- `/spec-writing` - Create formal spec for large items (Spiral Grove integration)

## References

- **Spec**: REQ-F-8, REQ-F-9, REQ-F-10, REQ-F-7, REQ-NF-3, Explicit Constraint #1
- **Plan**: TD-5 (Item Type Strategy - Repository Issues Only)
- **Skill**: `compass-rose/skills/gh-api-scripts/SKILL.md` (GitHub Project API operations)
