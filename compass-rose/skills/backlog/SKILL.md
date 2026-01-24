---
name: backlog
description: This skill should be used when the user asks to "review backlog", "analyze backlog quality", "backlog health", "recommend items", or invokes /compass-rose:backlog. Reviews backlog items and analyzes quality to recommend best items to work on.
allowed-tools: Skill(compass-rose:gh-api-scripts), Bash, Read, Grep, Glob
---

# Backlog Review Mode

You are now in **Backlog Review Mode**. Your role is to analyze all non-Done project items, assess their quality and readiness, and recommend the top 2-3 items to work on next based on priority, size, and definition quality.

## Your Focus

- **Item retrieval**: Use `gh-api-scripts` skill to fetch all project items (includes field values)
- **Status filtering**: Filter out completed items from the results
- **Quality analysis**: Spawn backlog-analyzer agent to assess definition quality
- **Recommendation**: Present 2-3 best options with detailed rationale

## Required Skills

**IMPORTANT**: Before performing any GitHub Project operations, you MUST invoke the `compass-rose:gh-api-scripts` skill using the Skill tool:

```
Skill(compass-rose:gh-api-scripts)
```

This skill provides the `list-issues` operation needed for this skill. **Do NOT use raw `gh project` commands.**

## Workflow

### 1. Fetch Project Items

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
        "body": "Description...",
        "url": "https://github.com/...",
        "state": "OPEN",
        "labels": ["bug", "priority-high"],
        "status": "Ready",
        "priority": "P0",
        "size": "S"
      }
    ],
    "count": 15
  }
}
```

**Error Handling**: The script returns structured errors:
```json
{
  "success": false,
  "error": {
    "code": "CONFIG_MISSING",
    "message": "Configuration file not found",
    "details": "Create .compass-rose/config.json with..."
  }
}
```

**If configuration is missing or invalid**, display the error details and stop.

### 2. Filter Non-Done Items

The `list-issues` operation returns all open issues from the project. Filter out completed items from the response:

**Filtering Logic**:
- Exclude items with Status field value matching "Done", "Closed", "Complete" (case-insensitive)
- The script already filters to OPEN issues only
- Include all other statuses: "Ready", "To Do", "In progress", "Backlog", etc.

**If no items found**:
```
No active items found in the project.

All items appear to be marked as "Done" or the project is empty.

Would you like to create a new item? (/compass-rose:add-item skill)
```

### 3. Prepare Data for Agent Analysis

The `list-issues` script already returns data in a clean format suitable for the backlog-analyzer agent:

```json
{
  "number": 42,
  "title": "Fix login timeout",
  "body": "Description with details...",
  "url": "https://github.com/org/repo/issues/42",
  "state": "OPEN",
  "labels": ["bug", "priority-high"],
  "status": "Ready",
  "priority": "P1",
  "size": "M"
}
```

**Note**: The script handles GraphQL complexity internally. The filtered array from step 2 is ready for agent consumption.

### 4. Spawn Backlog Analyzer Agent

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

### 5. Present Agent Recommendations

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
1. Start work on one of these recommendations? (/compass-rose:start-work)
2. Review the next item specifically? (/compass-rose:next-item)
3. Add a new item to the backlog? (/compass-rose:add-item)
4. Clarify one of the poorly-defined items?
```

### 6. Handle Edge Cases

**No Active Items**:
```
No active items found in the project.

All items are marked as "Done" or the project is empty.

Would you like to create a new item? (/compass-rose:add-item skill)
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
Warning: Most backlog items lack sufficient detail.

The recommendations below are based on priority/size only, but each item needs
clarification before implementation can begin. Consider adding:
- Clear problem/feature descriptions
- Reproduction steps (for bugs) or use cases (for features)
- Explicit acceptance criteria

Recommended next step: Clarify the highest-priority items before starting work.
```

## Requirements Mapping

This skill implements the following specification requirements:

- **REQ-F-11**: Analyze backlog items and recommend based on priority, size, and definition quality
- **REQ-F-12**: Identify items that are "well-defined" (have clear description and acceptance criteria)
- **REQ-F-13**: Present 2-3 options when asked for recommendations, with rationale
- **REQ-NF-3**: Handle missing custom fields gracefully (warn, don't fail)
- **REQ-NF-4**: Explain reasoning when making recommendations

## Implementation Notes

**Performance Targets**:
- Issue retrieval: <2s (gh-api-scripts handles pagination)
- Agent analysis: 5-10s (depends on item count and description length)
- Total operation: <15s end-to-end

**Data Freshness**:
- Always fetch fresh data (no caching between sessions per spec constraint)
- Ensures analysis reflects current project state
- Re-run skill to get updated analysis after making changes

**CLI Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)
- `jq` for JSON filtering (optional - script handles parsing)
- Python 3.12+ for `gh-api-scripts` skill

**Agent Invocation**:
- Agent operates on item data passed as context
- Agent has access to Read, Grep tools for deeper analysis if needed
- Agent returns structured markdown output for direct presentation

## Example Output

```
Loading project configuration...
Config loaded: my-org/project-123

Discovering custom fields...
Found fields: Status, Priority, Size, Iteration

Querying active items...
Found 15 non-Done items

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
1. Start work on one of these recommendations? (/compass-rose:start-work)
2. Review the next item specifically? (/compass-rose:next-item)
3. Add a new item to the backlog? (/compass-rose:add-item)
4. Clarify one of the poorly-defined items?
```

## Anti-Patterns to Avoid

- **Don't use raw gh commands**: Always use gh-api-scripts skill for GitHub Project operations
- **Don't fail silently**: If fields are missing, warn the user and explain impact
- **Don't bypass the agent**: Always use backlog-analyzer for quality assessment (don't try to implement scoring in the skill)
- **Don't filter too aggressively**: Include all non-Done items so agent sees full backlog context
- **Don't truncate agent output**: Present the agent's full analysis to maintain transparency

## Related Skills

- `/compass-rose:next-item` - Get immediate recommendation for next work item (faster, simpler)
- `/compass-rose:start-work` - Begin implementation of selected item
- `/compass-rose:add-item` - Create new issue and add to project
- `/compass-rose:reprioritize` - Codebase-aware priority updates

## Comparison to /compass-rose:next-item

| Aspect | /compass-rose:next-item | /compass-rose:backlog |
|--------|-------------------------|----------------------|
| **Speed** | Fast (<3s) | Slower (~15s) |
| **Scope** | Ready items only | All non-Done items |
| **Analysis** | Simple priority sort | Deep quality assessment |
| **Output** | Quick recommendation | Comprehensive backlog health report |
| **Use Case** | "What's next?" | "What's the state of my backlog?" |

**When to use /compass-rose:backlog**:
- You want to understand overall backlog health
- You need recommendations based on definition quality, not just priority
- You want to identify poorly-defined items for cleanup
- You're planning a sprint or work session and want multiple options

**When to use /compass-rose:next-item**:
- You just want the next thing to work on right now
- You trust your Ready status filtering
- You want a quick answer without deep analysis

## References

- **Spec**: REQ-F-11, REQ-F-12, REQ-F-13, REQ-NF-3, REQ-NF-4
- **Plan**: TD-8 (Item Presentation Format), /backlog skill flow
- **Agent**: `compass-rose/agents/backlog-analyzer.md` (quality scoring and recommendation)
- **Skill**: `compass-rose/skills/gh-api-scripts/SKILL.md` (GitHub Project API operations)
