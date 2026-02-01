# Compass Rose

<img src="logo.webp" align="right" width="128" height="128" alt="Compass Rose Logo">

A Claude Code plugin for project management using GitHub Projects.

## Overview

Compass Rose provides skills and agents to help users and Claude manage a project together. It uses GitHub's project functionality (`gh project ...`) to track work items.

## Purpose

Compass Rose complements [Lore Development](../lore-development/) (the specification and planning plugin) by providing a place for:

- **Tasks/Bugs**: Small, actionable items like "the input box is too big" or "when refresh is hit during a refresh the server crashes"
- **Feature Ideas**: Larger questions that may eventually need a full spec, like "add functionality for different rule-based RPG systems into the engine"

While Lore Development handles specification and planning (Spec → Plan), Compass Rose manages the backlog of work items that feed into that process. After planning, Claude Code handles implementation natively.

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- A GitHub Project linked to your repository

## Configuration

Each repository using Compass Rose must define which GitHub Project it uses. Configuration is stored in `.compass-rose/config.json` at the repository root.

### Setup

Create `.compass-rose/config.json` with your project details:

```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  }
}
```

**Values for `owner_type`**:
- `"organization"` - For projects owned by GitHub organizations
- `"user"` - For projects owned by personal GitHub accounts

**Finding your project number:**

The project number appears in the GitHub Projects URL:
```
https://github.com/orgs/<owner>/projects/<number>
```

For example, if your project URL is:
```
https://github.com/orgs/my-org/projects/42
```

Your configuration would be:
```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 42
  }
}
```

### Required Fields

- `project.owner` - GitHub organization or username that owns the project
- `project.owner_type` - Either `"organization"` or `"user"` (determines API query format)
- `project.number` - Project number (visible in project URL)

### Optional Fields

You can customize behavior with optional preferences:

```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  },
  "preferences": {
    "promptForLargeItems": true,
    "largeSizeThreshold": ["L", "XL"]
  }
}
```

**Preferences:**

- `promptForLargeItems` (default: `true`) - Whether to prompt before starting L-sized items, suggesting spec-writing via Lore Development
- `largeSizeThreshold` (default: `["L", "XL"]`) - Array of size values that trigger spec-writing prompts

### Example Configurations

**Minimal configuration** (personal project):
```json
{
  "project": {
    "owner": "my-username",
    "owner_type": "user",
    "number": 7
  }
}
```

**Minimal configuration** (organization project):
```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  }
}
```

**Full configuration** (with preferences):
```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  },
  "preferences": {
    "promptForLargeItems": true,
    "largeSizeThreshold": ["L", "XL"]
  }
}
```

### Migrating Existing Configurations

If you have an existing `.compass-rose/config.json` from before v0.2.0, you need to add the `owner_type` field:

**Before** (legacy format):
```json
{
  "project": {
    "owner": "my-org",
    "number": 123
  }
}
```

**After** (current format):
```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  }
}
```

**How to determine your owner_type**:
- Check your project URL:
  - `github.com/orgs/<owner>/projects/<n>` → Use `"organization"`
  - `github.com/users/<owner>/projects/<n>` → Use `"user"`

The `owner_type` field is required because GitHub's GraphQL API uses different query roots for user and organization projects.

### Error Messages

If configuration is missing or invalid, Compass Rose will provide clear instructions:

**Missing configuration file:**
```
Error: Configuration file not found.

Please create .compass-rose/config.json with your project details:

{
  "project": {
    "owner": "<org-or-username>",
    "owner_type": "<user|organization>",
    "number": <project-number>
  }
}

Find your project number in the project URL:
https://github.com/orgs/<owner>/projects/<number>
```

**Invalid configuration:**
```
Error: Invalid configuration.

Fields 'project.owner', 'project.owner_type', and 'project.number' are required.

Example:
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  }
}
```

