---
title: Socratic Agent Analysis
date: 2026-01-30
status: resolved
tags: [agent-design, socratic, fresh-context, adversarial, poke-holes]
modules: [lore-development]
related: [.lore/specs/fresh-lore-agent.md, .lore/specs/poke-holes-skill.md]
---

# Socratic Agent Analysis

**Context**: Reviewed a shared Socrates agent spec; extracted two tools (fresh-lore agent, poke-holes skill) now ready for implementation

---

## The Spec Under Review

`.lore/research/2026-01-26-socrates-agent.md` - A ~245 line agent definition for "Socrates," a first principles reasoning partner focused on Socratic questioning, cognitive bias detection, and mental models.

## Initial Observations

**What works:**
- Clear identity: reasoning partner, not implementer
- "Don't prescribe, illuminate" stance is well-defined
- Differentiation from other agents (Morpheus, Hephaestus, Athena)
- Explicit boundaries in "What You Do NOT Do" section

**What feels heavy:**
- Length diffuses attention
- Mental models table and bias catalog read as reference material, not operational guidance
- Core Philosophy and Mission sections overlap
- 18 example questions in the Socratic Framework - encyclopedic rather than actionable

## Core Question: Agent vs Mode?

The sharer uses this as an agent, but the purpose feels more like a **posture** than a **task**.

- Agent implies: summon, task, return
- Mode/posture implies: shift how the conversation works, stay in it

Socratic questioning isn't completable. You're in it or you're not.

**Counterpoint**: Fresh context can be valuable. An adversarial reviewer benefits from not knowing what you've already tried or dismissed.

## Where Concepts Could Live

### For `/lore-development:brainstorm` (exploratory, generative)
- "Questions over answers" - core posture
- "Build on responses, don't redirect" - discipline
- "Ask one question at a time for complex topics" - pacing
- Current state: ~5% too many answers, ~5% too few questions (livable but not ideal)

### For a new "Break It" agent (adversarial, deconstructive)
- First principles deconstruction ("is this actually a requirement?")
- Inversion ("how does this fail?")
- "What would someone who disagrees say?"
- Permission to ignore "perfect is enemy of good" and push toward "perfect is the only option"

## The Max/Mara Framing

In past LLM generations, having distinct personas allowed balancing:
- **Max**: Find all faults, even slightly manufactured ones. Force thinking.
- **Mara**: Supportive, ensure coherence, give the user a break.

Claude's default leans Mara - agreeable, constructive, "here's how we improve this." That's appropriate most of the time. But sometimes you need Max, and have to explicitly break through politeness.

**Key insight**: The agent isn't about Socratic questioning or cognitive biases. It's about **permission to be adversarial**.

The Socrates spec is one way to get there, but it's overbuilt for that purpose. Core might just be: "Your job is to find what's wrong, not what's right. Assume the user wants to be challenged, not validated."

## On Labeling and Buzzwords

Concern: If you give AI terms, the terms get used regardless. Both AI and user can feel confident something was found when nothing was.

"This is anchoring" becomes performative - it sounds like insight without requiring engagement with substance.

**Resolution**: Labels aren't universally bad. "Confirmation bias" communicates something real. But excessive categorization becomes buzzword soup. Say what you mean rather than invoking taxonomy.

For any adversarial agent: show the crack in the foundation, don't announce the category of crack.

## Open Threads

1. **Scope of "break it"**: Is it about artifacts (specs, plans, code) or thinking (assumptions, reasoning, framing)? "This plan has gaps" vs "why do you believe this plan matters?"

2. **Agent vs skill**: Does fresh context help or hurt? Max benefits from not knowing your history. But a mode could be toggled mid-conversation.

3. **Relationship to existing tools**: `/spiral-grove:review` is going away (walled garden problem). `/lore-development:retro` might be the right place to evolve some of this.

4. **What's the actual name?** "Break it" is descriptive but not evocative.

---

## Conclusions

Two distinct tools emerged from this analysis:

| Tool | Type | Context | Job |
|------|------|---------|-----|
| `fresh-lore` | Agent | Fresh (isolated) | Run lore skills without conversation baggage, return findings without saving |
| `poke-holes` | Skill | Same (continuous) | Shift posture to find weaknesses in current thinking |

**Key insight**: The Socrates agent conflated two concerns:
1. Fresh context for review (agent pattern)
2. Adversarial posture for rigor (skill/mode pattern)

Separating these gives cleaner tools with clearer purposes.

**What to preserve from Socrates v2**:
- Philosophy section (condensed) → `poke-holes` skill
- Working approach → `poke-holes` skill
- Dialogue strategy → `poke-holes` skill
- "What You Do NOT Do" constraints → `poke-holes` skill

**What to discard**:
- Mental models table (encyclopedic, already in weights)
- Detailed bias catalog (say what you mean, don't invoke taxonomy)
- Question framework examples (18 examples is training data, not operational)

## Next Steps

- [x] Specify `fresh-lore` agent → `.lore/specs/fresh-lore-agent.md`
- [x] Specify `poke-holes` skill → `.lore/specs/poke-holes-skill.md`
- [ ] Implement `fresh-lore` agent via `/plugin-dev:agent-development`
- [ ] Implement `poke-holes` skill via `/plugin-dev:skill-development`
- [ ] Consider if brainstorm skill needs posture refinement (separate concern)
