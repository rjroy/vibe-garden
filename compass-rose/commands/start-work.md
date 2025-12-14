---
argument-hint: [issue-number-or-url-or-"next"]
description: Begin work on an item with XL/L escalation prompts and status tracking
allowed-tools: Bash, Read, Grep, Glob
---

# Start Work Mode

You are now in **Start Work Mode**. Your role is to help the user begin work on a selected GitHub Project item, checking for size-based escalation to Spiral Grove spec-writing, updating the item status, and reading the full issue context.

## Your Focus

- **Item selection**: Accept issue number, URL, or "next" for recommendation
- **Configuration loading**: Read `.compass-rose/config.json` and validate project settings
- **Field discovery**: Detect available custom fields (Size, Status, etc.)
- **Size-based escalation**: Check for XL/L items and prompt about spec-writing
- **Status update**: Update item Status to "In Progress"
- **Context loading**: Read full issue description and linked context
- **Implementation guidance**: Help user start working on the item

## Workflow

### 1. Item Selection

Accept one of three input formats:

**Option A: Issue Number**
```
User: /start-work 156
```

**Option B: Issue URL**
```
User: /start-work https://github.com/my-org/my-repo/issues/156
```

**Option C: Next Item (Recommendation)**
```
User: /start-work next
```

If "next" is specified, internally invoke the `/next-item` workflow to get the highest-priority ready item recommendation.

**Validation**:
- Issue number must be a positive integer
- URL must be a valid GitHub issue URL
- If "next", defer to `/next-item` recommendation logic

**Error Handling**:
```
Error: Invalid issue reference.

Valid formats:
- Issue number: /start-work 156
- Issue URL: /start-work https://github.com/my-org/my-repo/issues/156
- Next ready item: /start-work next
```

### 2. Load Configuration

Read `.compass-rose/config.json` from the repository root:

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
  echo ""
  echo "Find your project number in the project URL:"
  echo "https://github.com/orgs/<owner>/projects/<number>"
  exit 1
fi

# Parse config (using jq)
OWNER=$(jq -r '.project.owner' .compass-rose/config.json)
NUMBER=$(jq -r '.project.number' .compass-rose/config.json)

# Load preferences (with defaults)
PROMPT_FOR_LARGE=$(jq -r '.preferences.promptForLargeItems // true' .compass-rose/config.json)
LARGE_THRESHOLD=$(jq -r '.preferences.largeSizeThreshold // ["L", "XL"] | @json' .compass-rose/config.json)

# Validate required fields
if [ "$OWNER" = "null" ] || [ "$NUMBER" = "null" ]; then
  echo "Error: Invalid configuration."
  echo ""
  echo "Both 'project.owner' and 'project.number' are required."
  exit 1
fi
```

**If configuration is missing or invalid**, show clear error message with setup instructions and stop.

### 3. Get Item Details

Retrieve the full issue details and project item metadata:

```bash
# Get repository name from git remote
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)

# Read full issue details
ISSUE_DATA=$(gh issue view $ISSUE_NUMBER --repo $REPO --json title,body,url,number)

TITLE=$(echo "$ISSUE_DATA" | jq -r .title)
BODY=$(echo "$ISSUE_DATA" | jq -r .body)
ISSUE_URL=$(echo "$ISSUE_DATA" | jq -r .url)
ISSUE_NUMBER=$(echo "$ISSUE_DATA" | jq -r .number)

# Get project item data (for custom fields)
PROJECT_ITEMS=$(gh project item-list $NUMBER --owner $OWNER --format json --limit 100)

