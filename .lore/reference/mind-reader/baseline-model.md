---
title: mind-reader baseline model
date: 2026-04-25
status: current
tags: [mind-reader, baseline, bucket-model, temporal-detection]
modules: [mind-reader]
---

# mind-reader Baseline Model

The v2 bucket-based baseline replaces a v1 single-value baseline. The v1 fields (`session_duration_minutes`, `prompts_per_session`, `typical_hours`) still exist as fallback for when v2 data isn't available (`baseline.has_v2_data()` returns false), but they are not the destination.

## Why bucket model over single-value baselines

The bucket model exists because single-value baselines average across distinct usage modes. A user who works mornings *and* late evenings has two genuine session types. A single "typical session duration" lands between them and fits neither — it nudges a 60-minute morning session as "long" when 60 is the morning median, and lets a 60-minute evening session pass when 90 is the evening median.

**Why:** the v1 baseline treated day-of-week and hour-of-day as independent dimensions. They aren't — Monday 8am behaves nothing like Monday 8pm. Treating them independently discards the structure that makes the nudge meaningful.

**How to apply:** don't refactor back to single-value baselines under "simplification" pressure. The v1 fields are fallback, not target.

## Four boundaries, five buckets

Each day has four discovered hour boundaries that divide the 24-hour day into five named regions: `late_night`, `early_morning`, `morning`, `afternoon`, `evening`. The fifth region exists because of wrap-around — late_night (hours before the first boundary) and evening (hours after the last boundary) are separate regions, not folded into one "night" bucket.

**Why:** a 1am session and an 11pm session sit on opposite sides of the working day even though both are "night" colloquially. Folding them into one bucket would re-introduce the averaging problem the bucket model exists to avoid.

**How to apply:** if you're tempted to merge late_night and evening into a single night bucket, you're undoing the wrap-around handling on purpose. Don't.

## Why the 6-week window

Baseline computation uses a 6-week (42-day) rolling window. Long enough to accumulate meaningful samples per day-bucket; short enough to drift with changing habits.

**Why:** habits shift seasonally, with project phases, and with role changes. A longer window (say 90 days) accumulates more data per bucket but locks the user's "typical" into a past that no longer matches the present, which makes nudges feel wrong. A shorter window (say 2 weeks) reacts to the present but produces unstable percentiles in sparse buckets.

**How to apply:** if you're tempted to raise `window_days` to get more data into sparse buckets, the right answer is usually to handle sparsity explicitly (see below), not to widen the window.

## Sparse-bucket policy: no fallback

A bucket with few or zero historical sessions does not fall back to day-level or global statistics. Zero-session buckets trigger the rarity nudge as "no sessions recorded in this slot — new territory?" Partial-data buckets use whatever percentiles they have.

**Why:** falling back would defeat the purpose of the bucket model. A Tuesday-night session compared against the user's overall median would inherit nudge thresholds from busy buckets that don't represent Tuesday night.

**How to apply:** if a bucket feels too sparse to nudge from, the right move is to widen the bucket (rediscover boundaries) or skip the check, not to borrow stats from another bucket.
