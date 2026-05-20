---
name: research
description: Pulls context from the internet. Use when specifics matter more than general training knowledge, or when details are newer than the training cutoff. Triggers: "research this", "find documentation for", "look up how X works", "what's the current state of".
---

# Research

Go to the internet. Training knowledge is general and dated — use this when you need specifics or recency.

Synthesize what you find into a saved document. Don't just dump links — capture what matters and why.

## Saving

Save to `.lore/work/research/[topic].md` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields. Use the `date:` field — research goes stale and future sessions need to know when it was gathered. The document body is freeform.
