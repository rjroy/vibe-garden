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
| `/lore-development:plan` | Direct AI planner with context, save output |
| `/lore-development:validate` | Define testing approach, record deviations |
| `/lore-development:retro` | Review work, capture lessons learned |

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
└── retros/         # Lessons learned
```

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

# Planning implementation
/lore-development:plan

# During/after implementation
/lore-development:validate

# Reflecting on completed work
/lore-development:retro
```

## Principles

- **Light touch** - skills guide, they don't dictate
- **Context over process** - build lore, not bureaucracy
- **Independent but connected** - each skill works alone but knows about the others
- **Trust the LLM** - don't over-specify what modern AI already does well
