# Lore Development

A lightweight plugin for building and organizing project context.

<img src="logo.webp" align="right" width="128" height="128" alt="Lore Development Logo">

## Philosophy

Modern LLMs have strong native planning and implementation capabilities. This plugin doesn't teach process - it helps build findable, organized context (the "lore" of your project) that informs better work.

## Skills

| Skill | Purpose |
|-------|---------|
| `/lore-development:research` | Gather context from outside the project |
| `/lore-development:brainstorm` | Explore ideas, record "what if" thinking |
| `/lore-development:specify` | Define requirements and success criteria |
| `/lore-development:plan` | Build implementation plans as reviewable lore artifacts |
| `/lore-development:tend` | Periodic hygiene to maintain document status accuracy |
| `/lore-development:retro` | Review work, capture lessons learned |
| `/lore-development:excavate` | **Design archaeology** - discover and document existing systems |
| `/lore-development:ddp` | **Draw the Damn Picture** - visualize flows and relationships with Mermaid |
| `/lore-development:update-lore-agents` | Build/update the project's agent registry |

## Artifact Storage

All context lives in `.lore/`:

```
.lore/
├── research/       # External findings
├── brainstorm/     # Recorded explorations
├── specs/          # Requirements
├── plans/          # Implementation plans (reviewed, persistent)
├── retros/         # Lessons learned
├── reference/      # Excavated feature documentation
├── excavations/    # Design archaeology session tracking
├── diagrams/       # Visual representations (Mermaid)
└── lore-agents.md  # Agent registry (optional)
```

## Agent Registry

Skills can leverage specialized agents for domain-specific concerns (security, performance, architecture, etc.). Instead of hardcoding agent names into every skill, the plugin uses a project-level registry.

**How it works**:
1. Run `/lore-development:update-lore-agents` to scan available agents
2. The skill creates `.lore/lore-agents.md` with agents relevant to your project
3. Other skills check this file and invoke agents when appropriate

**Benefits**:
- Add new agents without updating the plugin
- Each project declares what's relevant to it
- Project-specific notes (e.g., "always use security-guidance for auth specs")

## Usage

Skills can run independently. Use what you need:

```
# Exploring something new
/lore-development:research

# Thinking through possibilities
/lore-development:brainstorm

# Ready to define what to build
/lore-development:specify

# Planning implementation (with lore context)
/lore-development:plan

# Checking document health
/lore-development:tend

# Reflecting on completed work
/lore-development:retro

# Documenting an existing codebase (design archaeology)
/lore-development:excavate

# Visualizing flows and relationships
/lore-development:ddp how messages flow from user to AI

# Setting up/updating agent registry
/lore-development:update-lore-agents
```

## Two Modes of Operation

### Forward Mode (Building New)
Use `research → brainstorm → specify → plan → retro` when building something new. This creates lore as you work.

### Backward Mode (Excavating Existing)
Use `excavate` when inheriting or joining an existing codebase. This discovers the lore that should have been documented.

```
Forward:  Intent → Spec → Plan → Code → Lore
Backward: Code → Survey → Features → Design → Lore
```

The output is the same (`.lore/specs/`, architecture docs), but the process is inverted.

## The Compound Loop

Knowledge compounds when past learnings inform new work. The plugin closes this loop automatically:

```
/specify or /plan
        │
        ├─► lore-researcher agent searches .lore/ for related work
        │
        ▼
   findings included in new spec/plan
        │
        ... work happens ...
        │
        ▼
      /retro
        │
        └─► captures lessons → writes to .lore/retros/
```

The `lore-researcher` agent runs automatically at the start of `/specify` and `/plan`, surfacing relevant retros, specs, and brainstorms before new work begins.

## Frontmatter Schema

All lore documents use YAML frontmatter for searchability. The schema is defined in `shared/frontmatter-schema.md`.

```yaml
---
title: Descriptive title
date: YYYY-MM-DD
status: draft|approved|complete|etc
tags: [relevant, keywords]
modules: [affected-modules]
---
```

Documents without frontmatter won't be found by `lore-researcher`. Use `/tend` to retrofit old documents.

## Principles

- **Light touch** - skills guide, they don't dictate
- **Context over process** - build lore, not bureaucracy
- **Independent but connected** - each skill works alone but knows about the others
- **Trust the LLM** - don't over-specify what modern AI already does well
- **Human checkpoints** - excavation requires confirmation at each layer
- **Compound knowledge** - past learnings automatically surface for new work
