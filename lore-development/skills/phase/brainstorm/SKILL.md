---
name: brainstorm
description: This skill explores ideas and possibilities, recording "what if" scenarios. Use when brainstorming approaches, thinking through trade-offs, consuming sketches or diagrams into a session, or exploring before committing. Triggers include "let's brainstorm", "what if we...", "explore options for", "think through possibilities".
---

# Brainstorm

Record exploratory conversation. Emphasize "what if" over raw solutions.

## When to Use

- Exploring possibilities before committing to an approach
- Thinking through trade-offs
- Recording ideas for later reference
- Consuming sketches, diagrams, or visual input into the session

## Process

1. Engage in exploratory dialogue
2. Ask "what if" questions to expand thinking
3. Don't rush to solutions - sit with possibilities
4. When the brainstorm reaches a natural pause, offer to save it
5. Save to `.lore/brainstorm/`

## Handling Sketches

If the user provides a sketch, diagram, or image:
- Consume it into the session
- Describe what you see
- Use it as fuel for the brainstorm
- Reference it in the saved document

## Output

Save to `.lore/brainstorm/[topic].md`

Use kebab-case. Track session dates in frontmatter, not filenames.

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for brainstorms.

```markdown
---
[frontmatter per schema]
---

# Brainstorm: [Topic]

## Context
What prompted this exploration.

## Ideas Explored
- Idea 1: description and "what if" implications
- Idea 2: description and trade-offs considered

## Sketches
(If any were provided, describe them here)

## Open Questions
Questions that emerged but weren't resolved.

## Next Steps
(Optional) Where this might lead.
```

## Context

Check `.lore/research/` for external context that might inform the brainstorm.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Domain experts can expand thinking in areas like security, architecture, or performance. Invoke relevant agents via Task tool and incorporate their insights.
