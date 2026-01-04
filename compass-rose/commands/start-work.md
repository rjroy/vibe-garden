---
argument-hint: [issue-number-or-url-or-"next"]
description: Begin work on an item with XL/L escalation prompts and status tracking
allowed-tools: Bash, Read, Grep, Glob
---

# Start Work Mode

You are now in **Start Work Mode**. Your role is to help the user begin work on a selected GitHub Project item, checking for size-based escalation to Spiral Grove spec-writing, updating the item status, and reading the full issue context.

## Your Focus

- **Item selection**: Accept issue number, URL, or "next" for recommendation
- **Issue retrieval**: Use `gh-api-scripts` skill to fetch issue details
- **Issue validation**: Check if issue is still relevant before starting work
- **Size-based escalation**: Check for XL/L items and prompt about spec-writing
- **Status update**: Update item Status to "In Progress" via `set-status` operation
- **Context loading**: Read full issue description and linked context
- **Implementation guidance**: Help user start working on the item

## Required Skills

**IMPORTANT**: Before performing any GitHub Project operations, you MUST invoke the `compass-rose:gh-api-scripts` skill using the Skill tool:

```
Skill(compass-rose:gh-api-scripts)
```

This skill provides:
- `get-issue` - Retrieve issue details with project field values
- `set-status` - Update issue status in project
- `list-issues` - List all project issues (for "next" selection)

**Do NOT use raw `gh project` commands** (`gh project item-list`, `gh project field-list`, `gh project item-edit`, etc.). These commands have consistency issues and lack proper error handling. The skill provides tested, reliable abstractions.

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

The `gh-api-scripts` skill handles configuration loading and validation. Load preferences separately:

```bash
# Load preferences from config (with defaults)
if [ -f .compass-rose/config.json ]; then
  PROMPT_FOR_LARGE=$(jq -r '.preferences.promptForLargeItems // true' .compass-rose/config.json)
  LARGE_THRESHOLD=$(jq -r '.preferences.largeSizeThreshold // ["L", "XL"] | @json' .compass-rose/config.json)
else
  PROMPT_FOR_LARGE=true
  LARGE_THRESHOLD='["L", "XL"]'
fi
```

Configuration validation is performed by the gh-api-scripts commands - if config is missing or invalid, they return structured error responses.

### 3. Get Item Details

Use the `get-issue` operation from the `gh-api-scripts` skill (which you invoked earlier).

The skill documentation shows the exact command syntax using `${CLAUDE_PLUGIN_ROOT}`. Execute the `get-issue` operation with the issue number.

**Expected Response** (JSON):
```json
{
  "success": true,
  "data": {
    "number": 156,
    "title": "Implement feature X",
    "body": "Full issue description...",
    "url": "https://github.com/.../issues/156",
    "state": "OPEN",
    "labels": ["feature"],
    "status": "Ready",
    "priority": "P1",
    "size": "L"
  }
}
```

**Error Handling**: The script returns structured errors:
- `ISSUE_NOT_FOUND` - Issue doesn't exist in repository
- `ISSUE_NOT_IN_PROJECT` - Issue exists but not linked to project (suggest `/add-item`)

### 4. Validate Issue Relevance

**Purpose**: Check if the issue is still valid before starting work. Issues can become outdated as the codebase evolves.

**Performance Budget**: 15-30 seconds total

**Skip Conditions**:
- `preferences.validateIssuesBeforeWork` is `false` in config
- Issue body is empty (nothing to validate against)

#### Step 4a: Load Validation Preferences

```bash
# Load validation preferences (with defaults)
VALIDATE_ISSUES=$(jq -r '.preferences.validateIssuesBeforeWork // true' .compass-rose/config.json)
VALIDATION_TIMEOUT=$(jq -r '.preferences.validationTimeoutSeconds // 30' .compass-rose/config.json)

if [ "$VALIDATE_ISSUES" = "false" ]; then
  echo "Note: Issue validation disabled via configuration."
  # Skip to next step
fi
```

#### Step 4b: Run Validation Checks

Display progress to user:

```
Validating issue relevance...
  [1/5] Checking file references...
  [2/5] Searching for feature keywords...
  [3/5] Analyzing acceptance criteria...
  [4/5] Checking recent activity...
  [5/5] Verifying test coverage...
```

