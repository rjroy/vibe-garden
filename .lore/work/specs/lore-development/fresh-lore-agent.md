---
title: fresh-lore Agent
date: 2026-01-30
status: implemented
tags: [agent-design, fresh-context, review, analysis]
modules: [lore-development]
related: [.lore/work/brainstorm/lore-development/socratic-agent-analysis.md]
---

# Spec: fresh-lore Agent

## Overview

An agent that provides fresh-context analysis using lore-development skills. Used when current conversation is too deep in the weeds to think clearly about a question. Returns findings to a temp file without modifying project files.

## Entry Points

- Explicit: User asks for fresh perspective ("get fresh eyes on this", "have fresh-lore look at...")
- Implicit: Main agent recognizes it needs a second opinion on something it's too close to

**Example triggers for implicit invocation:**
- "We keep going in circles on this"
- "Something feels off but I can't articulate it"
- "Is this spec actually coherent or am I too close to it?"

## Requirements

- REQ-1: Agent has access to lore-development skills: specify, brainstorm, retro, ddp, research, define-validation (via `Skill(lore-development:*)` or equivalent in allowedTools)
- REQ-2: Agent can ONLY write to `/tmp/` - no project file modifications (enforced by instruction, not filesystem)
- REQ-3: Agent returns findings as a temp file path that invoker reads (no conversation summary)
- REQ-4: Agent receives context via Task tool invocation (file paths, questions, concerns) but NOT the conversation history
- REQ-5: Agent knows which skill applies to which type of question (see guidance table)
- REQ-6: Temp file naming includes what was analyzed to prevent overwrites (e.g., `fresh-lore-checkout-flow-spec-2026-01-30-143022.md`)
- REQ-7: If file already exists, append counter suffix (-1, -2, etc.)

## Skill Invocation Guidance

| Skill | When to use |
|-------|-------------|
| `specify` | "Is this spec complete? What's missing?" |
| `brainstorm` | "Explore this question without our existing assumptions" |
| `retro` | "What can we learn from what just happened?" |
| `ddp` | "Visualize this flow/relationship to see if it makes sense" |
| `research` | "What external context would help here?" |
| `define-validation` | "How would we know this is actually working?" |

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Return file path | Analysis complete | Path to `/tmp/fresh-lore-[subject]-[timestamp].md` |
| Escalate confusion | Agent can't make sense of input | Message back to invoker explaining what's missing; invoker decides to retry with more context or abort |

## Behavior: No Summary

The agent writes findings to the temp file and returns ONLY the file path. It does not summarize in conversation. This forces the invoker to read the actual findings rather than skimming a summary and assuming it understood.

## Success Criteria

- [ ] Agent can invoke any of the 6 listed skills
- [ ] All output goes to `/tmp/`, never to project directories
- [ ] Invoker receives file path, not content summary
- [ ] Fresh context provides perspective that in-conversation analysis couldn't (value is felt, not measured)

## AI Validation

**Custom** (this is an agent definition, not code):
- Manual test: invoke agent, verify output file lands in `/tmp/`
- Manual test: invoke agent, verify response is file path only
- Review: agent definition includes correct skill access in allowedTools

## Constraints

- No access to conversation history (that's the point)
- No modification of project files
- No delegation to other agents (keeps it simple)
- No summarizing findings in conversation (force invoker to read the file)

## Context

- Source: `.lore/work/brainstorm/lore-development/socratic-agent-analysis.md`
- Related: `.lore/work/specs/lore-development/poke-holes-skill.md` (the other tool from this analysis)

## Next Step

Use `/plugin-dev:agent-development` skill with this spec to generate the agent definition.
