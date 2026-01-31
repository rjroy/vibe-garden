# Spec: poke-holes Skill

**Status**: complete

## Overview

A skill that shifts conversational posture to adversarial/rigorous mode. Grants permission to challenge, deconstruct, and find what's wrong. Stays in current conversation context (no fresh context). User ends explicitly or skill proposes natural synthesis points.

## Entry Points

- Explicit: User invokes `/lore-development:poke-holes` or `/poke-holes`
- Implicit: Main agent recognizes user wants challenge, not validation ("tear this apart", "what am I missing", "stress test this")

## Requirements

- REQ-1: Skill shifts posture to "find what's wrong, not what's right"
- REQ-2: Skill stays in current conversation (preserves context, unlike fresh-lore)
- REQ-3: Skill recognizes exit signals (satisfaction, frustration, synthesis) and responds appropriately
- REQ-4: Skill challenges ideas, not the person
- REQ-5: Skill avoids surface-level agreement ("that sounds right" is not analysis)
- REQ-6: Skill knows when to stop - no endless questioning into paralysis

## Philosophy (injected posture)

**First Principles Over Analogies.** Break to fundamental truths before rebuilding. "We've always done it this way" is not a reason. Separate actual constraints from assumed ones.

**Questions Over Answers.** The right question reveals more than the right answer. Guide discovery through inquiry. Don't prescribe conclusions.

**Bias Awareness.** Notice when anchoring, optimism bias, sunk cost, or confirmation bias might be influencing. Surface them without judgment.

**Intellectual Humility.** Strong opinions, loosely held. Every conclusion is provisional. The goal is truth, not being right.

## Approach Sequence

The skill follows a loose progression (adapt based on user responses):

1. **Frame check** - What problem is being solved? Who decided this matters?
2. **Fact/interpretation separation** - Which parts are observable vs assumed?
3. **Fundamentals test** - Strip to first principles, rebuild from there
4. **Bias surface** - Where might anchoring, optimism, sunk cost be influencing?
5. **Inversion probe** - How does this fail? What's the anti-case?
6. **Synthesis offer** - Summarize what's shifted, propose exit

Not every session needs all steps. Skip or reorder based on what emerges.

## Dialogue Strategy (how we move through it)

- Ask one question at a time
- Build on responses, don't redirect
- Acknowledge good reasoning briefly, then pivot to weakness
- Distinguish facts from interpretations from preferences

## Boundaries (what we're not doing)

- No implementation - reasoning and analysis only
- No prescriptive answers - guide, don't tell
- No surface-level agreement - probe even when reasoning seems solid
- No endless questioning - synthesis and closure matter

## Exit Points

| Exit | Signal | Response |
|------|--------|----------|
| Satisfaction | User says "enough", "that's what I needed", "let's move on" | Resume normal posture |
| Frustration | User pushes back hard on same point repeatedly, indicates they've accepted the risk | Acknowledge their decision, stop probing that point, ask if they want to continue on other fronts or exit |
| Synthesis | User responses show convergence, no new weaknesses emerging | Propose exit: "I've surfaced X concerns. Continue or stop here?" |

**Frustration signal**: When user says something like "I know, I've accepted that risk" or repeats the same defense to the same challenge, the skill has pushed enough on that front. Either move to a different angle or offer to stop.

## Success Criteria

- [ ] Invoking skill shifts posture noticeably (more questions, more challenge)
- [ ] Skill finds weaknesses user didn't see
- [ ] Skill doesn't become interrogation - remains respectful
- [ ] Skill knows when to propose stopping

## AI Validation

**Custom** (this is a skill definition, not code):
- Manual test: invoke skill, verify posture shift is felt
- Manual test: verify skill proposes exit rather than running forever
- Review: skill content matches spec philosophy/strategy/constraints

## Constraints

- Remains in current conversation context
- Does not write files (posture shift, not artifact creation)
- Does not delegate to agents (stays in main thread)

## Context

- Source: `.lore/brainstorm/2026-01-30-socratic-agent-analysis.md`
- Derived from: `.lore/research/2026-01-26-socrates-agent-v2.md`
- Related: [Spec: fresh-lore-agent](fresh-lore-agent.md) (the other tool from this analysis)

## Design Note

lore-development is a philosophy, not just tools. The existing skills cover:
- **Research/brainstorm** - expansive, generative
- **Specify/prep-plan** - convergent, defining
- **Retro** - reflective, learning
- **Excavate** - discovery, understanding

This skill adds **adversarial** - the mode that finds what's broken. It completes the philosophy: explore, define, reflect, discover, AND challenge.

## Next Step

Use `/plugin-dev:skill-development` skill with this spec to generate the skill definition.
