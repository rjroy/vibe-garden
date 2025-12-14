---
argument-hint: []
description: Recommend the highest-priority ready item with rationale
allowed-tools: Bash, Read, Grep, Glob
---

# Next Item Recommendation Mode

You are now in **Next Item Recommendation Mode**. Your role is to analyze the project backlog and recommend the highest-priority work item that is ready to be implemented.

## Your Focus

- **Configuration loading**: Read `.compass-rose/config.json` and validate project settings
- **Field discovery**: Detect available custom fields (Priority, Size, Status, etc.)
- **Item filtering**: Query items with Ready status (or equivalent)
- **Priority sorting**: Sort by Priority field (P0 > P1 > P2 > P3), then creation date
- **Presentation**: Display top 2-3 options in tabular format with rationale

## Workflow

### 1. Load Configuration

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

# Validate required fields
if [ "$OWNER" = "null" ] || [ "$NUMBER" = "null" ]; then
  echo "Error: Invalid configuration."
  echo ""
  echo "Both 'project.owner' and 'project.number' are required."
  exit 1
fi
```

**If configuration is missing or invalid**, show clear error message with setup instructions and stop.

### 2. Discover Custom Fields

Use `gh project field-list` to detect available fields:

```bash
gh project field-list $NUMBER --owner $OWNER --format json
```

**Field Matching Patterns** (case-insensitive):
- **Priority**: Fields containing "priority", "p0-p3", "severity", "importance"
- **Size**: Fields containing "size", "estimate", "points", "effort"
- **Status**: Fields containing "status", "state", "column"
- **Iteration**: Fields containing "iteration", "sprint", "cycle", "milestone"

**Graceful Degradation**: If Priority field is missing:
```
Warning: Priority field not found in project. All items will be treated as equal priority.

Available fields: Status, Size, Iteration

To enable priority-based sorting, add a "Priority" field to your project with values like P0, P1, P2, P3.
```

Continue with available data even if some fields are missing.

### 3. Query Ready Items

Fetch project items and filter by status:

```bash
gh project item-list $NUMBER --owner $OWNER --format json --limit 100
```

**Status Filtering**:
- Look for items with Status field value matching "Ready" (case-insensitive)
- If no exact match, look for similar values: "Ready for Dev", "To Do", "Backlog"
- Parse JSON output using `jq` to filter items

Example filter:
```bash
# Filter items with "Ready" status
echo "$items" | jq -r '[.items[] | select(.status | test("ready"; "i"))]'
```

**If no ready items found**:
```
No items found with "Ready" status.

Available statuses in project: To Do, In Progress, Done

Would you like me to show items from a different status instead?
```

### 4. Sort by Priority

**Priority Ordering**:
- P0 (critical) > P1 (high) > P2 (medium) > P3 (low)
- Extract numeric suffix from priority values (P0 → 0, P1 → 1, etc.)
- Sort ascending by priority number (lower number = higher priority)

**Secondary Sort**:
- When priority is equal (or missing), sort by creation date (oldest first)
- Older items have been waiting longer and should be prioritized

**Implementation Pattern**:
```bash
# Sort by priority (P0 first), then by creation date
echo "$ready_items" | jq -r '
  sort_by(
    .priority | sub("P"; "") | tonumber? // 999,  # Priority (missing = 999)
    .createdAt                                     # Creation date
  )
'
```

### 5. Present Recommendations

Display top 2-3 options in tabular format following TD-8 specification:

```
| # | Title                      | Priority | Size | Status |
|---|----------------------------|----------|------|--------|
| 1 | Fix login timeout bug      | P0       | S    | Ready  |
| 2 | Add user preferences page  | P1       | M    | Ready  |
| 3 | Improve error messages     | P1       | S    | Ready  |

**Recommendation**: Item #1 (P0 priority, small scope, ready for work)

**Rationale**: This is the highest priority item in the backlog. The P0 designation
indicates critical urgency, and the small size (S) makes it achievable in a single
focused session. The issue has clear acceptance criteria and is ready for immediate
implementation.

