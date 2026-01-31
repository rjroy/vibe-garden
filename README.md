# Vibe Garden

<img src="logo.png" align="right" width="128" height="128" alt="Vibe Garden Logo">

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Plugins](https://img.shields.io/badge/plugins-3-purple.svg)

> A collection of Claude Code plugins for project management, development workflows, and notifications.

<br clear="right"/>

---

## Plugins

### Compass Rose - Project Management

**Purpose**: GitHub Projects integration for Claude Code

**Version**: 1.3.0
**Location**: `compass-rose/`

Manage GitHub Projects directly from Claude Code with skills for task tracking, backlog analysis, and priority recommendations.

**Features**:
- Skill-based project management
- Issue tracking and backlog analysis
- Priority recommendations
- Work item lifecycle management

```bash
# Install in Claude Code
/plugin install compass-rose@vibe-garden
```

[Documentation →](compass-rose/README.md)

---

### Lore Development - Project Context

**Purpose**: Build and organize project context for development workflows

**Version**: 0.12.0
**Location**: `lore-development/`

A lightweight plugin for research, brainstorming, specifications, planning, and retrospectives. Helps maintain project knowledge in `.lore/` directories.

**Features**:
- Research and brainstorm tracking
- Specification writing
- Plan mode integration
- Retrospective capture
- Diagram generation (Mermaid)

```bash
# Install in Claude Code
/plugin install lore-development@vibe-garden
```

[Documentation →](lore-development/README.md)

---

### Notify Hook - Notifications

**Purpose**: Desktop and mobile notifications when Claude needs attention

**Version**: 1.0.0
**Location**: `notify-hook/`

Get notified when Claude Code asks a question or completes a long-running task.

**Features**:
- Desktop notifications (Linux/macOS)
- Mobile push notifications via ntfy.sh
- Configurable triggers

```bash
# Install in Claude Code
/plugin install notify-hook@vibe-garden
```

[Documentation →](notify-hook/README.md)

---

## Utilities

### Mind Reader - Usage Analysis

**Location**: `mind-reader/`

Analyzes Claude Code usage history to generate insights about work patterns, project focus, and interaction style.

**Features**:
- Temporal analysis (peak hours, trends)
- Project focus tracking
- Command usage patterns
- BERTopic topic modeling

[Documentation →](mind-reader/CLAUDE.md)

---

## Repository Structure

```
vibe-garden/
├── compass-rose/              # GitHub Projects management plugin
│   ├── .claude-plugin/        # Plugin metadata (v1.3.0)
│   ├── skills/                # Skill implementations
│   └── agents/                # Agent definitions
│
├── lore-development/          # Project context and workflow plugin
│   ├── .claude-plugin/        # Plugin metadata (v0.12.0)
│   ├── skills/                # Workflow skills
│   ├── agents/                # Agent definitions
│   └── shared/                # Shared resources
│
├── notify-hook/               # Desktop/mobile notification plugin
│   ├── .claude-plugin/        # Plugin metadata (v1.0.0)
│   ├── hooks/                 # Hook implementations
│   └── scripts/               # Notification scripts
│
└── mind-reader/               # Usage analysis utility
    ├── preprocess.py          # History preprocessing
    └── topic_model.py         # BERTopic analysis
```

---

## Installation

Install plugins from this repository in Claude Code:

```bash
/plugin install compass-rose@vibe-garden        # Project management
/plugin install lore-development@vibe-garden    # Development workflows
/plugin install notify-hook@vibe-garden         # Notifications
```

---

## Contributing

Contributions welcome:

1. **Bug Fixes** - All plugins welcome improvements
2. **New Plugins** - Add Claude Code plugins to the ecosystem
3. **Documentation** - Enhance setup guides and tutorials

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Contact

**Author:** Ronald Roy
**Email:** gsdwig@gmail.com
**Repository:** [github.com/rjroy/vibe-garden](https://github.com/rjroy/vibe-garden)

---

<div align="center">

*Last Updated: 2026-01-31*

</div>
