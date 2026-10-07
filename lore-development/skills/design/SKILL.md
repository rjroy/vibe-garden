---
name: design
description: Use when the user has a specific architecture, tool, or technique in mind and wants to explore whether and how it applies. Not full-feature design but a focused technical investigation of one element. Triggers include "design this", "I want to use X for this", "how should this work technically", and "explore this approach".
---

# Design

The user has something specific in mind: an architecture, a tool, a technique. This skill explores it technically — whether it fits, how it would work, what the tradeoffs are. It can be a slice of a feature, not necessarily the whole thing.

End with a decision. A design without one is just research.

## Saving

Save to `.lore/work/design/[topic].md` using kebab-case. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields before writing. New documents start `draft`; use `approved` only for explicit user approval (including editing to approve) or a request for the relevant next process step, never infer it from arbitrary edits. Use `completed` when applicable agent work is done, independently of approval; use `archived` when archived. Status tracks lifecycle, not maturity/correctness. Current user direction may revise approved artifacts; approval is not a veto or mandatory gate. Don't ask approval for minor transitions or every document.

Write the body Markdown-first per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML when topology or trade-offs need it — inline-SVG architecture or flow diagrams that beat prose, and side-by-side visual comparison of competing options.

After saving, use Claude Code's current `Agent` tool with `subagent_type: "lore-development:design-reviewer"` in
`initial-review` mode on the saved design; on versions without `Agent`, use `Task` with
the same fully qualified `subagent_type`. If the bundled agent is unavailable, use
`Agent` (or older-version `Task`) with `subagent_type: "general-purpose"` and the role
from `${CLAUDE_PLUGIN_ROOT}/agents/design-reviewer.md`. If
findings are corrected, invoke `verification` mode with the complete unresolved
finding records and changed sections. After those findings close, run one
terminal broad acceptance review. Corrections from that review receive targeted
verification with their complete finding records; do not run another broad
review unless accepted scope changed.
