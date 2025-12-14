# Manual Testing Protocol

## Overview

This document provides step-by-step instructions for manually testing all acceptance tests (AT-1 through AT-7) from the Compass Rose Core specification. Each test includes setup instructions, execution steps, expected outcomes, and troubleshooting guidance.

## Prerequisites

Before running any tests, ensure:

1. **GitHub CLI authenticated**:
   ```bash
   gh auth login
   gh auth refresh -s project
   ```

2. **Test repository access**: You have admin access to a test repository with GitHub Projects enabled

3. **Plugin installed**: Compass Rose plugin is available in Claude Code

## Test Project Setup

### Initial Setup

Create a test GitHub Project with the following configuration:

**Project Fields**:

| Field Name | Field Type | Values |
|------------|-----------|--------|
| Status | Single Select | Backlog, Ready, In Progress, Done |
| Priority | Single Select | P0, P1, P2, P3 |
| Size | Single Select | S, M, L, XL |
| Iteration | Single Select | Sprint 1, Sprint 2, Sprint 3 |

**Test Configuration File**:

Create `.compass-rose/config.json` in your test repository:

```json
{
  "project": {
    "owner": "your-org-or-username",
    "number": 123
  }
}
```

Replace `owner` and `number` with your test project details.

---

## AT-1: Config Loading

**Objective**: Verify that Claude can load and query a project using valid configuration.

### Setup

1. Ensure `.compass-rose/config.json` exists with valid project details
2. Project should contain at least 1-2 issues

### Test Steps

1. In Claude Code, ask: "Can you check my compass-rose project?"
2. Or run: `/next-item` command

### Expected Outcome

- Configuration loads without errors
- Claude successfully queries the project
- Claude displays project items (if any exist)
- No authentication errors
- No "configuration not found" errors

### Failure Scenarios

**Configuration not found**:
```
Error: Configuration file not found.
Please create .compass-rose/config.json...
```

**Authentication failure**:
```
Error: GitHub CLI is not authenticated.
Run the following command to authenticate:
  gh auth login
```

**Invalid project**:
```
Error: Could not find project #123 for owner "your-org"
```

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| "Configuration file not found" | Verify `.compass-rose/config.json` exists at repository root |
| "GitHub CLI is not authenticated" | Run `gh auth login` and `gh auth refresh -s project` |
| "Could not find project" | Verify project number in GitHub Projects URL |
| Permission denied | Ensure authenticated user has access to project |

---

## AT-2: Next Item Query

**Objective**: Verify that Claude recommends P0 items before P1 items when querying for next work.

### Setup

1. Create test issues in your project with the following configuration:

**Issue 1**:
- Title: "Fix critical authentication bug"
- Priority: P0
- Status: Ready
- Size: M

**Issue 2**:
- Title: "Update documentation"
- Priority: P1
- Status: Ready
- Size: S

**Issue 3**:
- Title: "Refactor login component"
- Priority: P1
- Status: Ready
- Size: L

**Issue 4**:
- Title: "Explore new framework"
- Priority: P2
- Status: Backlog

### Test Steps

1. Run: `/next-item`
2. Observe the recommended item

### Expected Outcome

- Claude presents a table with top 2-3 Ready items
- **P0 issue appears first** in the recommendations
- P1 issues appear after P0 issue
- P2 Backlog issue does NOT appear (wrong status)
- Rationale explains priority-based sorting
- Response time < 5 seconds

**Example output**:
```
Here are your top ready items:

| Priority | Title | Size | Status |
|----------|-------|------|--------|
| P0 | Fix critical authentication bug | M | Ready |
| P1 | Update documentation | S | Ready |
| P1 | Refactor login component | L | Ready |

Recommendation: Start with "Fix critical authentication bug" (P0 priority, critical)
```

### Failure Scenarios

**P1 item recommended before P0**:
- Priority sorting is broken
- Check field discovery logs

**No items returned**:
- Verify items have "Ready" status
- Check project configuration

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Wrong priority order | Verify Priority field values match exactly: P0, P1, P2, P3 |
| No items shown | Check that at least one item has "Ready" status |
| "Priority field not found" warning | Add Priority field to project |
| Slow response (>10s) | Check network connection to GitHub API |

