# Compass Rose Plugin

**Last Generated**: 2025-12-14T00:00:00Z

## Purpose

A Claude Code plugin for project management using GitHub Projects. Provides commands and agents for managing backlog items (bugs, tasks, feature ideas) and deciding what to work on next. Complements Spiral Grove by handling work item triage and escalating large items to structured development.

## Quick Start

1. Create `.compass-rose/config.json` at repository root:
```json
{
  "project": {
    "owner": "your-org-or-username",
    "number": 123
  }
}
```

2. Authenticate with GitHub CLI:
```bash
gh auth login
gh auth refresh -s project
```

3. Use commands to manage your backlog (see Commands section below)

## Commands

### `/add-item` - Create New Work Item

Creates a repository issue and adds it to the GitHub Project with custom fields.

**What it does**:
- Interactively prompts for title, description, priority, size, status
- Discovers available custom fields at runtime (no hardcoded field names)
- Creates repository issue (not draft item)
- Links issue to project
- Sets custom fields via `gh project item-edit`
- Warns if selecting XL size (prompts about spec-writing)

**Key behaviors**:
- Gracefully handles missing fields (warns, continues with available fields)
- Always creates repository issues (per spec constraint)
- Sequential field updates (gh CLI limitation: one field per call)

**Example usage**:
```
/add-item

[Interactive prompts guide you through creation]
```

### `/next-item` - Get Next Work Item

Recommends highest-priority ready item with rationale, using lightweight codebase signals as a tiebreaker.

**What it does**:
- Queries items with "Ready" status (or similar)
- Sorts by Priority (P0 > P1 > P2 > P3)
- Uses codebase signals as secondary tiebreaker (within same priority)
- Shows top 2-3 options in table format with codebase relevance
- Explains why top item is recommended

**Key behaviors**:
- Fast (<8s typical, includes 2-5s for codebase analysis)
- Runs lightweight git heuristics on top 5 candidates
- Degrades gracefully if git unavailable or Priority field missing
- Codebase signals: recent file activity, file existence, related directory commits

**When to use**: Quick "what should I work on now?" query

**Example usage**:
```
/next-item
```

### `/backlog` - Comprehensive Backlog Analysis

Reviews all non-Done items and analyzes quality to recommend best options.

**What it does**:
- Fetches all active items (excludes Done status)
- Spawns `backlog-analyzer` agent to assess definition quality
- Scores each item on clarity, completeness, acceptance criteria (0-10 scale)
- Recommends top 2-3 items based on priority + size + quality
- Reports backlog health summary
- Lists poorly-defined items needing clarification

**Key behaviors**:
- Slower (~10-15s) due to quality analysis
- Uses agent for scoring (0-3 clarity, 0-3 completeness, 0-4 acceptance criteria)
- Transparent rationale for each recommendation
- Identifies items needing improvement

**When to use**: Understanding backlog health, finding well-defined work, planning sprint

**Example usage**:
```
/backlog
```

### `/reprioritize` - Codebase-Aware Priority Updates

Analyzes codebase to recommend priority changes based on current state.

**What it does**:
- Queries all non-Done project items
- Spawns `codebase-scanner` agent to assess issue relevance
- Compares issue descriptions against actual codebase
- Recommends priority changes with confidence levels
- Identifies resolved issues (feature already exists)
- Identifies more urgent issues (prerequisites now met)
- Presents high/medium confidence changes separately
- Batch-updates approved changes via `gh project item-edit`

**Key behaviors**:
- Time-intensive (5-15 minutes for large backlogs)
- Requires Priority field (fails if missing)
- Evidence-based recommendations (cites commits, files, code patterns)
- User approval required before batch updates
- Sequential updates (~1s per item due to rate limiting)

**When to use**: After major refactors, quarterly backlog cleanup, when priorities feel stale

**Example usage**:
```
/reprioritize

[Agent analyzes codebase for 10-15 minutes]
[Presents recommendations with evidence]
[User approves changes]
[Batch updates executed]
```

### `/start-work` - Begin Implementation

Starts work on an item with issue validation, XL/L escalation checks, and status tracking.

**What it does**:
- Accepts issue number, URL, or "next" for recommendation
- Loads item details from project and repository
- **Validates issue relevance** (15-30s) before starting:
  - Checks if files referenced in issue exist
  - Searches for keywords suggesting feature is implemented
  - Analyzes if acceptance criteria are satisfied
  - Checks recent activity in related code areas
  - Presents findings (RESOLVED/OUTDATED/STALE/VALID) with recommendation
- Checks Size field for escalation:
  - **XL items**: Always prompts about spec-writing (recommended)
  - **L items**: Prompts if `preferences.promptForLargeItems` is true (default)
  - **S/M items**: No prompt, proceed directly
- Offers choice: "Write spec first" or "Start implementation directly"
- If user chooses spec-writing, invokes `/spec-writing` (Spiral Grove)
- Updates Status to "In Progress"
- Displays full issue description with acceptance criteria
- Provides size-appropriate implementation guidance

**Key behaviors**:
- Issue validation catches resolved/outdated issues before wasting time
- Validation findings show evidence and let user decide (never auto-closes)
- Can disable validation via `preferences.validateIssuesBeforeWork: false`
- Spiral Grove integration point (XL/L → spec-writing prompt)
- User retains control (can always proceed without spec)
- Status update via `gh project item-edit`
- Different guidance for S/M/L/XL items

