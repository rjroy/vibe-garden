---
name: plan
description: This skill creates implementation plans by gathering project context and saving planning sessions. Use when ready to plan implementation, thinking through technical approach, or wanting to capture planning decisions. Triggers include "plan the implementation", "how should we build this", "create a plan for", "think through the approach".
---

# Plan

Direct the AI's planning capabilities with project context, then save the output.

## When to Use

- Ready to plan implementation for a chunk of work
- Want to capture a planning session for future reference
- Need to think through technical approach

## Process

1. Gather context from `.lore/`:
   - Relevant specs from `.lore/specs/`
   - Work breakdown from `.lore/work/`
   - Research from `.lore/research/`
   - Brainstorms from `.lore/brainstorm/`
2. Present this context to inform planning
3. Plan the implementation (use native planning capabilities)
4. Save the plan to `.lore/plans/`

## Output

Save to `.lore/plans/[feature-or-chunk-name].md`

### Document Structure

```markdown
# Plan: [Feature/Chunk Name]

## Context
Links to relevant `.lore/` documents.

## Approach
High-level approach and key decisions.

## Steps
1. Step one
2. Step two
3. ...

## Considerations
Any technical decisions, trade-offs, or risks noted.
```

## Philosophy

This skill doesn't teach planning - the AI already knows how to plan. It ensures:
1. Relevant project context is loaded
2. The plan gets saved for future reference
3. Decisions are documented
