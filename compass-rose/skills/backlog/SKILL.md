---
name: backlog
description: Use when the user asks to "review backlog", "analyze backlog quality", "backlog health", or invokes /compass-rose:backlog. Reads all open and wontfix issue files and analyzes quality via the backlog-analyzer agent.
allowed-tools: Bash, Read, Glob, Agent
---

# Backlog Review Mode

You are now in **Backlog Review Mode**. Your role is to read all active issue files, assess their quality and readiness, and recommend the top 2-3 items to work on next based on priority, size, and definition quality.

## Your Focus

- **Issue discovery**: Glob all `.lore/work/issues/*.html` files
- **Status filtering**: Include items with status `open` or `wontfix` (exclude `done` and `closed`)
- **Quality analysis**: Spawn backlog-analyzer agent to assess definition quality
- **Recommendation**: Present 2-3 best options with detailed rationale

## Workflow

### 1. Discover Issue Files

Use Glob to find all issue files:

```
.lore/work/issues/*.html
```

If no files exist, stop and say:

```
No issue files found in .lore/work/issues/.

To get started, create your first issue with /compass-rose:add-item.
```

### 2. Parse Each Issue File

For each file, use Read to extract the meta tags from the `<head>` and the body text:

**Meta tags to extract**:
- `priority` — e.g., `P0`, `P1`, `P2`, `P3`
- `size` — e.g., `S`, `M`, `L`, `XL`
- `status` — e.g., `open`, `wontfix`, `done`, `closed`
- `date` — creation date
- `title` — issue title (also available as `<title>` tag)

**Body text**: Extract the readable text content from the HTML body.

### 3. Filter by Status

Include items where status is `open` or `wontfix`. Exclude items where status is `done` or `closed`.

`wontfix` items are intentionally included. They are deferred, not done, and should surface if context changes.

**If no items remain after filtering**:

```
No open or deferred issues found in .lore/work/issues/.

All issues are either done or closed.

To add new work, use /compass-rose:add-item.
```

### 4. Prepare Data for Agent Analysis

Build a JSON array from the filtered items:

```json
[
  {
    "filepath": ".lore/work/issues/fix-login-timeout.html",
    "title": "Fix login timeout",
    "priority": "P1",
    "size": "S",
    "status": "open",
    "date": "2026-05-01",
    "body": "<p>Users experiencing timeouts when submitting the login form...</p>"
  }
]
```

### 5. Spawn Backlog Analyzer Agent

Invoke the backlog-analyzer agent with the prepared item data:

```
Analyze these project items and recommend the top 2-3 to work on next:

[Paste the formatted JSON array]

Focus on:
- Definition quality (clarity, completeness, acceptance criteria)
- Priority distribution
- Size balance (prefer a mix of quick wins and substantial work)
- Overall backlog health

Return your analysis with detailed rationale for each recommendation.
```

**Agent Reference**: `compass-rose/agents/backlog-analyzer.md`

The agent will:
1. Score each item on definition quality (0-10 scale)
2. Identify well-defined items (score 8-10)
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

### Recommendation 1: [Title] ([filename])

**Priority**: [P0/P1/P2/P3] | **Size**: [S/M/L/XL] | **Definition Quality**: [Well-Defined/Defined/Vague/Poorly Defined] ([score]/10)

**Rationale**:
- [Why this is recommended - link priority, size, definition quality]
- [What makes it ready to work on]
- [Any specific strengths]

**Definition Assessment**:
- **Clarity** ([0-3]/3): [Brief assessment]
- **Completeness** ([0-3]/3): [Brief assessment]
- **Acceptance Criteria** ([0-4]/4): [Brief assessment]

**File**: [filepath]

---

### Recommendation 2: [Title] ([filename])
[Same structure as Recommendation 1]

---

### Recommendation 3: [Title] ([filename]) [OPTIONAL]
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

1. **[Title]** ([filename]) - Score: [X]/10
   - Missing: [What needs to be added]
   - Suggest: [How to improve definition]
```

### 7. Handle Edge Cases

**All Items Poorly Defined**:

If the backlog-analyzer agent reports all items have low quality scores (<5), still present the top 2-3 but emphasize the need for clarification:

```
Warning: Most backlog items lack sufficient detail.

The recommendations below are based on priority and size only. Each item needs
clarification before implementation can begin. Consider adding:
- Clear problem or feature descriptions
- Reproduction steps (for bugs) or use cases (for features)
- Explicit acceptance criteria

Recommended next step: Clarify the highest-priority items before starting work.
```

**Missing Priority or Size Fields**:

```
Warning: Some items are missing priority or size fields.

Recommendations for those items will fall back to definition quality and date.
Consider setting priority and size in each issue file's meta tags.
```

## Requirements Mapping

This skill implements the following specification requirements:

- **REQ-CR-5**: Read and analyze file-based issue tracking from `.lore/work/issues/`
- **REQ-F-11**: Analyze backlog items and recommend based on priority, size, and definition quality
- **REQ-F-12**: Identify items that are well-defined (clear description and acceptance criteria)
- **REQ-F-13**: Present 2-3 options when asked for recommendations, with rationale
- **REQ-NF-3**: Handle missing custom fields gracefully (warn, don't fail)
- **REQ-NF-4**: Explain reasoning when making recommendations

## Anti-Patterns to Avoid

- **Don't query GitHub**: This skill reads local files only
- **Don't exclude wontfix**: These items are deferred, not done; the agent needs them
- **Don't fail silently**: If meta tags are missing, warn and continue with defaults
- **Don't bypass the agent**: Always use backlog-analyzer for quality assessment
- **Don't truncate agent output**: Present the agent's full analysis to maintain transparency

## Related Skills

- `/compass-rose:next-item` - Get an immediate recommendation for next work item (faster, simpler)
- `/compass-rose:add-item` - Create a new issue file
- `/compass-rose:reprioritize` - Codebase-aware priority updates

## Comparison to /compass-rose:next-item

| Aspect | /compass-rose:next-item | /compass-rose:backlog |
|--------|-------------------------|----------------------|
| **Speed** | Fast | Slower |
| **Scope** | Ready items only | All open and wontfix items |
| **Analysis** | Simple priority sort | Deep quality assessment |
| **Output** | Quick recommendation | Comprehensive backlog health report |
| **Use Case** | "What's next?" | "What's the state of my backlog?" |

## References

- **Spec**: REQ-CR-5, REQ-F-11, REQ-F-12, REQ-F-13, REQ-NF-3, REQ-NF-4
- **Agent**: `compass-rose/agents/backlog-analyzer.md` (quality scoring and recommendation)