---

## AT-3: Backlog Review

**Objective**: Verify that Claude can analyze backlog quality and present 2-3 recommendations with rationale.

### Setup

Create 10 backlog items with varying quality levels:

**Well-Defined Items (3)**:

**Issue 5**:
- Title: "Add password reset flow"
- Description: "Users cannot reset passwords if they forget them. Add a password reset flow that sends a secure reset link via email."
- Acceptance Criteria:
  - User can request password reset via email
  - Reset link expires after 1 hour
  - User can set new password using valid link
- Priority: P1
- Size: M
- Status: Ready

**Issue 6**:
- Title: "Fix API timeout on large queries"
- Description: "Dashboard API times out after 30s when querying >1000 records. Reproduce by navigating to /dashboard with admin account. Expected: Query completes in <5s."
- Acceptance Criteria:
  - Queries return in <5s for up to 10,000 records
  - Add pagination if necessary
  - No N+1 query issues
- Priority: P0
- Size: L
- Status: Ready

**Issue 7**:
- Title: "Add user profile photos"
- Description: "Allow users to upload profile photos (PNG/JPG, max 5MB). Display photo in navbar and profile page. Handle missing photos gracefully with default avatar."
- Acceptance Criteria:
  - Upload UI accepts PNG/JPG up to 5MB
  - Photos displayed in navbar and profile
  - Default avatar shown if no photo
- Priority: P2
- Size: S
- Status: Ready

**Vague Items (4)**:

**Issue 8**:
- Title: "Improve performance"
- Description: "The app feels slow"
- Priority: P1
- Size: M
- Status: Backlog

**Issue 9**:
- Title: "Better error handling"
- Description: "Errors should be handled better"
- Priority: P2
- Size: S
- Status: Backlog

**Issue 10**:
- Title: "Make UI prettier"
- Description: "UI needs improvement"
- Priority: P2
- Size: L
- Status: Backlog

**Issue 11**:
- Title: "Fix the bug"
- Description: "There's a bug that needs fixing"
- Priority: P1
- Size: M
- Status: Backlog

**Medium-Quality Items (3)**:

**Issue 12**:
- Title: "Add sorting to user table"
- Description: "Users should be able to sort the user table by name, email, and creation date"
- Priority: P2
- Size: S
- Status: Backlog

**Issue 13**:
- Title: "Cache API responses"
- Description: "Add caching to reduce API calls. Cache should expire after 5 minutes."
- Priority: P1
- Size: M
- Status: Backlog

**Issue 14**:
- Title: "Add search to dashboard"
- Description: "Dashboard needs a search feature so users can find items quickly"
- Priority: P1
- Size: L
- Status: Backlog

### Test Steps

1. Run: `/backlog`
2. Wait for agent analysis to complete (~10-15 seconds)
3. Review recommendations and rationale

### Expected Outcome

- Command completes in 10-20 seconds
- Claude presents **2-3 recommendations** (not all 10 items)
- Recommendations include well-defined items (Issues 5, 6, 7)
- Each recommendation includes:
  - Item title and priority
  - Quality score (0-10 scale)
  - Rationale explaining why it's recommended
- Backlog health summary provided
- Poorly-defined items identified (Issues 8, 9, 10, 11)
- Suggestions for improving vague items

**Example output structure**:
```
=== TOP RECOMMENDATIONS ===

1. Fix API timeout on large queries (P0, Size: L)
   Quality Score: 9/10
   Rationale: Well-defined problem with clear repro steps, specific
   acceptance criteria, and measurable performance target.

2. Add password reset flow (P1, Size: M)
   Quality Score: 8/10
   Rationale: Complete description with security considerations and
   testable acceptance criteria.

3. Add user profile photos (P2, Size: S)
   Quality Score: 8/10
   Rationale: Clear requirements, size constraints specified, edge
   cases addressed.

=== BACKLOG HEALTH ===
- Total items: 10
- Well-defined (8-10): 3 items
- Defined (5-7): 3 items
- Vague (2-4): 4 items

=== ITEMS NEEDING CLARIFICATION ===
- "Improve performance" - No specific metrics or problem area
- "Better error handling" - No examples or failure scenarios
- "Make UI prettier" - No design guidance or target components
- "Fix the bug" - No description of the bug
```

