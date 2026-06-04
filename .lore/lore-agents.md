---
title: Lore Agents Registry
date: 2026-01-30
status: approved
tags: [registry, agents, reference]
---

# Lore Agents

Specialized agents available for lore-development work in this project.

## Discovery

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `Explore` | Fast codebase exploration - find files, search code, answer questions | Open-ended exploration, understanding structure |
| `lore-development:surface-surveyor` | Entry point discovery for progressive feature excavation | During /excavate, finding codebase entry points |

## Documentation Review

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `lore-development:lore-docs-reviewer` | Fresh-context review of specs and plans | After completing a spec or plan, when docs feel unclear |
| `lore-development:fresh-lore` | Fresh-context analysis using lore skills | When conversation is too deep in weeds, need second opinion, "get fresh eyes on this" |

## Architecture & Planning

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `Plan` | Software architect for designing implementation plans | When planning implementation strategy |

## Code Quality

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `pr-review-toolkit:code-reviewer` | Reviews code for guideline adherence and best practices | After writing code, before commits/PRs |
| `pr-review-toolkit:code-simplifier` | Simplifies code for clarity and maintainability | When code feels over-engineered |
| `pr-review-toolkit:comment-analyzer` | Analyzes comments for accuracy and maintainability | After adding documentation comments |
| `pr-review-toolkit:type-design-analyzer` | Expert analysis of type design (encapsulation, invariants) | When introducing new types |
| `code-simplifier:code-simplifier` | Simplifies and refines code while preserving functionality | Post-implementation cleanup |

## Testing

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `pr-review-toolkit:pr-test-analyzer` | Reviews PR test coverage quality and completeness | Before finalizing PRs |

## Error Handling

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `pr-review-toolkit:silent-failure-hunter` | Identifies silent failures and inadequate error handling | Reviewing code with try-catch blocks or fallbacks |

## Plugin Development

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `plugin-dev:plugin-validator` | Validates plugin configuration and structure | After creating/modifying plugins |
| `plugin-dev:skill-reviewer` | Reviews skill implementations | After creating/modifying skills |
| `plugin-dev:agent-creator` | Creates new agent definitions | When adding agents to plugins |

## Backlog & Project Management

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `compass-rose:backlog-analyzer` | Analyzes backlog items for quality and readiness | Reviewing project backlog health |
| `compass-rose:codebase-scanner` | Scans codebase to assess issue relevance | Reprioritizing based on current state |

## Project-Specific Notes

- This is a research repository - most work involves documentation rather than code
- Plugin development agents are highly relevant since spiral-grove is developed here
- Code quality agents apply when working on plugin implementations
- Discovery agents help navigate the research materials in `seeds/`
