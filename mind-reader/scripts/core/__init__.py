"""
Mind-reader plugin library.
Provides settings, state management, and detection logic.
"""

from .boundaries import (
    DEFAULT_BOUNDARIES,
    discover_boundaries,
    get_all_bucket_names,
    get_bucket_name,
    is_scipy_available,
)
from .sentiment import (
    SentimentNudge,
    analyze_prompt,
    check_rolling_sentiment,
    is_vader_available,
    update_sentiment_window,
)
from .settings import (
    DEFAULT_SETTINGS,
    SentimentSettings,
    Settings,
    TemporalSettings,
    load_settings,
)
from .state import (
    Baseline,
    BucketStats,
    DayBaseline,
    SessionState,
    acquire_baseline_lock,
    cleanup_old_sessions,
    get_baseline_path,
    get_data_dir,
    get_session_path,
    is_baseline_locked,
    read_baseline,
    read_session_state,
    release_baseline_lock,
    write_baseline,
    write_session_state,
)
from .temporal import (
    TemporalNudge,
    check_bucket_duration,
    check_bucket_rarity,
    check_duration_threshold,
    check_prompt_threshold,
    check_unusual_hour,
    get_current_bucket,
)

__all__ = [
    # Settings
    "Settings",
    "TemporalSettings",
    "SentimentSettings",
    "DEFAULT_SETTINGS",
    "load_settings",
    # State
    "SessionState",
    "Baseline",
    "BucketStats",
    "DayBaseline",
    "get_data_dir",
    "get_baseline_path",
    "get_session_path",
    "acquire_baseline_lock",
    "release_baseline_lock",
    "is_baseline_locked",
    "read_baseline",
    "write_baseline",
    "read_session_state",
    "write_session_state",
    "cleanup_old_sessions",
    # Boundaries
    "DEFAULT_BOUNDARIES",
    "is_scipy_available",
    "discover_boundaries",
    "get_bucket_name",
    "get_all_bucket_names",
    # Temporal
    "TemporalNudge",
    "check_duration_threshold",
    "check_prompt_threshold",
    "check_unusual_hour",
    "get_current_bucket",
    "check_bucket_rarity",
    "check_bucket_duration",
    # Sentiment
    "SentimentNudge",
    "is_vader_available",
    "analyze_prompt",
    "check_rolling_sentiment",
    "update_sentiment_window",
]
