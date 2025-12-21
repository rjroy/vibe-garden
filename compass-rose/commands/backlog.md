---
argument-hint: []
description: Review backlog items and analyze quality to recommend best items to work on
allowed-tools: Bash, Read, Grep, Glob
---

# Backlog Review Mode

You are now in **Backlog Review Mode**. Your role is to analyze all non-Done project items, assess their quality and readiness, and recommend the top 2-3 items to work on next based on priority, size, and definition quality.

## Your Focus

- **Configuration loading**: Read `.compass-rose/config.json` and validate project settings
- **Field discovery**: Detect available custom fields (Priority, Size, Status, etc.)
- **Item retrieval**: Query all non-Done items from the project
- **Quality analysis**: Spawn backlog-analyzer agent to assess definition quality
- **Recommendation**: Present 2-3 best options with detailed rationale

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
Warning: Priority field not found in project. Recommendations will be based on size and definition quality only.

Available fields: Status, Size, Iteration

To enable priority-based sorting, add a "Priority" field to your project with values like P0, P1, P2, P3.
```

Continue with available data even if some fields are missing.

### 3. Query All Non-Done Items

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
              repository { nameWithOwner }
              assignees(first: 5) { nodes { login } }
              labels(first: 10) { nodes { name } }
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

**Pagination**: If `pageInfo.hasNextPage` is true, make additional requests with `after: $endCursor` until all items are fetched.

**Status Filtering**:
- Exclude items with Status field value matching "Done", "Closed", "Complete" (case-insensitive)
- Also filter to OPEN issues only (exclude closed GitHub issues)
- Include all other statuses: "Ready", "To Do", "In Progress", "Backlog", etc.

Example filter:
```bash
# Filter out "Done" items and closed issues, keep everything else
echo "$ITEMS_RESPONSE" | jq -r '[
  .data.user.projectV2.items.nodes[] |
  select(.content.state == "OPEN") |
  {
    id: .id,
    title: .content.title,
    body: .content.body,
    number: .content.number,
    url: .content.url,
    status: ([.fieldValues.nodes[] | select(.field.name == "Status") | .name] | first // "Unknown"),
    priority: ([.fieldValues.nodes[] | select(.field.name == "Priority") | .name] | first // null),
    size: ([.fieldValues.nodes[] | select(.field.name == "Size") | .name] | first // null),
    assignees: [.content.assignees.nodes[].login],
    labels: [.content.labels.nodes[].name]
  } |
  select(.status | test("done|closed|complete"; "i") | not)
]'
```

**If no items found**:
```
No active items found in the project.

All items appear to be marked as "Done" or the project is empty.

Would you like to create a new item? (/add-item command)
```

### 4. Prepare Data for Agent Analysis

Transform the GraphQL response into a clean JSON array suitable for the backlog-analyzer agent:

```bash
# The filtering in step 3 already produces the correct format for the agent
# Items are already transformed to:
# {
#   id: "PVTI_...",
#   title: "...",
#   body: "...",
#   number: 42,
#   url: "https://github.com/...",
#   status: "Ready",
#   priority: "P1",
#   size: "M",
#   assignees: ["username"],
#   labels: ["bug", "frontend"]
# }
```

**Note**: The GraphQL response structure is consistent. The jq transformation in step 3 normalizes the data for agent consumption.

### 5. Spawn Backlog Analyzer Agent

Invoke the backlog-analyzer agent with the prepared item data:

```
Analyze these project items and recommend the top 2-3 to work on next:

[Paste the formatted JSON array from step 4]

Focus on:
- Definition quality (clarity, completeness, acceptance criteria)
- Priority distribution (if Priority field exists)
- Size balance (prefer mix of quick wins and substantial work)
- Overall backlog health

Return your analysis with detailed rationale for each recommendation.
```

**Agent Reference**: `compass-rose/agents/backlog-analyzer.md`

The agent will:
1. Score each item on definition quality (0-10 scale)
2. Identify "well-defined" items (score 8-10)
3. Calculate recommendation scores (priority + size + quality)
4. Return top 2-3 recommendations with rationale
5. Provide backlog health summary
6. List items needing clarification

### 6. Present Agent Recommendations

Display the agent's analysis output directly to the user. The agent returns structured markdown with:

```markdown
# Backlog Analysis Results

**Items Analyzed**: [N total]
**Well-Defined Items**: [X items with score 8-10]
**Items Needing Clarification**: [Y items with score <5]

## Top Recommendations

### Recommendation 1: [Title] (#[number])

**Priority**: [P0/P1/P2/P3] | **Size**: [S/M/L/XL] | **Definition Quality**: [Well-Defined/Defined/Vague/Poorly Defined] ([score]/10)

**Rationale**:
- [Why this is recommended - link priority, size, definition quality]
- [What makes it ready to work on]
- [Any specific strengths]

**Definition Assessment**:
- **Clarity** ([0-3]/3): [Brief assessment]
- **Completeness** ([0-3]/3): [Brief assessment]
- **Acceptance Criteria** ([0-4]/4): [Brief assessment]

**Link**: [URL to issue]

---

### Recommendation 2: [Title] (#[number])
[Same structure as Recommendation 1]

---

### Recommendation 3: [Title] (#[number]) [OPTIONAL]
[Same structure as Recommendation 1]

---

## Backlog Health Summary

**Priority Distribution**: [X P0, Y P1, Z P2, W P3]
**Size Distribution**: [A S, B M, C L, D XL]
**Definition Quality**:
- Well-Defined (8-10): [X items]
- Defined (5-7): [Y items]
- Vague (2-4): [Z items]
- Poorly Defined (0-1): [W items]

**Observations**:
- [Notable patterns]
- [Quality trends]
- [Recommendations for backlog improvement]

## Items Needing Clarification

1. **[Title]** (#[number]) - Score: [X]/10
   - Missing: [What needs to be added]
   - Suggest: [How to improve definition]
```

After presenting the agent's output, add:

```
Would you like to:
1. Start work on one of these recommendations? (/start-work)
2. Review the next item specifically? (/next-item)
3. Add a new item to the backlog? (/add-item)
4. Clarify one of the poorly-defined items?
```

### 7. Handle Edge Cases

**No Active Items**:
```
No active items found in the project.

All items are marked as "Done" or the project is empty.

Would you like to create a new item? (/add-item command)
```

**Missing Priority Field**:
```
Warning: Priority field not found in project.

Recommendations will be based on:
- Definition quality (clarity, completeness, acceptance criteria)
- Size (prefer smaller items for quick wins)
- Creation date (older items first)

To enable priority-based recommendations, add a "Priority" field to your project.
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

**All Items Poorly Defined**:

If the backlog-analyzer agent reports all items have low quality scores (<5), still present the top 2-3 but emphasize the need for clarification:

```
⚠️ Warning: Most backlog items lack sufficient detail.

The recommendations below are based on priority/size only, but each item needs
clarification before implementation can begin. Consider adding:
- Clear problem/feature descriptions
- Reproduction steps (for bugs) or use cases (for features)
- Explicit acceptance criteria

Recommended next step: Clarify the highest-priority items before starting work.
```

## Requirements Mapping

This command implements the following specification requirements:

- **REQ-F-11**: Analyze backlog items and recommend based on priority, size, and definition quality
- **REQ-F-12**: Identify items that are "well-defined" (have clear description and acceptance criteria)
- **REQ-F-13**: Present 2-3 options when asked for recommendations, with rationale
- **REQ-NF-3**: Handle missing custom fields gracefully (warn, don't fail)
- **REQ-NF-4**: Explain reasoning when making recommendations

## Implementation Notes

**Performance Targets**:
- Config load: <100ms (local file read)
- Field discovery: <1s (single API call)
- Item listing: <2s (typical backlog of <100 items)
- Agent analysis: 5-10s (depends on item count and description length)
- Total operation: <15s end-to-end

**Data Freshness**:
- Always fetch fresh data (no caching between sessions per spec constraint)
- Ensures analysis reflects current project state
- Re-run command to get updated analysis after making changes

**CLI Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)
- `jq` for JSON parsing (check availability, provide clear error if missing)

**Agent Invocation**:
- Agent operates on item data passed as context
- Agent has access to Read, Grep tools for deeper analysis if needed
- Agent returns structured markdown output for direct presentation

## Example Output

```
Loading project configuration...
✓ Config loaded: my-org/project-123

Discovering custom fields...
✓ Found fields: Status, Priority, Size, Iteration

Querying active items...
✓ Found 15 non-Done items

Analyzing backlog quality with backlog-analyzer agent...

---

# Backlog Analysis Results

**Items Analyzed**: 15 total
**Well-Defined Items**: 4 items with score 8-10
**Items Needing Clarification**: 6 items with score <5

## Top Recommendations

### Recommendation 1: Fix login timeout on Chrome (#42)

**Priority**: P0 | **Size**: S | **Definition Quality**: Well-Defined (9/10)

**Rationale**:
- Highest priority (P0) issue affecting 15% of users
- Small scope (S) makes it achievable in single session
- Excellent definition with clear repro steps, acceptance criteria, and impact data
- Can be completed quickly to unblock users

**Definition Assessment**:
- **Clarity** (3/3): Clear problem description with specific browser versions and reproduction steps
- **Completeness** (3/3): Includes repro steps, environment details, server log insights, and user impact percentage
- **Acceptance Criteria** (3/4): Explicit success conditions but could include performance target (e.g., p95 < 5s)

**Link**: https://github.com/my-org/my-repo/issues/42

---

### Recommendation 2: Add user preferences panel (#58)

**Priority**: P1 | **Size**: M | **Definition Quality**: Defined (7/10)

**Rationale**:
- High priority (P1) feature request from multiple users
- Medium scope (M) - more involved but still manageable
- Good definition with use cases and most details present
- Complements login fix (both improve user experience)

**Definition Assessment**:
- **Clarity** (3/3): Clear use cases and user needs described
- **Completeness** (2/3): Core requirements present but missing edge cases
- **Acceptance Criteria** (2/4): Basic success conditions but not fully testable

**Link**: https://github.com/my-org/my-repo/issues/58

---

## Backlog Health Summary

**Priority Distribution**: 3 P0, 7 P1, 4 P2, 1 P3
**Size Distribution**: 5 S, 6 M, 3 L, 1 XL
**Definition Quality**:
- Well-Defined (8-10): 4 items
- Defined (5-7): 5 items
- Vague (2-4): 4 items
- Poorly Defined (0-1): 2 items

**Observations**:
- P0 items are generally well-defined (good crisis management)
- Many P1 features lack explicit acceptance criteria (common pattern)
- XL item (#72: "Implement notification system") should be broken down or escalated to Spiral Grove spec

## Items Needing Clarification

1. **Improve error messages** (#51) - Score: 3/10
   - Missing: Which errors? What makes them bad currently? What should they say instead?
   - Suggest: List specific error scenarios, current messages, and desired improvements

2. **Refactor auth module** (#73) - Score: 2/10
   - Missing: What problems exist? What's the goal of refactoring? Success criteria?
   - Suggest: Describe technical debt, refactoring objectives, and measurable improvements

---

Would you like to:
1. Start work on one of these recommendations? (/start-work)
2. Review the next item specifically? (/next-item)
3. Add a new item to the backlog? (/add-item)
4. Clarify one of the poorly-defined items?
```

## Anti-Patterns to Avoid

- **Don't skip config validation**: Always verify config exists and is valid before querying
- **Don't assume field names**: Use discovery pattern, don't hardcode "Priority" or "Status"
- **Don't fail silently**: If fields are missing, warn the user and explain impact
- **Don't bypass the agent**: Always use backlog-analyzer for quality assessment (don't try to implement scoring in the command)
- **Don't filter too aggressively**: Include all non-Done items so agent sees full backlog context
- **Don't truncate agent output**: Present the agent's full analysis to maintain transparency

## Related Commands

- `/next-item` - Get immediate recommendation for next work item (faster, simpler)
- `/start-work` - Begin implementation of selected item
- `/add-item` - Create new issue and add to project
- `/reprioritize` - Codebase-aware priority updates

## Comparison to /next-item

| Aspect | /next-item | /backlog |
|--------|------------|----------|
| **Speed** | Fast (<3s) | Slower (~15s) |
| **Scope** | Ready items only | All non-Done items |
| **Analysis** | Simple priority sort | Deep quality assessment |
| **Output** | Quick recommendation | Comprehensive backlog health report |
| **Use Case** | "What's next?" | "What's the state of my backlog?" |

**When to use /backlog**:
- You want to understand overall backlog health
- You need recommendations based on definition quality, not just priority
- You want to identify poorly-defined items for cleanup
- You're planning a sprint or work session and want multiple options

**When to use /next-item**:
- You just want the next thing to work on right now
- You trust your Ready status filtering
- You want a quick answer without deep analysis

## References

- **Spec**: REQ-F-11, REQ-F-12, REQ-F-13, REQ-NF-3, REQ-NF-4
- **Plan**: TD-8 (Item Presentation Format), /backlog command flow
- **Agent**: `compass-rose/agents/backlog-analyzer.md` (quality scoring and recommendation)
- **Skill**: `compass-rose/skills/gh-project-reference/SKILL.md` (config patterns, field discovery)
