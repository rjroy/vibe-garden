---
specification: [.sdd/specs/compass-rose-core.md](./../specs/compass-rose-core.md)
status: Draft
version: 1.0.0
created: 2025-12-14
last_updated: 2025-12-14
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Compass Rose Core - Technical Plan

## Overview

Compass Rose implements GitHub Projects integration for Claude Code as a plugin following the established Spiral Grove pattern. The architecture centers on **command-driven interaction** with the `gh` CLI as the sole data access layer, ensuring no custom API integration is required.

Key design strategies:
- **CLI-first data access**: All GitHub interactions through `gh project` and `gh issue` commands
- **Discovery-based field handling**: Detect available custom fields rather than assuming specific names
- **Stateless operation**: Fetch fresh project data on each request (no caching between sessions)
- **Spiral Grove integration**: XL/L items trigger spec-writing prompts

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Commands   │    │    Agents    │    │    Skills    │   │
│  │              │    │              │    │              │   │
│  │ /next-item   │    │ backlog-     │    │ gh-project-  │   │
│  │ /backlog     │    │  analyzer    │    │  reference   │   │
│  │ /reprioritize│    │ codebase-    │    │              │   │
│  │ /add-item    │    │  scanner     │    │              │   │
│  │ /start-work  │    │              │    │              │   │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘   │
│         │                   │                               │
│         └─────────┬─────────┘                               │
│                   │                                         │
│         ┌─────────▼─────────┐                               │
│         │  gh CLI Wrapper   │                               │
│         │  (Bash commands)  │                               │
│         └─────────┬─────────┘                               │
└───────────────────│─────────────────────────────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  GitHub Projects │
         │  (gh project)    │
         └──────────────────┘
```

### Components

| Component | Responsibility |
|-----------|----------------|
| **Commands** | User-facing slash commands for project operations |
| **Agents** | Complex multi-step analysis operations |
| **Skills** | Reference documentation for `gh` CLI patterns |
| **Config** | Repository-specific project binding (`.compass-rose/config.json`) |

### Data Flow

1. **User invokes command** → Command reads config → Builds `gh` CLI command
2. **gh CLI executes** → Returns JSON data → Command parses response
3. **Claude analyzes** → Presents options → User selects action
4. **Action executed** → gh CLI updates GitHub → Confirmation shown

## Technical Decisions

### TD-1: gh CLI as Sole Data Layer

**Choice**: Use `gh project` and `gh issue` CLI commands exclusively for all GitHub interactions

**Requirements**: REQ-NF-1, REQ-NF-2

**Rationale**:
- `gh` CLI handles authentication, rate limiting, and pagination automatically
- No custom API client maintenance required
- GitHub actively maintains `gh` with new Projects features
- JSON output (`--format json`) provides structured data for parsing

**Alternatives Considered**:
- Direct GitHub GraphQL API: Rejected due to auth complexity, rate limit management burden, violates REQ-NF-1
- Octokit library: Rejected due to dependency weight, same auth issues, violates REQ-NF-1

### TD-2: Discovery-Based Field Handling

**Choice**: Discover custom fields at runtime using `gh project field-list` rather than hardcoding field names

**Requirements**: REQ-F-7, REQ-NF-3, REQ-NF-5

**Rationale**:
- Users name their custom fields differently ("Priority" vs "P" vs "Severity")
- Discovery enables graceful degradation when fields are missing
- Reduces configuration burden (only project owner/number required)

**Implementation**:
```bash
# Discover fields
gh project field-list <number> --owner <owner> --format json

# Returns: [{name: "Status", id: "PVTSSF_...", type: "SINGLE_SELECT"}, ...]
```

**Field Matching Strategy**:
- Priority: Match fields containing "priority", "p0-p3", or "severity" (case-insensitive)
- Size: Match fields containing "size", "estimate", or "points"
- Status: Match fields containing "status" or "state"
- Iteration: Match fields containing "iteration", "sprint", or "cycle"

### TD-3: Stateless Session Model

**Choice**: Fetch fresh project data on every command invocation; no caching between sessions

**Requirements**: Explicit Constraint #5 ("Do NOT cache project state between sessions")

**Rationale**:
- Project state changes frequently (other team members, GitHub web UI)
- Caching adds complexity (invalidation, staleness, storage)
- `gh` CLI is fast enough for single-project queries (<2 seconds typical)
- Eliminates entire class of bugs around stale data

**Alternatives Considered**:
- In-memory session caching: Rejected due to staleness in multi-user scenarios, invalidation complexity
- File-based caching with TTL: Rejected due to added file management, marginal performance gain

**Trade-off**: Slightly slower operations but always accurate data.

### TD-4: Configuration Schema

**Choice**: Minimal JSON configuration stored in repository at `.compass-rose/config.json`

**Requirements**: REQ-F-1, REQ-F-2, REQ-F-3, REQ-NF-5

**Configuration Schema**:
```json
{
  "project": {
    "owner": "<org-or-username>",
    "number": <project-number>
  },
  "preferences": {
    "promptForLargeItems": true,
    "largeSizeThreshold": ["L", "XL"]
  }
}
```

**Rationale**:
- Owner + number are the only required fields (REQ-NF-5)
- Preferences section is optional with sensible defaults
- JSON format is widely understood and easy to edit
- `.compass-rose/` directory mirrors Spiral Grove's `.sdd/` pattern

### TD-5: Item Type Strategy - Repository Issues Only

**Choice**: Always create repository issues, never draft items

**Requirements**: REQ-F-8, REQ-F-10, Explicit Constraint #1

**Rationale**:
- Draft items lack issue numbers, making them hard to reference
- Draft items can't be linked across projects
- Repository issues have better visibility (appear in repo Issues tab)
- Two-step process: `gh issue create` → `gh project item-add`

**Implementation Flow**:
```bash
# 1. Create repository issue
gh issue create --title "..." --body "..." --repo OWNER/REPO

