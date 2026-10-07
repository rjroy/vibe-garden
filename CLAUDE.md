# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

**Vibe Garden** is a collection of five Claude Code plugins for project management, development workflows, project knowledge, and notifications.

## Repository Structure

```
vibe-garden/
├── compass-rose/              # GitHub Projects management plugin (v1.3.0)
│   ├── .claude-plugin/        # Plugin metadata
│   ├── skills/                # Skill implementations
│   └── agents/                # Agent definitions
│
├── lore-development/          # Project context and workflow plugin (v4.0.0)
│   ├── .claude-plugin/        # Plugin metadata
│   ├── skills/                # Workflow skills (intent, research, brainstorm, implementation, etc.)
│   ├── agents/                # Agent definitions
│   └── shared/                # Shared resources
│
├── notify-hook/               # Desktop/mobile notification plugin (v1.0.0)
│   ├── .claude-plugin/        # Plugin metadata
│   ├── hooks/                 # Hook implementations
│   └── scripts/               # Notification scripts
│
├── field-guide/               # Selective project knowledge wiki plugin
│   ├── .claude-plugin/        # Plugin metadata
│   └── skills/                # Wiki and distillation skills
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

Project context and workflow management. Captures intent and supports research, brainstorming, optional planning, implementation, and retrospectives. Its four `.lore/` zones are `local/` (gitignored execution context), `work/` (shared historical artifacts), `reference/` (maintained explanatory knowledge), and `learned/` (operational mistakes). Historical work artifacts are nonbinding context; current user direction takes precedence.

### Field Guide

Selectively distills useful project understanding into `.lore/reference/`. Eligible historical artifacts can serve as leads, but this is not automatic compilation: verify current behavior against code/tests, preserve only knowledge that adds value, and treat adding nothing as a valid outcome.

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
- `/intent` captures what to build and why; `/prep-plan` can create a disposable plan in `.lore/local/`. Neither historical intents nor plans override the current request.
- Specs for AI-guided skills should be lighter than application specs. Leave room for model growth and agent flexibility. Over-constraining a prompt removes the AI's ability to adapt to project-specific context.
- Skill reviewer is worth running on any skill edit, not just new skills. It catches structural and consistency issues that spec-compliance validators miss.