### Failure Scenarios

**No recommendations provided**:
- Agent may have failed
- Check that items have descriptions

**All 10 items listed**:
- Agent is not prioritizing
- Check scoring algorithm

**Vague items recommended**:
- Scoring is broken
- Review agent prompt

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Agent times out | Reduce number of items, check Claude Code connection |
| No quality scores shown | Agent invocation failed, check logs |
| Recommendations include vague items | Review scoring criteria, verify acceptance criteria exist |
| Takes >30 seconds | Normal for large backlogs (>20 items) |

---

## AT-4: Priority Update

**Objective**: Verify that Claude can batch-update priorities via `gh` CLI and report changes.

### Setup

1. Ensure Priority field exists in project
2. Create test items with potentially outdated priorities:

**Issue 15**:
- Title: "Add dark mode"
- Description: "Add dark mode theme support"
- Priority: P0
- Status: Backlog
- (This should probably be P2, not P0)

**Issue 16**:
- Title: "Fix SQL injection vulnerability"
- Description: "User input is not sanitized in /api/search endpoint"
- Priority: P2
- Status: Backlog
- (This should be P0, not P2)

**Issue 17**:
- Title: "Update README"
- Description: "README is out of date"
- Priority: P1
- Status: Backlog
- (This should stay P1 or become P2)

### Test Steps

1. Run: `/reprioritize`
2. Wait for codebase analysis (5-15 minutes depending on repository size)
3. Review recommendations
4. When prompted, approve recommended changes
5. Observe batch update execution

### Expected Outcome

- Agent analyzes codebase and compares against issues
- Recommendations presented with:
  - Current priority
  - Recommended priority
  - Confidence level (high/medium)
  - Evidence from codebase (commits, files, patterns)
- High-confidence and medium-confidence changes shown separately
- User is prompted: "Apply these changes? (yes/no)"
- Upon approval, batch updates execute via `gh project item-edit`
- Summary report shows:
  - Number of items updated
  - Number of items unchanged
  - Any failures
- Expected changes:
  - Issue 15 (dark mode): P0 → P2 (nice-to-have feature)
  - Issue 16 (SQL injection): P2 → P0 (security vulnerability)
  - Issue 17 (README): Possibly P1 → P2 or no change

**Example output**:
```
=== HIGH CONFIDENCE RECOMMENDATIONS ===

1. Fix SQL injection vulnerability
   Current: P2 → Recommended: P0
   Evidence: Security vulnerability in /api/search endpoint.
   No sanitization found in codebase. Critical security issue.

2. Add dark mode
   Current: P0 → Recommended: P2
   Evidence: No references to dark mode in current codebase.
   Not blocking any other work. Can be deferred.

=== MEDIUM CONFIDENCE RECOMMENDATIONS ===

3. Update README
   Current: P1 → Recommended: P2
   Evidence: README was updated 2 days ago. Not critical.

Apply these changes? (yes/no): yes

Updating priorities...
✓ Issue #16: P2 → P0
✓ Issue #15: P0 → P2
✓ Issue #17: P1 → P2

Summary: 3 of 3 issues updated successfully.
```

### Failure Scenarios

**Priority field not found**:
```
Error: Priority field not found in project.
Cannot update priorities. Please add a Priority field to your project.
```

**Agent provides no recommendations**:
- Codebase analysis found no clear evidence
- All priorities are already accurate

**Batch update fails**:
```
✓ Issue #16: P2 → P0
✗ Issue #15: Failed to update (rate limit)
✓ Issue #17: P1 → P2

Summary: 2 of 3 issues updated. 1 failed.
```

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| "Priority field not found" | Add Priority field to project |
| Agent takes >20 minutes | Normal for large codebases (>10k files) |
| No recommendations | Priorities may already be accurate |
| Rate limit errors | Wait 1 minute between updates, reduce batch size |
| Update failures | Check GitHub CLI authentication and permissions |

