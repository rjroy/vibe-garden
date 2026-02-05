---
title: Socratic Agent Analysis
date: 2026-01-30
status: complete
tags: [agent-design, socratic, fresh-context, adversarial, spec-process]
modules: [lore-development]
related: [.lore/brainstorm/2026-01-30-socratic-agent-analysis.md, .lore/specs/fresh-lore-agent.md, .lore/specs/poke-holes-skill.md]
---

# Retro: Socratic Agent Analysis

## Summary

Analyzed a shared 245-line Socrates agent spec to determine what was useful and where concepts belonged. Discovered the spec conflated two distinct concerns (fresh context vs adversarial posture). Extracted and specified two focused tools: `fresh-lore` agent and `poke-holes` skill.

## What Went Well

- **Brainstorm-first approach worked**: Starting with open exploration before jumping to specs let the real structure emerge. The agent vs skill distinction wasn't obvious until we talked through it.

- **Fresh-eyes reviews caught real gaps**: The lore-docs-reviewer found the missing structure in poke-holes (the 7-steps compression lost too much). Would have shipped a diffuse skill without that check.

- **Iterating on reviewer feedback was efficient**: Pushing back on "critical" findings that were actually implementation details (agent development's job, not spec's job) kept the spec focused on WHAT not HOW.

- **The Max/Mara framing unlocked the design**: Naming the adversarial posture as "permission to be harsh" clarified that poke-holes isn't about Socratic method - it's about mode permission.

## What Could Improve

- **Wished for the tool we were building**: Multiple times wanted to invoke fresh-lore to get a side perspective without breaking context. The need validated the design.

- **Two spec passes in one session is heavy**: By the time we hit poke-holes, some fatigue. Could have split across sessions.

- **Exit criteria took two tries**: First pass was vague ("skill feels synthesis"). Reviewer caught it. Should probe exit conditions earlier in specify process.

## Lessons Learned

- **Agents are for fresh context, skills are for posture shifts**: If you need continuity, it's a skill. If you need fresh eyes, it's an agent. Don't conflate.

- **Structure isn't process**: poke-holes has an approach sequence (structure) but it's not a rigid process. The 6 steps are available moves, not a script. This distinction matters for skills.

- **Frustration is an exit signal**: When user pushes back hard on the same point repeatedly, that's not resistance to overcome - it's signal that enough pressure has been applied. Build this into adversarial tools.

- **"Too much detail" diffuses AI attention**: The original 245-line spec had encyclopedic sections (mental models table, bias catalog) that likely diluted effectiveness. Trust the weights; prompt for posture.

- **lore-development is a philosophy**: The plugin isn't just tools - it's a way of working. poke-holes completes the philosophy by adding adversarial mode to the existing expansive/convergent/reflective modes.

## Artifacts

- Source: `.lore/research/2026-01-26-socrates-agent.md` (original)
- Source: `.lore/research/2026-01-26-socrates-agent-v2.md` (simplified)
- Brainstorm: `.lore/brainstorm/2026-01-30-socratic-agent-analysis.md`
- Spec: `.lore/specs/fresh-lore-agent.md`
- Spec: `.lore/specs/poke-holes-skill.md`
