"""
Boundary discovery for mind-reader plugin.
Finds natural activity valleys to define time buckets.
"""

from __future__ import annotations

# Default boundaries when scipy is unavailable or discovery fails
DEFAULT_BOUNDARIES = [6, 12, 18, 22]

# Bucket names for each segment (wraps around from late_night to early_morning)
BUCKET_NAMES = ["early_morning", "morning", "afternoon", "evening", "late_night"]

# Lazy-loaded scipy state
_scipy_available: bool | None = None


def is_scipy_available() -> bool:
    """
    Check if scipy is installed.

    Returns:
        True if scipy is available.
    """
    global _scipy_available

    if _scipy_available is not None:
        return _scipy_available

    try:
        from scipy.signal import argrelmin  # noqa: F401

        _scipy_available = True
    except ImportError:
        _scipy_available = False

    return _scipy_available


def discover_boundaries(hourly_counts: list[int]) -> list[int]:
    """
    Discover natural boundaries from hourly activity counts.

    Uses local minima detection with circular wrap-around to find
    valleys in activity that make good bucket boundaries.

    Args:
        hourly_counts: List of 24 integers representing activity per hour (0-23)

    Returns:
        List of 4 boundary hours, or DEFAULT_BOUNDARIES if discovery fails.
    """
    if not hourly_counts or len(hourly_counts) != 24:
        return DEFAULT_BOUNDARIES.copy()

    if not is_scipy_available():
        return DEFAULT_BOUNDARIES.copy()

    # Need enough variation to find valleys
    if max(hourly_counts) == 0 or max(hourly_counts) == min(hourly_counts):
        return DEFAULT_BOUNDARIES.copy()

    try:
        import numpy as np
        from scipy.signal import argrelmin

        # Create circular array (duplicate to handle wrap-around)
        counts = np.array(hourly_counts, dtype=float)
        circular = np.concatenate([counts, counts, counts])

        # Find local minima with order=2 (must be lower than 2 neighbors on each side)
        minima_indices = argrelmin(circular, order=2)[0]

        # Filter to the middle section (hours 24-47) to get original hour indices
        minima = [idx - 24 for idx in minima_indices if 24 <= idx < 48]

        # Remove duplicates and sort
        minima = sorted(set(minima))

        if len(minima) < 4:
            return DEFAULT_BOUNDARIES.copy()

        # Select 4 boundaries that best divide the day
        # Prefer boundaries near typical transitions (6am, noon, 6pm, 10pm)
        preferred = [6, 12, 18, 22]
        selected = []

        for target in preferred:
            # Find the minimum closest to this target
            # Use default argument to bind loop variable
            closest = min(
                minima,
                key=lambda x, t=target: min(abs(x - t), 24 - abs(x - t)),
            )
            selected.append(closest)
            # Remove to avoid reselection
            if closest in minima:
                minima.remove(closest)

        return sorted(selected)

    except Exception:
        return DEFAULT_BOUNDARIES.copy()


def get_bucket_name(hour: int, boundaries: list[int]) -> str:
    """
    Map an hour to its bucket name.

    Args:
        hour: Hour of day (0-23)
        boundaries: List of 4 boundary hours (must be sorted)

    Returns:
        Bucket name string.
    """
    if not boundaries or len(boundaries) != 4:
        boundaries = DEFAULT_BOUNDARIES

    # Ensure sorted
    b = sorted(boundaries)

    # Map hour to bucket
    # Structure: late_night (0-b[0]), early_morning (b[0]-b[1]),
    #            morning (b[1]-b[2]), afternoon (b[2]-b[3]),
    #            evening (b[3]-24/0)
    if hour < b[0]:
        return "late_night"
    elif hour < b[1]:
        return "early_morning"
    elif hour < b[2]:
        return "morning"
    elif hour < b[3]:
        return "afternoon"
    else:
        return "evening"


def get_all_bucket_names() -> list[str]:
    """Return all bucket names in order."""
    return ["late_night", "early_morning", "morning", "afternoon", "evening"]
