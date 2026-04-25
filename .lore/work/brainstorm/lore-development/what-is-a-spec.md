---
title: What is a spec? Design as a separate tool
date: 2026-02-03
status: resolved
tags: [methodology, spec, design, workflow, lore-development]
modules: [lore-development]
related: [.lore/work/brainstorm/lore-development/spec-review-what-vs-how.md]
---

# Brainstorm: What is a spec?

## Context

The lore-development workflow has brainstorm, research, and specify. But what exactly is a spec? There's PRD (what), TDD (how), and then implementation (plan mode). Where does design fit?

The trigger: some requirements are trivial to implement ("button for Daily Prep on Ground Tab") while others *are* the problem ("algorithm for deduplication of persistent history and active stream data"). The button needs a spec. The algorithm needs a design.

## Ideas Explored

### Spec vs Design distinction

- **Spec (PRD-level)**: What does the user need? What does "done" look like? Acceptance criteria. Can be written without knowing how to solve the problem.
- **Design (TDD-level)**: How will we achieve this? What's the algorithm? Data structures? Trade-offs? Requires deep understanding of the problem.

Current `/specify` does PRD-level work. That's sufficient for trivial implementations. Complex problems need design work *before* plan mode.

### The "100 forks" test

If you ran `/prep-plan` 100 times with the current context:
- **Without enough context**: Plans diverge wildly, AI invents different solutions
- **With enough context**: Plans converge, AI finds the obvious solution

Design exists to make the 100 forks converge for problems where spec alone doesn't provide enough constraint.

### Lore Development is a toolbox, not a pipeline

Key insight: the skills aren't steps in a process. They're tools you reach for as needed.

```
brainstorm  →  broaden (questions)
research    →  narrow (examples)
specify     →  answer (requirements)
design      →  answer deeper (technical decisions)
prep-plan   →  load answers → implement
```

Any order. Any combination. Skip what you don't need. The context accumulates in `.lore/`. When you have enough that `/prep-plan` yields consistent plans, you're ready.

### ADRs live in the documents that spawn them

In lore-dev, you don't need a separate ADR folder. Decisions emerge from:
- Retros (when something goes wrong)
- Designs (when something needs deciding)

The decision lives in context where it matters.

### When to use design vs skip it

**Needs design:**
- Algorithms (non-trivial logic)
- Data structures (how things relate)
- System boundaries (where does it live?)
- Performance-sensitive code
- Security-sensitive code

**Skip design:**
- UI changes where spec describes outcome
- CRUD operations
- Wiring existing pieces together
- Config changes

## Open Questions

1. What does the `/design` skill look like? What's its output structure?
2. How does design relate to diagrams? (Maybe `/ddp` becomes part of design workflow?)
3. Should design documents link back to specs, or can they stand alone?

## Next Steps

- Create `/design` skill
- Design documents live in `.lore/work/design/`
- Status values: `draft`, `approved`, `implemented`, `superseded` (already added to frontmatter schema)
