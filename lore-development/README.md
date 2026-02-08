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
| `/lore-development:design` | Make technical decisions when the "how" is the problem |
| `/lore-development:prep-plan` | Build implementation plans as reviewable lore artifacts |
| `/lore-development:implement` | Orchestrate implementation from a plan via sub-agents |
| `/lore-development:retro` | Review work, capture lessons learned |
| `/lore-development:poke-holes` | Challenge ideas adversarially |
| `/lore-development:excavate` | **Design archaeology** - discover and document existing systems |
| `/lore-development:ddp` | **Draw the Damn Picture** - visualize flows and relationships with Mermaid |
| `/lore-development:tend` | Periodic hygiene to maintain document status accuracy |
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

Skills can run independently. Use what you need. For the recommended flow when building something new, see the **Workflow** section below.

## Workflow

Skills flow from exploration to implementation. The key decision is when to start a fresh session.

### Explore (same session)

Run `/brainstorm`, `/research`, `/specify`, and `/design` in the same conversation. These phases are conversational. The value is in the back-and-forth, the rejected ideas, the "not that because X" reasoning. Let context accumulate.

When `/design` or `/specify` completes, you have written artifacts in `.lore/`. The exploration phase is done.

### Plan (fresh session)

Start a new session. Run `/prep-plan` pointing at the artifacts from the explore phase. The planner synthesizes from the documents, not from conversational memory. This is intentional: if the written artifacts aren't clear enough for a fresh context to produce a good plan, they need revision before implementation.

### Build (fresh session)

Start a new session. Run `/implement` pointing at the plan. The implement skill delegates to sub-agents who get their own fresh context. The orchestrator shouldn't carry exploration history when it needs full attention on dispatching, testing, and reviewing.

### Learn (same session)

Run `/retro` at the end of any session where something worth capturing happened. The retro benefits from the messy context: what went wrong, what the LLM got confused by, which assumptions broke. A fresh context would lose exactly the things worth capturing.

Retros aren't only for build. An explore session that surfaced a surprising constraint, or a plan session that revealed a spec gap, are both worth a `/retro` before closing out.

### Why break context

Rolling context helps when work is exploratory. It hurts when work is procedural and artifact-driven. Breaking context before `/prep-plan` also serves as a forcing function: if the specs and designs can't stand on their own without the conversation that produced them, they aren't ready.

### Excavating existing code

Use `/excavate` when inheriting or joining an existing codebase. This discovers the lore that should have been documented. The output is the same (`.lore/specs/`, architecture docs), but the process starts from code instead of intent.

## The Compound Loop

Knowledge compounds when past learnings inform new work. The plugin closes this loop automatically:

```
/specify or /prep-plan
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

The `lore-researcher` agent runs automatically at the start of `/specify` and `/prep-plan`, surfacing relevant retros, specs, and brainstorms before new work begins.

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
