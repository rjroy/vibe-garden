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
4. Save to `.lore/research/`

## Output

Save findings to `.lore/research/[topic].md`

Use kebab-case for filenames. Include date if the research is time-sensitive (e.g., `react-19-changes-2026-01.md`).

### Document Structure

Keep it simple:

```markdown
# Research: [Topic]

## Summary
Brief overview of what was found.

## Key Findings
- Finding 1
- Finding 2

## Sources
- [Source name](url)

## Notes
Any additional context or observations.
```

## Context

Check `.lore/brainstorm/` for related ideas that prompted this research.
