---
name: research
description: This skill gathers context from outside the project scope. Use for exploring external documentation, finding prior art, understanding libraries or frameworks, or gathering reference material. Triggers include "research this", "find documentation for", "what's the prior art", "look up how X works".
---

# Research

Gather context from outside the project scope.

## When to Use

- Exploring external documentation or APIs
- Finding prior art or existing solutions
- Understanding libraries, frameworks, or tools
- Gathering reference material

## Process

1. Clarify what the user wants to research if unclear
2. Use web search, fetch docs, or read external resources
3. Synthesize findings into a research document
4. Save to `.lore/work/research/`

## Output

Save findings to `.lore/work/research/[topic].html`

Use kebab-case for filenames. Use the `lore-date` meta tag for time-sensitive research.

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get the HTML shell and frontmatter field definitions for research.

Copy the HTML base template verbatim. Replace `<main>` with these sections:

```html
<main>
  <section id="summary">
    <h2>Summary</h2>
    <p>Brief overview of what was found.</p>
  </section>

  <section id="findings">
    <h2>Key Findings</h2>
    <ul>
      <li>Finding 1</li>
      <li>Finding 2</li>
    </ul>
  </section>

  <section id="sources">
    <h2>Sources</h2>
    <ul>
      <li><a href="[url]">[Source name]</a></li>
    </ul>
  </section>

  <section id="notes">
    <h2>Notes</h2>
    <p>Any additional context or observations.</p>
  </section>
</main>
```

Research is a simple artifact. No collapsibles needed.

## Context

Check `.lore/work/brainstorm/` for related ideas that prompted this research.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help focus research. Domain experts can identify what's worth investigating and what to prioritize. Invoke relevant agents via Task tool and incorporate their insights.
