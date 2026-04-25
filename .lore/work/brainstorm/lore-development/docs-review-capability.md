---
title: Documentation Review via Fresh Context
date: 2026-01-29
status: resolved
tags: [fresh-context, review, documentation, agents]
modules: [lore-development]
related: [.lore/work/plans/lore-development/docs-review-capability.md]
---

# Brainstorm: Documentation Review via Fresh Context

## Context

Lore-development is missing a concept: documentation should be reviewed with fresh eyes. In Claude Code, "fresh eyes" means a sub-agent with a clean context window. The main thread accumulates assumptions and mental models that can blind it to problems in its own output.

## Ideas Explored

### Review vs Validate

The existing `/lore-development:validate` skill is about correctness (did we follow the plan? what deviated?). Documentation review is about clarity (can someone else understand this without context?).

These are distinct operations:
- **Validate**: Checks against defined criteria, tracks deviations
- **Review**: "Read this as if you've never seen this codebase and tell me what's confusing"

### What Benefits from Fresh-Context Review

Ranked by value:
1. **Specs** - very high. Requirements that make sense to the author might be ambiguous to implementers.
2. **Plans** - high. Technical approach should be understandable without conversation history.
3. **CLAUDE.md** - high. Literally "context for fresh Claude", so fresh Claude is the test.
4. **Brainstorm/excavations** - low. Working notes, not meant for external consumption.

### Design Decision: Agent, Not Skill

Sub-agents inherently have fresh context. No skill wrapper needed because:
- Users can invoke agents directly ("use the lore-docs-reviewer agent")
- The `specify` and `plan` skills already consult `.lore/lore-agents.md` and invoke relevant agents
- Adding another skill would be redundant orchestration

### Integration via Agent Registry

The `lore-agents.md` pattern already exists. A `lore-docs-reviewer` agent:
- Gets documented in the registry by `update-lore-agents`
- Skills that produce reviewable artifacts (specify, plan) see it and can offer to invoke it
- Users can invoke it explicitly anytime

### Consistent Documentation

Update `update-lore-agents` skill to ensure `lore-docs-reviewer` is always documented the same way across projects. This gives skills reliable information about when to suggest it.

## Open Questions

- Should the agent have specific review lenses (clarity, completeness, consistency, actionability) or be open-ended?
- Should it return structured findings (like spiral-grove validators) or prose feedback?

## Next Steps

1. Create `lore-docs-reviewer` agent in `lore-development/agents/`
2. Update `update-lore-agents` skill to ensure consistent registry entry
3. Verify `specify` and `plan` skills already invoke registered agents appropriately
