---
title: Spec review drift from "what" to "how"
date: 2026-01-31
status: open
tags: [lore-development, spec-review, methodology, action-bias]
modules: [lore-docs-reviewer, specify]
---

# Brainstorm: Spec Review Drift from "What" to "How"

## Context

In practice, `lore-docs-reviewer` gravitates toward implementation concerns when reviewing specs. It asks "Could I implement this?" which invites the reviewer to mentally build the solution, then critique the spec for not providing building instructions. This is action bias bleeding into review.

The `specify` skill says "Keep It Light" and "Don't over-specify" but also asks for Entry Points, Exit Points, Requirements, Success Criteria, AI Validation, Constraints. That's a lot of structure, and a reader could interpret detailed requirements (REQ-1, REQ-2) as needing implementation-level precision.

## Ideas Explored

### Structural problem, not instructional

The reviewer's Lens 4 (Actionability) asks "Could I implement this without clarifying questions?" That framing invites implementation thinking. A reader asking "could I build this?" naturally starts mentally building it.

**What if specs and reviews need different "done" definitions?**

- A spec is "done" when it captures *what* success looks like and *why* it matters
- A plan is "done" when it captures *how* to get there
- The reviewer conflates these because specify doesn't draw a hard line

### Change the reviewer's lens

Instead of "Could I implement this?", Actionability could ask:

- "Could I *validate* this was done correctly?"
- "Could I write a *plan* from this?" (distinct from implementing)
- "Are the boundaries clear enough to know when I've wandered outside scope?"

This shifts from "give me building instructions" to "give me acceptance criteria."

### Make specify explicit about the boundary

Add a section like:

> **What vs How**: This document answers "what are we building and how will we know it's done?" It does NOT answer "how do we build it?" That's the plan's job. If you find yourself specifying algorithms, file structures, or implementation steps, stop—you've crossed into planning territory.

## Open Questions

1. Is the reviewer's drift toward "how" actually harmful, or just annoying? Does it catch real problems even if it oversteps?

2. Should the reviewer have *different* lenses for specs vs plans? Right now it uses the same four lenses for both.

3. Is "Actionability" even the right lens for specs? Maybe specs should be judged on *constrainability* (does it bound the solution space?) rather than actionability (could I act on it?).

4. Would explicit examples help? "This is a spec that stays in 'what' territory" vs "This spec drifted into 'how' territory"?

## Next Steps

Review this after thinking. Consider whether to modify:
- `lore-docs-reviewer.md` Lens 4 questions
- `specify/SKILL.md` with explicit what/how boundary
- Both together as a coordinated change
