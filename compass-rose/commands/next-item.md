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
- **Priority sorting**: Sort by Priority field (P0 > P1 > P2 > P3)
- **Codebase signals**: Use lightweight git heuristics as secondary tiebreaker
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

Fetch project items using GraphQL (never use `gh project item-list` - it silently truncates results):

```bash
# Use GraphQL for reliable, complete item retrieval
# Note: Use "user" for personal accounts, "organization" for org-owned projects
ITEMS_RESPONSE=$(gh api graphql -f query='
query($owner: String!, $number: Int!) {
  user(login: $owner) {
    projectV2(number: $number) {
      id
      items(first: 100) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          content {
            ... on Issue {
              number
              title
              body
              state
              url
              createdAt
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2SingleSelectField { name } }
              }
            }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -F number="$NUMBER")
```

**Pagination**: If `pageInfo.hasNextPage` is true, make additional requests with `after: $endCursor`.

**Status Filtering**:
- Look for items with Status field value matching "Ready" (case-insensitive)
- Also filter to OPEN issues only (exclude closed GitHub issues)
- If no exact match, look for similar values: "Ready for Dev", "To Do", "Backlog"

Example filter:
```bash
# Filter items with "Ready" status and OPEN state
ready_items=$(echo "$ITEMS_RESPONSE" | jq -r '[
  .data.user.projectV2.items.nodes[] |
  select(.content.state == "OPEN") |
  {
    id: .id,
    title: .content.title,
    body: .content.body,
    number: .content.number,
    url: .content.url,
    createdAt: .content.createdAt,
    status: ([.fieldValues.nodes[] | select(.field.name == "Status") | .name] | first // "Unknown"),
    priority: ([.fieldValues.nodes[] | select(.field.name == "Priority") | .name] | first // null),
    size: ([.fieldValues.nodes[] | select(.field.name == "Size") | .name] | first // null)
  } |
  select(.status | test("ready"; "i"))
]')
```

**If no ready items found**:
```
No items found with "Ready" status.

Available statuses in project: To Do, In Progress, Done

Would you like me to show items from a different status instead?
```

### 4. Analyze Codebase Signals and Sort

This step uses lightweight git heuristics to add codebase relevance as a secondary tiebreaker (after priority, before creation date). Budget: 2-5 seconds total.

#### Step 4a: Initial Priority Sort

Sort items by priority to identify top 5 candidates:

```bash
# Initial sort by priority only
top_candidates=$(echo "$ready_items" | jq -r '
  sort_by(.priority | sub("P"; "") | tonumber? // 999) |
  .[0:5]
')
```

#### Step 4b: Codebase Signal Analysis

**Check Git Availability**:

```bash
# Verify we're in a git repository
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  CODEBASE_ENABLED=true

  # Cache recently modified files (last 7 days)
  RECENT_FILES=$(timeout 1s git log --since="7 days ago" --name-only --pretty=format: 2>/dev/null | sort -u | grep -v '^$' || echo "")
else
  CODEBASE_ENABLED=false
fi
```

**Calculate Signal Score** (for each top 5 candidate):

```bash
calculate_signal_score() {
  local title="$1"
  local body="$2"
  local score=0

  # Extract keywords from title and body (3+ char words, no stop words)
  keywords=$(echo "$title $body" | tr '[:upper:]' '[:lower:]' | \
    grep -oE '\b[a-z]{3,}\b' | \
    grep -vE '^(the|and|for|are|but|not|you|all|can|had|was|one|has|this|that|with|from|they|have|been|will|what|when|your|which|would|there|their|about|could|other|these|than|into|some|them|only|over|such|after|also|most|made|just|very|where|while|should|since|because|using|without)$' | \
    sort -u | head -10)

  # Heuristic A: Keywords match recently modified files (+30 points)
  for kw in $keywords; do
    if echo "$RECENT_FILES" | grep -qi "$kw"; then
      score=$((score + 30))
      break  # Only count once
    fi
  done

  # Heuristic B: File paths mentioned in issue exist (+20 points)
  file_refs=$(echo "$body" | grep -oE '[a-zA-Z0-9_/-]+\.(ts|js|py|json|md|yaml|yml)' | head -3)
  for ref in $file_refs; do
    if git ls-files --cached 2>/dev/null | grep -q "$ref"; then
      score=$((score + 20))
      break  # Only count once
    fi
  done

  # Heuristic C: Related directory has recent commits (+5 per commit, max 50)
  dirs=$(echo "$body" | grep -oE '\b(src|lib|test|tests|config|utils)/[a-zA-Z0-9_/-]+' | head -2)
  for dir in $dirs; do
    commits=$(timeout 0.5s git log --since="30 days ago" --oneline -- "$dir" 2>/dev/null | wc -l || echo 0)
    score=$((score + commits * 5))
  done

  # Cap at 100
  [ $score -gt 100 ] && score=100
  echo $score
}
```

**Signal Scoring Summary**:
- **+30 points**: Issue keywords match recently modified files (7 days)
- **+20 points**: File paths mentioned in issue exist in codebase
- **+5 per commit**: Related directories have recent activity (30 days, max 50 points)
- **Maximum**: 100 points

#### Step 4c: Final Sort with Codebase Signals

**Sort Order** (most significant to least):
1. **Priority** (P0=0, P1=1, P2=2, P3=3, missing=999)
2. **Codebase Signal Score** (0-100, higher is better)
3. **Creation Date** (oldest first)

```bash
# Re-sort candidates with codebase signals
echo "$candidates_with_scores" | jq -r '
  sort_by(
    (.priority | sub("P"; "") | tonumber? // 999),  # Primary: Priority
    (100 - (.codebase_score // 0)),                  # Secondary: Codebase signal (inverted)
    .createdAt                                       # Tertiary: Creation date
  ) |
  .[0:3]
'
```

