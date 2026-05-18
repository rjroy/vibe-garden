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
5. Save to `.lore/work/brainstorm/`

## Handling Sketches

If the user provides a sketch, diagram, or image:
- Consume it into the session
- Describe what you see
- Use it as fuel for the brainstorm
- Reference it in the saved document

## Output

Save to `.lore/work/brainstorm/[topic].html`

Use kebab-case. Track session dates in frontmatter meta tags, not filenames.

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get the HTML shell and frontmatter field definitions for brainstorms.

Copy the HTML base template verbatim. Fill in the `<meta>` tags and replace `<main>` with these sections:

```html
<main>
  <section id="context">
    <h2>Context</h2>
    <p>What prompted this exploration.</p>
  </section>

  <section id="ideas">
    <h2>Ideas Explored</h2>
    <details>
      <summary>[Idea 1 title]</summary>
      <p>Description and "what if" implications.</p>
    </details>
    <details>
      <summary>[Idea 2 title]</summary>
      <p>Description and trade-offs considered.</p>
    </details>
  </section>

  <!-- Include only if sketches were provided -->
  <section id="sketches">
    <h2>Sketches</h2>
    <p>Description of provided sketches or diagrams.</p>
  </section>

  <section id="open-questions">
    <h2>Open Questions</h2>
    <ul>
      <li>Question 1</li>
      <li>Question 2</li>
    </ul>
  </section>

  <!-- Optional -->
  <section id="next-steps">
    <h2>Next Steps</h2>
    <p>Where this might lead.</p>
  </section>
</main>
```

Use `<details>`/`<summary>` for individual ideas when there are multiple options to compare. The `open-questions` section receives the highlighted amber styling automatically from the base template.

## Context

Check `.lore/work/research/` for external context that might inform the brainstorm.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Domain experts can expand thinking in areas like security, architecture, or performance. Invoke relevant agents via Task tool and incorporate their insights.
