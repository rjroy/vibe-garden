# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

**Vibe Garden** is a collection of Claude Code plugins for project management, development workflows, and notifications.

## Repository Structure

```
vibe-garden/
├── compass-rose/              # GitHub Projects management plugin (v1.3.0)
│   ├── .claude-plugin/        # Plugin metadata
│   ├── skills/                # Skill implementations
│   └── agents/                # Agent definitions
│
├── lore-development/          # Project context and workflow plugin (v0.12.0)
│   ├── .claude-plugin/        # Plugin metadata
│   ├── skills/                # Workflow skills (research, brainstorm, specify, etc.)
│   ├── agents/                # Agent definitions
│   └── shared/                # Shared resources
│
├── notify-hook/               # Desktop/mobile notification plugin (v1.0.0)
│   ├── .claude-plugin/        # Plugin metadata
│   ├── hooks/                 # Hook implementations
│   └── scripts/               # Notification scripts
│
└── mind-reader/               # Active feedback plugin (v1.0.0)
    ├── .claude-plugin/        # Plugin metadata
    ├── hooks/                 # UserPromptSubmit hook
    ├── skills/                # Init skill
    ├── scripts/               # Hook and baseline scripts
    └── tests/                 # Unit tests
```

## Plugins

### Compass Rose

GitHub Projects integration. Skills for task tracking, backlog analysis, and priority recommendations.

### Lore Development

Project context and workflow management. Skills for research, brainstorming, specifications, planning, and retrospectives. Stores artifacts in `.lore/` directories.

### Notify Hook

Desktop and mobile notifications when Claude needs attention (questions, task completion).

### Mind Reader

Active feedback based on session patterns and sentiment analysis. Nudges when sessions exceed typical duration or detect frustration.

## Package Metadata Guidelines

When creating package configuration files (pyproject.toml, package.json, setup.py, etc.):

- **Author**: Ronald Roy
- **Email**: gsdwig@gmail.com
- **Repository URLs**: Use paths under `rjroy/vibe-garden` (e.g., `https://github.com/rjroy/vibe-garden`)
- **Do NOT** use Anthropic as author or include Anthropic URLs in code artifacts
- **Commit messages**: Anthropic attribution in commit messages is acceptable

## Critical Lessons

- Marketplace registration for vibe-garden is just an entry in `.claude-plugin/marketplace.json` at repo root
