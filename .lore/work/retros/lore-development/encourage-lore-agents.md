---
title: Agent fallback defaults and registry gaps in implement/update-lore-agents
date: 2026-02-06
status: complete
tags: [agents, registry, fallback, skill-design, cross-skill-contracts]
modules: [lore-development]
related:
  - .lore/work/plans/encourage-lore-agents.md
  - .lore/work/specs/lore-development/implementation-skill.md
  - .lore/work/retros/lore-development/implementation-skill.md
---

# Retro: Encourage Lore Agents

## Summary

Added concrete fallback `subagent_type` values to `/implement` and an Implementation category to `/update-lore-agents` so the registry and skill stay coordinated. Also fixed a stale `plan` reference (should be `prep-plan`) and added the missing `design` consumer.

## What Went Well

- Scope stayed tight. Two files, focused edits, no feature creep.
- Fresh-context validation (plan-reviewer, fresh-lore) caught no spec violations, confirming the approach threaded the needle between "hardcoded" and "vague."
- Skill reviewer caught a real bug: the consumer list still said `plan` instead of `prep-plan` from a prior rename. That would have misled anyone reading the Context section.
- The table format for fallback mapping in `/implement` serves three purposes at once: documents the roles, shows the registry category, and names the fallback. Compact and scannable.

## What Could Improve

- The stale `plan` reference in `/update-lore-agents` was pre-existing from the rename in commit `fc37c5d`. It wasn't introduced by this work, but it was only caught because we happened to run the skill reviewer. Consumer lists that reference other skills by name are fragile when skills get renamed.
- The `design` skill was missing from the consumer list entirely. This means the original `/update-lore-agents` implementation didn't audit which skills actually check for the registry. Consumer lists should be verified against the codebase, not written from memory.

## Lessons Learned

- When a skill is renamed, grep for the old name across all skills. Consumer lists, cross-references, and documentation all need updating. The rename itself is easy; finding every reference is the real work.
- Cross-skill contracts (one skill produces an artifact, another consumes it) need explicit documentation on both sides. The producer should list its consumers, and the consumer should name its expected categories/keys. Without this, the two drift apart silently.
- Skill reviewer is worth running on any skill edit, not just new skills. It caught issues that the fresh-lore validator didn't because it reads the skill with different eyes (structure and consistency vs. spec compliance).

## Artifacts

- Plan: `.lore/work/plans/encourage-lore-agents.md`
- Spec (referenced): `.lore/work/specs/lore-development/implementation-skill.md`
- PR: https://github.com/rjroy/vibe-garden/pull/110