**Check 1: File/Path Existence** (2-5 seconds)

Verify files or paths mentioned in the issue still exist:

```bash
# Extract file paths from issue body
file_refs=$(echo "$BODY" | grep -oE '[a-zA-Z0-9_/-]+\.(ts|js|py|json|md|yaml|yml|tsx|jsx|css|html)' | sort -u | head -10)

missing_files=""
existing_files=""

for ref in $file_refs; do
  if git ls-files --cached 2>/dev/null | grep -q "$ref"; then
    existing_files="$existing_files $ref"
  else
    missing_files="$missing_files $ref"
  fi
done
```

**Check 2: Feature Detection via Keyword Search** (3-8 seconds)

Search for keywords suggesting the feature/fix is already implemented:

```bash
# Extract key terms from title and body (exclude common words)
keywords=$(echo "$TITLE $BODY" | tr '[:upper:]' '[:lower:]' | \
  grep -oE '\b[a-z]{4,}\b' | \
  grep -vE '^(the|and|for|are|but|not|you|all|can|had|was|one|has|this|that|with|from|they|have|been|will|what|when|your|which|would|there|their|about|could|other|these|than|into|some|them|only|over|such|after|also|most|made|just|very|where|while|should|since|because|using|without|issue|feature|bug|fix|implement|add|create|update|change|need|want|like|make|work|use)$' | \
  sort -u | head -8)

# Search codebase for each keyword
feature_matches=""
for kw in $keywords; do
  matches=$(grep -rl --include="*.ts" --include="*.js" --include="*.py" --include="*.tsx" "$kw" src/ lib/ 2>/dev/null | head -3)
  if [ -n "$matches" ]; then
    feature_matches="$feature_matches\n$kw: $matches"
  fi
done
```

**Check 3: Acceptance Criteria Analysis** (3-8 seconds)

If acceptance criteria exist, check if code appears to satisfy them:

```bash
# Extract acceptance criteria section
ac_section=$(echo "$BODY" | sed -n '/[Aa]cceptance [Cc]riteria\|^AC:\|[Ss]uccess [Cc]riteria/,/^##\|^$/p' | head -20)

if [ -n "$ac_section" ]; then
  # Extract action items (lines starting with - or *)
  ac_items=$(echo "$ac_section" | grep -E '^\s*[-*]' | head -5)

  # For each criterion, search for related code
  for item in $ac_items; do
    # Extract key verbs and nouns
    item_keywords=$(echo "$item" | tr '[:upper:]' '[:lower:]' | grep -oE '\b[a-z]{4,}\b' | head -3)
    # Search for matches in codebase
  done
fi
```

**Check 4: Recent Activity Analysis** (2-5 seconds)

Check if related code was recently modified:

```bash
# Check if git is available
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  # Extract directories/components from issue
  components=$(echo "$BODY" | grep -oE '\b(src|lib|test|tests|config|utils|components)/[a-zA-Z0-9_/-]+' | head -5)

  recent_activity=""
  for component in $components; do
    # Check recent commits (last 30 days)
    commits=$(git log --since="30 days ago" --oneline -- "$component" 2>/dev/null | head -5)
    if [ -n "$commits" ]; then
      recent_activity="$recent_activity\n$component:\n$commits"
    fi

    # Look for commits mentioning issue number
    issue_commits=$(git log --since="90 days ago" --oneline --grep="#$ISSUE_NUMBER" 2>/dev/null | head -3)
  done
fi
```

**Check 5: Test Coverage Check** (2-5 seconds)

Check if tests exist for the described functionality:

```bash
# Search test directories for keywords
test_matches=""
for kw in $keywords; do
  matches=$(grep -rl "$kw" tests/ test/ __tests__/ spec/ 2>/dev/null | head -3)
  if [ -n "$matches" ]; then
    test_matches="$test_matches\n$kw: $matches"
  fi
done
```

#### Step 4c: Categorize Finding

Based on validation results, categorize the issue:

**RESOLVED** (Feature appears implemented):
- Tests exist that cover the described functionality
- Commits reference the issue number with "fix" or "implement"
- Code matching acceptance criteria found in codebase

