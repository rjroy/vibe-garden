---
title: Time-bucket baselines for mind-reader
date: 2026-02-01
status: draft
tags: [mind-reader, baselines, temporal-patterns, session-tracking]
modules: [mind-reader]
related:
  - .lore/brainstorm/time-bucket-baselines-2026-02-01.md
  - .lore/specs/mind-reader-plugin.md
  - .lore/research/typical-hours-algorithm.md
  - .lore/research/boundary-discovery-algorithms.md
---

# Spec: Time-Bucket Baselines

## Overview

Enhance mind-reader's temporal baseline to track session patterns across 28 contexts (7 days × 4 time buckets) instead of treating days and hours as independent dimensions. Bucket boundaries are discovered from activity patterns per day, and percentiles are tracked within each bucket.

## Entry Points

- **Baseline cron**: Daily cron job computes baselines; boundaries recalculated weekly
- **UserPromptSubmit hook**: Reads baseline to determine current context and compare session against it

## Requirements

### Baseline Structure

- REQ-1: Replace flat `typical_hours` and `typical_days` with per-day bucket structure:
  ```json
  {
    "computed_at": "2026-02-01T03:00:00Z",
    "boundaries_computed_at": "2026-01-27T03:00:00Z",
    "window_days": 42,
    "days": {
      "monday": {
        "boundaries": [7, 12, 18, 23],
        "buckets": {
          "morning": {
            "session_count": 8,
            "session_rate": 0.19,
            "duration": { "p50": 45, "p75": 90, "p90": 150 }
          },
          "afternoon": {
            "session_count": 12,
            "session_rate": 0.29,
            "duration": { "p50": 20, "p75": 35, "p90": 60 }
          },
          "evening": {
            "session_count": 6,
            "session_rate": 0.14,
            "duration": { "p50": 90, "p75": 180, "p90": 240 }
          },
          "night": {
            "session_count": 2,
            "session_rate": 0.05,
            "duration": { "p50": 15, "p75": 25, "p90": 40 }
          }
        }
      },
      "tuesday": { ... }
    },
    "global": {
      "session_count": 142,
      "duration": { "p50": 40, "p75": 85, "p90": 160 }
    }
  }
  ```
- REQ-2: Boundaries array defines hour transitions: `[7, 12, 18, 23]` means morning=7-11, afternoon=12-17, evening=18-22, night=23-6
- REQ-2a: Bucket names are hardcoded in order: morning, afternoon, evening, night
- REQ-3: Global baseline preserved for fallback when window has insufficient total sessions
- REQ-3a: `session_rate` = session_count / window_days (e.g., 2 sessions / 42 days = 0.05)

### Boundary Discovery

- REQ-4: Discover bucket boundaries per day using local minima detection:
  1. Compute hourly activity counts for the day (24 values)
  2. Apply 3-point moving average to smooth noise (circular, hour 23 neighbors hour 0)
  3. Find local minima using `scipy.signal.argrelextrema` with `mode='wrap'`
  4. Score each minimum by depth (difference from average of neighbors)
  5. Select 3 deepest minima that are at least 3 hours apart
  6. If fewer than 3 valid minima, use default boundaries
- REQ-5: Boundaries recalculated weekly (track `boundaries_computed_at` separately from `computed_at`)
- REQ-6: Default boundaries `[6, 12, 18, 22]` used when:
  - Insufficient data for the day (< 20 sessions in window)
  - Fewer than 3 valleys found with adequate spacing
  - All hours have uniform activity (no clear valleys)
- REQ-6a: See `.lore/research/boundary-discovery-algorithms.md` for algorithm details and alternatives considered

### Data Window

