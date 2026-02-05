---
title: Typical hours/days algorithm options
date: 2026-01-31
status: active
tags: [algorithm, statistics, baselines, temporal-patterns]
modules: [mind-reader]
related: [.lore/specs/mind-reader/mind-reader-plugin.md]
---

# Research: Typical Hours/Days Algorithm

## Summary

For mind-reader's temporal detection, we need to identify which hours and days are "typical" for a user. This research evaluates three practical approaches: threshold-based, percentile-based, and statistical (standard deviation). Recommendation: **percentile-based** for simplicity and robustness.

## Problem Statement

Given a user's prompt history with timestamps, determine:
- `typical_hours`: Which hours of the day (0-23) represent normal activity
- `typical_days`: Which days of the week represent normal activity

These are used to detect temporal anomalies like "you're working at 2 AM, which is unusual for you."

## Approach 1: Threshold-Based

**Method**: Hours/days with more than X% of total activity are "typical."

```python
def typical_hours_threshold(prompts_by_hour, threshold=0.05):
    total = sum(prompts_by_hour.values())
    return [h for h, count in prompts_by_hour.items()
            if count / total >= threshold]
```

**Example**: If threshold=5%, and hour 19 has 8% of prompts, it's typical. Hour 3 with 0.1% is not.

**Pros**:
- Simple to understand and explain
- Intuitive threshold (">5% of your activity")

**Cons**:
- Fixed threshold doesn't adapt to activity spread
- User with concentrated activity (3 hours) vs. spread activity (12 hours) need different thresholds
- May include too many hours for users with flat distributions

## Approach 2: Percentile-Based

**Method**: Hours/days in the top Nth percentile of activity are "typical."

```python
def typical_hours_percentile(prompts_by_hour, percentile=0.8):
    counts = sorted(prompts_by_hour.values(), reverse=True)
    threshold = counts[int(len(counts) * (1 - percentile))]
    return [h for h, count in prompts_by_hour.items()
            if count >= threshold]
```

**Example**: If percentile=80%, the hours with activity in the top 20% of all hours are typical.

**Pros**:
- Adapts to user's actual distribution
- Works for both concentrated and spread activity patterns
- Standard statistical approach (used in anomaly detection baselines)

**Cons**:
- Percentile cutoff is less intuitive to explain
- May be sensitive to outlier hours

**Variant**: Use Jenks natural breaks algorithm to find natural clustering of hours into "active" and "inactive" groups. More sophisticated but harder to implement.

## Approach 3: Standard Deviation

**Method**: Hours with activity within mean ± k*std are "typical."

```python
def typical_hours_std(prompts_by_hour, k=1.0):
    counts = list(prompts_by_hour.values())
    mean = sum(counts) / len(counts)
    std = (sum((c - mean)**2 for c in counts) / len(counts)) ** 0.5
    threshold = mean - k * std  # Below this = atypical
    return [h for h, count in prompts_by_hour.items()
            if count >= threshold]
```

**Example**: If k=1, hours with activity below (mean - 1*std) are flagged as atypical.

**Pros**:
- Standard statistical approach (3-sigma rule variants)
- Well-understood in anomaly detection literature

**Cons**:
- Assumes roughly normal distribution (activity often isn't)
- Sensitive to outliers affecting mean/std
- Harder to explain to users

## Comparison with Real Data

Using the USAGE_REPORT data as reference:
- Peak hour: 19:00 (13.1%)
- Activity spread: 06:00-21:00 with bimodal peaks

| Approach | Likely Result |
|----------|---------------|
| Threshold (5%) | ~8 hours (most of 6 PM - 10 PM, some morning) |
| Percentile (80%) | ~5 hours (top quintile) |
| Std (k=1) | ~10-12 hours (depends on distribution shape) |

## Recommendation

**Use percentile-based (80th percentile)** for `typical_hours`:
- Adapts to individual patterns without manual tuning
- Robust to both concentrated and spread activity
- Easy to compute, no distribution assumptions

**Algorithm**:
```python
def compute_typical_hours(history):
    # Count prompts per hour
    hour_counts = Counter(
        datetime.fromtimestamp(e["timestamp"]/1000).hour
        for e in history
    )

    # Find 80th percentile threshold
    counts = sorted(hour_counts.values())
    p80_index = int(len(counts) * 0.2)  # Top 20%
    threshold = counts[-(p80_index + 1)] if p80_index < len(counts) else 0

    # Hours at or above threshold are typical
    return sorted(h for h, c in hour_counts.items() if c >= threshold)
```

**For `typical_days`**: Same approach, but count by day of week. Days above 80th percentile (or above median, since only 7 days) are typical.

```python
def compute_typical_days(history):
    day_counts = Counter(
        datetime.fromtimestamp(e["timestamp"]/1000).strftime("%A")
        for e in history
    )

    # For 7 days, use median as threshold (simpler)
    counts = sorted(day_counts.values())
    median = counts[len(counts) // 2]

    return [d for d, c in day_counts.items() if c >= median]
```

## Edge Cases

1. **Insufficient data**: If <50 prompts, typical hours/days are unreliable. Mark baseline as `insufficient_data: true` and skip temporal checks.

2. **Uniform distribution**: If user has roughly equal activity across all hours, percentile approach will still pick ~5 hours. This is acceptable; the nudge "you're working at 3 AM" is still meaningful if 3 AM isn't in their top 20%.

3. **Single-hour users**: If >80% of activity is in one hour, only that hour is typical. This correctly identifies any other hour as unusual.

## Update to Spec

REQ-8b should be updated to:

> `typical_hours`: Hours in top 20% of activity (80th percentile by prompt count)

REQ-8c should be updated to:

> `typical_days`: Days with prompt count at or above median

## Sources

- [Simple statistics for anomaly detection on time-series data](https://www.tinybird.co/blog-posts/anomaly-detection)
- [The role of baselines in anomaly detection](https://www.eyer.ai/blog/the-role-of-baselines-in-anomaly-detection/)
- [Anomaly Detection in Time Series Using Statistical Analysis](https://medium.com/booking-com-development/anomaly-detection-in-time-series-using-statistical-analysis-cc587b21d008)
- [Types of Thresholds (eG Innovations)](https://www.eginnovations.com/documentation/Admin/Types-of-Thresholds.htm)
- [How profiling employee working hours helps detect security incidents](https://www.imperva.com/blog/how-profiling-employee-working-hours-helps-to-detect-security-incidents/)
