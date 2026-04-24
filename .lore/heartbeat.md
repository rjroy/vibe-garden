---
status: active
---
# Heartbeat

This file controls what the guild does autonomously. Every hour (configurable),
a Guild Master session reads this file and decides which standing orders warrant
action: creating commissions, dispatching work, or starting meetings.

**Standing Orders** are lines starting with `- `. Write them in plain language.
If you want the guild to check with you before acting on an order, say so in the
order itself.

**Watch Items** are things to monitor. The guild reads these for context but won't
create commissions from them directly.

**Context Notes** are operational context the guild should know (merge freezes, priorities).

**Recent Activity** is managed by the daemon. Don't edit this section manually.
Workers can also add entries to this file during their sessions.

## Standing Orders

## Watch Items

## Context Notes

## Recent Activity
- 15:35 commission-Dalton-20260424-151647 result: Plan written to `.lore/plans/lore-redesign.md`. Reviewed by plan-reviewer (lore-development:plan-reviewer), findings integrated.

**Structure**: 6 implementation phases + a final validation phase, gro...

- 15:35 commission-Dalton-20260424-151647 completed