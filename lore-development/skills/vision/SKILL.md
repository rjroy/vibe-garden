---
name: vision
description: Defines the north star for a project. Why does it exist? What problems is it solving? What would it never become? Use at the start of a project or when direction feels unclear. Triggers: "define the project vision", "what should this project become", "create a vision document", "what are we building toward".
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

Save to `.lore/reference/vision.md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields. Set `status: draft` — the user marks it approved, not you. The document body is freeform: what the project is, what it values, what it refuses.