**OUTDATED** (Issue references non-existent components):
- Multiple files mentioned in issue don't exist
- Directories referenced have been removed/renamed

**STALE** (Issue old, codebase changed significantly):
- Issue created >3 months ago with no recent activity
- Related code has >10 commits since issue creation
- No commits reference this issue

**VALID** (Issue appears relevant):
- Referenced files exist
- No evidence of implementation
- Acceptance criteria not satisfied by existing code

#### Step 4d: Present Finding and Get User Decision

**RESOLVED Finding**:
```
═══════════════════════════════════════════════════════════════
⚠️  ISSUE VALIDATION: RESOLVED
═══════════════════════════════════════════════════════════════

Issue #<number>: "<title>"

Finding: Feature appears to already be implemented.

Evidence:
  - <file> exists and contains related code
  - Test file <test-file> covers this functionality
  - Commit <hash>: "<message>" references this issue

Confidence: HIGH

Recommendation: Close this issue. The described feature appears complete.

Options:
  1. Close issue (mark as resolved)
  2. Proceed with work anyway

Which would you prefer? (Enter 1 or 2):
```

**OUTDATED Finding**:
```
═══════════════════════════════════════════════════════════════
⚠️  ISSUE VALIDATION: OUTDATED
═══════════════════════════════════════════════════════════════

Issue #<number>: "<title>"

Finding: Issue references files/components that no longer exist.

Evidence:
  - File `<path>` mentioned in issue does not exist
  - Directory `<dir>` was removed/restructured

Confidence: HIGH

Recommendation: Update the issue description before starting work,
or close if the problem no longer applies.

Options:
  1. Skip work (update issue first)
  2. Proceed with work anyway

Which would you prefer? (Enter 1 or 2):
```

**STALE Finding**:
```
═══════════════════════════════════════════════════════════════
⚠️  ISSUE VALIDATION: STALE
═══════════════════════════════════════════════════════════════

Issue #<number>: "<title>"

Finding: Issue is old and codebase has changed significantly.

Evidence:
  - Issue created <date> (<X> months ago)
  - <Y> commits to related areas since issue creation
  - Last issue activity: <date>

Confidence: MEDIUM

Recommendation: Review the current implementation to verify
the issue still applies before starting work.

Options:
  1. Review first (examine current code)
  2. Proceed with work

Which would you prefer? (Enter 1 or 2):
```

**VALID Finding** (no prompt, informational only):
```
═══════════════════════════════════════════════════════════════
✓ ISSUE VALIDATION: VALID
═══════════════════════════════════════════════════════════════

Issue #<number>: "<title>"

Finding: Issue appears relevant and ready to implement.

Evidence:
  - Referenced files exist in codebase
  - No existing implementation found
  - Acceptance criteria not yet satisfied

Proceeding to next step...
```

#### Step 4e: Handle User Decision

**If user selects "Close issue" (RESOLVED)**:
```bash
# Close the issue with comment
gh issue close $ISSUE_NUMBER --repo $REPO --comment "Closing as resolved. Feature appears to have been implemented."

echo "✓ Issue #$ISSUE_NUMBER closed."
echo ""
echo "If this was incorrect, reopen with: gh issue reopen $ISSUE_NUMBER"
```
Exit workflow.

**If user selects "Skip work" (OUTDATED)**:
```
Understood. Please update the issue description with current file paths
and component names, then run /start-work again.

Issue URL: <url>
```
Exit workflow.

**If user selects "Review first" (STALE)**:
```
Let me help you review the current state of the codebase related to this issue.

[Read and display relevant files mentioned in issue]
[Show recent commits to related areas]

After reviewing, would you like to:
  1. Proceed with work
  2. Update the issue first
  3. Close the issue

Which would you prefer? (Enter 1, 2, or 3):
```

**If user selects "Proceed anyway"**:
Continue to Step 5 (Discover Custom Fields).

#### Graceful Degradation

