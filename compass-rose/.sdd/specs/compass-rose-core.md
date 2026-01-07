---
version: 1.0.0
status: Approved
created: 2025-12-14
last_updated: 2025-12-14
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Compass Rose Core Specification

## Executive Summary

Compass Rose is a Claude Code plugin that enables Claude to interact with GitHub Projects for repository work management. It provides awareness of a project's backlog, allowing Claude to recommend next work items, analyze priorities, and assist with backlog triage.

The plugin complements Spiral Grove (SDD) by managing ad-hoc tasks and bugs that don't require formal specifications, while prompting users to escalate larger items to the spec-driven workflow.

## User Stories

1. As a developer, I want Claude to recommend my next work item based on priority and readiness, so that I spend less time triaging and more time coding.
2. As a developer, I want Claude to review my backlog and suggest well-defined items to work on, so that I can make informed decisions about what to tackle.
3. As a developer, I want Claude to reprioritize my backlog based on current codebase state, so that priorities stay relevant as the project evolves.
4. As a developer, I want Claude to start working on an issue directly from the project board, so that I have a seamless workflow from triage to implementation.

## Stakeholders

- **Primary**: Developers using Claude Code with GitHub Projects
- **Secondary**: Team leads reviewing project progress

## Success Criteria

1. Claude can identify the highest-priority ready item within 30 seconds of being asked
2. Claude can update issue priorities via `gh` CLI without manual user intervention
3. Large items (XL/L) trigger a prompt suggesting Spiral Grove spec-writing
4. All project interactions use existing `gh project` CLI (no custom API integration)

## Functional Requirements

### Project Configuration

- **REQ-F-1**: System must allow configuration of one GitHub Project per repository
- **REQ-F-2**: Configuration must specify project owner (org or user) and project number
- **REQ-F-3**: Configuration must be stored in `.compass-rose/config.json` within the repository

### Issue Viewing

- **REQ-F-4**: System must retrieve project items filtered by status (e.g., "Ready", "In progress")
- **REQ-F-5**: System must sort items by priority field (P0 > P1 > P2 > P3)
- **REQ-F-6**: System must display item summary, priority, size, and iteration when presenting options
- **REQ-F-7**: System must handle projects with custom field configurations gracefully

### Issue Management

- **REQ-F-8**: System must create new repository issues (not draft items) when adding work items
- **REQ-F-9**: System must update issue custom fields (Priority, Size, Iteration, Status)
- **REQ-F-10**: System must link newly created issues to the configured project

### Backlog Analysis

- **REQ-F-11**: System must analyze backlog items and recommend based on priority, size, and definition quality
- **REQ-F-12**: System must identify items that are "well-defined" (have clear description and acceptance criteria)
- **REQ-F-13**: System must present 2-3 options when asked for recommendations, with rationale

### Codebase-Aware Reprioritization

- **REQ-F-14**: System must explore current codebase state before reprioritizing
- **REQ-F-15**: System must compare issue descriptions against codebase to assess relevance
- **REQ-F-16**: System must batch-update priorities via `gh` CLI
- **REQ-F-17**: System must report summary of changes made (e.g., "10 of 60 issues updated")

### Spiral Grove Integration

- **REQ-F-18**: System must detect when an issue is sized XL and prompt user about spec-writing
- **REQ-F-19**: System must optionally prompt for L-sized items (user preference)
- **REQ-F-20**: Prompt must offer choice: "Write spec first" or "Start implementation directly"

### Work Initiation

- **REQ-F-21**: System must allow user to request starting work on next ready item
- **REQ-F-22**: System must update issue status to "In progress" when work begins
- **REQ-F-23**: System must read full issue description and any linked context before starting

## Non-Functional Requirements

- **REQ-NF-1** (Dependency): Must use only `gh` CLI for GitHub interactions (no direct API calls)
- **REQ-NF-2** (Compatibility): Must work with GitHub Projects (new) not classic Projects
- **REQ-NF-3** (Resilience): Must handle missing custom fields gracefully (warn, don't fail)
- **REQ-NF-4** (Transparency): Must explain reasoning when making recommendations
- **REQ-NF-5** (Minimal Config): Must work with minimal configuration (project owner + number only)

## Explicit Constraints (DO NOT)

- Do NOT create draft items in projects (always create proper repository issues)
- Do NOT require specific custom field names (discover and adapt to existing fields)
- Do NOT auto-start work without user confirmation
- Do NOT modify issues outside the configured project
- Do NOT cache project state between sessions (always fetch fresh data)

## Technical Context

- **Existing Stack**: Claude Code plugin system (commands, agents, skills)
- **Integration Points**:
  - GitHub CLI (`gh project`, `gh issue`)
  - Spiral Grove plugin (for spec escalation)
- **Patterns to Respect**:
  - Plugin structure from spiral-grove
  - Skill-based knowledge organization

## Expected Custom Fields

The following fields are expected but not required. System should discover and adapt:

| Field | Expected Values | Fallback |
|-------|----------------|----------|
| Priority | P0, P1, P2, P3 | Treat all as equal priority |
| Size | S, M, L, XL | Skip size-based recommendations |
| Iteration | Sprint number | Ignore iteration filtering |
| Status | Ready, In progress, Done, etc. | Use project column position |

## Acceptance Tests

1. **Config Loading**: Given a `.compass-rose/config.json` with valid project details, Claude can query the project
2. **Next Item Query**: Given a project with P0 and P1 items in Ready status, Claude recommends the P0 item first
3. **Backlog Review**: Given 10 backlog items, Claude presents 2-3 recommendations with rationale
4. **Priority Update**: Given user approval, Claude updates priorities via `gh` and reports changes
5. **XL Escalation**: Given an XL-sized ready item, Claude prompts about spec-writing before starting
6. **Missing Fields**: Given a project without Priority field, Claude warns but continues with available data
7. **Issue Creation**: Given user request to add bug, Claude creates repository issue and links to project

## Open Questions

- [x] One project per repo or multiple? → **One project per repo**
- [x] Draft items or always issues? → **Always repository issues**
- [x] Custom field handling? → **Hybrid: expect standard fields, adapt to what exists**

## Out of Scope

- GitHub Projects (classic) support
- Multi-repository project views
- Automated priority algorithms (Claude recommends, user decides)
- Time tracking or velocity calculations
- Integration with external project management tools (Jira, Linear, etc.)

---

**Next Phase**: Once approved, use `/spiral-grove:plan-generation` to create technical implementation plan.