---

## AT-5: XL Escalation

**Objective**: Verify that Claude prompts about spec-writing before starting work on XL-sized items.

### Setup

Create an XL-sized item:

**Issue 18**:
- Title: "Redesign user authentication system"
- Description: "Replace current password-only auth with OAuth2, SAML, and MFA support"
- Priority: P1
- Size: **XL**
- Status: Ready

### Test Steps

1. Run: `/start-work 18` (or `/start-work next` if this is the top item)
2. Observe prompt before work begins

### Expected Outcome

- Claude detects Size = XL
- Claude presents a prompt **before starting implementation**:

```
This item is sized XL, which typically indicates a large, complex change.

For items of this size, we recommend starting with a specification:
- Define the problem and requirements
- Design the technical architecture
- Break down into smaller, manageable tasks

Would you like to:
1. Write a specification first (recommended for XL items)
2. Start implementation directly

Your choice: _
```

- If user chooses "1", Claude invokes `/spec-writing` (Spiral Grove)
- If user chooses "2", Claude proceeds with implementation
- Status is updated to "In Progress" (if user proceeds)

### Failure Scenarios

**No prompt shown**:
- Size field not detected
- Escalation logic not triggered

**Prompt shown for S/M items**:
- Escalation threshold set too low

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| No XL prompt shown | Verify Size field exists and value is "XL" |
| Prompt shown for all items | Check escalation configuration |
| Spiral Grove not invoked | Verify Spiral Grove plugin is installed |
| Status not updated | Check `gh project item-edit` permissions |

---

## AT-6: Missing Fields

**Objective**: Verify that Claude handles missing custom fields gracefully by warning the user but continuing with available data.

### Setup

1. Create a test project **without a Priority field**
2. Include only: Status, Size, Iteration
3. Create 3-4 test issues with various statuses

### Test Steps

1. Run: `/next-item`
2. Observe warning message
3. Verify command still works

### Expected Outcome

- Claude detects missing Priority field
- Warning message displayed:

```
Warning: Priority field not found in project.
All items will be treated as equal priority.

Available fields: Status, Size, Iteration

To enable priority-based sorting, add a "Priority" field to your project.
```

- Command **continues execution** (does not fail)
- Items sorted by creation date or Status (fallback behavior)
- Results still displayed

### Alternative Tests

Test missing fields for other commands:

