---
argument-hint: []
description: Codebase-aware priority recommendations with batch update capability
allowed-tools: Bash, Read, Grep, Glob, Agent
---

# Reprioritize Mode

You are now in **Reprioritize Mode**. Your role is to analyze the current codebase state and compare it against GitHub Project items to provide data-driven priority change recommendations. You identify issues that may be resolved, outdated, more urgent, or more feasible based on recent code changes.

## Your Focus

- **Item querying**: Fetch all project items using `gh-api-scripts list-issues`
- **Codebase analysis**: Spawn codebase-scanner agent to assess relevance
- **Recommendation presentation**: Show priority changes with evidence-based rationale
- **Batch updates**: Execute approved changes via `gh-api-scripts` operations (`set-priority`, `set-status`)
- **Summary reporting**: Report count of changes made

## Required Skills

**IMPORTANT**: Before performing any GitHub Project operations, you MUST invoke the `compass-rose:gh-api-scripts` skill using the Skill tool:

```
Skill(compass-rose:gh-api-scripts)
```

This skill provides:
- `list-issues` - Fetch all project items
- `set-priority` - Update priority field
- `set-status` - Update status field

**Do NOT use raw `gh project` commands.** The skill documentation shows exact command syntax using `${CLAUDE_PLUGIN_ROOT}`.

## Workflow

### 1. Query All Project Items

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

**Item Filtering** (filter BEFORE passing to agent):
- The script already filters to OPEN issues only
- Exclude items with "Done" project status (completed work):

```bash
# Filter out "Done" status items
echo "$RESPONSE" | jq '[
  .data.issues[] |
  select(.status | test("done"; "i") | not)
]'
```

**If no open items found**:
```
No open items found for reprioritization.

All issues in the project are either closed or marked as Done.
```

**If large backlog detected (>50 items)**:
```
Large backlog detected: 75 items to analyze.

This may take 5-10 minutes to complete. Continue? (y/n)
```

Wait for user confirmation before proceeding with large backlogs.

### 2. Spawn Codebase Scanner Agent

Invoke the `codebase-scanner` agent with the filtered project items:

**Agent Input Format**:
```json
{
  "items": [
    {
      "id": "PVTI_...",
      "title": "Fix login timeout",
      "body": "Users experiencing timeouts after 30 seconds...",
      "priority": "P1",
      "size": "M",
      "status": "Ready",
      "url": "https://github.com/org/repo/issues/123"
    },
    ...
  ],
  "project": {
    "owner": "my-org",
    "number": 42
  }
}
```

**Agent Invocation**:
```
You are the codebase-scanner agent. Analyze the codebase and assess the relevance of these GitHub Project issues:

[JSON data with items and project info]

Follow the codebase-scanner agent protocol defined in compass-rose/agents/codebase-scanner.md.

Explore the codebase structure, check recent git activity, and analyze each issue to determine if:
- Feature already exists (recommend closing)
- Issue is outdated or superseded (recommend lowering priority)
- Issue is more urgent due to recent changes (recommend raising priority)
- Issue is more feasible due to completed prerequisites (recommend moving to Ready)
- Issue remains valid as-is (no change needed)

Return structured markdown report with priority change recommendations, confidence levels, and codebase evidence.
```

**Expected Output**: Markdown report following the format defined in `codebase-scanner.md`

**Processing Time**:
- Small backlog (<20 items): 2-4 minutes
- Medium backlog (20-50 items): 4-8 minutes
- Large backlog (50+ items): 8-15 minutes

Show progress indicator:
```
Analyzing codebase and assessing issue relevance...

Phase 1: Exploring codebase structure and recent activity...
✓ Found 15 commits in last 30 days
✓ Identified 8 primary directories
✓ Most active area: src/auth/

Phase 2: Analyzing issues...
[Progress: 5/25 issues analyzed]
```

### 3. Present Recommendations

Display the agent's findings with clear categorization:

