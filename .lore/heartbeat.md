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
- 21:42 commission-Dalton-20260424-180556 result: Phase 4 complete. /excavate → /distill rename and reshape landed.

- 21:42 commission-Dalton-20260424-180556 completed
- 21:46 commission-Thorne-20260424-180617 result: Phase 4 review complete. The rewritten `distill/SKILL.md` is brainstorm-faithful, structurally sound, and free of spec-replacement ambition. Migration is mostly complete. One fix-now finding around th...
- 21:46 commission-Thorne-20260424-180617 completed
- 21:49 commission-Dalton-20260424-180627 result: All four findings from Thorne's Phase 4 review addressed.

- 21:49 commission-Dalton-20260424-180627 completed
- 22:29 commission-Dalton-20260424-222341 result: ## Phase 5 — `/learn` (new) + `/retro` reshape (coupled)

Both skills shipped in this commission. No split needed.

### Files touched

- `lore-development/skills/learn/SKILL.md` — new file, full promp...
- 22:29 commission-Dalton-20260424-222341 completed
- 22:33 commission-Thorne-20260424-222404 result: ## Phase 5 review — `/learn` (new) + `/retro` reshape

**Verdict: clean. No blockers, no fix-now items.** Two nits below.

Both SKILL.md files comply with their requirements. The anti-checks the spec ...
- 22:33 commission-Thorne-20260424-222404 completed
## Per-finding resolution

### Fix-now

**1. `lore-development/skills/tend/references/directories.md` — soft distill-before-archive prompt mi...
## Files touched
- **Renamed** (git mv, history preserved): `lore-development/skills/excavate/SKILL.md` → `lore-development/skills/di...
