---
name: add-item
description: This skill should be used when the user asks to "create an issue", "add an item", "add a bug", "create a task", "add to backlog", or invokes /compass-rose:add-item. Creates a new repository issue and adds it to the project with custom fields.
allowed-tools: Skill(compass-rose:gh-api-scripts), Bash, Read, Grep, Glob
---

# Add Item Mode

You are now in **Add Item Mode**. Your role is to interactively gather details about a new work item, create a repository issue, link it to the configured GitHub Project, and set appropriate custom fields.

## Your Focus

- **Interactive gathering**: Ask user for title, description, priority, size, and status
- **Issue creation**: Create repository issue via `gh issue create`
- **Project linking**: Add issue to project via `gh-api-scripts add-to-project`
- **Field updates**: Set custom fields via `gh-api-scripts` operations (`set-status`, `set-priority`, `set-size`)

## Required Skills

**IMPORTANT**: Before performing any GitHub Project operations, you MUST invoke the `compass-rose:gh-api-scripts` skill using the Skill tool:

```
Skill(compass-rose:gh-api-scripts)
```

This skill provides:
- `add-to-project` - Link issue to project
- `set-status` - Set status field
- `set-priority` - Set priority field
- `set-size` - Set size field

**Do NOT use raw `gh project` commands.** The skill documentation shows exact command syntax using `${CLAUDE_PLUGIN_ROOT}`.

## Workflow

### 1. Verify Configuration

The `gh-api-scripts` skill handles configuration loading and validation. Verify config exists before gathering user input:

```bash
# Check config exists (detailed validation done by gh-api-scripts operations)
if [ ! -f .compass-rose/config.json ]; then
  echo "Error: Configuration file not found."
  echo ""
  echo "Please create .compass-rose/config.json with your project details."
  exit 1
fi
```

Configuration validation is performed by the `add-to-project` operation - if config is missing or invalid, it returns structured error responses.

### 2. Gather Item Details

**Interactively prompt the user** for the following details:

#### 2.1. Title (Required)

```
What is the title of the new item?

Example: "Fix login timeout bug" or "Add dark mode support"
```

**Validation**:
- Must not be empty
- Keep concise (ideally <80 characters)

#### 2.2. Description (Optional)

```
Provide a description for this item (optional, press Enter to skip):

Include:
- What needs to be done
- Why it's important
- Any relevant context or links
- Acceptance criteria (for larger items)
```

**Default**: Empty string if user skips

#### 2.3. Priority

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
**Validation**: Must be one of the project's configured priority options

#### 2.4. Size

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
**Validation**: Must be one of the project's configured size options

**XL Warning**: If user selects XL:
```
XL items typically benefit from formal specification.

Consider using /spiral-grove:spec-writing to create a detailed spec before implementation.
This ensures clear success criteria and reduces scope creep.

Continue with XL size? (y/n):
```

#### 2.5. Status

```
Select initial status for this item:

Available options:
1. Ready - Ready for implementation
2. To Do - Backlog (needs refinement)
3. Blocked - Cannot proceed yet

Enter number (1-3) or press Enter for "Ready" (default):
```

**Default**: "Ready" if user skips
**Validation**: Must be one of the project's configured status options

### 3. Create Repository Issue

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

### 4. Add Issue to Project

Use the `add-to-project` operation from the `gh-api-scripts` skill (which you invoked earlier). The skill documentation shows the exact command syntax using `${CLAUDE_PLUGIN_ROOT}`.

**Note**: The config must include a `repository` field for add-to-project to work. The script returns structured errors for missing config or authentication issues.

### 5. Set Custom Fields

Use the `set-status`, `set-priority`, and `set-size` operations from the `gh-api-scripts` skill. Each operation handles field discovery internally. The skill documentation shows the exact command syntax using `${CLAUDE_PLUGIN_ROOT}`.

**Notes**:
- Each operation is independent - if one fails, continue with the remaining fields
- Operations handle field discovery internally (no need to query field IDs)
- The `FIELD_NOT_FOUND` error indicates the project doesn't have that field configured

**Error Handling**:
```
Warning: Failed to set <field> field.

The item was created successfully but some fields could not be set.
You can manually update these fields in the GitHub Projects web UI.
```

### 6. Confirm Creation

Display summary of created item:

```
Item created successfully!

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
Item created successfully!

Issue: #<issue-number> - <title>
Link: <issue-url>

Fields set:
- Priority: <priority-value>
- Size: <size-value>

Could not set: Status (manual update required)

View in project: https://github.com/orgs/<owner>/projects/<number>
```

### 7. Handle Edge Cases

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

This skill implements the following specification requirements:

- **REQ-F-8**: Create new repository issues (not draft items)
- **REQ-F-9**: Update issue custom fields (Priority, Size, Iteration, Status)
- **REQ-F-10**: Link newly created issues to the configured project
- **REQ-F-7**: Handle projects with custom field configurations gracefully
- **REQ-NF-3**: Handle missing custom fields gracefully (warn, don't fail)
- **Explicit Constraint #1**: Do NOT create draft items (always create proper repository issues)

## Implementation Notes

**Performance Targets**:
- Config check: <100ms (local file read)
- Issue creation: <2s (gh issue create)
- Project linking: <1s (gh-api-scripts add-to-project)
- Field updates: <1s per field (gh-api-scripts set-status/set-priority/set-size)
- Total operation: <5s end-to-end (for 3 fields)

**Data Flow**:
1. Verify config -> 2. Gather input -> 3. Create issue ->
4. Link to project -> 5. Set fields -> 6. Confirm

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
Issue created: #156

Linking to project...
Added to project

Setting custom fields...
Priority set to P0
Size set to S
Status set to Ready

Item created successfully!

Issue: #156 - Fix authentication timeout on mobile
Link: https://github.com/my-org/my-repo/issues/156

Fields set:
- Priority: P0
- Size: S
- Status: Ready

View in project: https://github.com/orgs/my-org/projects/123
```

## Anti-Patterns to Avoid

- **Don't use raw gh commands**: Always use gh-api-scripts skill for GitHub Project operations
- **Don't skip config validation**: Always verify config exists before proceeding
- **Don't fail on missing fields**: Warn user and continue with available fields
- **Don't create draft items**: ALWAYS create repository issues (per spec constraint)
- **Don't skip confirmation**: Always show summary of created item with link
- **Don't store credentials**: Rely on `gh` CLI authentication
- **Don't skip XL warning**: Always prompt user when they select XL size

## Related Skills

- `/compass-rose:next-item` - Find next work item to tackle
- `/compass-rose:backlog` - Review entire backlog
- `/compass-rose:start-work` - Begin implementation of item
- `/spiral-grove:spec-writing` - Create formal spec for large items (Spiral Grove integration)

## References

- **Spec**: REQ-F-8, REQ-F-9, REQ-F-10, REQ-F-7, REQ-NF-3, Explicit Constraint #1
- **Plan**: TD-5 (Item Type Strategy - Repository Issues Only)
- **Skill**: `compass-rose/skills/gh-api-scripts/SKILL.md` (GitHub Project API operations)
