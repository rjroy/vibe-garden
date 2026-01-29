# Plan: Lore Development Plugin

**Status**: complete (plugin exists and is in active use)

## Context

Spiral Grove works but feels heavy for modern LLMs. The bones are good (spec, plan, breakdown, implement) but:
- Modern LLMs have native planning capabilities
- Don't need to teach process, need to capture context
- Focus on building findable, organized lore - not outputting artifacts

## Design Decisions

**Name**: `lore-development` - the lore of the project, building and developing context

**Philosophy**:
- Very lightweight skills (40-80 lines each)
- Trust the LLM, don't over-specify process
- About building context files, not precision
- Each skill runs independently but can be informed they connect

**Artifact Storage**: `.lore/` with subdirectories by type
- Not mirrored structures like `.sdd/`
- Organized for findability

## Skills

| Skill | Purpose | Output Location |
|-------|---------|-----------------|
| `research` | Find context outside project scope | `.lore/research/` |
| `brainstorm` | Record conversation, "what if" emphasis, consume sketches | `.lore/brainstorm/` |
| `specify` | Define requirements, success criteria | `.lore/specs/` |
| `breakdown` | Decompose into releasable work | `.lore/work/` |
| `plan` | Direct AI planner with context, save output | `.lore/plans/` |
| `validate` | Deviation tracking, testing/review guidelines | `.lore/validations/` |
| `retro` | Review artifacts, record lessons learned | `.lore/retros/` |

## Skill Design Principles

Each skill should only specify:
- What kind of output to create
- Where to save it
- How to name it
- What other `.lore/` context to consider (optional)

No heavy process. No agents. No validation orchestration.

## Directory Structure

```
lore-development/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── research/
│   │   └── SKILL.md
│   ├── brainstorm/
│   │   └── SKILL.md
│   ├── specify/
│   │   └── SKILL.md
│   ├── breakdown/
│   │   └── SKILL.md
│   ├── plan/
│   │   └── SKILL.md
│   ├── validate/
│   │   └── SKILL.md
│   └── retro/
│       └── SKILL.md
└── README.md

.lore/ (created during use)
├── research/
├── brainstorm/
├── specs/
├── work/
├── plans/
├── validations/
└── retros/
```

## Implementation Order

1. Create plugin scaffold (`plugin.json`, directory structure)
2. Write skills in dependency order:
   - `research` and `brainstorm` (context gathering, no dependencies)
   - `specify` (may reference research/brainstorm)
   - `breakdown` (references specs)
   - `plan` (references breakdown, specs)
   - `validate` (references plans)
   - `retro` (references all)
3. README with quick usage guide

## Open Questions

- File naming convention within `.lore/` subdirs? (kebab-case, date prefix, feature name?)
- Should skills suggest related skills at the end, or stay fully independent?
