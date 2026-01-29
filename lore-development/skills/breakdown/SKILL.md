---
name: breakdown
description: This skill decomposes work into releasable chunks. Use for breaking specs into implementable pieces, organizing work into logical phases, or identifying incremental release boundaries. Triggers include "break this down", "decompose the work", "what are the tasks", "chunk this into pieces".
---

# Breakdown

Decompose work into releasable chunks.

## When to Use

- Breaking a spec into implementable pieces
- Organizing work into logical phases
- Identifying what can be released incrementally

## Process

1. Review the relevant spec in `.lore/specs/`
2. Identify natural boundaries in the work
3. Chunk into pieces that could be released independently
4. Order by dependencies or value
5. Save to `.lore/work/`

## Output

Save to `.lore/work/[feature-name].md`

### Document Structure

```markdown
# Work Breakdown: [Feature Name]

Spec: `.lore/specs/[feature-name].md`

## Chunks

### 1. [Chunk Name]
**What**: Brief description
**Delivers**: What's usable after this chunk
**Depends on**: Any prerequisites

### 2. [Chunk Name]
**What**: Brief description
**Delivers**: What's usable after this chunk
**Depends on**: Any prerequisites

## Suggested Order
1. Chunk name (reason)
2. Chunk name (reason)
```

## Principles

- Each chunk should deliver something usable or testable
- Smaller is better - aim for chunks that take hours, not days
- Don't over-plan - enough detail to start, refine as you go

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Architecture or sizing experts can validate chunk boundaries and dependencies. Invoke relevant agents via Task tool and incorporate their insights.
