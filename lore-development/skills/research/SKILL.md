---
name: research
description: This skill should be used when specifics matter more than general training knowledge, or when details are newer than the training cutoff. Triggers: "research this", "find documentation for", "look up how X works", "what's the current state of", "what's the prior art".
---

# Research

Go to the internet. Training knowledge is general and dated — use this when you need specifics or recency.

Synthesize what you find into a saved document. Don't just dump links — capture what matters and why.

## Saving

Save to `.lore/work/research/[topic].html` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md` for the meta tag fields. Include the `date` meta — research goes stale and future sessions need to know when it was gathered.

The output is HTML — use it. A freshness badge near the title, collapsible source summaries, a prominent "Key Findings" section above the detail. Research that buries its conclusions in prose gets skipped. Inline CSS and JS are fine; no external dependencies.