# 2. Add to project
gh project item-add <number> --owner <owner> --url <issue-url>

# 3. Set custom fields (one call per field - gh CLI limitation)
gh project item-edit --id <item-id> --field-id <priority-field-id> --project-id <project-id> --single-select-option-id <p1-option-id>
gh project item-edit --id <item-id> --field-id <size-field-id> --project-id <project-id> --single-select-option-id <medium-option-id>
gh project item-edit --id <item-id> --field-id <status-field-id> --project-id <project-id> --single-select-option-id <ready-option-id>
```

**Note**: `gh project item-edit` can only update one field per invocation. Setting multiple fields (Priority, Size, Status) requires multiple sequential calls.

### TD-6: Priority Sorting Algorithm

**Choice**: Sort by discovered priority field values, treating P0 > P1 > P2 > P3

**Requirements**: REQ-F-5, REQ-F-11

**Rationale**:
- Common priority naming convention (P0 = critical, P3 = low)
- When priority field is missing, all items treated as equal priority
- Secondary sort by item creation date (oldest first)

**Field Value Detection**:
1. Query `gh project field-list` for priority field
2. Get field options via JSON output
3. Sort options by numeric suffix (P0 < P1 < P2 < P3) or by position in list
4. Apply sort to items

### TD-7: Spiral Grove Integration Points

**Choice**: Detect XL-sized items and prompt for spec-writing; respect user preference for L-sized items

**Requirements**: REQ-F-18, REQ-F-19, REQ-F-20

**Integration Flow**:
```
User: /start-work

Claude: [Detects XL item]
        "This item is sized XL, which typically requires detailed planning."

        Options:
        1. Write spec first (/spec-writing) - Recommended for XL items
        2. Start implementation directly

        Which approach would you prefer?