# Find this issue in project items
ITEM_DATA=$(echo "$PROJECT_ITEMS" | jq --arg url "$ISSUE_URL" '
  .items[] | select(.content.url == $url)
')

ITEM_ID=$(echo "$ITEM_DATA" | jq -r .id)
```

**Error Handling**:
```
Error: Issue #<number> not found in project.

Verify that:
1. Issue exists: gh issue view <number>
2. Issue is linked to project: <project-url>
3. Issue URL matches project item
```

### 4. Discover Custom Fields

Use `gh project field-list` to detect available fields:

```bash
# Get project ID (needed for item-edit later)
PROJECT_ID=$(gh project view $NUMBER --owner $OWNER --format json --jq .id)

# Discover fields
FIELDS=$(gh project field-list $NUMBER --owner $OWNER --format json)
```

**Field Matching Patterns** (case-insensitive):
- **Size**: Fields containing "size", "estimate", "points", "effort"
- **Status**: Fields containing "status", "state", "column"

**Extract Field and Option IDs**:
```bash
# Get Size field metadata
SIZE_FIELD_ID=$(echo "$FIELDS" | jq -r '
  .fields[] |
  select(.name | test("size|estimate|points|effort"; "i")) |
  .id
' | head -1)

SIZE_OPTIONS=$(echo "$FIELDS" | jq -r --arg fid "$SIZE_FIELD_ID" '
  .fields[] |
  select(.id == $fid) |
  .options[] |
  "\(.name):\(.id)"
')

# Get current size value from item
SIZE_VALUE=$(echo "$ITEM_DATA" | jq -r --arg fid "$SIZE_FIELD_ID" '
  .fieldValues[] |
  select(.field.id == $fid) |
  .name
')

# Get Status field metadata
STATUS_FIELD_ID=$(echo "$FIELDS" | jq -r '
  .fields[] |
  select(.name | test("status|state|column"; "i")) |
  .id
' | head -1)

# Find "In Progress" status option ID
IN_PROGRESS_OPTION_ID=$(echo "$FIELDS" | jq -r --arg fid "$STATUS_FIELD_ID" '
  .fields[] |
  select(.id == $fid) |
  .options[] |
  select(.name | test("in.?progress"; "i")) |
  .id
' | head -1)
```

**Graceful Degradation**: If Size or Status fields are missing:
```
Note: <Field> field not found in project. Skipping <field>-based features.
```

Continue with available fields even if some are missing.

### 5. XL/L Escalation Check

**Requirements**: REQ-F-18, REQ-F-19, REQ-F-20

Check the Size field value and prompt user based on configuration:

**XL Items (Always Prompt)**:
```
═══════════════════════════════════════════════════════════════
📏 Large Item Detected: XL
═══════════════════════════════════════════════════════════════

This item is sized XL, which typically requires detailed planning and
specification before implementation.

XL items often benefit from Spiral Grove's Spec-Driven Development workflow:
1. /spec-writing - Define clear success criteria and constraints
2. /plan-generation - Create technical architecture and decisions
3. /task-breakdown - Decompose into manageable tasks
4. /implementation - Execute with progress tracking

Options:
  1. Write spec first (/spec-writing) - ⭐ RECOMMENDED for XL items
  2. Start implementation directly

Which approach would you prefer? (Enter 1 or 2):
```

**L Items (Prompt if Enabled)**:

Check `preferences.promptForLargeItems` (default: `true`):

```bash
if [ "$SIZE_VALUE" = "L" ] && [ "$PROMPT_FOR_LARGE" = "true" ]; then
  # Show prompt
fi
```

Prompt text for L items:
```
═══════════════════════════════════════════════════════════════
📏 Large Item Detected: L
═══════════════════════════════════════════════════════════════

This item is sized L (3-5 days). Consider whether formal specification
would help clarify requirements and reduce rework.

Options:
  1. Write spec first (/spec-writing) - Good practice for larger items
  2. Start implementation directly

Which approach would you prefer? (Enter 1 or 2):
```

**S/M Items (No Prompt)**:
Skip escalation check and proceed directly to status update.

**User Choice Handling**:

If user selects **Option 1 (Write spec first)**:
```
Great! Let's create a specification for this item.

I'll invoke /spec-writing with this issue as context.

Would you like me to proceed with /spec-writing now? (y/n):
```

If user confirms:
- Invoke `/spec-writing` command with issue context
- Stop current workflow (spec-writing takes over)

If user selects **Option 2 (Start directly)** or declines spec-writing:
```
Understood. Proceeding with direct implementation.

Note: You can create a spec later if you find the scope expanding.
```

Continue to status update.

**Override Configuration**:

To disable L-item prompts, user can edit `.compass-rose/config.json`:
```json
{
  "project": {
    "owner": "my-org",
    "number": 123
  },
  "preferences": {
    "promptForLargeItems": false
  }
}
```

### 6. Update Status to "In Progress"

**Requirement**: REQ-F-22

Update the item's Status field to "In Progress":

```bash
if [ -n "$STATUS_FIELD_ID" ] && [ -n "$IN_PROGRESS_OPTION_ID" ]; then
  gh project item-edit \
    --id $ITEM_ID \
    --project-id $PROJECT_ID \
    --field-id $STATUS_FIELD_ID \
    --single-select-option-id $IN_PROGRESS_OPTION_ID

  echo "✓ Status updated to 'In Progress'"
else
  echo "Note: Status field not available. Manual status update required."
fi
```

**Error Handling**:
```
Warning: Could not update status to "In Progress".

The item is still ready to work on, but you'll need to manually update the
status in the GitHub Projects web UI.
```

### 7. Read and Display Full Issue Context

**Requirement**: REQ-F-23

Display the full issue details to provide context for implementation:

```
═══════════════════════════════════════════════════════════════
📋 Issue #<number>: <title>
═══════════════════════════════════════════════════════════════

Priority: <priority>
Size: <size>
Status: In Progress

URL: <issue-url>

Description:
───────────────────────────────────────────────────────────────
<full-issue-body>
───────────────────────────────────────────────────────────────

Ready to begin implementation!
```

**If issue has acceptance criteria** (detected via "Acceptance criteria:", "AC:", or similar):
```
Acceptance Criteria:
───────────────────────────────────────────────────────────────
<extracted-acceptance-criteria>
───────────────────────────────────────────────────────────────
```

### 8. Provide Implementation Guidance

Offer guidance based on item size and type:

**For Small Items (S)**:
```
Implementation Guidance:
───────────────────────────────────────────────────────────────
This is a small item (estimated < 4 hours). Recommended approach:

1. Read the issue carefully and identify affected code
2. Make focused changes with minimal scope
3. Test locally to verify acceptance criteria
4. Create a PR when complete

This item should be achievable in a single focused session.
```

**For Medium Items (M)**:
```
Implementation Guidance:
───────────────────────────────────────────────────────────────
This is a medium item (estimated 1-2 days). Recommended approach:

1. Break down into 2-3 sub-tasks if needed
2. Implement incrementally with frequent testing
3. Consider creating a feature branch for this work
4. Document any technical decisions or trade-offs

Check in with progress after first sub-task to validate direction.
```

**For Large Items (L) - If proceeding without spec**:
```
Implementation Guidance:
───────────────────────────────────────────────────────────────
This is a large item (estimated 3-5 days). Recommended approach:

⚠️  Without a formal spec, pay extra attention to:
1. Clarifying requirements upfront (ask questions if unclear)
2. Breaking into smaller milestones (aim for daily progress checkpoints)
3. Documenting decisions as you go (consider a design doc)
4. Frequent validation with stakeholders

If scope starts expanding, STOP and consider writing a spec.
```

**For XL Items - If proceeding without spec**:
```
Implementation Guidance:
───────────────────────────────────────────────────────────────
⚠️  WARNING: XL items without specs have high risk of:
- Scope creep and extended timelines
- Misalignment with expectations
- Rework due to unclear requirements

STRONGLY RECOMMEND: Stop now and create a spec (/spec-writing).

If proceeding anyway:
1. Document ALL assumptions clearly upfront
2. Break into week-long milestones with explicit deliverables
3. Create design documents for architecture decisions
4. Get stakeholder review at each milestone
5. Be prepared to backtrack if requirements are unclear

Consider this a risk you're consciously accepting.
```

### 9. Handle Edge Cases

**Issue Not in Project**:
```
Error: Issue #<number> is not linked to the configured project.

To add this issue to the project, use:
  /add-item

Or manually add it via the GitHub Projects web UI:
  <project-url>
```

**Status Already "In Progress"**:
```
Note: This item is already marked "In Progress".

If you're resuming work, great! If not, verify no one else is working on it.

Current Status: In Progress (no change needed)
```

**Authentication Issues**:
```
Error: GitHub CLI is not authenticated.

Run the following command to authenticate:
  gh auth login

After authentication, you may need to add the 'project' scope:
  gh auth refresh -s project
```

**Issue Closed**:
```
Warning: Issue #<number> is closed.

This issue may have already been resolved. Verify that you want to reopen
and work on it before proceeding.

Current state: Closed
```

## Requirements Mapping

This command implements the following specification requirements:

- **REQ-F-18**: Detect when an issue is sized XL and prompt user about spec-writing
- **REQ-F-19**: Optionally prompt for L-sized items (user preference)
- **REQ-F-20**: Prompt must offer choice: "Write spec first" or "Start implementation directly"
- **REQ-F-21**: Allow user to request starting work on next ready item
- **REQ-F-22**: Update issue status to "In Progress" when work begins
- **REQ-F-23**: Read full issue description and any linked context before starting

## Implementation Notes

**Performance Targets**:
- Config load: <100ms (local file read)
- Field discovery: <1s (single API call)
- Item lookup: <2s (project item-list query)
- Status update: <1s (gh project item-edit)
- Total operation: <5s end-to-end

**Data Flow**:
1. Select item → 2. Load config → 3. Get item details → 4. Discover fields →
5. Check size escalation → 6. Update status → 7. Display context → 8. Provide guidance

**CLI Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)
- `jq` for JSON parsing (check availability, provide clear error if missing)
- `git` for repository context

**Spiral Grove Integration**:
- Escalation prompts reference `/spec-writing` command
- Clear explanation of SDD workflow benefits
- User retains control (can always override and proceed)

## Example Sessions

### Session 1: XL Item with Spec Escalation

```
User: /start-work 156

Loading project configuration...
✓ Config loaded: my-org/project-123

Retrieving issue details...
✓ Found: #156 - "Implement multi-tenancy support"

Discovering custom fields...
✓ Found fields: Status, Priority, Size

═══════════════════════════════════════════════════════════════
📏 Large Item Detected: XL
═══════════════════════════════════════════════════════════════

This item is sized XL, which typically requires detailed planning and
specification before implementation.

XL items often benefit from Spiral Grove's Spec-Driven Development workflow:
1. /spec-writing - Define clear success criteria and constraints
2. /plan-generation - Create technical architecture and decisions
3. /task-breakdown - Decompose into manageable tasks
4. /implementation - Execute with progress tracking

Options:
  1. Write spec first (/spec-writing) - ⭐ RECOMMENDED for XL items
  2. Start implementation directly

Which approach would you prefer? (Enter 1 or 2):
> 1

Great! Let's create a specification for this item.

I'll invoke /spec-writing with this issue as context.

Would you like me to proceed with /spec-writing now? (y/n):
> y

[Transfers to /spec-writing command with issue #156 as context]
```

### Session 2: Small Item (Direct Implementation)

```
User: /start-work next

Loading project configuration...
✓ Config loaded: my-org/project-123

Finding highest-priority ready item...

| # | Title                      | Priority | Size | Status |
|---|----------------------------|----------|------|--------|
| 1 | Fix login timeout bug      | P0       | S    | Ready  |

Selected: #142 - "Fix login timeout bug"

Discovering custom fields...
✓ Found fields: Status, Priority, Size

Size: S (no escalation needed)

Updating status...
✓ Status updated to 'In Progress'

═══════════════════════════════════════════════════════════════
📋 Issue #142: Fix login timeout bug
═══════════════════════════════════════════════════════════════

Priority: P0
Size: S
Status: In Progress

URL: https://github.com/my-org/my-repo/issues/142

Description:
───────────────────────────────────────────────────────────────
Users on mobile devices are experiencing session timeouts after
30 seconds of inactivity. The web app timeout is configured for
30 minutes.

Acceptance Criteria:
- Mobile timeout matches web (30 minutes)
- Existing sessions are not affected
- Timeout is configurable via environment variable
───────────────────────────────────────────────────────────────

Implementation Guidance:
───────────────────────────────────────────────────────────────
This is a small item (estimated < 4 hours). Recommended approach:

1. Read the issue carefully and identify affected code
2. Make focused changes with minimal scope
3. Test locally to verify acceptance criteria
4. Create a PR when complete

This item should be achievable in a single focused session.

Ready to begin implementation!
```

### Session 3: L Item with Preference Override

```
User: /start-work 158

Loading project configuration...
✓ Config loaded: my-org/project-123

Retrieving issue details...
✓ Found: #158 - "Add export to CSV feature"

Discovering custom fields...
✓ Found fields: Status, Priority, Size

═══════════════════════════════════════════════════════════════
📏 Large Item Detected: L
═══════════════════════════════════════════════════════════════

This item is sized L (3-5 days). Consider whether formal specification
would help clarify requirements and reduce rework.

Options:
  1. Write spec first (/spec-writing) - Good practice for larger items
  2. Start implementation directly

Which approach would you prefer? (Enter 1 or 2):
> 2

Understood. Proceeding with direct implementation.

Note: You can create a spec later if you find the scope expanding.

Updating status...
✓ Status updated to 'In Progress'

═══════════════════════════════════════════════════════════════
📋 Issue #158: Add export to CSV feature
═══════════════════════════════════════════════════════════════

Priority: P1
Size: L
Status: In Progress

URL: https://github.com/my-org/my-repo/issues/158

Description:
───────────────────────────────────────────────────────────────
Allow users to export their data to CSV format from the dashboard.

Requirements:
- Export all visible columns
- Respect current filters
- Include headers
- Download as attachment (not inline)

Acceptance Criteria:
- Export button appears on dashboard
- CSV downloads with correct data
- Column order matches display
- Filters are applied to export
───────────────────────────────────────────────────────────────

Implementation Guidance:
───────────────────────────────────────────────────────────────
This is a large item (estimated 3-5 days). Recommended approach:

⚠️  Without a formal spec, pay extra attention to:
1. Clarifying requirements upfront (ask questions if unclear)
2. Breaking into smaller milestones (aim for daily progress checkpoints)
3. Documenting decisions as you go (consider a design doc)
4. Frequent validation with stakeholders

If scope starts expanding, STOP and consider writing a spec.

Ready to begin implementation!
```

## Anti-Patterns to Avoid

- **Don't skip config validation**: Always verify config exists and is valid before proceeding
- **Don't skip size check**: Always check Size field for XL/L items (critical for spec escalation)
- **Don't force spec-writing**: User must have choice to proceed directly
- **Don't skip status update**: Always attempt to update Status (or warn if not possible)
- **Don't truncate issue body**: Display full description for context
- **Don't ignore preferences**: Respect `promptForLargeItems` configuration
- **Don't proceed if user selects spec-writing**: Transfer to /spec-writing command
- **Don't skip guidance**: Provide size-appropriate implementation advice

## Related Commands

- `/next-item` - Find next work item to tackle (used internally for "next" selection)
- `/add-item` - Create new issue and add to project
- `/backlog` - Review entire backlog
- `/spec-writing` - Create formal spec (Spiral Grove integration point)

## References

- **Spec**: REQ-F-18, REQ-F-19, REQ-F-20, REQ-F-21, REQ-F-22, REQ-F-23
- **Plan**: TD-7 (Spiral Grove Integration Points)
- **Skill**: `compass-rose/skills/gh-project-reference/SKILL.md` (config patterns, field discovery)
