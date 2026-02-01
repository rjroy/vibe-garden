"""
Settings management for mind-reader plugin.
Loads and merges user settings with defaults.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary (not modified)
        override: Override dictionary

    Returns:
        New dictionary with overrides applied.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class TemporalSettings:
    """Settings for temporal detection."""

    enabled: bool = True
    duration_threshold: str = "p95"
    prompt_threshold: str = "p95"
    check_hours: bool = True

    # V2 bucket-based thresholds
    bucket_rarity_threshold: float = 0.1  # Nudge if session_rate below this
    bucket_duration_threshold: str = "p90"  # Percentile to use for duration check


@dataclass
class SentimentSettings:
    """Settings for sentiment detection."""

    enabled: bool = True
    window_size: int = 5
    threshold: float = -0.2
    min_prompts: int = 3
    cooldown_prompts: int = 10


DEFAULT_SETTINGS = {
    "enabled": True,
    "temporal": {
        "enabled": True,
        "duration_threshold": "p95",
        "prompt_threshold": "p95",
        "check_hours": True,
        "bucket_rarity_threshold": 0.1,
        "bucket_duration_threshold": "p90",
    },
    "sentiment": {
        "enabled": True,
        "window_size": 5,
        "threshold": -0.2,
        "min_prompts": 3,
        "cooldown_prompts": 10,
    },
    "quiet_until": None,
}


@dataclass
class Settings:
    """Mind-reader plugin settings."""

    enabled: bool = True
    temporal: TemporalSettings = field(default_factory=TemporalSettings)
    sentiment: SentimentSettings = field(default_factory=SentimentSettings)
    quiet_until: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Settings:
        """
        Create Settings from a dictionary, merging with defaults.

        Args:
            data: User settings dictionary (may be partial)

        Returns:
            Settings instance with defaults applied.
        """
        merged = _deep_merge(DEFAULT_SETTINGS, data)

        temporal = TemporalSettings(
            enabled=merged["temporal"].get("enabled", True),
            duration_threshold=merged["temporal"].get("duration_threshold", "p95"),
            prompt_threshold=merged["temporal"].get("prompt_threshold", "p95"),
            check_hours=merged["temporal"].get("check_hours", True),
            bucket_rarity_threshold=merged["temporal"].get(
                "bucket_rarity_threshold", 0.1
            ),
            bucket_duration_threshold=merged["temporal"].get(
                "bucket_duration_threshold", "p90"
            ),
        )

        sentiment = SentimentSettings(
            enabled=merged["sentiment"].get("enabled", True),
            window_size=merged["sentiment"].get("window_size", 5),
            threshold=merged["sentiment"].get("threshold", -0.2),
            min_prompts=merged["sentiment"].get("min_prompts", 3),
            cooldown_prompts=merged["sentiment"].get("cooldown_prompts", 10),
        )

        quiet_until = None
        if merged.get("quiet_until"):
            try:
                quiet_until = datetime.fromisoformat(merged["quiet_until"])
            except (ValueError, TypeError):
                pass

        return cls(
            enabled=merged.get("enabled", True),
            temporal=temporal,
            sentiment=sentiment,
            quiet_until=quiet_until,
        )

    def is_quiet(self) -> bool:
        """Check if nudges are currently suppressed."""
        if self.quiet_until is None:
            return False
        return datetime.now() < self.quiet_until


def get_settings_path() -> Path:
    """Get path to settings file."""
    return Path.home() / ".claude" / "mind-reader" / "settings.json"


def load_settings(path: Path | None = None) -> Settings:
    """
    Load settings from file, falling back to defaults.

    Args:
        path: Path to settings file. Uses default if not specified.

    Returns:
        Settings instance.
    """
    if path is None:
        path = get_settings_path()

    if not path.exists():
        return Settings.from_dict({})

    try:
        with open(path) as f:
            data = json.load(f)
        return Settings.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return Settings.from_dict({})