**Invalid owner_type:**
```
Error: Invalid owner_type.

owner_type must be "user" or "organization", got: "invalid"

- Use "organization" for org-owned projects (URL: github.com/orgs/<owner>/projects/<n>)
- Use "user" for personal projects (URL: github.com/users/<owner>/projects/<n>)
```

**Project not found:**
```
Error: Project not found.

Verify that:
1. Project owner is correct: <owner>
2. Project number is correct: <number>
3. You have access to the project
4. You are authenticated: gh auth status
```

## Installation

```bash
/plugin install compass-rose@vibe-garden
```

## Quick Start

Get started with Compass Rose in 3 steps:

1. **Install the GitHub CLI and authenticate**:
   ```bash
   gh auth login
   gh auth refresh -s project
   ```

2. **Create configuration file** at repository root (`.compass-rose/config.json`):
   ```json
   {
     "project": {
       "owner": "my-org",
       "owner_type": "organization",
       "number": 123
     }
   }
   ```

   > **Note**: Use `"owner_type": "user"` for personal account projects.

3. **Start using skills**:
   ```bash
   /compass-rose:next-item        # Find what to work on next
   /compass-rose:start-work next  # Begin work on recommended item
   ```

## Skills Reference

### `/compass-rose:next-item`

Get the highest-priority ready item to work on next.

**Usage**:
```bash
/compass-rose:next-item
```

**What it does**:
- Loads project configuration and discovers custom fields
- Queries all items with "Ready" status (or similar)
- Sorts by Priority field (P0 > P1 > P2 > P3), then creation date
- Displays top 2-3 options in table format with rationale

**Example output**:
```
| # | Title                      | Priority | Size | Status |
|---|----------------------------|----------|------|--------|
| 1 | Fix login timeout bug      | P0       | S    | Ready  |
| 2 | Add user preferences page  | P1       | M    | Ready  |
| 3 | Improve error messages     | P1       | S    | Ready  |

Recommendation: Item #1 (P0 priority, small scope, ready for work)

Rationale: This is the highest priority item in the backlog. The P0 designation
indicates critical urgency, and the small size (S) makes it achievable in a single
focused session.
```

**When to use**: You want a quick answer for "what should I work on next?"

---

### `/compass-rose:add-item`

Create a new repository issue and add it to the project with custom fields.

**Usage**:
```bash
/compass-rose:add-item
```

**What it does**:
- Interactively prompts for title, description, priority, size, and status
- Creates repository issue via `gh issue create`
- Links issue to project via `gh project item-add`
- Sets custom fields via `gh project item-edit`

**Example session**:
```
What is the title of the new item?
> Fix authentication timeout on mobile

Provide a description (optional):
> Users on mobile devices are experiencing session timeouts after 30 seconds.
>
> Acceptance criteria:
> - Mobile timeout matches web (30 minutes)
> - Existing sessions are not affected

Select priority (1-4) or press Enter for P2 (default):
> 1

Select size (1-4) or press Enter for M (default):
> 1

Select initial status (1-3) or press Enter for "Ready" (default):
> 1

✓ Item created successfully!

Issue: #156 - Fix authentication timeout on mobile
Link: https://github.com/my-org/my-repo/issues/156

Fields set:
- Priority: P0
- Size: S
- Status: Ready
```

**When to use**: You need to add a new bug, task, or feature idea to the backlog.

---

### `/compass-rose:start-work`

Begin work on an item with size-based escalation prompts and status tracking.

**Usage**:
```bash
/compass-rose:start-work <issue-number>       # Start work on issue #123
/compass-rose:start-work <issue-url>          # Start work using full URL
/compass-rose:start-work next                 # Start work on highest-priority ready item
```

**What it does**:
- Retrieves full issue details and project metadata
- Checks item size (XL/L) and prompts about spec-writing if appropriate
- Updates item status to "In progress"
- Displays full issue description and acceptance criteria
- Provides implementation guidance based on item size

