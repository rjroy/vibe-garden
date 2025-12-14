# Compass Rose Plugin

**Last Generated**: 2025-12-14T00:00:00Z

## Purpose

A Claude Code plugin for project management using GitHub Projects. Provides skills, commands, and agents for managing tasks, bugs, and feature ideas. Complements Spiral Grove (SDD) by tracking the backlog of work items that feed into structured development.

## Key Concepts

### Relationship to Spiral Grove

- **Spiral Grove**: Handles structured development (Spec → Plan → Tasks → Implementation) for features in active development
- **Compass Rose**: Manages the broader backlog of work items before they enter development

### Work Item Types

1. **Bugs**: Issues with existing functionality ("server crashes on double-refresh")
2. **Tasks**: Small improvements or fixes ("input box is too big")
3. **Feature Ideas**: Larger concepts that may need specs ("support multiple RPG systems")

### GitHub Projects Integration

Uses `gh project` CLI commands to:
- Create and manage project items
- Track status across columns (To Do, In Progress, Done, etc.)
- Link items to repository issues

## Configuration

Each repository must specify its GitHub Project. Configuration stored in `.compass-rose/config.json`:

```json
{
  "project": {
    "owner": "<org-or-user>",
    "number": <project-number>
  }
}
```

## Components

### Commands (`commands/*.md`)

*To be implemented in spec phase*

Planned commands:
- `add-item`: Add a new work item to the project
- `list-items`: View current backlog
- `triage`: Review and prioritize items
- `promote`: Escalate a feature idea to Spiral Grove spec

### Agents (`agents/*.md`)

*To be implemented based on spec*

### Skills (`skills/`)

*To be implemented based on spec*

## Integration Points

**Dependencies**:
- GitHub CLI (`gh`) with authentication
- GitHub Project linked to repository
- Optional: Spiral Grove for promoting items to specs

**Workflow Integration**:
```
[Bug/Task/Idea] → Compass Rose → [Triage] → [Small item: Direct fix]
                                         → [Large item: Spiral Grove spec]
```

## Design Philosophy

1. **Lightweight**: Quick to add items, minimal ceremony
2. **Complementary**: Works with Spiral Grove, not against it
3. **GitHub-native**: Uses standard GitHub Projects, no custom storage
4. **Triage-focused**: Help prioritize and categorize, not just collect

## Status

**v0.1.0** - Initial project setup. Ready for spec phase.

<!-- BEGIN: HAND-EDITED -->
<!-- Users can add custom sections here -->
<!-- END: HAND-EDITED -->
