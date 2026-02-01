"""
Temporal detection logic for mind-reader plugin.
Checks session duration, prompt count, and unusual hours.
Includes v2 bucket-based detection.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .boundaries import get_bucket_name
from .settings import Settings
from .state import Baseline, BucketStats, SessionState


@dataclass
class TemporalNudge:
    """Result of a temporal check."""

    check_type: str
    message: str


def check_duration_threshold(
    state: SessionState,
    baseline: Baseline,
    settings: Settings,
) -> TemporalNudge | None:
    """
    Check if session duration exceeds threshold.

    Args:
        state: Current session state
        baseline: Historical baseline
        settings: Plugin settings

    Returns:
        TemporalNudge if threshold exceeded, None otherwise.
    """
    if not settings.temporal.enabled:
        return None

    if baseline.insufficient_data:
        return None

    threshold_key = settings.temporal.duration_threshold
    threshold = baseline.session_duration_minutes.get(threshold_key)
    if threshold is None:
        return None

    duration_minutes = (datetime.now() - state.started_at).total_seconds() / 60

    if duration_minutes <= threshold:
        return None

    msg = (
        f"{int(duration_minutes)} minutes "
        f"(your {threshold_key} is {int(threshold)}). Long session?"
    )
    return TemporalNudge(check_type="duration", message=msg)


def check_prompt_threshold(
    state: SessionState,
    baseline: Baseline,
    settings: Settings,
) -> TemporalNudge | None:
    """
    Check if prompt count exceeds threshold.

    Args:
        state: Current session state
        baseline: Historical baseline
        settings: Plugin settings

    Returns:
        TemporalNudge if threshold exceeded, None otherwise.
    """
    if not settings.temporal.enabled:
        return None

    if baseline.insufficient_data:
        return None

    threshold_key = settings.temporal.prompt_threshold
    threshold = baseline.prompts_per_session.get(threshold_key)
    if threshold is None:
        return None

    if state.prompt_count <= threshold:
        return None

    msg = (
        f"{state.prompt_count} prompts "
        f"(your {threshold_key} is {int(threshold)}). Deep in the weeds?"
    )
    return TemporalNudge(check_type="prompts", message=msg)


def check_unusual_hour(
    baseline: Baseline,
    settings: Settings,
    current_hour: int | None = None,
) -> TemporalNudge | None:
    """
    Check if current hour is unusual.

    Args:
        baseline: Historical baseline
        settings: Plugin settings
        current_hour: Hour to check (0-23), uses current time if None

    Returns:
        TemporalNudge if unusual hour, None otherwise.
    """
    if not settings.temporal.enabled:
        return None

    if not settings.temporal.check_hours:
        return None

    if not baseline.typical_hours:
        return None

    if current_hour is None:
        current_hour = datetime.now().hour

    if current_hour in baseline.typical_hours:
        return None

    msg = (
        f"Working at {current_hour:02d}:00, outside your typical hours. "
        "Burning the midnight oil?"
    )
    return TemporalNudge(check_type="hour", message=msg)


# ============================================================================
# V2 Bucket-Based Detection
# ============================================================================


def get_current_bucket(
    baseline: Baseline,
    now: datetime | None = None,
) -> tuple[str, str, BucketStats | None]:
    """
    Get the current day/bucket and its stats from baseline.

    Args:
        baseline: Historical baseline with v2 data
        now: Current datetime, uses datetime.now() if None

    Returns:
        Tuple of (day_name, bucket_name, bucket_stats or None if not found).
    """
    if now is None:
        now = datetime.now()

    day_name = now.strftime("%A").lower()
    hour = now.hour

    # Check if baseline has v2 data
    if not baseline.has_v2_data() or baseline.days is None:
        return day_name, "unknown", None

    day_baseline = baseline.days.get(day_name)
    if day_baseline is None:
        return day_name, "unknown", None

    bucket_name = get_bucket_name(hour, day_baseline.boundaries)
    bucket_stats = day_baseline.buckets.get(bucket_name)

    return day_name, bucket_name, bucket_stats


def check_bucket_rarity(
    baseline: Baseline,
    settings: Settings,
    now: datetime | None = None,
) -> TemporalNudge | None:
    """
    Check if current time bucket is rare (low session rate).

    This is the first stage of the two-stage hurdle model:
    "How unusual is it that you're working at all right now?"

    Args:
        baseline: Historical baseline with v2 data
        settings: Plugin settings
        now: Current datetime, uses datetime.now() if None

    Returns:
        TemporalNudge if bucket is rare, None otherwise.
    """
    if not settings.temporal.enabled:
        return None

    if not baseline.has_v2_data():
        return None

    day_name, bucket_name, bucket_stats = get_current_bucket(baseline, now)

    if bucket_stats is None:
        return None

    threshold = settings.temporal.bucket_rarity_threshold

    # Zero sessions = maximally rare
    if bucket_stats.session_count == 0:
        return TemporalNudge(
            check_type="bucket_rarity",
            message=f"Working {day_name.capitalize()} {bucket_name.replace('_', ' ')} "
            f"(no sessions recorded in this slot). New territory?",
        )

    if bucket_stats.session_rate >= threshold:
        return None

    # Convert rate to percentage for human-readable message
    rate_pct = int(bucket_stats.session_rate * 100)

    return TemporalNudge(
        check_type="bucket_rarity",
        message=f"Working {day_name.capitalize()} {bucket_name.replace('_', ' ')} "
        f"(rare for you, ~{rate_pct}% of {day_name.capitalize()}s). Unusual schedule?",
    )


def check_bucket_duration(
    state: SessionState,
    baseline: Baseline,
    settings: Settings,
    now: datetime | None = None,
) -> TemporalNudge | None:
    """
    Check if session duration exceeds bucket's typical duration.

    This is the second stage of the two-stage hurdle model:
    "Given that you're working now, how long is too long?"

    Args:
        state: Current session state
        baseline: Historical baseline with v2 data
        settings: Plugin settings
        now: Current datetime, uses datetime.now() if None

    Returns:
        TemporalNudge if duration exceeds threshold, None otherwise.
    """
    if not settings.temporal.enabled:
        return None

    if not baseline.has_v2_data():
        return None

    if now is None:
        now = datetime.now()

    day_name, bucket_name, bucket_stats = get_current_bucket(baseline, now)

    if bucket_stats is None:
        return None

    # Get the threshold percentile
    threshold_key = settings.temporal.bucket_duration_threshold
    threshold = bucket_stats.duration.get(threshold_key, 0)

    # No threshold or zero means no comparison possible
    if threshold <= 0:
        return None

    # Calculate current session duration
    duration_minutes = (now - state.started_at).total_seconds() / 60

    if duration_minutes <= threshold:
        return None

    return TemporalNudge(
        check_type="bucket_duration",
        message=f"{int(duration_minutes)} minutes "
        f"(your {day_name.capitalize()} {bucket_name.replace('_', ' ')} "
        f"{threshold_key} is {int(threshold)}). Long session?",
    )