**Example session (small item)**:
```
User: /compass-rose:start-work next

Loading project configuration...
✓ Config loaded: my-org/project-123

Finding highest-priority ready item...
Selected: #142 - "Fix login timeout bug"

Size: S (no escalation needed)

Updating status...
✓ Status updated to 'In progress'

═══════════════════════════════════════════════════════════════
Issue #142: Fix login timeout bug
═══════════════════════════════════════════════════════════════

Priority: P0
Size: S
Status: In progress

Description:
───────────────────────────────────────────────────────────────
Users on mobile devices are experiencing session timeouts after
30 seconds of inactivity.

Acceptance Criteria:
- Mobile timeout matches web (30 minutes)
- Existing sessions are not affected
───────────────────────────────────────────────────────────────

Implementation Guidance:
This is a small item (estimated < 4 hours). Recommended approach:

1. Read the issue carefully and identify affected code
2. Make focused changes with minimal scope
3. Test locally to verify acceptance criteria
4. Create a PR when complete
```

**Example session (XL item)**:
```
User: /compass-rose:start-work 156

═══════════════════════════════════════════════════════════════
Large Item Detected: XL
═══════════════════════════════════════════════════════════════

This item is sized XL, which typically requires detailed planning and
specification before implementation.

XL items benefit from formal specification before implementation:
1. /lore-development:specify - Define requirements and success criteria
2. /lore-development:prep-plan - Plan technical approach

After planning, proceed with implementation directly.

Options:
  1. Write spec first (/lore-development:specify) - RECOMMENDED for XL items
  2. Start implementation directly

Which approach would you prefer? (Enter 1 or 2):
```

**When to use**: You're ready to start implementing an item.

**Configuration**: Disable L-item prompts in `.compass-rose/config.json`:
```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  },
  "preferences": {
    "promptForLargeItems": false
  }
}
```

---

### `/compass-rose:backlog`

Review entire backlog with quality analysis and recommendations.

**Usage**:
```bash
/compass-rose:backlog
```

**What it does**:
- Queries all non-Done items from the project
- Spawns backlog-analyzer agent to assess definition quality
- Scores each item on clarity, completeness, and acceptance criteria
- Recommends top 2-3 items to work on based on priority, size, and quality
- Reports backlog health summary

**Example output**:
```
# Backlog Analysis Results

Items Analyzed: 15 total
Well-Defined Items: 4 items with score 8-10
Items Needing Clarification: 6 items with score <5

## Top Recommendations

### Recommendation 1: Fix login timeout on Chrome (#42)

Priority: P0 | Size: S | Definition Quality: Well-Defined (9/10)

Rationale:
- Highest priority (P0) issue affecting 15% of users
- Small scope (S) makes it achievable in single session
- Excellent definition with clear repro steps and acceptance criteria

Definition Assessment:
- Clarity (3/3): Clear problem with specific browser versions
- Completeness (3/3): Includes repro steps, environment, impact data
- Acceptance Criteria (3/4): Explicit success conditions present

Link: https://github.com/my-org/my-repo/issues/42

---

## Backlog Health Summary

Priority Distribution: 3 P0, 7 P1, 4 P2, 1 P3
Size Distribution: 5 S, 6 M, 3 L, 1 XL
Definition Quality:
- Well-Defined (8-10): 4 items
- Defined (5-7): 5 items
- Vague (2-4): 4 items
- Poorly Defined (0-1): 2 items

Observations:
- P0 items are generally well-defined
- Many P1 features lack explicit acceptance criteria
- XL item should be broken down or escalated to Lore Development spec

## Items Needing Clarification

1. Improve error messages (#51) - Score: 3/10
   - Missing: Which errors? What should they say?
   - Suggest: List specific error scenarios with improvements
```

**When to use**:
- You want to understand overall backlog health
- You need recommendations based on definition quality, not just priority
- You want to identify poorly-defined items for cleanup
- You're planning a sprint and want multiple options

**Comparison to `/compass-rose:next-item`**:

| Aspect | /compass-rose:next-item | /compass-rose:backlog |
|--------|------------|----------|
| Speed | Fast (<3s) | Slower (~15s) |
| Scope | Ready items only | All non-Done items |
| Analysis | Simple priority sort | Deep quality assessment |
| Output | Quick recommendation | Comprehensive health report |

---

### `/compass-rose:reprioritize`

Codebase-aware priority recommendations with batch update capability.

**Usage**:
```bash
/compass-rose:reprioritize
```

**What it does**:
- Queries all non-Done project items
- Spawns codebase-scanner agent to analyze codebase state
- Compares issue descriptions against current code
- Identifies issues that are resolved, outdated, more urgent, or more feasible
- Presents priority change recommendations with codebase evidence
- Batch-updates priorities after user approval

**Example output**:
```
## Reprioritization Analysis Complete

Items Analyzed: 25
Recommendations: 7 changes proposed

### Summary
- Increase Priority: 2 issues (prerequisites now met)
- Decrease Priority: 3 issues (less urgent than before)
- Mark Resolved/Close: 2 issues (feature already implemented)
- No Change: 18 issues (remain valid as-is)

### High Confidence Changes (5 items)

| Issue | Current | Recommended | Rationale |
|-------|---------|-------------|-----------|
| #123: Fix login timeout | P1 | Close | Feature implemented in auth/login.ts (commit abc123) |
| #456: Add OAuth support | P2 | P0 | Auth system refactored, OAuth now feasible |
| #789: Migrate to PostgreSQL | P1 | P3 | DB abstraction added, no longer urgent |

Codebase Evidence: Click any issue number to see detailed findings below.

---

## Detailed Findings

### Issue #123: Fix login timeout
Current Priority: P1
Recommended: Close (mark as resolved)
Confidence: High

Codebase Evidence:
- File `src/auth/login.ts` added 2025-11-15
- Contains timeout handling implementation (lines 45-67)
- Tests cover timeout scenarios (`tests/auth/login.test.ts`)
- Recent commit: "Add session timeout handling" (commit abc123)

Rationale: The feature described in this issue is fully implemented with
test coverage. Issue can be closed.

---

Would you like to proceed with these changes?

Options:
1. Apply all high confidence changes (5 items)
2. Review and select specific changes
3. Cancel

Enter choice (1/2/3):
```

**When to use**:
- Your codebase has evolved and the backlog may be out of sync
- You want data-driven priority updates based on actual code state
- You suspect some issues may already be resolved
- Recent development has changed feasibility of certain features

**Performance**: Analysis takes 2-15 minutes depending on backlog size.

**Report**: Full analysis saved to `.compass-rose/reprioritize-report-YYYY-MM-DD.md`

---

## Workflow Examples

### Typical Daily Workflow

```bash
# 1. Find what to work on next
/compass-rose:next-item

# 2. Start work on recommended item
/compass-rose:start-work next

# 3. Implement the feature/fix

# 4. Create PR and mark as Done in GitHub Projects UI
```

### Backlog Review and Triage

```bash
# 1. Review entire backlog health
/compass-rose:backlog

# 2. Add new item from user feedback
/compass-rose:add-item

# 3. Start work on highest priority well-defined item
/compass-rose:start-work next
```

### Periodic Backlog Maintenance

```bash
# 1. Analyze codebase and get priority recommendations
/compass-rose:reprioritize

# 2. Review recommendations and apply changes

# 3. Check updated backlog
/compass-rose:next-item
```

### Large Item Escalation to Lore Development

```bash
# 1. Attempt to start work on large item
/compass-rose:start-work 156

# 2. Compass Rose detects XL size and prompts:
#    "Write spec first (/lore-development:specify) - RECOMMENDED for XL items"

# 3. User chooses Option 1 (Write spec first)
#    -> Transfers to /lore-development:specify

# 4. Follow Lore Development workflow:
#    /lore-development:specify -> /lore-development:prep-plan -> implementation
```

## Troubleshooting

### Configuration Issues

**Problem**: `Error: Configuration file not found`

