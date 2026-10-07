---
name: brainstorm
description: Use when exploring before committing, thinking through trade-offs, or digesting sketches and diagrams. Triggers include "let's brainstorm", "what if we...", and "explore options". Bad ideas welcome, questions over answers, mistakes on purpose.
---

# Brainstorm

Bad ideas belong here. Questions without answers belong here. Mistakes are the point.

Don't rush toward solutions. Don't ask for permission to be wrong. When the session reaches a natural pause, offer to save it.

## Saving

Save to `.lore/work/brainstorm/[topic].md` using kebab-case. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields before writing. New documents start `draft`; use `approved` only for explicit user approval (including editing to approve) or a request for the relevant next process step, never infer it from arbitrary edits. Use `completed` when applicable agent work is done, independently of approval; use `archived` when archived. Status tracks lifecycle, not maturity/correctness. Current user direction may revise approved artifacts; approval is not a veto or mandatory gate. Don't ask approval for minor transitions or every document.

Write the body Markdown-first per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML only when a sketch or diagram carries the idea in a way prose can't.
