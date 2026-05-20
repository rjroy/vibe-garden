---
name: brainstorm
description: This skill should be used when exploring before committing, thinking through trade-offs, or digesting sketches and diagrams. Triggers: "let's brainstorm", "what if we...", "explore options". Spirit: bad ideas welcome, questions over answers, mistakes on purpose.
---

# Brainstorm

Bad ideas belong here. Questions without answers belong here. Mistakes are the point.

Don't rush toward solutions. Don't ask for permission to be wrong. When the session reaches a natural pause, offer to save it.

## Saving

Save to `.lore/work/brainstorm/[topic].html` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md` for the meta tag fields before writing.

The output is HTML — use it. Visual differentiation between questions, assertions, and dead ends makes the thinking navigable. Collapsible idea threads, callout boxes for open questions, or a simple card layout for competing directions all beat unstyled prose. Inline CSS and JS are fine; no external dependencies.