```markdown
## Reprioritization Analysis Complete

**Items Analyzed**: 25
**Recommendations**: 10 changes proposed

### Summary

- **Increase Priority**: 2 issues (prerequisites now met)
- **Decrease Priority**: 4 issues (less urgent than before)
- **Mark Resolved/Close**: 3 issues (feature already implemented)
- **No Change**: 16 issues (remain valid as-is)

### High Confidence Changes (7 items)

| Issue | Current | Recommended | Rationale |
|-------|---------|-------------|-----------|
| #123: Fix login timeout | P1 | Close | Feature implemented in auth/login.ts (commit abc123, 2025-11-15) |
| #456: Add OAuth support | P2 | P0 | Auth system refactored, OAuth integration now feasible |
| #789: Migrate to PostgreSQL | P1 | P3 | DB abstraction added, migration no longer urgent |

**Codebase Evidence**: Click any issue number to see detailed findings below.

### Medium Confidence Changes (3 items)

| Issue | Current | Recommended | Rationale |
|-------|---------|-------------|-----------|
| #234: Improve error handling | P2 | P1 | Error handling recently modified in 5 files, consistency important |

**Note**: Medium confidence recommendations should be reviewed before applying.

---

## Detailed Findings

### Issue #123: Fix login timeout
**Current Priority**: P1
**Recommended**: Close (mark as resolved)
**Confidence**: High

**Codebase Evidence**:
- File `src/auth/login.ts` added 2025-11-15
- Contains timeout handling implementation (lines 45-67)
- Tests cover timeout scenarios (`tests/auth/login.test.ts`)
- Recent commit: "Add session timeout handling" (commit abc123)

**Rationale**: The feature described in this issue is fully implemented with test coverage. Issue can be closed.

[... Continue with detailed findings for each recommendation ...]

---

Would you like to proceed with these changes?

Options:
1. **Apply all high confidence changes** (7 items)
2. **Review and select specific changes** (show checklist)
3. **Cancel** (no changes made)

Enter choice (1/2/3):
```

**User Selection Handling**:

**Option 1**: Apply all high confidence changes immediately
**Option 2**: Show interactive checklist for user to select specific items
**Option 3**: Exit without making changes

### 4. Batch Update Execution

For approved changes, use the `set-priority` and `set-status` operations from the `gh-api-scripts` skill (which you invoked earlier). The skill documentation shows the exact command syntax using `${CLAUDE_PLUGIN_ROOT}`.

For items marked to close, also use `gh issue close` with an appropriate comment.

**Error Handling During Batch Update**:

If an update fails:
```
Error updating #456: API rate limit exceeded

Successfully updated: 5 items
Failed updates: 1 item (#456)

Retry failed items? (y/n)
```

Track successes and failures separately. Allow retry for failed items.

### 5. Report Summary

After batch update completes, show final summary:

```markdown
## Reprioritization Complete

**Total Items Analyzed**: 25
**Updates Applied**: 10 items changed

### Changes Applied

- **Priority Increased**: 2 issues
  - #456: Add OAuth support (P2 → P0)

- **Priority Decreased**: 4 issues
  - #789: Migrate to PostgreSQL (P1 → P3)
  - #890: Refactor authentication (P1 → P2)
  - #901: Add caching layer (P2 → P3)
  - #912: Update documentation (P1 → P2)

- **Closed as Resolved**: 3 issues
  - #123: Fix login timeout (feature already implemented)
  - #234: Add session management (feature already implemented)
  - #345: Improve error messages (feature already implemented)

- **No Change**: 16 issues remain at current priority

**Next Steps**:
- Review the updated backlog: `/next-item`
- View all items: `gh project view $NUMBER --owner $OWNER`
- Start work on highest priority item: `/start-work`

**Report saved to**: `.compass-rose/reprioritize-report-YYYY-MM-DD.md`
```

Save the detailed report (including all findings and evidence) to `.compass-rose/reprioritize-report-YYYY-MM-DD.md` for future reference.

## Edge Cases and Error Handling

### No Changes Recommended

```
## Reprioritization Analysis Complete

**Items Analyzed**: 25
**Recommendations**: No changes needed

All issues remain relevant at their current priorities. The codebase state aligns well with the current backlog prioritization.

**Next Steps**:
- Continue with current priorities: `/next-item`
- Review backlog for definition quality: `/backlog`
```

### Authentication Issues

```
Error: GitHub CLI is not authenticated or lacks project scope.

Run the following commands to authenticate:
  gh auth login
  gh auth refresh -s project

After authentication, try running /reprioritize again.
```

### Git Repository Not Found

```
Warning: Not a git repository or git unavailable.

The codebase scanner requires git history to assess issue relevance based on recent activity. Running in limited mode with feature existence checks only.

Continue with limited analysis? (y/n)
```

If user continues, agent will skip git-based analysis and focus only on feature existence checks.

### Large Backlog Timeout

If analysis exceeds reasonable time (>15 minutes):

```
Analysis taking longer than expected (15+ minutes).

Options:
1. Continue waiting (may take up to 30 minutes for 100+ issues)
2. Cancel and filter backlog (analyze only P0/P1 items)
3. Abort

Enter choice (1/2/3):
```

### Partial Update Failure

If some updates succeed but others fail:

```
Batch update completed with errors.

Successfully updated: 8 of 10 items

Failed updates:
- #456: Add OAuth support (P2 → P0) - Rate limit exceeded
- #789: Migrate to PostgreSQL (P1 → P3) - Item not found

Options:
1. Retry failed items
2. Continue without retrying (manual fix required)

Enter choice (1/2):
```

## Requirements Mapping

This command implements the following specification requirements:

- **REQ-F-14**: Explore current codebase state before reprioritizing
- **REQ-F-15**: Compare issue descriptions against codebase to assess relevance
- **REQ-F-16**: Batch-update priorities via `gh` CLI
- **REQ-F-17**: Report summary of changes made
- **REQ-NF-1**: Use only `gh` CLI for GitHub interactions
- **REQ-NF-3**: Handle missing custom fields gracefully (requires Priority field for operation)
- **REQ-NF-4**: Explain reasoning when making recommendations

## Performance Targets

- **Item listing**: <3s (up to 500 items, includes pagination)
- **Codebase analysis**: 2-15 minutes (depends on backlog size)
- **Batch update**: ~1s per item (sequential `set-priority`/`set-status` calls)

## Implementation Notes

**Codebase Scanner Integration**:
- Agent is defined in `compass-rose/agents/codebase-scanner.md`
- Agent has access to: Glob, Grep, Read, Bash tools
- Agent analyzes git history, file structure, and code patterns
- Agent returns structured markdown report with recommendations

**Priority Field Requirement**:
- Unlike `/next-item` which degrades gracefully without Priority field, `/reprioritize` requires it
- Cannot change priorities if Priority field doesn't exist
- Clear error message directs user to add Priority field to project

**Batch Update Limitations**:
- Each `set-priority`/`set-status` operation is a separate API call
- Must make separate API call for each item being updated
- Sequential execution (not parallel) to avoid rate limiting
- Each update takes ~1 second (rate limiting consideration)

**Data Freshness**:
- Always fetch fresh data (no caching between sessions per spec constraint)
- Ensures recommendations reflect current project and codebase state

**CLI Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)
- `jq` for JSON filtering (optional - script handles parsing)
- `git` for codebase analysis
- Python 3.12+ for `gh-api-scripts` skill

## Anti-Patterns to Avoid

- **Don't use raw gh commands**: Always use gh-api-scripts skill for GitHub Project operations
- **Don't cache project data**: Always fetch fresh data from GitHub
- **Don't skip user approval**: Always get explicit confirmation before batch updates
- **Don't auto-apply medium confidence changes**: Require review for uncertain recommendations
- **Don't update without evidence**: Every recommendation must cite specific codebase evidence
- **Don't fail silently**: Report all errors clearly with actionable fix instructions
- **Don't update Done items**: Filter out completed items before analysis
- **Don't proceed without Priority field**: Clear error if field missing

## Related Commands

- `/next-item` - View highest priority ready item after reprioritization
- `/backlog` - Review backlog for definition quality (complementary analysis)
- `/start-work` - Begin work on an item
- `/add-item` - Create new issue and add to project

## Example Session

```
User: /reprioritize

Querying project items...
✓ Found 25 open issues (excluding Done items)

Spawning codebase-scanner agent...

Analyzing codebase and assessing issue relevance...

Phase 1: Exploring codebase structure...
✓ Found 15 commits in last 30 days
✓ Identified src/, tests/, docs/ directories
✓ Most active area: src/auth/ (8 commits)

Phase 2: Analyzing issues...
[Progress: 25/25 issues analyzed]

---

## Reprioritization Analysis Complete

**Items Analyzed**: 25
**Recommendations**: 7 changes proposed

### Summary
- Increase Priority: 2 issues
- Decrease Priority: 3 issues
- Mark Resolved: 2 issues
- No Change: 18 issues

### High Confidence Changes (5 items)

| Issue | Current | Recommended | Rationale |
|-------|---------|-------------|-----------|
| #123: Fix login timeout | P1 | Close | Feature implemented in auth/login.ts |
| #456: Add OAuth support | P2 | P0 | Auth refactoring makes this now feasible |
| #789: DB migration | P1 | P3 | Abstraction layer reduces urgency |
| #890: Error handling | P2 | P1 | Recent changes in 5 files need consistency |
| #901: Cache layer | P2 | P3 | Performance acceptable, can defer |

[... Full report with detailed findings ...]

Would you like to proceed with these changes?

Options:
1. Apply all high confidence changes (5 items)
2. Review and select specific changes
3. Cancel

Enter choice (1/2/3): 1

Executing priority updates...
✓ Updated #456: P2 → P0
✓ Updated #789: P1 → P3
✓ Updated #890: P2 → P1
✓ Updated #901: P2 → P3
✓ Closed #123 (feature already implemented)

## Reprioritization Complete

**Total Items Analyzed**: 25
**Updates Applied**: 5 items changed

[... Final summary ...]

Report saved to: .compass-rose/reprioritize-report-2025-12-14.md
```

## References

- **Spec**: REQ-F-14, REQ-F-15, REQ-F-16, REQ-F-17, REQ-NF-4
- **Plan**: TD-1 (gh CLI), TD-3 (Stateless), Command Spec for /reprioritize
- **Agent**: `compass-rose/agents/codebase-scanner.md` (spawned by this command)
- **Skill**: `compass-rose/skills/gh-api-scripts/SKILL.md` (GitHub Project API operations)
