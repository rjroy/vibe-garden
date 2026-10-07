---
name: vision
description: This skill should be used when the user wants to define the north star for a project — why it exists, what problems it solves, what it would never become. Suited for the start of a project or when direction feels unclear. Triggers include "define the project vision", "what should this project become", "create a vision document", "what are we building toward".
---

# Vision

The vision is the north star. It doesn't define requirements or validate behavior — it tells you whether a decision is keeping with the spirit of the project or going against it.

If `.lore/reference/vision.md` already exists, load it and offer to review or revise.

## Two Paths

**Existing codebase**: Read broadly first — source code, `.lore/` artifacts, `CLAUDE.md`, README. Look for implicit values: what gets built, what gets rejected, what wins when things conflict. Draft from evidence. Where it's ambiguous, say so rather than inventing coherence.

**New project**: Walk through questions to pull the vision out. Adapt based on responses.

1. What is this project? Who does it serve? What problem does it solve that isn't solved elsewhere?
2. What matters most? If you had to name three things this project should always be, what are they?
3. What should this project never become? What reasonable-sounding ideas would you reject on principle?
4. Where do your values pull in opposite directions? When one conflicts with another, which wins by default?

Synthesize the user's own words into the document — don't replace their vocabulary with yours.

## Refinement

The first draft is a conversation starter. Probe:
- "Does this principle describe how you actually make decisions, or is it aspirational?"
- "Are these anti-goals things you'd genuinely reject, or just things you haven't prioritized yet?"

Principles should be behavioral guidelines, not trait aspirations. "We build for simplicity" is a trait. "Every new feature must justify the complexity it adds" is a guideline.

When the document has been reviewed at least once, offer to save. The user can keep refining or defer.

## Saving

Save to `.lore/reference/vision.md`. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields. Set `status: draft` for a new agent-created document; set `approved` only after explicit user approval (including editing to approve) or when the user asks for its relevant next process step. Arbitrary edits are not approval. Mark applicable work `completed` when the agent's work is done; completion does not imply user approval. Status is lifecycle, not maturity or correctness; current user direction can revise approved artifacts without approval becoming a veto or mandatory gate. Do not ask approval for minor transitions or every document. The document body is freeform: what the project is, what it values, what it refuses.

Write the body Markdown-first per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML only when a visual genuinely clarifies the north star.
