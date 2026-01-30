# Lore Development

A lightweight plugin for building and organizing project context.

## Philosophy

Modern LLMs have strong native planning and implementation capabilities. This plugin doesn't teach process - it helps build findable, organized context (the "lore" of your project) that informs better work.

## Skills

| Skill | Purpose |
|-------|---------|
| `/lore-development:research` | Gather context from outside the project |
| `/lore-development:brainstorm` | Explore ideas, record "what if" thinking |
| `/lore-development:specify` | Define requirements and success criteria |
| `/lore-development:breakdown` | Decompose work into releasable chunks |
| `/lore-development:execute` | Orchestrate implement → review → test cycle per chunk |
| `/lore-development:plan` | Direct AI planner with context, save output |
| `/lore-development:validate` | Define testing approach, record deviations |
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
├── work/           # Releasable breakdowns
├── plans/          # Saved planning sessions
├── validations/    # Testing guidelines, deviation logs
├── retros/         # Lessons learned
├── excavations/    # Design archaeology findings
│   ├── layer-1-survey.md
│   ├── layer-2-features.md
│   ├── layer-3-design.md
│   └── sessions/
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

# Breaking it into pieces
/lore-development:breakdown

# Executing the breakdown (implement → review → test)
/lore-development:execute

# Planning implementation
/lore-development:plan

# Checking document health
/lore-development:tend

# During/after implementation
/lore-development:validate

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
Use `research → brainstorm → specify → breakdown → plan → validate → retro` when building something new. This creates lore as you work.

### Backward Mode (Excavating Existing)
Use `excavate` when inheriting or joining an existing codebase. This discovers the lore that should have been documented.

```
Forward:  Intent → Spec → Plan → Code → Lore
Backward: Code → Survey → Features → Design → Lore
```

The output is the same (`.lore/specs/`, architecture docs), but the process is inverted.

## Principles

- **Light touch** - skills guide, they don't dictate
- **Context over process** - build lore, not bureaucracy
- **Independent but connected** - each skill works alone but knows about the others
- **Trust the LLM** - don't over-specify what modern AI already does well
- **Human checkpoints** - excavation requires confirmation at each layer
