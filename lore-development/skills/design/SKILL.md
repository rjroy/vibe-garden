---
name: design
description: This skill should be used when the user has a specific architecture, tool, or technique in mind and wants to explore whether and how it applies. Not full-feature design — a focused technical investigation of one element. Triggers: "design this", "I want to use X for this", "how should this work technically", "explore this approach".
---

# Design

The user has something specific in mind: an architecture, a tool, a technique. This skill explores it technically — whether it fits, how it would work, what the tradeoffs are. It can be a slice of a feature, not necessarily the whole thing.

End with a decision. A design without one is just research.

## Saving

Save to `.lore/work/design/[topic].html` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md` for the meta tag fields before writing.

The output is HTML — use it. Tabbed sections for alternatives under consideration, side-by-side comparison tables for trade-offs, a prominent callout box for the final decision. Architecture or flow diagrams rendered as inline SVG beat description alone when topology is what matters. Inline CSS and JS are fine; no external dependencies.