**Missing Size field + `/start-work`**:
- No XL escalation prompt (can't detect size)
- Warning: "Size field not found. XL escalation disabled."
- Implementation proceeds normally

**Missing Status field + `/next-item`**:
- Falls back to project column position
- Warning: "Status field not found. Using column position."

### Failure Scenarios

**Command fails entirely**:
```
Error: Required field 'Priority' not found. Cannot continue.
```
- This is incorrect behavior - commands should degrade gracefully

**No warning shown**:
- User may not realize functionality is limited

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Command fails with missing field | Check field discovery logic |
| No warning message | Verify warning is emitted before main logic |
| Unexpected behavior | Review fallback logic for each command |
| "Field not found" for existing fields | Check field name matching patterns (case-insensitive) |

---

## AT-7: Issue Creation

**Objective**: Verify that Claude can create a repository issue and link it to the project with custom fields.

### Setup

1. Ensure configuration is valid
2. Ensure project has custom fields: Priority, Size, Status

### Test Steps

1. Ask Claude: "I found a bug in the login page - password reset doesn't send emails"
2. Alternatively, run: `/add-item`
3. Follow interactive prompts (if any)

### Expected Outcome

- Claude creates a **repository issue** (not a draft item)
- Issue is linked to the configured project
- Custom fields are set via `gh project item-edit`:
  - Priority (e.g., P1)
  - Size (e.g., M)
  - Status (e.g., Backlog or Ready)
- Issue has a clear title and description
- Success message shows:
  - Issue number
  - Project link
  - Fields that were set

**Example output**:
```
Created issue #19: Password reset emails not sending

Repository: https://github.com/your-org/your-repo/issues/19
Project: https://github.com/orgs/your-org/projects/123

Fields set:
✓ Priority: P1
✓ Size: M
✓ Status: Backlog
```

### Verification

1. Navigate to the issue URL
2. Verify issue is visible in repository issues
3. Navigate to project board
4. Verify issue appears in correct Status column
5. Verify custom fields are set (Priority, Size)

### Failure Scenarios

**Issue created but not linked to project**:
```
✓ Created issue #19
✗ Failed to add to project (permission denied)
```

**Issue created but fields not set**:
```
✓ Created issue #19
✓ Added to project
✗ Failed to set Priority field (field not found)
✓ Set Size: M
✓ Set Status: Backlog
```

**Draft item created instead of issue**:
- Verify issue is in repository issues (not just project)
- Check GitHub API calls

### Troubleshooting

| Symptom | Solution |
|---------|----------|
| Issue created but not in project | Check `gh project item-add` permissions |
| Fields not set | Verify field names match project configuration |
| Draft item instead of issue | Review `gh issue create` vs `gh project item-create` |
| "Permission denied" | Ensure authenticated user can create issues and edit project |

---

## Smoke Test Suite

Quick validation that all core functionality works:

```bash
# 1. Verify config loads
Ask: "Check my compass-rose project"
Expected: Project data loads without errors

# 2. Verify next item query
/next-item
Expected: Top 2-3 ready items displayed, sorted by priority

# 3. Verify issue creation
Ask: "Add a bug: Login button doesn't work on mobile"
Expected: Issue created and linked to project

# 4. Verify backlog analysis
/backlog
Expected: Recommendations with quality scores

# 5. Verify start-work
/start-work next
Expected: Status updated to In Progress, XL prompt if applicable
```

Run this suite after any significant changes to verify no regressions.

---

## Test Data Cleanup

After testing, clean up test data:

1. **Close test issues**:
   ```bash
   gh issue close 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
   ```

2. **Archive project** (optional):
   - Navigate to project settings
   - Select "Close project"

3. **Delete test repository** (optional):
   - Only if created specifically for testing
   - Navigate to repository settings
   - Select "Delete this repository"

---

## Common Test Failures

### Authentication Issues

**Symptom**: "gh: command not found" or "Not authenticated"

**Solution**:
```bash
# Install GitHub CLI
brew install gh   # macOS
apt install gh    # Linux

# Authenticate
gh auth login
gh auth refresh -s project
```

### Field Discovery Issues

**Symptom**: "Priority field not found" when field exists

**Solution**:
- Verify field name matches patterns (case-insensitive): "priority", "p0-p3", "severity"
- Check field type: must be Single Select or Text
- Try exact match: rename field to "Priority"

### Rate Limiting

**Symptom**: "API rate limit exceeded" during batch updates

**Solution**:
- Wait 1 minute between large batch operations
- Reduce batch size (update 10 items at a time)
- Check rate limit status: `gh api rate_limit`

### Permission Denied

**Symptom**: "Permission denied" when creating issues or updating fields

**Solution**:
- Verify authenticated user is member of organization
- Check project permissions (must be admin or write)
- Re-authenticate: `gh auth refresh -s project`

---

## Test Reporting Template

Use this template to report test results:

```markdown
## Test Report: AT-X

**Date**: YYYY-MM-DD
**Tester**: Your Name
**Environment**: [Production | Staging | Local]

### Setup
- [ ] Configuration file created
- [ ] Test project configured
- [ ] Test data created
- [ ] GitHub CLI authenticated

### Test Execution
- [ ] Test steps completed
- [ ] Expected outcome observed
- [ ] No unexpected errors

### Results
**Status**: [PASS | FAIL | BLOCKED]

**Notes**:
[Any observations, deviations, or issues encountered]

### Evidence
[Screenshots, logs, or command output]
```

---

## Next Steps

After completing manual testing:

1. Document any bugs found in GitHub issues
2. Update acceptance tests if behavior differs from spec
3. Create automated tests for regression prevention
4. Update CLAUDE.md if user-facing behavior changed