**Alternative Options**:
- Item #2: Larger scope (M) but high priority (P1). Consider if you have more time.
- Item #3: Also P1 priority but smaller scope. Good backup if item #1 is blocked.
```

**Rationale Elements to Include**:
- **Priority justification**: Why this item ranks highest (P0 designation, urgency)
- **Size assessment**: Small items are more achievable in single session
- **Definition quality**: Mention if acceptance criteria are clear
- **Context**: Any relevant technical considerations or dependencies

**If all items have equal priority** (missing Priority field):
```
**Recommendation**: Item #1 (oldest item, small scope, ready for work)

**Rationale**: No priority field found in project, so recommending based on age
(oldest first) and size. This item has been waiting longest and is small enough
to complete in one session.
```

### 6. Handle Edge Cases

**No Ready Items**:
```
No items found with "Ready" status.

Available statuses: To Do (15 items), In Progress (3 items), Done (42 items)

Would you like me to analyze the "To Do" backlog instead?
```

**Missing Priority Field**:
```
Warning: Priority field not found. Sorting by creation date instead.

All items shown below are treated as equal priority.
```

**Authentication Issues**:
```
Error: GitHub CLI is not authenticated.

Run the following command to authenticate:
  gh auth login

After authentication, you may need to add the 'project' scope:
  gh auth refresh -s project
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

## Requirements Mapping

This command implements the following specification requirements:

- **REQ-F-4**: Retrieve project items filtered by status
- **REQ-F-5**: Sort items by priority field (P0 > P1 > P2 > P3)
- **REQ-F-6**: Display item summary, priority, size, and iteration
- **REQ-F-11**: Recommend based on priority, size, and definition quality
- **REQ-NF-3**: Handle missing custom fields gracefully (warn, don't fail)
- **REQ-NF-4**: Explain reasoning when making recommendations

## Implementation Notes

**Performance Targets**:
- Config load: <100ms (local file read)
- Field discovery: <1s (single API call)
- Item listing: <2s (typical backlog of <100 items)
- Total operation: <3s end-to-end

**Data Freshness**:
- Always fetch fresh data (no caching between sessions per spec constraint)
- Ensures recommendations reflect current project state

**CLI Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)
- `jq` for JSON parsing (check availability, provide clear error if missing)

## Example Output

```
Loading project configuration...
✓ Config loaded: my-org/project-123

Discovering custom fields...
✓ Found fields: Status, Priority, Size, Iteration

Querying ready items...
✓ Found 8 items with "Ready" status

Analyzing and sorting by priority...

| # | Title                           | Priority | Size | Status |
|---|---------------------------------|----------|------|--------|
| 1 | Fix authentication timeout      | P0       | S    | Ready  |
| 2 | Implement user preferences API  | P1       | M    | Ready  |
| 3 | Add error logging to webhook    | P1       | S    | Ready  |

**Recommendation**: Item #1 - "Fix authentication timeout"

**Rationale**: This is the highest priority item (P0 = critical) and has the
smallest scope (S). The issue describes a production bug affecting user login
sessions, with clear reproduction steps and acceptance criteria. This can be
completed in a single focused session.

**Alternative Options**:
- Item #2 (P1/M): Higher effort but important feature. Good choice if you have
  a longer work session planned.
- Item #3 (P1/S): Also small scope and high priority. Consider as backup if
  authentication issue proves more complex than estimated.

Would you like to start work on item #1? (/start-work command)
```

## Anti-Patterns to Avoid

- **Don't skip config validation**: Always verify config exists and is valid before querying
- **Don't assume field names**: Use discovery pattern, don't hardcode "Priority" or "Status"
- **Don't fail silently**: If fields are missing, warn the user and explain impact
- **Don't show too many options**: Limit to top 2-3 items to avoid decision paralysis
- **Don't forget rationale**: Always explain WHY you're recommending an item
- **Don't ignore creation date**: Use as secondary sort when priorities are equal

## Related Commands

- `/backlog` - Review entire backlog with quality analysis
- `/start-work` - Begin implementation of selected item
- `/add-item` - Create new issue and add to project
- `/reprioritize` - Codebase-aware priority updates

## References

- **Spec**: REQ-F-4, REQ-F-5, REQ-F-6, REQ-F-11, REQ-NF-3, REQ-NF-4
- **Plan**: TD-6 (Priority Sorting), TD-8 (Item Presentation Format)
- **Skill**: `compass-rose/skills/gh-project-reference/SKILL.md` (config patterns, field discovery)
