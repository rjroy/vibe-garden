---
title: Integrate Plan Skill with Claude Code Plan Mode
date: 2026-01-29
status: executed
tags: [plan-mode, integration, workflow]
modules: [lore-development]
---

# Plan: Integrate Plan Skill with Claude Code Plan Mode

## Context

- **Discussion**: During docs-review-capability planning, identified that lore `/plan` skill and Claude Code's built-in plan mode serve complementary purposes
- **Problem**: Current skill framing ("Direct the AI's planning capabilities") is misleading. Users who invoke `/lore-development:plan` expect to plan there, but the real planning should use Claude Code's plan mode.

## The Distinction

| Concern | Plan Mode | Lore `/plan` |
|---------|-----------|--------------|
| When | Before implementing | After deciding |
| Why | Alignment checkpoint | Organizational memory |
| Lifespan | Session | Persistent |
| Audience | User approving now | Future sessions/people |

## Approach

Update lore `/plan` to explicitly orchestrate plan mode rather than working alongside it:

1. Gather `.lore/` context (specs, brainstorms, research)
2. **Enter plan mode** with that context loaded
3. Plan mode explores, designs, gets approval
4. After approval, save result to `.lore/plans/`

The skill becomes a wrapper that adds context-loading and persistence around Claude Code's native planning.

## Steps

1. Update `lore-development/skills/plan/SKILL.md`:
   - Reframe purpose: "Orchestrate planning with context, persist the result"
   - Add explicit step to enter plan mode (EnterPlanMode tool)
   - Clarify that plan mode does the actual planning work
   - Add step to save approved plan as `.lore/` artifact

2. Consider skill rename:
   - Current: `/lore-development:plan`
   - Alternative: `/lore-development:plan-and-save` or keep as-is with clearer docs
   - Decision: Keep name, update description to clarify role

## Considerations

- Plan mode requires user approval before proceeding. The skill needs to handle the flow where plan mode is approved, then persistence happens.
- If user declines plan mode, skill should gracefully handle (maybe still offer to save what was discussed).
- This changes the skill from "do planning" to "orchestrate planning" which is more aligned with lore-development's philosophy of not teaching what the AI already knows.

