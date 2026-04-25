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
- 17:04 commission-Dalton-20260424-164331 result: Phase 0 Thorne findings addressed. All four fix-now items, the nit, and the open question are resolved. Tests pass (78/78), validator runs clean across all three fixture subtrees, in-scope legacy-path...
- 17:04 commission-Dalton-20260424-164331 completed
- 17:21 commission-Dalton-20260424-171700 result: 
# Phase 2 — Agent description updates

All five lore-development agents updated for the three-directory model. Search-priority inversion in lore-researcher.md is the load-bearing semantic change; all...
- 17:21 commission-Dalton-20260424-171700 completed
- 17:25 commission-Thorne-20260424-171731 result: 
# Phase 2 Review — lore-development agent description updates

**Verdict: Pass with two minor observations.** No blockers. No fix-now items. The load-bearing priority inversion (REQ-REDESIGN-42) is d...
- 17:25 commission-Thorne-20260424-171731 completed