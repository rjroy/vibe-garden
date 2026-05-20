---
name: reprioritize
description: Use when the user asks to "reprioritize", "update priorities", "scan codebase for relevance", or invokes /compass-rose:reprioritize. Scans codebase against local issue files and updates their priority/status meta tags.
allowed-tools: Bash, Read, Glob, Edit, Agent
---

# Reprioritize Mode

You are now in **Reprioritize Mode**. Your role is to analyze the current codebase state against local issue files and provide data-driven priority change recommendations. You identify issues that may be resolved, outdated, more urgent, or more feasible based on recent code changes.

## Your Focus

- **Issue reading**: Load all open issues from `.lore/work/issues/*.html`
- **Codebase analysis**: Spawn `codebase-scanner` agent to assess relevance
- **Recommendation presentation**: Show priority/status changes with evidence-based rationale
- **Meta tag updates**: Apply approved changes directly to the HTML files

## Workflow

### 1. Read All Open Issues

Use Glob to find all HTML files under `.lore/work/issues/`:

```bash
find .lore/work/issues -name "*.html" 2>/dev/null
```

For each file found, use Read to extract the meta tags and body content. The relevant tags are:

```html
<meta name="title" content="...">
<meta name="priority" content="...">
<meta name="size" content="...">
<meta name="status" content="...">
<meta name="date" content="...">
```

Filter to only files where `<meta name="status" content="open">`.

**If no open issues exist**:

```
No open issues found in .lore/work/issues/.

Nothing to reprioritize.
```

Stop here.

**If a large set is detected (>50 open issues)**:

```
Large backlog detected: [N] open issues to analyze.

This may take 5-10 minutes. Continue? (y/n)
```

Wait for confirmation before proceeding.

### 2. Spawn Codebase Scanner Agent

Build a JSON array from the parsed issue files and pass it to the `codebase-scanner` agent:

**Agent Input Format**:
```json
{
  "items": [
    {
      "filepath": ".lore/work/issues/fix-login-timeout.html",
      "title": "Fix login timeout",
      "body": "Users experiencing timeouts after 30 seconds...",
      "priority": "P1",
      "size": "M",
      "status": "open",
      "date": "2026-05-01"
    }
  ]
}
```

**Agent Invocation**:
```
You are the codebase-scanner agent. Analyze the codebase and assess the relevance of these local issues:

[JSON data]

Follow the codebase-scanner agent protocol defined in compass-rose/agents/codebase-scanner.md.

Explore the codebase structure, check recent git activity, and analyze each issue to determine if:
- Feature already exists (recommend status: resolved)
- Issue is outdated or superseded (recommend lowering priority)
- Issue is more urgent due to recent changes (recommend raising priority)
- Issue is more feasible due to completed prerequisites (recommend raising priority or status: ready)
- Issue remains valid as-is (no change)

Return a structured markdown report with recommendations, confidence levels, and codebase evidence.
```

**Expected Output**: Structured markdown report following the format defined in `codebase-scanner.md`.

### 3. Present Recommendations

Display the agent's findings:

```markdown
## Reprioritization Analysis Complete

**Issues Analyzed**: 25
**Recommendations**: 10 changes proposed

### Summary

- **Increase Priority**: 2 issues (prerequisites now met)
- **Decrease Priority**: 4 issues (less urgent than before)
- **Mark Resolved**: 3 issues (feature already implemented)
- **No Change**: 16 issues (remain valid as-is)

### High Confidence Changes (7 items)

| File | Current | Recommended | Rationale |
|------|---------|-------------|-----------|
| fix-login-timeout.html | P1 | resolved | Feature implemented in auth/login.ts (commit abc123, 2025-11-15) |
| add-oauth-support.html | P2 | P0 | Auth system refactored, OAuth integration now feasible |
| migrate-to-postgresql.html | P1 | P3 | DB abstraction added, migration no longer urgent |

### Medium Confidence Changes (3 items)

| File | Current | Recommended | Rationale |
|------|---------|-------------|-----------|
| improve-error-handling.html | P2 | P1 | Error handling recently modified in 5 files, consistency important |

**Note**: Medium confidence recommendations should be reviewed before applying.

---

## Detailed Findings

### fix-login-timeout.html
**Current Priority**: P1
**Recommended**: status → resolved
**Confidence**: High

**Codebase Evidence**:
- File `src/auth/login.ts` added 2025-11-15
- Contains timeout handling implementation (lines 45-67)
- Tests cover timeout scenarios (`tests/auth/login.test.ts`)
- Recent commit: "Add session timeout handling" (commit abc123)

**Rationale**: The feature described in this issue is fully implemented with test coverage.

[... continue for each recommendation ...]

---

Would you like to proceed with these changes?

Options:
1. **Apply all high confidence changes** ([N] items)
2. **Review and select specific changes** (show checklist)
3. **Cancel** (no changes made)

Enter choice (1/2/3):
```

### 4. Apply Updates

For Option 1: apply all high confidence changes.
For Option 2: show a checklist of all recommended changes; apply only the ones the user selects.
For Option 3: exit without changes.

For each approved change, use the Edit tool to update the relevant meta tag in the target HTML file.

**Priority update example** (changing priority to P0 in `fix-login-timeout.html`):

Update the `content` attribute of `<meta name="priority" content="...">` to the new value.

**Status update example** (marking as resolved):

Update the `content` attribute of `<meta name="status" content="open">` to `resolved`.

After applying all changes, show a summary:

```markdown
## Reprioritization Complete

**Issues Analyzed**: 25
**Updates Applied**: 7 items changed

### Changes Applied

- **Priority Increased**: 2 issues
  - add-oauth-support.html (P2 -> P0)

- **Priority Decreased**: 4 issues
  - migrate-to-postgresql.html (P1 -> P3)
  - refactor-authentication.html (P1 -> P2)
  - add-caching-layer.html (P2 -> P3)
  - update-documentation.html (P1 -> P2)

- **Marked Resolved**: 1 issue
  - fix-login-timeout.html

- **No Change**: 18 issues remain at current priority

**Next Steps**:
- View open issues: `/compass-rose:backlog`
```

## Edge Cases

### No Changes Recommended

```
## Reprioritization Analysis Complete

**Issues Analyzed**: 25
**Recommendations**: No changes needed

All issues remain relevant at their current priorities. The codebase state aligns well with the current backlog.

**Next Steps**:
- Continue with current priorities: `/compass-rose:next-item`
- Review backlog for definition quality: `/compass-rose:backlog`
```

### Git Repository Not Found

```
Warning: Not a git repository or git unavailable.

The codebase scanner requires git history to assess issue relevance based on recent activity. Running in limited mode with feature existence checks only.

Continue with limited analysis? (y/n)
```

If the user continues, the agent skips git-based analysis and focuses on feature existence checks only.

## Anti-Patterns to Avoid

- **Don't skip user approval**: Always get explicit confirmation before applying updates
- **Don't auto-apply medium confidence changes**: Require review for uncertain recommendations
- **Don't update without evidence**: Every recommendation must cite specific codebase evidence
- **Don't save a report file**: Present findings inline; no disk artifact
- **Don't use GitHub API**: All reads and writes are local HTML file operations only

## Related Skills

- `/compass-rose:next-item` - View highest priority ready item after reprioritization
- `/compass-rose:backlog` - Review backlog for definition quality
- `/compass-rose:add-item` - Create a new issue file

## Requirements Mapping

- **REQ-CR-6**: Read local issue files, scan codebase, update meta tags after confirmation
