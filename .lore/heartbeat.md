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
- 22:39 commission-Dalton-20260424-222441 result: ## Phase 6 — Plugin docs + full audit + dry-run dogfood

### Files touched (lore-development scope only)

- `lore-development/README.md` — replaced flat `.lore/` tree with three-directory model (`buil...

- 22:39 commission-Dalton-20260424-222441 completed
- 22:42 commission-Octavia-20260424-222511 result: README review of `lore-development/README.md` (Phase 6 rewrite).

- 22:42 commission-Octavia-20260424-222511 completed
## Overall

The README's framing of `build/`, `reference/`, and `learned/` matches the spec's three-directory model faithfully. The "s...