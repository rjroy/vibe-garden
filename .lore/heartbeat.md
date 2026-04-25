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
- 16:55 commission-Dalton-20260424-164303 result: Phase 0 complete: schema foundation + directory canon.

**Files touched:**
- `lore-development/shared/frontmatter-schema.md` — rewrote per three-status-set model. Documents the `.lore/build/` / `.lore...

- 16:55 commission-Dalton-20260424-164303 completed
- 17:01 commission-Thorne-20260424-164323 result: Phase 0 review — gate decision: **not yet ready**. Schema, validator, and per-directory status sets are correctly encoded; tests pass (78/78); legacy-path grep across the in-scope files is clean. Four...
- 17:01 commission-Thorne-20260424-164323 completed