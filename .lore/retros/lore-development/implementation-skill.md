---
title: Implementation skill - prompts are not programs
date: 2026-02-05
status: complete
tags: [skill-design, orchestrator, over-specification, prompt-design, methodology]
modules: [lore-development]
related:
  - .lore/brainstorm/lore-development/implementation-skill-orchestrator.md
  - .lore/specs/lore-development/implementation-skill.md
  - .lore/retros/lore-development/remove-breakdown-execute.md
---

# Retro: Implementation Skill

## Summary

Brainstormed, specified, and built the `/implement` skill for lore-development. The skill orchestrates implementation by delegating to sub-agents while recording notes as retro fuel. Went from brainstorm through spec through skill creation in one session.

## What Went Well

- The brainstorm surfaced the key insight early: context poisoning makes it impossible for one agent to implement and record simultaneously. Separating the concerns into an orchestrator + worker agents solved this cleanly.
- The lore-researcher found rich prior context, especially the "remove breakdown/execute" retro, which kept us honest about not repeating the ceremony problem.
- User course-corrections were sharp and fast. "You are getting into the weeds" redirected from over-specifying agent contracts to trusting the AI and leaving space for model growth.
- The skill reviewer caught real structural issues (missing validation step, agent selection ordering, process vs policy mixing) that improved the final skill.

## What Could Improve

- Over-specified the spec initially. Treated it like a software interface contract instead of a guide for AI. The user had to pull back twice: once on agent contracts, once on "same issue" detection. The spec is a prompt, not a program.
- The spec reviewer's findings were calibrated for application specs, not prompt/skill specs. Several "critical" findings were actually plan territory or acceptable risk for an AI-guided workflow. Filtering reviewer output for the right context took user effort.

## Lessons Learned

- Specs for AI-guided skills should be lighter than application specs. Leave room for model growth and agent flexibility. Over-constraining a prompt removes the AI's ability to adapt to project-specific context.
- "This is a prompt, not a program" is a useful check when specification starts drifting toward interface contracts and data structures. If the spec describes something that would appear in code, it's gone too far.
- The skill development skill (plugin-dev) provides the structural guidance that the spec reviewer was asking for. Trust the skill creation process to handle "how" concerns rather than front-loading them into the spec.

## Artifacts

- Brainstorm: `.lore/brainstorm/lore-development/implementation-skill-orchestrator.md`
- Spec: `.lore/specs/lore-development/implementation-skill.md`
- Skill: `lore-development/skills/phase/implement/SKILL.md`
- Updated: `lore-development/shared/frontmatter-schema.md` (added notes document type)
