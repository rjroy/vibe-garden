---
title: Time-bucket baselines for mind-reader
date: 2026-02-01
status: open
tags: [mind-reader, session-tracking, baselines, time-patterns]
modules: [mind-reader]
---

# Brainstorm: Time-Bucket Baselines for Mind-Reader

## Context

Current mind-reader baseline tracks "typical session duration" as a single value, with days and hours as separate dimensions. This doesn't capture real usage patterns where:

1. Day and hour are intertwined (Monday 8am ≠ Monday 8pm)
2. Usage has multiple modes (morning spike, midday slow burn, evening spike)
3. A single "typical" value averages out distinct session types

## Ideas Explored

### Time Buckets Instead of Raw Hours

Break each day into 4 buckets: morning, afternoon, evening, night. This gives 28 contexts (7 days × 4 buckets) instead of the full 168-cell matrix (24 hours × 7 days) which would be too sparse.

**What if** bucket boundaries were discovered from data rather than predefined?
- Activity density valleys: find hours with lowest activity, use those as natural boundaries
- Per-day boundaries: Monday's morning might end at 11am, Saturday's morning at 1pm
- Avoids the "is 5pm afternoon or evening?" arbitrary decision

**Trade-offs:**
- More complex than fixed boundaries
- Needs enough data before boundaries stabilize
- Boundaries might drift, requiring periodic recalculation

### Distribution-Based Instead of Single Values

Track percentiles within each bucket rather than averages.

```
morning: { p25: 15, p50: 45, p75: 90, p90: 150 }
```

**What if** nudges were percentile-triggered?
- Gentle at p75 ("longer than usual")
- Firmer at p90 ("significantly longer")
- Concerned at p99 ("this is an outlier")

**Trade-offs:**
- Handles natural variance (some sessions should be long)
- Avoids misleading averages when sessions are bimodal
- Needs more data per bucket to establish stable percentiles

### Rolling Window for Drift

Use last 6 weeks of data. Long enough to accumulate meaningful samples, short enough to drift with changing habits.

**What if** patterns change seasonally or with project phases?
- 6 weeks captures recent behavior without locking in stale patterns
- Implies storing raw session records (not just aggregates) for recomputation

## Data Structure Sketch

```yaml
baselines:
  monday:
    boundaries: [7, 12, 18, 23]  # discovered from activity patterns
    buckets:
      morning:
        sessions: [...]  # raw records for last 6 weeks
        p50: 45
        p75: 90
        p90: 150
      afternoon: { ... }
      evening: { ... }
      night: { ... }
  tuesday:
    boundaries: [...]
    buckets: { ... }
```

## Open Questions

1. **Boundary discovery algorithm**: Valley detection in activity histogram seems simplest. What's the threshold for "a valley"?

2. **Recalculation triggers**: When do boundaries get recalculated? Weekly? When pattern shift detected? On-demand?

3. **Sparse buckets**: Tuesday night might have 1 session in 6 weeks. How to handle insufficient data? Fall back to day-level? Global?

4. **What else to track**: Session length is the current metric. What about prompt count, time between prompts (burst vs slow), tool usage patterns? These could distinguish session types even within the same time bucket.

5. **Session type clustering**: Could layer clustering on top later to discover patterns like "deep work," "quick check," "exploration" that correlate loosely with time but aren't determined by it.

## Next Steps

- Implement boundary discovery (activity valley detection)
- Extend baseline data structure to support per-day-bucket storage
- Add percentile tracking within buckets
- Evaluate whether this captures the morning/evening spike pattern better than current approach
