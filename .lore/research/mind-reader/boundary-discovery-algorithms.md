---
title: Boundary discovery algorithms for time buckets
date: 2026-02-01
status: active
tags: [algorithm, time-series, segmentation, local-minima, mind-reader]
modules: [mind-reader]
related:
  - .lore/specs/time-bucket-baselines.md
  - .lore/research/typical-hours-algorithm.md
---

# Research: Boundary Discovery Algorithms

## Summary

For mind-reader's time-bucket baselines, we need to discover natural boundaries that segment a day into 4 buckets (morning, afternoon, evening, night). This research evaluates four approaches. Recommendation: **local minima detection** for simplicity and fit to the problem structure.

## Problem Statement

Given hourly activity counts for a day (24 values), find 3 boundary hours that naturally separate activity periods. Boundaries should be at "valleys" between activity peaks.

Constraints:
- Hours are temporally ordered (0-23, wrapping to 0)
- Need exactly 3 boundaries to create 4 buckets
- Boundaries should be at least 3 hours apart
- Must handle sparse data gracefully

## Approach 1: Jenks Natural Breaks

**Method**: Minimize within-class variance while maximizing between-class variance. Classic algorithm for choropleth maps.

**Implementation**: `jenkspy` Python package or ~30 lines of code.

**Pros**:
- Well-understood, deterministic
- Designed for 1D classification

**Cons**:
- Groups by *value similarity*, not *temporal position*
- Would cluster hour 8 with hour 20 if they have similar activity counts
- Doesn't respect the ordering of hours

**Verdict**: Not suitable. Jenks answers "which hours have similar activity?" but we need "where does morning end?"