**Solution**: Create `.compass-rose/config.json` at repository root:
```json
{
  "project": {
    "owner": "my-org",
    "owner_type": "organization",
    "number": 123
  }
}
```

Find your project number in the GitHub Projects URL:
```
https://github.com/orgs/<owner>/projects/<number>
                                           ^^^^^^
```

---

**Problem**: `Error: Invalid configuration`

**Solution**: Ensure all required fields are present:
```json
{
  "project": {
    "owner": "my-org",           // Required: GitHub org or username
    "owner_type": "organization", // Required: "user" or "organization"
    "number": 123                 // Required: Project number (not ID)
  }
}
```

---

**Problem**: `Error: Project not found`

**Solution**: Verify:
1. Project owner is correct in config
2. Project number is correct (check GitHub Projects URL)
3. You have access to the project
4. You are authenticated: `gh auth status`

---

### Authentication Issues

**Problem**: `Error: GitHub CLI is not authenticated`

**Solution**:
```bash
# Authenticate with GitHub
gh auth login

# Add project scope (required for project commands)
gh auth refresh -s project

# Verify authentication
gh auth status
```

---

**Problem**: Commands fail with "insufficient scopes" or "unauthorized"

**Solution**: Refresh authentication with project scope:
```bash
gh auth refresh -s project
```

---

### Field Detection Issues

**Problem**: `Warning: Priority field not found in project`

**Impact**:
- `/compass-rose:next-item`: Falls back to creation date sorting
- `/compass-rose:backlog`: Recommendations based on size and quality only
- `/compass-rose:reprioritize`: Skill requires Priority field and will not run

**Solution**: Add a "Priority" field to your GitHub Project with options like P0, P1, P2, P3.

---

**Problem**: `Note: Status field not available`

**Impact**:
- Cannot filter by Ready status
- Cannot auto-update to "In progress"
- Manual status management required

**Solution**: Add a "Status" field to your GitHub Project with options like Ready, In progress, Done.

---

### Item Issues

**Problem**: `Error: Issue #123 not found in project`

**Solution**: Add the issue to the project:
```bash
/compass-rose:add-item
# Or manually add via GitHub Projects web UI
```

---

**Problem**: `No items found with "Ready" status`

**Solution**: Check available statuses and update items:
```
Available statuses: To Do, In progress, Done

Would you like to analyze "To Do" items instead?
```

Either update items to "Ready" status or analyze a different status.

---

### Performance Issues

**Problem**: `/compass-rose:backlog` or `/compass-rose:reprioritize` taking too long

**Context**: Large backlogs (50+ items) can take 5-15 minutes to analyze.

**Solutions**:
1. **For `/compass-rose:backlog`**: Use `/compass-rose:next-item` for quick recommendations
2. **For `/compass-rose:reprioritize`**: Filter backlog to only P0/P1 items before running
3. **General**: Archive or close Done items to reduce backlog size

---

### Missing Dependencies

**Problem**: Commands fail with `jq: command not found`

**Solution**: Install `jq` for JSON parsing:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt install jq

# Arch Linux
sudo pacman -S jq
```

---

**Problem**: `git: command not found` (for `/reprioritize`)

**Solution**: Install git:
```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Arch Linux
sudo pacman -S git
```

---

### Batch Update Failures

**Problem**: `/compass-rose:reprioritize` reports partial update failures

**Example**:
```
Successfully updated: 8 of 10 items

Failed updates:
- #456: Add OAuth support (P2 → P0) - Rate limit exceeded
```

**Solutions**:
1. **Rate limiting**: Wait a few minutes and retry failed items
2. **Item not found**: Verify issue still exists and is linked to project
3. **Insufficient permissions**: Check write access to project

**Recovery**: Failed items can be manually updated via GitHub Projects web UI.

## Status

**v1.2.0** - Converted commands to skills architecture for automatic discovery.

**v1.1.3** - Previous release with command-based interface.

**v0.1.0** - Initial project setup.