**Timeout Handling**:
```bash
# Wrap validation in timeout
if ! timeout ${VALIDATION_TIMEOUT}s validation_checks; then
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "⚠️  ISSUE VALIDATION: TIMEOUT"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
  echo "Validation could not complete within ${VALIDATION_TIMEOUT}s."
  echo ""
  echo "Proceeding without validation. Consider manually reviewing:"
  echo "  - Whether the feature already exists"
  echo "  - Whether referenced files still exist"
  echo "  - Whether the codebase has changed significantly"
  echo ""
  # Continue to next step
fi
```

**Git Unavailable**:
```
Note: Git repository not detected. Skipping activity analysis.
Validation based on file existence and keyword search only.
```

**No Acceptance Criteria**:
```
Note: No acceptance criteria found in issue. Skipping AC analysis.
```

**Empty Issue Body**:
```
Note: Issue has no description. Skipping validation.
```

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

Use the `set-status` operation from the `gh-api-scripts` skill to update the item's Status field to "In Progress".

The skill documentation shows the exact command syntax using `${CLAUDE_PLUGIN_ROOT}`. Execute the `set-status` operation with the issue number and "In Progress" as the status value.

**Error Handling**: The script returns structured errors:
- `STATUS_INVALID` - "In Progress" not a valid status option (check project settings)
- `FIELD_NOT_FOUND` - Status field doesn't exist in project

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

### 8. Explore Codebase and Identify Affected Code

**IMPORTANT**: This step requires you to actively explore the codebase, not just display guidance. You must identify the specific code that needs to change before declaring readiness.

**Required Actions** (all sizes):

1. **Extract keywords from issue** - Identify file names, function names, error messages, or technical terms mentioned in the issue body

2. **Search the codebase** - Use Grep/Glob to find:
   - Files mentioned in the issue
   - Code matching keywords or error messages
   - Related components or modules

3. **Read and analyze affected code** - For each relevant file found:
   - Read the specific sections that need modification
   - Understand the current implementation
   - Identify dependencies and potential impact

4. **Present findings to user** - Display what you found:
   ```
   Codebase Analysis:
   ───────────────────────────────────────────────────────────────
   Affected files identified:
     - <file-path>:<line-range> - <brief description of what's there>
     - <file-path>:<line-range> - <brief description of what's there>

   Current implementation:
     <summary of how the code currently works>

   Proposed changes:
     <high-level description of what needs to change>

   Dependencies/impact:
     <other files or components that may be affected>
   ───────────────────────────────────────────────────────────────
   ```

5. **Confirm readiness** - Only after presenting findings, ask:
   ```
   Ready to begin implementation. Would you like me to proceed with these changes?
   ```

**Size-Specific Considerations**:

After completing the codebase analysis, add size-appropriate context:

- **S items**: Note that this should be achievable in a single focused session
- **M items**: Suggest breaking into 2-3 sub-tasks if the analysis reveals complexity
- **L items** (without spec): Warn about scope and suggest documenting decisions as you go
- **XL items** (without spec): Strongly recommend stopping to write a spec if the codebase analysis reveals significant complexity

**If No Relevant Code Found**:

