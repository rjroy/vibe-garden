---
title: Implementation skill as orchestrator with agent delegation
date: 2026-02-05
status: resolved
tags: [implementation, orchestrator, agents, testing, code-review, notes]
modules: [lore-development]
---

# Brainstorm: Implementation Skill Orchestrator Model

## Context

Exploring what the implementation phase should enforce beyond "take the plan and go." Three enforcement points: testing, code review, and implementation notes. The first two are obvious. The third required thought: what is an implementation note, and how does it get written without degrading the work?

## Ideas Explored

### Implementation Notes as Decision Dust

During implementation, dozens of small decisions never make it into commits, tests, or specs. Things like:
- "Tried approach X, didn't work because Y"
- "This API behaves differently than documented"
- "Chose this data structure because the alternative had Z trade-off"

These evaporate between sessions. Code says *what*, tests say *what should happen*, but nobody records *why this way and not that way*. Notes sit between code comments (explain the code) and ADRs (architectural decisions). They're tactical decisions too small for an ADR but too important to lose.

### Context Poisoning Problem

If the AI writes notes *during* implementation, every note competes for context window space with the code it's trying to write. More notes = less room for implementation context. This isn't time fatigue, it's *thinking capacity* fatigue. The act of being thorough about recording could degrade the quality of the decisions themselves.

### The Reframe: Orchestrator Model

Instead of one agent doing implementation + notes, separate the concerns entirely:

**Orchestrator (main agent):** Holds the full plan, dispatches phases one at a time, records what happened. Its entire job is coordination and recording. Notes aren't a side effect, they're the primary output.

**Implementation agent:** Gets a single phase, executes, reports what it did and why. Doesn't see the full plan. Doesn't make sequencing decisions.

**Testing agent:** Gets the code, reports findings clean. No log dumps. Hints at cause when useful.

**Review agent:** Gets the code, reports non-conformances. Nothing else.

This solves context poisoning by design. Each agent only holds what it needs. The orchestrator only holds coordination state and the narrative. Nobody's context is polluted with someone else's job.

### Orchestrator Responsibilities

Maintains three things:
1. **Progress tracker** - what's done
2. **Implementation notes** - what happened and why
3. **Divergence log** - should be empty, but tracked when reality forces deviation from plan

Routes work: test failure goes back to implementation with the finding. Review concern goes back to implementation with the concern. Pass moves to next phase.

### Escalation Rules (Human Intervention)

Two triggers, everything else is autonomous:
- **Stuck loop:** Implementation can't resolve what testing/review keeps finding after multiple attempts. The orchestrator recognizes the cycle isn't converging.
- **Plan divergence:** Reality requires something the plan didn't account for. The orchestrator can't authorize changing the plan, only following it.

### Note Format: Structured Minimalism

Constraint prevents note fatigue. The orchestrator's log is the natural output:

```
- Dispatched: implement auth middleware per plan step 3
- Result: agent chose JWT over session tokens, noted plan didn't specify
- Dispatched: tests for auth middleware
- Result: 2 failures - token expiry edge case, missing header handling
- Dispatched: fix token expiry and missing header
- Result: fixed, also discovered framework validates headers automatically
- Dispatched: re-test → passing
- Dispatched: code review
- Result: flagged const correctness on 2 functions, no architectural concerns
- Dispatched: address review feedback → applied
```

### Notes Have a TTL

Purpose is retro fuel. Implementation notes get consumed by the retro, and the retro is the durable artifact. Notes can archive after the retro extracts value. Keeps `.lore/notes/` from becoming a graveyard of stale context.

## Open Questions

- One note file per feature/plan, or per session?
- What threshold does the orchestrator use for "stuck loop" detection? N failures on the same issue?
- How much plan context does the orchestrator feed to implementation? Confirmed: one phase at a time, not the full plan.
- Should notes reference the plan they came from, enabling the retro to diff plan vs reality automatically?

## Next Steps

- Specify the implementation skill design (orchestrator behavior, agent contracts, note format, escalation rules)
- Design the agent interfaces: what each agent receives and what it reports back
- Define the note-to-retro consumption pipeline
