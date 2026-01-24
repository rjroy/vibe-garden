---
name: next-item
description: This skill should be used when the user asks "what should I work on", "next item", "highest priority", "what's ready", or invokes /compass-rose:next-item. Recommends the highest-priority ready item with rationale.
allowed-tools: Skill(compass-rose:gh-api-scripts), Bash, Read, Grep, Glob
---

# Next Item Recommendation Mode

You are now in **Next Item Recommendation Mode**. Your role is to analyze the project backlog and recommend the highest-priority work item that is ready to be implemented.

## Your Focus

- **Issue retrieval**: Use `gh-api-scripts` to get all project issues with field values
- **Item filtering**: Filter items with Ready status (or equivalent)
- **Priority sorting**: Sort by Priority field (P0 > P1 > P2 > P3)
- **Codebase signals**: Use lightweight git heuristics as secondary tiebreaker
- **Presentation**: Display top 2-3 options in tabular format with rationale

## Required Skills

**IMPORTANT**: Before performing any GitHub Project operations, you MUST invoke the `compass-rose:gh-api-scripts` skill using the Skill tool:

```
Skill(compass-rose:gh-api-scripts)
```

This skill provides the `list-issues` operation needed for this skill. **Do NOT use raw `gh project` commands.**

## Workflow

### 1. Query All Issues

Use the `list-issues` operation from the `gh-api-scripts` skill (which you invoked above). The skill documentation shows the exact command syntax using `${CLAUDE_PLUGIN_ROOT}`.

**Output Format** (JSON):
```json
{
  "success": true,
  "data": {
    "issues": [
      {
        "number": 42,
        "title": "Fix login timeout",
        "body": "Users experiencing timeouts...",
        "url": "https://github.com/.../issues/42",
        "state": "OPEN",
        "labels": ["bug"],
        "status": "Ready",
        "priority": "P0",
        "size": "S"
      }
    ],
    "count": 8
  }
}
```

### 2. Filter Ready Items

Filter for items with "Ready" status (case-insensitive):

```bash
# Filter items with "Ready" status
ready_items=$(echo "$ALL_ISSUES" | jq -r '[
  .[] |
  select(.state == "OPEN") |
  select(.status | test("ready"; "i"))
]')
```

**Graceful Degradation**: If Priority field values are all null:
```
Warning: Priority field not found or not set on items. All items will be treated as equal priority.

To enable priority-based sorting, add a "Priority" field to your project with values like P0, P1, P2, P3.
```

Continue with available data even if some fields are missing.

**If no ready items found**:
```
No items found with "Ready" status.

Available statuses in project: To Do, In progress, Done

Would you like me to show items from a different status instead?
```

### 3. Analyze Codebase Signals and Sort

This step uses lightweight git heuristics to add codebase relevance as a secondary tiebreaker (after priority, before creation date). Budget: 2-5 seconds total.

#### Step 3a: Initial Priority Sort

Sort items by priority to identify top 5 candidates:

```bash
# Initial sort by priority only
top_candidates=$(echo "$ready_items" | jq -r '
  sort_by(.priority | sub("P"; "") | tonumber? // 999) |
  .[0:5]
')
```

#### Step 3b: Codebase Signal Analysis

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

#### Step 3c: Final Sort with Codebase Signals

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
- Do not block the skill

### 4. Present Recommendations

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

### 5. Handle Edge Cases

**No Ready Items**:
```
No items found with "Ready" status.

Available statuses: To Do (15 items), In progress (3 items), Done (42 items)

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

This skill implements the following specification requirements:

- **REQ-F-4**: Retrieve project items filtered by status
- **REQ-F-5**: Sort items by priority field (P0 > P1 > P2 > P3)
- **REQ-F-6**: Display item summary, priority, size, and iteration
- **REQ-F-11**: Recommend based on priority, size, and definition quality
- **REQ-NF-3**: Handle missing custom fields gracefully (warn, don't fail)
- **REQ-NF-4**: Explain reasoning when making recommendations

## Implementation Notes

**Performance Targets**:
- Issue retrieval: <2s (gh-api-scripts handles pagination)
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
Retrieving project issues...
Found 8 items with "Ready" status

Analyzing codebase signals...
Git repository detected, running heuristics on top 5 candidates

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

Would you like to start work on item #1? (/compass-rose:start-work skill)
```

## Anti-Patterns to Avoid

- **Don't use raw gh commands**: Always use gh-api-scripts skill for GitHub Project operations
- **Don't fail silently**: If fields are missing, warn the user and explain impact
- **Don't show too many options**: Limit to top 2-3 items to avoid decision paralysis
- **Don't forget rationale**: Always explain WHY you're recommending an item
- **Don't let codebase analysis block**: If git fails or times out, continue with priority sort
- **Don't over-weight codebase signals**: They are tiebreakers, not primary sort criteria

## Related Skills

- `/compass-rose:backlog` - Review entire backlog with quality analysis
- `/compass-rose:start-work` - Begin implementation of selected item
- `/compass-rose:add-item` - Create new issue and add to project
- `/compass-rose:reprioritize` - Codebase-aware priority updates

## References

- **Spec**: REQ-F-4, REQ-F-5, REQ-F-6, REQ-F-11, REQ-NF-3, REQ-NF-4
- **Plan**: TD-6 (Priority Sorting), TD-8 (Item Presentation Format)
- **Skill**: `compass-rose/skills/gh-api-scripts/SKILL.md` (GitHub Project API operations)
