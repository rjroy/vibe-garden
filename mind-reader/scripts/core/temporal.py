"""
Temporal detection logic for mind-reader plugin.
Checks session duration, prompt count, and unusual hours.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .settings import Settings
from .state import Baseline, SessionState


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

    return TemporalNudge(
        check_type="duration",
        message=f"{int(duration_minutes)} minutes (your {threshold_key} is {int(threshold)}). Long session?",
    )


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

    return TemporalNudge(
        check_type="prompts",
        message=f"{state.prompt_count} prompts (your {threshold_key} is {int(threshold)}). Deep in the weeds?",
    )


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

    return TemporalNudge(
        check_type="hour",
        message=f"Working at {current_hour:02d}:00, outside your typical hours. Burning the midnight oil?",
    )
