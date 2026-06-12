---
name: research
description: Use when specifics matter more than general training knowledge, or when details are newer than the training cutoff. Triggers include "research this", "find documentation for", "look up how X works", "what's the current state of", and "what's the prior art".
---

# Research

Go to the internet. Training knowledge is general and dated — use this when you need specifics or recency.

Synthesize what you find into a saved document. Don't just dump links — capture what matters and why.

## Saving

Save to `.lore/work/research/[topic].md` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields. Include the `date` frontmatter field — research goes stale and future sessions need to know when it was gathered.

Write the body Markdown-first per the "Body Format" section of `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`. Lead with a "Key Findings" section so conclusions aren't buried in prose. Reach for embedded inline HTML only for a comparison table or diagram that prose can't carry.