**Codebase Relevance Labels**:
- **High** (60-100): Active development area, concrete file references
- **Medium** (30-59): Some related activity or file references
- **Low** (0-29): No recent activity or file references
- **N/A**: Codebase analysis unavailable (not a git repo)

#### Graceful Degradation

If git is unavailable or heuristics fail:

```
Note: Codebase analysis unavailable (not a git repository).
Recommendations based on priority and creation date only.
```

If git operations time out:
- Use partial results if available
- Fall back to priority + creation date sort
- Do not block the command

### 5. Present Recommendations

Display top 2-3 options in tabular format following TD-8 specification:

```
| # | Title                      | Priority | Size | Status | Codebase |
|---|----------------------------|----------|------|--------|----------|
| 1 | Fix login timeout bug      | P0       | S    | Ready  | High     |
| 2 | Add user preferences page  | P1       | M    | Ready  | Medium   |
| 3 | Improve error messages     | P1       | S    | Ready  | Low      |

**Recommendation**: Item #1 (P0 priority, small scope, high codebase relevance)

**Rationale**: This is the highest priority item in the backlog. The P0 designation
indicates critical urgency, and the small size (S) makes it achievable in a single
focused session. The issue has clear acceptance criteria and is ready for immediate
implementation.

**Codebase Relevance**: High - The `auth/` directory mentioned in this issue has
8 commits in the last 30 days. The file `src/auth/session.ts` referenced in the
issue exists in the codebase.

**Alternative Options**:
- Item #2: Same priority (P1) as item #3 but ranked higher due to active development
  in the `preferences/` module (3 recent commits).
- Item #3: Also P1 priority but lower codebase relevance. Good backup if item #1 is blocked.
```

**Rationale Elements to Include**:
- **Priority justification**: Why this item ranks highest (P0 designation, urgency)
- **Size assessment**: Small items are more achievable in single session
- **Codebase relevance**: Explain why item scored High/Medium/Low
- **Definition quality**: Mention if acceptance criteria are clear
- **Context**: Any relevant technical considerations or dependencies

**If codebase signals caused reordering** (same priority items):
```
**Note**: Item #2 ranks ahead of item #3 (same priority P1) due to higher codebase
relevance - the feature area has recent commits suggesting active development context.
```

**If all items have equal priority** (missing Priority field):
```
**Recommendation**: Item #1 (highest codebase relevance, small scope, ready for work)

**Rationale**: No priority field found in project, so recommending based on codebase
relevance and age. This item relates to actively developed code and is small enough
to complete in one session.
```

**If codebase analysis unavailable**:
```
**Codebase Relevance**: N/A - Not a git repository.
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
- Codebase analysis: 2-5s (top 5 items, git heuristics)
- Total operation: <8s end-to-end

**Codebase Analysis Budget**:
- Recent file detection: ~50ms (single git log, cached)
- Per-item keyword check: ~10ms
- Per-item file existence: ~50ms
- Per-item related activity: ~100ms
- Total for 5 items: ~800ms typical, <3s worst case

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

Analyzing codebase signals...
✓ Git repository detected, running heuristics on top 5 candidates

Sorting by priority and codebase relevance...

| # | Title                           | Priority | Size | Status | Codebase |
|---|---------------------------------|----------|------|--------|----------|
| 1 | Fix authentication timeout      | P0       | S    | Ready  | High     |
| 2 | Implement user preferences API  | P1       | M    | Ready  | Medium   |
| 3 | Add error logging to webhook    | P1       | S    | Ready  | Low      |

**Recommendation**: Item #1 - "Fix authentication timeout"

**Rationale**: This is the highest priority item (P0 = critical) and has the
smallest scope (S). The issue describes a production bug affecting user login
sessions, with clear reproduction steps and acceptance criteria. This can be
completed in a single focused session.

**Codebase Relevance**: High - The `src/auth/` directory has 12 commits in the
last 30 days, indicating active development. The file `auth/session.ts` mentioned
in the issue exists in the codebase.

**Alternative Options**:
- Item #2 (P1/M): Ranked above item #3 due to recent activity in the `preferences/`
  module (5 commits). Higher effort but aligns with current development focus.
- Item #3 (P1/S): Small scope but low codebase relevance (no recent webhook changes).
  Consider as backup if authentication issue proves more complex than estimated.

Would you like to start work on item #1? (/start-work command)
```

## Anti-Patterns to Avoid

- **Don't skip config validation**: Always verify config exists and is valid before querying
- **Don't assume field names**: Use discovery pattern, don't hardcode "Priority" or "Status"
- **Don't fail silently**: If fields are missing, warn the user and explain impact
- **Don't show too many options**: Limit to top 2-3 items to avoid decision paralysis
- **Don't forget rationale**: Always explain WHY you're recommending an item
- **Don't let codebase analysis block**: If git fails or times out, continue with priority sort
- **Don't over-weight codebase signals**: They are tiebreakers, not primary sort criteria

## Related Commands

- `/backlog` - Review entire backlog with quality analysis
- `/start-work` - Begin implementation of selected item
- `/add-item` - Create new issue and add to project
- `/reprioritize` - Codebase-aware priority updates

## References

- **Spec**: REQ-F-4, REQ-F-5, REQ-F-6, REQ-F-11, REQ-NF-3, REQ-NF-4
- **Plan**: TD-6 (Priority Sorting), TD-8 (Item Presentation Format)
- **Skill**: `compass-rose/skills/gh-project-reference/SKILL.md` (config patterns, field discovery)