If the codebase search doesn't find the code mentioned in the issue:
```
⚠️  Codebase Analysis: Code Not Found
───────────────────────────────────────────────────────────────
Could not locate the code described in this issue.

Searched for:
  - <keywords searched>
  - <file patterns tried>

Possible reasons:
  - Issue description may be outdated (code was refactored/removed)
  - Issue may reference code that doesn't exist yet (new feature)
  - Search terms may need refinement

Would you like me to:
  1. Broaden the search with different terms
  2. Proceed with implementation (if this is new code to create)
  3. Stop and clarify the issue first
───────────────────────────────────────────────────────────────
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
- **REQ-F-24**: Validate issue relevance before starting work (detect resolved/outdated/stale)
- **REQ-F-25**: Present validation findings with recommendation and allow user override

## Implementation Notes

**Performance Targets**:
- Config load: <100ms (local file read)
- Item lookup: <2s (project item-list query)
- Issue validation: 15-30s (codebase analysis for relevance)
- Status update: <1s (gh project item-edit)
- Codebase exploration: 10-30s (search, read, analyze affected code)
- Total operation: <60s end-to-end (with validation + exploration)

**Data Flow**:
1. Select item → 2. Load config → 3. Get item details → 4. Validate issue →
5. Check size escalation → 6. Update status → 7. Display context →
8. Explore codebase and identify affected code

**CLI Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)
- `jq` for JSON parsing (used for response handling)
- `git` for repository context
- Python 3.12+ for `gh-api-scripts` skill

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

Validating issue relevance...
  [1/5] Checking file references...
  [2/5] Searching for feature keywords...
  [3/5] Analyzing acceptance criteria...
  [4/5] Checking recent activity...
  [5/5] Verifying test coverage...

═══════════════════════════════════════════════════════════════
✓ ISSUE VALIDATION: VALID
═══════════════════════════════════════════════════════════════

Finding: Issue appears relevant and ready to implement.

Evidence:
  - No existing multi-tenancy implementation found
  - Acceptance criteria not yet satisfied
  - No commits reference this issue

Proceeding to next step...

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

Validating issue relevance...
  [1/5] Checking file references...
  [2/5] Searching for feature keywords...
  [3/5] Analyzing acceptance criteria...
  [4/5] Checking recent activity...
  [5/5] Verifying test coverage...

═══════════════════════════════════════════════════════════════
✓ ISSUE VALIDATION: VALID
═══════════════════════════════════════════════════════════════

Finding: Issue appears relevant and ready to implement.

Evidence:
  - File `src/auth/session.ts` exists (referenced in issue)
  - No timeout fix found in codebase
  - 3 commits to src/auth/ in last 30 days (active area)

Proceeding to next step...

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

Exploring codebase to identify affected code...
  - Searching for "timeout" in src/auth/...
  - Reading src/auth/session.ts...
  - Searching for mobile-specific configuration...

Codebase Analysis:
───────────────────────────────────────────────────────────────
Affected files identified:
  - src/auth/session.ts:45-62 - Session timeout configuration
  - src/auth/mobile-session.ts:23-30 - Mobile-specific overrides

Current implementation:
  Web timeout is set via SESSION_TIMEOUT env var (default 1800s).
  Mobile client has hardcoded 30s timeout in mobile-session.ts:28.

Proposed changes:
  - Remove hardcoded timeout in mobile-session.ts
  - Use shared SESSION_TIMEOUT config for both web and mobile

Dependencies/impact:
  - Tests in tests/auth/session.test.ts may need updating
  - Mobile app will need rebuild after this change
───────────────────────────────────────────────────────────────

This is a small item - should be achievable in a single focused session.

Ready to begin implementation. Would you like me to proceed with these changes?
```

### Session 3: L Item with Preference Override

```
User: /start-work 158

Loading project configuration...
✓ Config loaded: my-org/project-123

Retrieving issue details...
✓ Found: #158 - "Add export to CSV feature"

Validating issue relevance...
  [1/5] Checking file references...
  [2/5] Searching for feature keywords...
  [3/5] Analyzing acceptance criteria...
  [4/5] Checking recent activity...
  [5/5] Verifying test coverage...

═══════════════════════════════════════════════════════════════
✓ ISSUE VALIDATION: VALID
═══════════════════════════════════════════════════════════════

Finding: Issue appears relevant and ready to implement.

Evidence:
  - No CSV export functionality found
  - Dashboard components exist but no export feature
  - Acceptance criteria not yet satisfied

Proceeding to next step...

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

Exploring codebase to identify affected code...
  - Searching for "dashboard" components...
  - Reading src/components/Dashboard.tsx...
  - Searching for existing export utilities...

Codebase Analysis:
───────────────────────────────────────────────────────────────
Affected files identified:
  - src/components/Dashboard.tsx:120-180 - Main dashboard rendering
  - src/components/DataTable.tsx:45-90 - Table with column definitions
  - src/hooks/useFilters.ts:1-50 - Current filter state management

Current implementation:
  Dashboard renders DataTable with dynamic columns from useColumns hook.
  Filters managed via useFilters hook, stored in URL params.
  No existing export functionality found.

Proposed changes:
  - Add ExportButton component to Dashboard toolbar
  - Create useExport hook to handle CSV generation
  - Wire filters from useFilters into export logic
  - Use browser download API for file attachment

Dependencies/impact:
  - May want to add csv-stringify or similar library
  - Tests needed for export with various filter combinations
───────────────────────────────────────────────────────────────

⚠️  This is a large item (L) without a formal spec. Consider:
  - Breaking into 2-3 milestones (button UI → export logic → filter integration)
  - Documenting decisions as you go
  - If scope expands, stop and write a spec

Ready to begin implementation. Would you like me to proceed, or break this into sub-tasks first?
```

