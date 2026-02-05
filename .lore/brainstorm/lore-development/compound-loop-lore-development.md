---
title: Compound Loop for Lore-Development
date: 2026-01-30
status: resolved
tags: [methodology, compound-loop, knowledge-management, feedback-loop]
modules: [lore-development]
related: [.lore/specs/lore-development/lore-researcher-agent.md]
---

# Brainstorm: Compound Loop for Lore-Development

## Context

Explored Every.to's compound-engineering approach after reading their article and examining their Claude Code plugin. The core question: what makes knowledge compound, and how can lore-development achieve this without over-engineering?

**Source material reviewed**:
- Article: https://every.to/source-code/compound-engineering-how-every-codes-with-agents-af3a1bae-cf9b-458e-8048-c6b4ba860e62
- Plugin: https://github.com/EveryInc/compound-engineering-plugin
- Key skill: compound-docs (auto-captures solved problems with YAML-validated frontmatter)

## Ideas Explored

### The Compound Step is the Competitive Advantage

Compound-engineering's loop: Plan → Work → Review → Compound. The "compound" step (documenting solved problems) is what creates the feedback loop. Most teams treat documentation as optional; here it's required and feeds the next cycle.

**Key insight**: The planning gets better because it has documented learnings to draw from. The compounding happens not in the capture, but in the retrieval during planning.

### Lore-Development's Gap: The Feedback Wire

Lore-development has context collection (research, brainstorm, excavate, specify, retro) but the loop doesn't close. The `/retro` captures lessons, but nothing forces those lessons to surface during new work.

**What's missing**: Automatic retrieval of past learnings during `/specify` and `/prep-plan`.

### The Minimal Compound Loop

Three requirements for compounding:
1. **Capture** - Write down what you learned (`/retro` does this)
2. **Store** - Put it somewhere findable with queryable structure (`.lore/retros/` with frontmatter)
3. **Retrieve** - Automatically consult it before new work (missing piece)

### Agent for Retrieval (Not Capture)

Fresh context for search is a feature, not a bug. A search agent can find related retros without polluting the main conversation context.

**Proposed**: `lore-researcher` agent spawned by `/specify` and `/prep-plan` to grep `.lore/retros/` for related work before the human starts writing.

### Skepticism of Over-Engineering

Compound-engineering has 30+ agents, 6 parallel agents for documentation, blocking YAML validation gates, and auto-invoke on phrase detection. This creates:
- Maintenance burden (each agent can drift)
- Coordination costs (agents need to know about each other)
- False confidence ("ran 6 reviewers so must be good")
- Brittleness disguised as precision

**Counter-position**: Fewer tools with better composition beats many specialized agents. The right number might be closer to 5 than 50.

### Auto-Invocation is Unreliable

Triggering on "that worked" sounds elegant but hits reality:
- Fires during debugging (not final fix)
- Misses actual fixes with different phrasing
- User ends up manually invoking anyway

When everything is implicit, nothing is reliable.

## Proposed Changes

### Retro Frontmatter (Minimal)

```yaml
---
title: N+1 query in brief generation
date: 2026-01-30
status: complete
tags: [performance, database, eager-loading]
modules: [brief-system, email-processing]
---
```

No schema validation gate. No enum enforcement. Grep finds what matches; missed matches have low cost.

### lore-researcher Agent

**Input**: Feature description or spec topic

**Process**:
1. Extract keywords (modules, problem indicators, technical terms)
2. Grep `.lore/retros/` frontmatter for matches
3. Optionally scan `.lore/specs/` for related prior work
4. Read matched files, distill to summaries

**Output**: Related learnings with file paths and key insights

**Invoked by**: `/specify` and `/prep-plan`, early in their flow

### Skill Modifications

**`/specify`**: Spawn lore-researcher agent with topic before defining requirements. Include findings in spec Context section.

**`/prep-plan`**: Spawn lore-researcher agent before entering plan mode. Surface lessons that might constrain the plan.

**`/retro`**: Ensure frontmatter includes: title, date, tags, modules.

## Open Questions

- Should the agent also search `.lore/brainstorm/` and `.lore/specs/` for related context?
- What's the right threshold for "related"? Strict keyword match vs. semantic similarity?
- Should findings be mandatory to acknowledge, or just surfaced for optional review?
- Does `/retro` need refinement, or is it working well enough as-is?

## Next Steps

1. Review current `/retro` output format - does it produce usable frontmatter?
2. Create `lore-researcher` agent with minimal scope
3. Wire it into `/specify` and `/prep-plan`
4. Test the loop: retro → new spec → did the lesson surface?

## References

- Compound-engineering plugin source: https://github.com/EveryInc/compound-engineering-plugin
- compound-docs skill: demonstrates YAML-validated capture (more complex than we need)
- learnings-researcher agent: demonstrates grep-first search strategy (good pattern, over-specified)
