#!/usr/bin/env python3
"""
Baseline computation script for mind-reader plugin.
Reads ~/.claude/history.jsonl and computes temporal statistics.
Run via cron daily (recommended: 0 3 * * *).
"""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Handle import from different directories
try:
    from lib.state import (
        acquire_baseline_lock,
        cleanup_old_sessions,
        release_baseline_lock,
        write_baseline,
    )
except ImportError:
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from lib.state import (
        acquire_baseline_lock,
        cleanup_old_sessions,
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


def compute_typical_days(entries: list[dict]) -> list[str]:
    """
    Compute typical days (at or above median prompt count).

    Args:
        entries: List of history entries

    Returns:
        List of typical day names.
    """
    day_counts: Counter[str] = Counter()

    for entry in entries:
        ts = entry.get("timestamp")
        if ts is None:
            continue
        dt = datetime.fromtimestamp(ts / 1000)
        day_counts[dt.strftime("%A")] += 1

    if not day_counts:
        return []

    # Find median threshold
    counts = sorted(day_counts.values())
    median = counts[len(counts) // 2]

    return [d for d, c in day_counts.items() if c >= median]


def compute_baseline(history_path: Path) -> dict:
    """
    Compute full baseline from history file.

    Args:
        history_path: Path to history.jsonl

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

    # Compute metrics
    durations, prompt_counts = compute_session_metrics(sessions)
    duration_percentiles = compute_percentiles(durations)
    prompt_percentiles = compute_percentiles([float(p) for p in prompt_counts])

    typical_hours = compute_typical_hours(entries)
    typical_days = compute_typical_days(entries)

    return {
        "computed_at": datetime.now().isoformat(),
        "session_duration_minutes": duration_percentiles,
        "prompts_per_session": prompt_percentiles,
        "typical_hours": typical_hours,
        "typical_days": typical_days,
        "insufficient_data": insufficient_data,
    }


def main():
    """
    Main entry point for baseline computation.

    Pipeline:
    1. Check if history.jsonl exists
    2. Acquire lock (skip if already locked)
    3. Compute baseline
    4. Write baseline.json
    5. Cleanup old session files
    6. Release lock
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
        # Compute and write baseline
        baseline = compute_baseline(history_path)

        if write_baseline(baseline):
            print(
                f"Baseline updated: {len(baseline['typical_hours'])} typical hours, "
                f"{len(baseline['typical_days'])} typical days",
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
