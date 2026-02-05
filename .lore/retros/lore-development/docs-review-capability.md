---
title: Docs Review Capability
date: 2026-01-29
status: complete
tags: [fresh-context, review, documentation, agents]
modules: [lore-development]
related: [.lore/brainstorm/lore-development/docs-review-capability.md, .lore/plans/lore-development/docs-review-capability.md]
---

# Retro: Docs Review Capability

## Summary

Added `lore-docs-reviewer` agent to lore-development plugin (v0.5.0). The agent reviews specs and plans with fresh context to catch clarity issues the author may have missed. Four review lenses: clarity, completeness, consistency, actionability.

## What Went Well

- **Brainstorm → Plan → Implement flow worked smoothly.** Each phase built naturally on the previous. The brainstorm clarified the "agent not skill" decision before planning started.

- **Leveraged existing patterns.** The agent registry pattern (`lore-agents.md`) meant no changes to consumer skills (`specify`, `plan`). They already have "Specialized Agents" sections that check the registry.

- **Ate our own cooking.** Used a fresh-context agent to review the agent definition itself. Found real gaps (output destination, invocation mechanism, severity levels). Fixed before shipping.

- **Side discovery tracked separately.** Realized lore `/plan` should integrate with Claude Code's plan mode. Recorded it in `.lore/plans/plan-skill-plan-mode-integration.md` without derailing current work.

## What Could Improve

- **Open questions from brainstorm weren't explicitly closed.** The brainstorm listed "structured vs prose?" and "specific lenses vs open-ended?" as open questions. These got answered during planning but weren't formally closed in the brainstorm doc.

- **Agent wasn't testable until installed.** Tried to invoke `lore-development:lore-docs-reviewer` but got "agent not found" because the plugin cache had the old version. Had to use `general-purpose` agent to simulate fresh-context review. Would be nice to test agents before committing.

- **No spec document.** Went brainstorm → plan → implement. For this size work that was fine, but a spec would have made the "what are we building" clearer earlier.

## Lessons Learned

- **Fresh-context review works.** The meta test (reviewing the reviewer) found legitimate issues. The pattern is validated. Use it.

- **Agent registry is a good composability pattern.** Adding a new agent required zero changes to consumer skills because they already check the registry. This scales.

- **"Agent not skill" is the right call for fresh-context work.** Sub-agents inherently get fresh context. Wrapping them in a skill would add orchestration without adding value.

- **Track tangents as separate plans.** The plan-mode integration discussion could have derailed us. Recording it separately kept focus while preserving the insight.

- **Built-in agents need consistent documentation.** Added a table to `update-lore-agents` ensuring lore-development's own agents are always documented the same way. Prevents drift across projects.

## Artifacts

- Brainstorm: `.lore/brainstorm/lore-development/docs-review-capability.md`
- Plan: `.lore/plans/lore-development/docs-review-capability.md`
- Side plan: `.lore/plans/plan-skill-plan-mode-integration.md`
- Commit: `a6b2497` (feat: Add lore-docs-reviewer agent)