**Sources**:
- [Jenks natural breaks - Wikipedia](https://en.wikipedia.org/wiki/Jenks_natural_breaks_optimization)
- [Finding Natural Breaks - Practical Business Python](https://pbpython.com/natural-breaks.html)
- [jenkspy - GitHub](https://github.com/mthh/jenkspy)

## Approach 2: Change Point Detection (PELT)

**Method**: Find points where statistical properties of a time series change. PELT (Pruned Exact Linear Time) is an exact method with O(n) complexity under certain conditions.

**Implementation**: `ruptures` Python library.

```python
import ruptures as rpt
algo = rpt.Pelt(model="l2").fit(hourly_counts)
result = algo.predict(pen=10)  # penalty parameter
```

**Pros**:
- Respects temporal ordering
- Well-studied in signal processing
- Handles varying noise levels

**Cons**:
- Designed for long time series (thousands of points)
- Requires penalty parameter tuning
- Overkill for 24 data points
- May not find exactly 3 boundaries

**Verdict**: Too heavy for this use case. PELT shines with long, complex signals, not 24-bin histograms.

**Sources**:
- [ruptures documentation](https://centre-borelli.github.io/ruptures-docs/)
- [PELT user guide](https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/)
- [ruptures - GitHub](https://github.com/deepcharles/ruptures)
- [Change Point Detection in Time Series - Forecastegy](https://forecastegy.com/posts/change-point-detection-time-series-python/)

## Approach 3: Local Minima Detection (Recommended)

**Method**: Smooth the hourly histogram, find local minima (valleys), select the deepest ones that are sufficiently spaced.

**Implementation**: `scipy.signal.argrelextrema` or custom with numpy.

```python
from scipy.signal import argrelextrema
from scipy.ndimage import uniform_filter1d
import numpy as np

def find_boundaries(hourly_counts):
    # Smooth with 3-point moving average
    smoothed = uniform_filter1d(hourly_counts, size=3, mode='wrap')

    # Find local minima
    minima = argrelextrema(smoothed, np.less, mode='wrap')[0]

    # Score by depth (how much lower than neighbors)
    depths = []
    for m in minima:
        left = smoothed[(m - 1) % 24]
        right = smoothed[(m + 1) % 24]
        depth = ((left + right) / 2) - smoothed[m]
        depths.append((m, depth))

    # Sort by depth, select top 3 that are >= 3 hours apart
    depths.sort(key=lambda x: -x[1])
    boundaries = []
    for hour, _ in depths:
        if all(abs(hour - b) >= 3 and abs(hour - b) <= 21 for b in boundaries):
            boundaries.append(hour)
            if len(boundaries) == 3:
                break

    return sorted(boundaries) if len(boundaries) == 3 else [6, 12, 18]
```

**Pros**:
- Simple to implement (~15 lines)
- Respects temporal ordering
- Handles circular wrap (hour 23 → hour 0)
- Intuitive: "find valleys between peaks"
- No external dependencies beyond numpy/scipy

**Cons**:
- Smoothing window size is a tunable parameter
- May need fallback for flat distributions

**Verdict**: Best fit for this problem. Simple, interpretable, matches our mental model.

**Sources**:
- [scipy.signal.argrelextrema](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.argrelextrema.html)
- [Persistence1D - KTH](https://www.csc.kth.se/~weinkauf/notes/persistence1d.html)
- [Finding local minima - ResearchGate discussion](https://www.researchgate.net/post/How_to_find_local_minima_in_a_histogram)

## Approach 4: Circadian Rhythm Analysis

**Method**: Research-grade approaches using FFT, penalized multiband learning, or hidden Markov models to characterize daily rhythms from continuous data.

**Implementation**: Custom or research code.

**Pros**:
- Handles complex, noisy wearable data
- Can identify underlying rhythms despite confounding factors

**Cons**:
- Designed for continuous sensor data, not 24-bin histograms
- Overkill for this use case
- Heavy dependencies

**Verdict**: Not suitable. These methods solve a harder problem than we have.

**Sources**:
- [Circadian Rhythm Analysis Using Wearable Device Data - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8554674/)
- [Circadian behavioral analysis suite - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12146638/)
- [JMIR - Penalized Multiband Learning](https://www.jmir.org/2021/10/e18403)

## Recommendation

**Use local minima detection** for boundary discovery:

1. Compute hourly activity counts for the day (24 values)
2. Apply 3-point moving average to smooth noise (handles sparse data)
3. Handle circular wrap (hour 23 neighbors hour 0)
4. Find local minima using `scipy.signal.argrelextrema` with `mode='wrap'`
5. Score each minimum by "depth" (difference from average of neighbors)
6. Select 3 deepest minima that are at least 3 hours apart
7. If fewer than 3 valid minima, fall back to default boundaries `[6, 12, 18]`

**Edge cases**:
- Uniform activity: All hours have similar counts → use defaults
- Single peak: Activity concentrated in one period → boundaries at 3 lowest hours
- Sparse data: Few total sessions → smoothing handles this, or use defaults
- No clear valleys: Depth threshold not met → use defaults

## Algorithm Pseudocode

```
function discover_boundaries(hourly_counts[24]):
    if sum(hourly_counts) < MIN_SESSIONS:
        return DEFAULT_BOUNDARIES  # [6, 12, 18]

    smoothed = moving_average(hourly_counts, window=3, circular=true)

    minima = []
    for hour in 0..23:
        left = smoothed[(hour - 1) mod 24]
        right = smoothed[(hour + 1) mod 24]
        if smoothed[hour] < left and smoothed[hour] < right:
            depth = ((left + right) / 2) - smoothed[hour]
            minima.append({hour, depth})

    minima.sort_by_depth_descending()

    boundaries = []
    for {hour, depth} in minima:
        if depth < MIN_DEPTH_THRESHOLD:
            continue
        if all boundaries are >= 3 hours away from hour:
            boundaries.append(hour)
            if len(boundaries) == 3:
                break

    if len(boundaries) < 3:
        return DEFAULT_BOUNDARIES

    return sort(boundaries)
```

**Parameters**:
- `MIN_SESSIONS`: Minimum total sessions to attempt discovery (suggest: 20)
- `MIN_DEPTH_THRESHOLD`: Minimum valley depth to count (suggest: 0, let spacing filter)
- `DEFAULT_BOUNDARIES`: Fallback when discovery fails (suggest: [6, 12, 18])
