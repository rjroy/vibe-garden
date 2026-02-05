---
title: Remove breakdown and execute skills
date: 2026-01-29
status: complete
tags: [deletion, skill-design, native-capability, philosophy]
modules: [lore-development]
related: [.lore/brainstorm/execute-skill-and-status-tracking.md, .lore/plans/status-tracking-and-document-lifecycle.md]
---

# Retro: Remove breakdown and execute skills

## Summary
Removed `/lore-development:breakdown` and `/lore-development:execute` skills. These were formalizing what Claude Code's native plan mode and implementation already handle. Also removed `.lore/work/` from the artifact structure.

## What Went Well
- Clean removal: 240 lines deleted, 7 added
- References caught across README, tend, prep-plan, update-lore-agents, plugin.json
- Version bump to 0.7.0 signals breaking change

## What Could Improve
- Could have caught this redundancy earlier. The bounded-specification work exposed it by demonstrating that skipping lore-development's workflow worked fine.

## Lessons Learned
- **Don't wrap native capability with ceremony.** Claude Code already breaks plans into steps and executes them. Adding `.lore/work/` artifacts and chunk tracking was overhead without insight.
- **Trust the LLM's native loop.** The philosophy section of the README says "Trust the LLM - don't over-specify what modern AI already does well." These skills violated that principle.
- **Deletion is a feature.** 240 lines removed makes the plugin lighter and more honest about what it actually provides: context management, not process enforcement.

## Artifacts
- Deleted: `lore-development/skills/breakdown/SKILL.md`
- Deleted: `lore-development/skills/execute/SKILL.md`
- Updated: README, tend, prep-plan, update-lore-agents, plugin.json