```

**Implementation**:
- Check Size field value after item selection
- If XL: Always prompt with recommendation
- If L: Check `preferences.promptForLargeItems` (default: true)
- User can override and proceed directly

## Integration Points

### GitHub CLI (`gh`)

| Command | Purpose | Data Flow |
|---------|---------|-----------|
| `gh project list` | Verify project exists | Read |
| `gh project view` | Get project metadata | Read |
| `gh project field-list` | Discover custom fields | Read |
| `gh project item-list` | Get project items | Read |
| `gh project item-add` | Link issue to project | Write |
| `gh project item-edit` | Update custom fields | Write |
| `gh issue create` | Create repository issue | Write |
| `gh issue view` | Get issue details | Read |

**Dependencies**:
- `gh` CLI installed and authenticated
- `project` scope authorized (`gh auth refresh -s project`)

### Spiral Grove Plugin

| Integration | Purpose |
|-------------|---------|
| `/spec-writing` command | Escalate large items to SDD workflow |
| Plugin structure patterns | Directory layout, command format, agent format |

## Error Handling, Performance, Security

### Error Strategy

| Error Type | Handling |
|------------|----------|
| Missing config | Prompt user to create `.compass-rose/config.json` with example |
| Invalid project | Clear message: "Project not found. Verify owner and number." |
| Missing fields | Warn and continue: "Priority field not found. Skipping priority-based sorting." |
| Auth failure | Direct to `gh auth status` and `gh auth refresh -s project` |
| Rate limiting | Unlikely with single-user CLI usage; surface gh error if occurs |

### Performance Targets

- **Config load**: <100ms (local file read)
- **Project query**: <2s (single `gh project item-list` call)
- **Field discovery**: <1s (single `gh project field-list` call)
- **Item creation**: <3s (issue create + project add + field edit)

### Security Measures

- No credential storage; relies on `gh` CLI's auth
- Config file contains no secrets (just project reference)
- All writes require user confirmation (Explicit Constraint #3)
- Modifications scoped to configured project only (Explicit Constraint #4)

## Testing Strategy

### Unit Testing

Not applicable - plugin is prompt-based markdown commands.

### Integration Testing

| Scenario | Validation |
|----------|------------|
| Config loading | Valid JSON parsed, invalid JSON shows clear error |
| Project connection | `gh project view` succeeds with configured owner/number |
| Field discovery | Fields detected and matched to known types |
| Item listing | Items returned, filtered by status, sorted by priority |
| Item creation | Issue created, linked to project, fields set |
| Missing fields | Warning shown, operation continues |
| XL escalation | Prompt appears, both options work |

### Manual Testing Protocol

1. Create test project with standard fields (Status, Priority, Size)
2. Add test items with various priorities and sizes
3. Run each command and verify behavior
4. Test with missing fields (remove Priority, verify fallback)
5. Test XL escalation flow end-to-end

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| gh CLI not installed/authenticated | Medium | High | Clear error with installation instructions; check on first command |
| gh CLI output format changes | Low | Medium | Pin to documented `--format json` output; monitor gh releases |
| Field matching heuristics fail | Medium | Low | Document expected field names; provide config override option in v2 |
| Project scope token not authorized | Medium | High | Clear error message with fix instructions (`gh auth refresh -s project`) |
| Large projects slow to query | Low | Low | Use `--limit` parameter; typical backlog is <100 items |

## Dependencies

### Technical

- **GitHub CLI**: `gh` version supporting `gh project` commands (v2.0+)
- **Claude Code**: Plugin system with commands, agents, skills support
- **Spiral Grove** (optional): For spec escalation workflow

### Team

- No external approvals required
- Self-contained within vibe-garden repository

## Plugin Structure

```
compass-rose/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata (existing)
├── CLAUDE.md                 # Plugin documentation (update)
├── README.md                 # User-facing docs (update)
├── commands/
│   ├── next-item.md          # Recommend next work item
│   ├── backlog.md            # Review and analyze backlog
│   ├── reprioritize.md       # Codebase-aware priority update
│   ├── add-item.md           # Create new issue and add to project
│   └── start-work.md         # Begin work on an item
├── agents/
│   ├── backlog-analyzer.md   # Analyzes items for recommendations
│   └── codebase-scanner.md   # Scans codebase for priority relevance
├── skills/
│   └── gh-project-reference/
│       └── SKILL.md          # gh CLI patterns and examples
└── .sdd/                     # SDD artifacts (existing)
    └── specs/
        └── compass-rose-core.md
```

## Command Specifications

### TD-8: Item Presentation Format

**Choice**: Display item summary, priority, size, and iteration in a consistent tabular format

**Requirements**: REQ-F-6, REQ-NF-4

**Rationale**:
- Consistent format enables quick scanning across commands
- Including all available fields (with fallbacks for missing) respects REQ-NF-3
- Rationale included with every recommendation satisfies REQ-NF-4 (transparency)

**Presentation Format**:
```
| # | Title                  | Priority | Size | Status |
|---|------------------------|----------|------|--------|
| 1 | Fix login timeout bug  | P0       | S    | Ready  |
| 2 | Add user preferences   | P1       | M    | Ready  |

**Recommendation**: Item #1 (P0 priority, small scope, ready for work)
**Rationale**: Highest priority item with clear acceptance criteria. Small size
makes it achievable in a single session.
```

### /next-item

**Purpose**: Recommend the highest-priority ready item (REQ-F-4, REQ-F-5, REQ-F-6, REQ-F-11, REQ-NF-4)

**Flow**:
1. Load config, discover fields
2. Query items with Status = "Ready" (or equivalent)
3. Sort by Priority (P0 first), then creation date
4. Present top 2-3 options in standard format (TD-8) with rationale

### /backlog

**Purpose**: Review backlog and analyze item quality (REQ-F-11, REQ-F-12, REQ-F-13, REQ-NF-4)

**Flow**:
1. Load config, discover fields
2. Query all non-Done items
3. Spawn backlog-analyzer agent for quality analysis
4. Present recommendations in standard format (TD-8) with rationale explaining why each is recommended

### /reprioritize

**Purpose**: Codebase-aware priority recommendations (REQ-F-14, REQ-F-15, REQ-F-16, REQ-F-17)

**Flow**:
1. Load config, discover fields
2. Query all items
3. Spawn codebase-scanner agent to analyze relevance
4. Present priority change recommendations
5. Batch-update with user approval

### /add-item

**Purpose**: Create issue and add to project (REQ-F-8, REQ-F-9, REQ-F-10)

**Flow**:
1. Gather item details (title, description, priority, size)
2. Create repository issue via `gh issue create`
3. Add to project via `gh project item-add`
4. Set custom fields via `gh project item-edit`

### /start-work

**Purpose**: Begin work on an item (REQ-F-21, REQ-F-22, REQ-F-23)

**Flow**:
1. Select item (from /next-item or user-specified)
2. Check Size field for XL/L escalation (REQ-F-18, REQ-F-19)
3. Update Status to "In progress"
4. Read full issue description
5. Begin implementation guidance

## Open Questions

- [x] How to handle projects with no custom fields at all? → **Use item position in project board as implicit priority**