**When to use**: Beginning implementation of any work item

**Example usage**:
```
/start-work 156
/start-work https://github.com/org/repo/issues/156
/start-work next
```

## Agents

### `backlog-analyzer`

**Invoked by**: `/backlog` command

**Purpose**: Assess definition quality of backlog items and recommend best options

**Scoring methodology**:
- Clarity (0-3): Problem/request clarity, context, examples
- Completeness (0-3): Repro steps, environment, impact, edge cases
- Acceptance Criteria (0-4): Specific, testable, covers edge cases
- Total Score: 0-10 (8-10 = well-defined, 5-7 = defined, 2-4 = vague, 0-1 = poorly defined)

**Recommendation algorithm**:
- Priority weight: P0=100, P1=75, P2=50, P3=25
- Size weight: S=10, M=8, L=5, XL=0
- Quality multiplier: ×3
- Final score = Priority + Size + (Quality × 3)

**Output**: Structured markdown with top 2-3 recommendations, detailed rationale, backlog health summary

### `codebase-scanner`

**Invoked by**: `/reprioritize` command

**Purpose**: Assess issue relevance based on current codebase state

**Analysis process**:
1. Baseline exploration (git history, directory structure, recent commits)
2. Per-issue analysis (feature existence checks, related code activity)
3. Relevance assessment (resolved, outdated, more urgent, more feasible)
4. Confidence scoring (high = direct evidence, medium = indirect)

**Recommendations**:
- Increase priority (prerequisites met, more urgent)
- Decrease priority (less relevant, superseded)
- Mark resolved (feature exists, can close)
- No change (remains valid)

**Output**: Markdown report with recommendations, codebase evidence, batch update commands

## Field Discovery

Compass Rose discovers custom fields at runtime rather than hardcoding field names.

**Matching patterns** (case-insensitive):
- **Priority**: "priority", "p0-p3", "severity", "importance"
- **Size**: "size", "estimate", "points", "effort"
- **Status**: "status", "state", "column"
- **Iteration**: "iteration", "sprint", "cycle", "milestone"

**Graceful degradation**: If expected fields are missing, commands warn the user and continue with available data.

**Example warning**:
```
Warning: Priority field not found in project. All items will be treated as equal priority.

Available fields: Status, Size, Iteration

To enable priority-based sorting, add a "Priority" field to your project.
```

## Spiral Grove Integration

Compass Rose escalates large items to Spiral Grove for structured development:

**Escalation points**:
- `/add-item`: Warns when user selects XL size, suggests spec-writing
- `/start-work`: Prompts before starting XL/L items, offers spec-writing option

**Size-based escalation**:
- **XL items**: Always prompt (strongly recommend spec-writing)
- **L items**: Prompt if `preferences.promptForLargeItems` is true (default)
- **S/M items**: No prompt (direct implementation fine)

**User control**: User can always choose "Start implementation directly" (override recommendation)

**Configuration override**:
```json
{
  "preferences": {
    "promptForLargeItems": false
  }
}
```

## Error Handling

### Missing Configuration

```
Error: Configuration file not found.

Please create .compass-rose/config.json with your project details:

{
  "project": {
    "owner": "<org-or-username>",
    "number": <project-number>
  }
}

Find your project number in the project URL:
https://github.com/orgs/<owner>/projects/<number>
```

### Authentication Issues

```
Error: GitHub CLI is not authenticated.

Run the following command to authenticate:
  gh auth login

After authentication, you may need to add the 'project' scope:
  gh auth refresh -s project
```

### Missing Custom Fields

Commands handle missing fields gracefully:
- Warn user about missing field
- Explain impact on functionality
- Continue with available fields
- Provide guidance on adding missing field

### Field Update Failures

If `gh project item-edit` fails for a field:
- Continue with remaining fields
- Report which fields succeeded and which failed
- Suggest manual update in GitHub Projects web UI

## Performance Notes

- Config load: <100ms (local file read)
- Field discovery: <1s (single API call)
- Item listing: <2s (typical backlog <100 items)
- Item creation: <5s (issue + project + fields)
- `/next-item`: <8s end-to-end (includes 2-5s codebase analysis)
- `/start-work`: <35s with validation (15-30s for issue validation), <5s without
- `/backlog`: ~10-15s (agent analysis)
- `/reprioritize`: 5-15 minutes (codebase scanning)

**No caching**: Always fetch fresh data (per spec constraint)

## Common Workflows

### Daily Work Session

```
/next-item                    # Quick: what should I work on?
/start-work next              # Validates issue, then begins work
[Implement the item]
[Create PR, mark Done in GitHub UI]
```

### Sprint Planning

```
/backlog                      # Review backlog health
                             # Identify well-defined items
                             # Note poorly-defined items

[Clarify poorly-defined items]

/next-item                    # Verify top priorities
```

### Quarterly Cleanup

```
/reprioritize                 # Codebase-aware priority updates
                             # Agent analyzes for 10-15 minutes
                             # Review recommendations
                             # Approve batch updates
```

### Adding New Work

```
/add-item                     # Interactive creation
                             # Title, description, priority, size, status
                             # XL warning if applicable
```

## Status

**v0.2.0** - Core commands implemented. Agents functional. Ready for testing.

<!-- BEGIN: HAND-EDITED -->
<!-- Users can add custom sections here -->
<!-- END: HAND-EDITED -->