- REQ-7: Use rolling 6-week window (42 days) for session data
- REQ-7a: Session data sourced from `~/.claude/history.jsonl` (Claude Code's history file)
- REQ-8: If total sessions across all buckets < 20, extend window until 20 sessions reached (or max 6 months)
- REQ-9: Absence of sessions is data, not missing data. A bucket with 2 sessions in 42 days has a session rate of 0.05, meaning working in that bucket at all is unusual.

### Two-Stage Detection

- REQ-10: Detection uses a hurdle model with two stages:
  1. **Bucket rarity**: Is having a session in this bucket unusual?
  2. **Duration given session**: Given you're working, is this session long?
- REQ-11: Bucket rarity threshold: session_rate < 0.1 (fewer than ~4 sessions in 6 weeks) triggers rarity nudge
- REQ-12: Duration threshold: session exceeds bucket's p90 triggers duration nudge
- REQ-13: Both nudges can fire independently. A rare bucket with a long session gets both signals.

### Hook Behavior

- REQ-14: Hook determines current bucket from day + hour + that day's boundaries
- REQ-15: Rarity nudge message: "You're working Saturday night (rare for you, ~5% of Saturdays)"
- REQ-16: Duration nudge message: "90 minutes (your Saturday evening p90 is 60)"
- REQ-17: If bucket has 0 sessions in history, treat any session as rare (session_rate = 0)
- REQ-18: If global baseline has insufficient data (< 20 total sessions), skip temporal checks entirely

### Backward Compatibility

- REQ-19: If baseline.json lacks `days` structure, fall back to existing flat behavior
- REQ-20: First run after upgrade computes new structure from existing history

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Rarity nudge | Bucket session_rate < 0.1 | Hook stdout message |
| Duration nudge | Session exceeds bucket's p90 | Hook stdout message |
| Window extension | Total sessions < 20 | Extend beyond 6 weeks |
| Skip checks | Global baseline insufficient | No nudge emitted |

## Success Criteria

- [ ] Baseline includes per-day bucket structure with discovered boundaries
- [ ] Each bucket tracks session_rate and duration percentiles
- [ ] Boundaries recalculate weekly (boundaries_computed_at updates only every 7 days)
- [ ] Hook correctly identifies current bucket from day + hour
- [ ] Rarity nudge fires when session_rate < 0.1
- [ ] Duration nudge fires when session exceeds bucket p90
- [ ] Zero-session buckets treated as maximally rare
- [ ] Existing installations upgrade gracefully

## AI Validation

**Defaults**:
- Unit tests with mocked time/filesystem
- 90%+ coverage on new code

**Custom**:
- Boundary discovery test: synthetic data with clear activity valleys produces expected boundaries
- Session rate test: bucket with 2 sessions in 42 days has session_rate = 0.048
- Rarity nudge test: session_rate 0.05 triggers rarity nudge; session_rate 0.15 does not
- Duration nudge test: 90-minute session in bucket with p90=60 triggers duration nudge
- Zero-session bucket test: bucket with 0 historical sessions triggers rarity nudge
- Both nudges test: rare bucket with long session emits both nudge types
- Upgrade test: old baseline.json format triggers migration

## Constraints

- Boundary discovery runs weekly to avoid churn
- Session data read from `~/.claude/history.jsonl` during baseline computation
- Hook must still complete in <500ms (bucket lookup is O(1), no history.jsonl reads at runtime)

## Context

Addresses limitations identified in brainstorm:
- Single "typical session" value averaged out distinct usage modes
- Day and hour treated independently, missing patterns like "Monday mornings are different from Monday evenings"
- User's actual pattern: morning spike, midday slow burn, evening spike

Key insight from brainstorm discussion: **absence of sessions is data, not missing data**. A bucket with 2 sessions in 6 weeks doesn't have "insufficient data"; it has a session rate of 5%, meaning working in that bucket at all is unusual. This leads to a two-stage hurdle model:
1. Is having a session here rare? (bucket rarity)
2. Given you're working, is this session long? (duration given session)

This is related to zero-inflated distributions and hurdle models in statistics, where many observations are zeros and need separate treatment from non-zero values.
