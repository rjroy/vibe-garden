---
title: Task tracking prevents rushed skill execution
date: 2026-01-31
status: complete
tags: [skill-design, task-tracking, thoroughness, pacing]
modules: [lore-development]
related: [lore-development/skills/tend/SKILL.md]
---

# Retro: Task Tracking in Tend Skill

## Summary

Added task tracking guidance to the `/tend` skill to prevent rushed execution that misses documents or skips verification steps.

## What Went Well

- Quick identification of the root cause: rushing through phases loses thoroughness
- Clean integration into existing skill structure (Process, Progressive Discovery, Acting on Findings sections)
- Reframed rationale after user feedback clarified the real concern (thoroughness, not visibility)

## What Could Improve

- Initial framing focused on "user visibility" when the actual problem was "agent might miss things"
- Should have asked clarifying question upfront about what "non-productive" meant

## Lessons Learned

- **Task tracking is a pacing mechanism, not just visibility**: The value isn't that users can see progress, it's that marking tasks complete forces the agent to actually finish work before moving on.
- **"Non-productive turns" can mean different things**: Could be "too fast" (rushing), "too slow" (spinning), or "wrong direction" (misunderstanding). Clarify which.
- **Skill design should account for agent tendencies**: Skills that involve multiple passes or verification steps need explicit pacing mechanisms. Without them, agents collapse phases and lose thoroughness.

## Artifacts

- Modified: `lore-development/skills/tend/SKILL.md`