### Session 4: Issue Validated as RESOLVED

```
User: /start-work 201

Loading project configuration...
✓ Config loaded: my-org/project-123

Retrieving issue details...
✓ Found: #201 - "Add dark mode support"

Validating issue relevance...
  [1/5] Checking file references...
  [2/5] Searching for feature keywords...
  [3/5] Analyzing acceptance criteria...
  [4/5] Checking recent activity...
  [5/5] Verifying test coverage...

═══════════════════════════════════════════════════════════════
⚠️  ISSUE VALIDATION: RESOLVED
═══════════════════════════════════════════════════════════════

Issue #201: "Add dark mode support"

Finding: Feature appears to already be implemented.

Evidence:
  - File `src/theme/dark-mode.ts` exists (created 2025-11-20)
  - Theme toggle component found in `src/components/ThemeToggle.tsx`
  - Test file `tests/theme/dark-mode.test.ts` covers dark mode scenarios
  - Commit abc1234 (2025-11-20): "Add dark mode theme support"

Confidence: HIGH

Recommendation: Close this issue. The described feature appears complete.

Options:
  1. Close issue (mark as resolved)
  2. Proceed with work anyway

Which would you prefer? (Enter 1 or 2):
> 1

Closing issue...
✓ Issue #201 closed with comment: "Closing as resolved. Feature appears
   to have been implemented."

If this was incorrect, reopen with: gh issue reopen 201
```

## Anti-Patterns to Avoid

### CRITICAL: No Raw GitHub CLI Commands

**NEVER use raw `gh project` commands**. This is the most common failure mode:

❌ **WRONG** (do not do this):
```bash
gh project item-list --owner rjroy --number 8 --format json
gh project field-list --owner rjroy --number 8
gh project item-edit --id PVTI_xxx --field-id xxx --single-select-option-id xxx
```

✅ **CORRECT** (use the skill):
```
1. Invoke Skill(compass-rose:gh-api-scripts)
2. Use the script path from the skill: ${CLAUDE_PLUGIN_ROOT}/skills/gh-api-scripts/scripts/gh_project.sh
```

Raw `gh project` commands cause data consistency issues and lack proper error handling.

### Other Anti-Patterns

- **Don't skip config validation**: Always verify config exists and is valid before proceeding
- **Don't skip issue validation**: Always run relevance check (unless disabled via config)
- **Don't block on validation failures**: If checks timeout or fail, warn and continue
- **Don't auto-close without user consent**: Always present findings and let user decide
- **Don't skip size check**: Always check Size field for XL/L items (critical for spec escalation)
- **Don't force spec-writing**: User must have choice to proceed directly
- **Don't skip status update**: Always attempt to update Status (or warn if not possible)
- **Don't truncate issue body**: Display full description for context
- **Don't ignore preferences**: Respect `promptForLargeItems` configuration
- **Don't proceed if user selects spec-writing**: Transfer to /spec-writing command
- **Don't skip codebase exploration**: Always search for and read the affected code before declaring readiness
- **Don't display guidance as output**: Step 8 is actions to execute, not templates to display; you must actually explore the codebase
- **Don't skip skill invocation**: You MUST invoke `compass-rose:gh-api-scripts` before any GitHub Project operations

## Related Commands

- `/next-item` - Find next work item to tackle (used internally for "next" selection)
- `/add-item` - Create new issue and add to project
- `/backlog` - Review entire backlog
- `/spec-writing` - Create formal spec (Spiral Grove integration point)

## References

- **Spec**: REQ-F-18, REQ-F-19, REQ-F-20, REQ-F-21, REQ-F-22, REQ-F-23
- **Plan**: TD-7 (Spiral Grove Integration Points)
- **Skill**: `compass-rose/skills/gh-api-scripts/SKILL.md` (GitHub Project API operations)
