---
name: research
description: Use when specifics matter more than general training knowledge, or when details are newer than the training cutoff. Triggers include "research this", "find documentation for", "look up how X works", "what's the current state of", and "what's the prior art".
---

# Research

Go to the internet. Training knowledge is general and dated — use this when you need specifics or recency.

Synthesize what you find into a saved document. Don't just dump links — capture what matters and why.

## Saving

Save to `.lore/work/research/[topic].md` using kebab-case. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields. New documents start `draft`; use `approved` only for explicit user approval (including editing to approve) or a request for the relevant next process step, never infer it from arbitrary edits. Use `completed` when applicable agent work is done, independently of approval; use `archived` when archived. Status tracks lifecycle, not maturity/correctness or freshness; `fg-status` is separate field-guide freshness. Current user direction may revise approved artifacts; approval is not a veto or mandatory gate. Don't ask approval for minor transitions or every document. Include the `date` frontmatter field — research goes stale and future sessions need to know when it was gathered.

Write the body Markdown-first per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Lead with a "Key Findings" section so conclusions aren't buried in prose. Reach for embedded inline HTML only for a comparison table or diagram that prose can't carry.
