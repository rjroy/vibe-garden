---
name: design
description: Use when the user has a specific architecture, tool, or technique in mind and wants to explore whether and how it applies. Not full-feature design but a focused technical investigation of one element. Triggers include "design this", "I want to use X for this", "how should this work technically", and "explore this approach".
---

# Design

The user has something specific in mind: an architecture, a tool, a technique. This skill explores it technically — whether it fits, how it would work, what the tradeoffs are. It can be a slice of a feature, not necessarily the whole thing.

End with a decision. A design without one is just research.

## Saving

Save to `.lore/work/design/[topic].md` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields before writing.

Write the body Markdown-first per the "Body Format" section of `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`. Reach for embedded inline HTML when topology or trade-offs need it — inline-SVG architecture or flow diagrams that beat prose, and side-by-side visual comparison of competing options.
