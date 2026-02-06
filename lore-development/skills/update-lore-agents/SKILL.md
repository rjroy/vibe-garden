---
name: update-lore-agents
description: This skill scans available agents and creates/updates the project's agent registry. Use when setting up lore-development in a new project, when new agents become available, or when you want to customize which agents are relevant. Triggers include "update lore agents", "set up agents for this project", "which agents are available", "configure project agents".
---

# Update Lore Agents

Build or update the project's agent registry so other lore-development skills can find specialized help.

## When to Use

- Setting up lore-development in a new project
- New agents have been added to your environment
- You want to customize which agents are relevant to this project
- Reviewing what specialized help is available

## Invocation

```
/lore-development:update-lore-agents              # Interactive: scan and configure
/lore-development:update-lore-agents refresh      # Re-scan, preserve existing notes
```

## Process

### Step 1: Discover Available Agents

Check the Task tool description for available agents. The Task tool lists all subagent types with descriptions in this format:

```
- agent-name: Description of what the agent does (Tools: ...)
```

Scan this list and categorize agents by their function:

- **Discovery**: Codebase exploration, entry point finding, structure scanning
- **Documentation Review**: Fresh-context review of specs and plans
- **Security**: Auth review, vulnerability analysis, secrets handling
- **Architecture**: System design, dependency analysis, patterns
- **Performance**: Profiling, optimization, caching strategies
- **Testing**: Test coverage, test design, validation
- **Code Quality**: Review, simplification, type analysis
- **Domain-Specific**: Agents tied to specific technologies or frameworks

Focus on agents with analysis/review capabilities (tools like Read, Grep, Glob, Bash). Skip generative agents (image/video), workflow-specific agents (music, stories), and internal system agents.

**Built-in lore-development agents** (always include these with consistent descriptions):

| Agent | Category | Standard Description |
|-------|----------|---------------------|
| `lore-development:surface-surveyor` | Discovery | Entry point discovery for progressive feature excavation |
| `lore-development:spec-reviewer` | Documentation Review | Fresh-context review of specs to catch clarity issues |
| `lore-development:design-reviewer` | Documentation Review | Fresh-context review of designs to catch weak decisions |
| `lore-development:plan-reviewer` | Documentation Review | Fresh-context review of plans to catch spec coverage gaps |

### Step 2: Present Findings

Show the user what agents are available, grouped by category. For each agent, include:
- Name (the subagent_type value to use with Task tool)
- Brief description (from the agent's description)
- When it would be useful in lore-development work

### Step 3: Customize for Project

Ask the user:
1. Which agents are relevant to this project?
2. Are there any project-specific notes about when to use certain agents?
3. Should any agents be marked as "always consult" for certain types of work?

### Step 4: Create/Update Registry

Write the registry to `.lore/lore-agents.md`.

If the file already exists:
- Show what's currently there
- Ask what should change
- Preserve any project-specific notes

## Output

Save to `.lore/lore-agents.md`

### Document Structure

```markdown
# Lore Agents

Specialized agents available for lore-development work in this project.

Last updated: [date]

## Discovery

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| surface-surveyor | Entry point discovery | During excavation, finding codebase entry points |

## Documentation Review

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| spec-reviewer | Fresh-context review of specs | After completing a spec, when docs feel unclear |

## Security

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| [agent-name] | [description] | [context for this project] |

## Architecture

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| [agent-name] | [description] | [context for this project] |

## Performance

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| [agent-name] | [description] | [context for this project] |

## Testing

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| [agent-name] | [description] | [context for this project] |

## Code Quality

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| [agent-name] | [description] | [context for this project] |

## Project-Specific Notes

- [Any notes about agent usage specific to this project]
- [e.g., "Always consult security-guidance for any auth-related specs"]
```

Omit empty categories. Only include agents the user selected as relevant.

## Context

This registry is consumed by other lore-development skills:
- `specify` - domain experts for requirements
- `plan` - architecture and security reviewers, plan-reviewer for spec coverage
- `excavate` - discovery agents beyond surface-surveyor
- `brainstorm`, `research`, `retro`, `ddp` - various domain experts

Each skill checks for `.lore/lore-agents.md` and invokes relevant agents via the Task tool.

## Maintenance

Run this skill whenever:
- You add new plugins with useful agents
- Project needs change
- You want to re-evaluate what's available

The registry is meant to evolve with your environment.
