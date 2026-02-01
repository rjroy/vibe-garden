---
title: Spec review what vs how separation
date: 2026-02-01
status: complete
tags: [lore-development, methodology, spec-review, action-bias, progressive-discovery]
modules: [spec-reviewer, specify, prep-plan]
related: [.lore/brainstorm/spec-review-what-vs-how.md, .lore/specs/spec-review-what-vs-how.md]
---

# Retro: Spec Review What vs How Separation

## Summary

Renamed `lore-docs-reviewer` to `spec-reviewer`, refocused it on specs only, and added explicit "What vs How" guidance to prevent specs from drifting into implementation territory. Also cleaned up `prep-plan` skill to remove unreachable code that could never execute after `EnterPlanMode`.

## What Went Well

- **Brainstorm surfaced the real issue**: The original observation ("reviewer drifts toward implementation concerns") led to discovering that plans can't be reviewed by this system at all. That realization simplified the solution.
- **Coordinated changes**: Updating both `spec-reviewer` and `specify` with the same "What vs How" framing ensures consistency.
- **Cleanup cascaded naturally**: While fixing the spec reviewer, noticed `prep-plan` had the same pattern of unreachable code (steps after `EnterPlanMode`). Fixed that too.
- **Clear anti-patterns**: "If you're writing something that would appear in code, stop" is actionable guidance.

## What Could Improve

- **Spec had stale module names**: The spec referenced `spec-reviewer` before the rename happened. Not a problem here, but shows that specs written before implementation can drift from reality.
- **prep-plan discovered during implementation**: The plan didn't include `prep-plan` cleanup. It was out of scope, then we did it anyway. The scope creep was beneficial but unplanned.

## Lessons Learned

- **"Could I implement this?" invites implementation thinking**: Question framing matters. Asking "could I verify this?" keeps focus on what, not how.
- **Skills lose control at handoff points**: Once `EnterPlanMode` or similar is called, the skill's context is gone. Any steps after the handoff are unreachable code. Design skills with this constraint in mind.
- **Plans live outside lore-development**: Native PlanMode generates plans that this system can't review. Don't pretend otherwise in skill documentation.

## Artifacts

- [Brainstorm](.lore/brainstorm/spec-review-what-vs-how.md) - Original exploration
- [Spec](.lore/specs/spec-review-what-vs-how.md) - Requirements
- [PR #89](https://github.com/rjroy/vibe-garden/pull/89) - Implementation
