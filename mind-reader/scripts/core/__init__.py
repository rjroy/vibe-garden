"""
Mind-reader plugin library.
Provides settings, state management, and detection logic.
"""

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
    check_duration_threshold,
    check_prompt_threshold,
    check_unusual_hour,
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
    # Temporal
    "TemporalNudge",
    "check_duration_threshold",
    "check_prompt_threshold",
    "check_unusual_hour",
    # Sentiment
    "SentimentNudge",
    "is_vader_available",
    "analyze_prompt",
    "check_rolling_sentiment",
    "update_sentiment_window",
]
