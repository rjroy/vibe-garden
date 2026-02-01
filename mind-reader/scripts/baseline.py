#!/usr/bin/env python3
"""
Baseline computation script for mind-reader plugin.
Reads ~/.claude/history.jsonl and computes temporal statistics.
Run via cron daily (recommended: 0 3 * * *).
"""

import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# Handle import from different directories
try:
    from core.boundaries import (
        DEFAULT_BOUNDARIES,
        discover_boundaries,
        get_all_bucket_names,
        get_bucket_name,
    )
    from core.state import (
        acquire_baseline_lock,
        cleanup_old_sessions,
        read_baseline,
        release_baseline_lock,
        write_baseline,
    )
except ImportError:
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from core.boundaries import (
        DEFAULT_BOUNDARIES,
        discover_boundaries,
        get_all_bucket_names,
        get_bucket_name,
    )
    from core.state import (
        acquire_baseline_lock,
        cleanup_old_sessions,
        read_baseline,
        release_baseline_lock,
        write_baseline,
    )


def get_history_path() -> Path:
    """Get path to Claude Code history file."""
    return Path.home() / ".claude" / "history.jsonl"


def parse_history(history_path: Path) -> list[dict]:
    """
    Parse history.jsonl into a list of entries.

    Args:
        history_path: Path to history.jsonl

    Returns:
        List of parsed history entries.
    """
    entries = []
    with open(history_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError as e:
                print(
                    f"Warning: Invalid JSON at line {line_num}: {e}",
                    file=sys.stderr,
                )
    return entries


def group_by_session(entries: list[dict]) -> dict[str, list[dict]]:
    """
    Group history entries by session ID.

    Args:
        entries: List of history entries

    Returns:
        Dict mapping session_id to list of entries.
    """
    sessions: dict[str, list[dict]] = {}
    for entry in entries:
        session_id = entry.get("sessionId", "")
        if not session_id:
            continue
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append(entry)
    return sessions


def compute_session_metrics(
    sessions: dict[str, list[dict]]
) -> tuple[list[float], list[int]]:
    """
    Compute duration and prompt count for each session.

    Args:
        sessions: Dict mapping session_id to entries

    Returns:
        Tuple of (durations_minutes, prompt_counts).
    """
    durations = []
    prompt_counts = []

    for _session_id, entries in sessions.items():
        if not entries:
            continue

        # Get timestamps (in milliseconds)
        timestamps = []
        for entry in entries:
            ts = entry.get("timestamp")
            if ts is not None:
                timestamps.append(ts)

        if len(timestamps) < 2:
            # Single-prompt session
            prompt_counts.append(len(entries))
            durations.append(0.0)
            continue

        timestamps.sort()
        duration_ms = timestamps[-1] - timestamps[0]
        duration_minutes = duration_ms / 1000 / 60

        durations.append(duration_minutes)
        prompt_counts.append(len(entries))

    return durations, prompt_counts


def compute_percentiles(values: list[float]) -> dict[str, float]:
    """
    Compute median, p75, and p95 for a list of values.

    Args:
        values: List of numeric values

    Returns:
        Dict with median, p75, p95 keys.
    """
    if not values:
        return {"median": 0, "p75": 0, "p95": 0}

    sorted_values = sorted(values)
    n = len(sorted_values)

    def percentile(p: float) -> float:
        idx = int(p * (n - 1))
        return sorted_values[idx]

    return {
        "median": percentile(0.5),
        "p75": percentile(0.75),
        "p95": percentile(0.95),
    }


def compute_typical_hours(entries: list[dict]) -> list[int]:
    """
    Compute typical hours (80th percentile by prompt count).

    Args:
        entries: List of history entries

    Returns:
        List of typical hours (0-23).
    """
    hour_counts: Counter[int] = Counter()

    for entry in entries:
        ts = entry.get("timestamp")
        if ts is None:
            continue
        dt = datetime.fromtimestamp(ts / 1000)
        hour_counts[dt.hour] += 1

    if not hour_counts:
        return []

    # Find 80th percentile threshold
    counts = sorted(hour_counts.values())
    p80_index = max(0, int(len(counts) * 0.2))  # Top 20%
    if p80_index >= len(counts):
        p80_index = len(counts) - 1
    threshold = counts[-(p80_index + 1)] if counts else 0

    # Hours at or above threshold are typical
    return sorted(h for h, c in hour_counts.items() if c >= threshold)


# ============================================================================
# V2 Baseline Computation: Time-Bucket Based
# ============================================================================


def compute_hourly_counts(entries: list[dict], day_name: str) -> list[int]:
    """
    Compute prompt counts per hour for a specific day of week.

    Args:
        entries: List of history entries
        day_name: Day name (e.g., "Monday", "tuesday" - case insensitive)

    Returns:
        List of 24 integers representing prompts per hour (index 0-23).
    """
    day_name_lower = day_name.lower()
    counts = [0] * 24

    for entry in entries:
        ts = entry.get("timestamp")
        if ts is None:
            continue
        dt = datetime.fromtimestamp(ts / 1000)
        if dt.strftime("%A").lower() == day_name_lower:
            counts[dt.hour] += 1

    return counts


def compute_bucket_percentiles(durations: list[float]) -> dict[str, float]:
    """
    Compute p50, p75, p90 percentiles for bucket duration.

    Args:
        durations: List of session durations in minutes

    Returns:
        Dict with p50, p75, p90 keys.
    """
    if not durations:
        return {"p50": 0, "p75": 0, "p90": 0}

    sorted_values = sorted(durations)
    n = len(sorted_values)

    def percentile(p: float) -> float:
        idx = int(p * (n - 1))
        return sorted_values[idx]

    return {
        "p50": percentile(0.5),
        "p75": percentile(0.75),
        "p90": percentile(0.90),
    }


def compute_bucket_stats(
    sessions: dict[str, list[dict]],
    day_name: str,
    boundaries: list[int],
    window_days: int,
) -> dict[str, dict]:
    """
    Compute statistics for each bucket on a given day.

    Args:
        sessions: Dict mapping session_id to list of entries
        day_name: Day name (e.g., "Monday")
        boundaries: List of 4 boundary hours
        window_days: Number of days in the analysis window

    Returns:
        Dict mapping bucket_name to stats dict.
    """
    day_name_lower = day_name.lower()

    # Count how many instances of this day are in the window
    # (window_days / 7, rounded to account for partial weeks)
    day_instances = max(1, window_days // 7)

    # Group sessions by bucket based on their start time
    bucket_sessions: dict[str, list[tuple[str, list[dict]]]] = {
        name: [] for name in get_all_bucket_names()
    }

    for session_id, entries in sessions.items():
        if not entries:
            continue

        # Get session start time
        timestamps = [e.get("timestamp") for e in entries if e.get("timestamp")]
        if not timestamps:
            continue

        start_ts = min(timestamps)
        start_dt = datetime.fromtimestamp(start_ts / 1000)

        # Check if session started on this day
        if start_dt.strftime("%A").lower() != day_name_lower:
            continue

        # Determine which bucket this session belongs to
        bucket = get_bucket_name(start_dt.hour, boundaries)
        bucket_sessions[bucket].append((session_id, entries))

    # Compute stats for each bucket
    result = {}
    for bucket_name in get_all_bucket_names():
        sessions_in_bucket = bucket_sessions[bucket_name]
        session_count = len(sessions_in_bucket)
        session_rate = session_count / day_instances

        # Compute durations for sessions in this bucket
        durations = []
        for _session_id, entries in sessions_in_bucket:
            timestamps = [e.get("timestamp") for e in entries if e.get("timestamp")]
            if len(timestamps) >= 2:
                duration_ms = max(timestamps) - min(timestamps)
                durations.append(duration_ms / 1000 / 60)
            else:
                durations.append(0.0)

        duration_percentiles = compute_bucket_percentiles(durations)

        result[bucket_name] = {
            "session_count": session_count,
            "session_rate": round(session_rate, 3),
            "duration": duration_percentiles,
        }

    return result


def should_recompute_boundaries(baseline: dict | None) -> bool:
    """
    Check if boundaries should be recomputed.

    Boundaries are recomputed weekly (every 7 days) to avoid
    unnecessary computation while still adapting to pattern changes.

    Args:
        baseline: Existing baseline dict, or None

    Returns:
        True if boundaries should be recomputed.
    """
    if baseline is None:
        return True

    boundaries_computed_at = baseline.get("boundaries_computed_at")
    if boundaries_computed_at is None:
        return True

    try:
        computed_dt = datetime.fromisoformat(boundaries_computed_at)
        age = datetime.now() - computed_dt
        return age > timedelta(days=7)
    except (ValueError, TypeError):
        return True


def compute_baseline_v2(
    history_path: Path,
    window_days: int = 42,
    existing_baseline: dict | None = None,
) -> dict:
    """
    Compute v2 baseline with time-bucket statistics.

    This computes per-day, per-bucket statistics including:
    - Session rate (sessions per day instance)
    - Duration percentiles (p50, p75, p90)

    Args:
        history_path: Path to history.jsonl
        window_days: Number of days to include in analysis (default 42 = 6 weeks)
        existing_baseline: Existing baseline for boundary reuse

    Returns:
        Dict with v2 baseline fields (to be merged with v1 baseline).
    """
    entries = parse_history(history_path)

    # Filter to window
    cutoff = datetime.now() - timedelta(days=window_days)
    cutoff_ms = int(cutoff.timestamp() * 1000)
    entries = [e for e in entries if e.get("timestamp", 0) >= cutoff_ms]

    sessions = group_by_session(entries)

    # Determine boundaries
    recompute = should_recompute_boundaries(existing_baseline)
    boundaries_computed_at = datetime.now().isoformat() if recompute else None

    if recompute:
        # Compute boundaries from all entries (aggregate across all days)
        all_hourly = [0] * 24
        for entry in entries:
            ts = entry.get("timestamp")
            if ts:
                dt = datetime.fromtimestamp(ts / 1000)
                all_hourly[dt.hour] += 1
        boundaries = discover_boundaries(all_hourly)
    else:
        # Reuse existing boundaries
        boundaries = DEFAULT_BOUNDARIES
        if existing_baseline and "days" in existing_baseline:
            # Get boundaries from first day that has them
            for day_data in existing_baseline["days"].values():
                if "boundaries" in day_data:
                    boundaries = day_data["boundaries"]
                    break
        boundaries_computed_at = existing_baseline.get("boundaries_computed_at")

    # Compute per-day stats
    day_names = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    days = {}
    for day_name in day_names:
        bucket_stats = compute_bucket_stats(
            sessions, day_name, boundaries, window_days
        )
        days[day_name] = {
            "boundaries": boundaries,
            "buckets": bucket_stats,
        }

    # Compute global stats (across all days/buckets)
    all_durations = []
    total_sessions = 0
    for _session_id, session_entries in sessions.items():
        timestamps = [e.get("timestamp") for e in session_entries if e.get("timestamp")]
        if len(timestamps) >= 2:
            duration_ms = max(timestamps) - min(timestamps)
            all_durations.append(duration_ms / 1000 / 60)
        else:
            all_durations.append(0.0)
        total_sessions += 1

    global_stats = {
        "session_count": total_sessions,
        "duration": compute_bucket_percentiles(all_durations),
    }

    result = {
        "window_days": window_days,
        "days": days,
        "global_stats": global_stats,
    }

    if boundaries_computed_at:
        result["boundaries_computed_at"] = boundaries_computed_at

    return result


def compute_baseline(
    history_path: Path,
    existing_baseline: dict | None = None,
) -> dict:
    """
    Compute full baseline from history file.

    Includes both v1 (legacy) and v2 (time-bucket) statistics.

    Args:
        history_path: Path to history.jsonl
        existing_baseline: Existing baseline for boundary reuse

    Returns:
        Baseline dict ready for JSON serialization.
    """
    entries = parse_history(history_path)
    sessions = group_by_session(entries)

    # Check minimum sessions
    min_sessions = 10
    insufficient_data = len(sessions) < min_sessions

    if insufficient_data:
        print(
            f"Warning: Only {len(sessions)} sessions in history "
            f"(minimum {min_sessions} recommended). Baseline may be unreliable.",
            file=sys.stderr,
        )

    # Compute v1 metrics (legacy, for backward compatibility)
    durations, prompt_counts = compute_session_metrics(sessions)
    duration_percentiles = compute_percentiles(durations)
    prompt_percentiles = compute_percentiles([float(p) for p in prompt_counts])

    typical_hours = compute_typical_hours(entries)

    baseline = {
        "computed_at": datetime.now().isoformat(),
        "session_duration_minutes": duration_percentiles,
        "prompts_per_session": prompt_percentiles,
        "typical_hours": typical_hours,
        "insufficient_data": insufficient_data,
    }

    # Compute v2 metrics (time-bucket based)
    v2_data = compute_baseline_v2(history_path, existing_baseline=existing_baseline)
    baseline.update(v2_data)

    return baseline


def main():
    """
    Main entry point for baseline computation.

    Pipeline:
    1. Check if history.jsonl exists
    2. Acquire lock (skip if already locked)
    3. Read existing baseline (for boundary reuse)
    4. Compute baseline
    5. Write baseline.json
    6. Cleanup old session files
    7. Release lock
    """
    history_path = get_history_path()

    if not history_path.exists():
        print(f"Error: History file not found: {history_path}", file=sys.stderr)
        print("Claude Code creates this file automatically when used.", file=sys.stderr)
        sys.exit(1)

    # Try to acquire lock
    if not acquire_baseline_lock():
        print("Info: Baseline update already in progress, skipping.", file=sys.stderr)
        sys.exit(0)

    try:
        # Read existing baseline for boundary reuse
        existing = read_baseline()
        existing_dict = None
        if existing is not None:
            # Convert to dict for compute_baseline_v2
            existing_dict = {
                "boundaries_computed_at": (
                    existing.boundaries_computed_at.isoformat()
                    if existing.boundaries_computed_at
                    else None
                ),
                "days": (
                    {
                        name: day.to_dict()
                        for name, day in existing.days.items()
                    }
                    if existing.days
                    else None
                ),
            }

        # Compute and write baseline
        baseline = compute_baseline(history_path, existing_baseline=existing_dict)

        if write_baseline(baseline):
            # Report v2 stats if available
            v2_info = ""
            if "days" in baseline:
                total_buckets = sum(
                    len(day.get("buckets", {}))
                    for day in baseline["days"].values()
                )
                v2_info = f", {total_buckets} bucket stats"

            print(
                f"Baseline updated: {len(baseline['typical_hours'])} typical hours"
                f"{v2_info}",
                file=sys.stderr,
            )
        else:
            print("Error: Failed to write baseline.", file=sys.stderr)
            sys.exit(1)

        # Cleanup old sessions
        removed = cleanup_old_sessions(max_age_days=7)
        if removed > 0:
            print(f"Cleaned up {removed} old session files.", file=sys.stderr)

    finally:
        release_baseline_lock()

    sys.exit(0)


if __name__ == "__main__":
    main()
