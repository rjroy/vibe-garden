#!/usr/bin/env python3
"""
Core library for notify-hook plugin.
Provides config loading, message sanitization, filtering, and rate limiting.
Stdlib only - no external dependencies.
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


# Default configuration
DEFAULT_CONFIG = {
    "topic_template": "claude-{owner}-repos",
    "backends": {
        "ntfy": {
            "enabled": True,
            "priority": "default",
            "tags": ["computer", "claude"],
        },
        "discord": {"enabled": False, "webhook_url": ""},
        "slack": {"enabled": False, "webhook_url": ""},
    },
    "filtering": {"exclude_patterns": ["^Debug:", "^Trace:"], "include_patterns": []},
    "privacy": {"max_message_length": 100, "strip_paths": True, "strip_code": True},
    "rate_limiting": {"enabled": True, "max_per_minute": 1},
}


@dataclass
class Config:
    """Configuration data class."""

    topic_template: str
    backends: Dict[str, Dict[str, Any]]
    filtering: Dict[str, List[str]]
    privacy: Dict[str, Any]
    rate_limiting: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        return cls(
            topic_template=data.get("topic_template", DEFAULT_CONFIG["topic_template"]),
            backends=data.get("backends", DEFAULT_CONFIG["backends"]),
            filtering=data.get("filtering", DEFAULT_CONFIG["filtering"]),
            privacy=data.get("privacy", DEFAULT_CONFIG["privacy"]),
            rate_limiting=data.get("rate_limiting", DEFAULT_CONFIG["rate_limiting"]),
        )


# In-memory rate limiting state (per-backend timestamps)
_rate_limit_state: Dict[str, datetime] = {}


def load_config() -> Config:
    """
    Load configuration from multiple sources with hierarchy:
    env vars > repo config > user config > defaults

    Returns:
        Config object with merged configuration
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()

    # Load user config (~/.claude/notify-config.json)
    user_config_path = Path.home() / ".claude" / "notify-config.json"
    if user_config_path.exists():
        try:
            with open(user_config_path) as f:
                user_config = json.load(f)
                _merge_config(config, user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load user config: {e}", file=sys.stderr)

    # Load repo config (.claude/notify-config.json)
    repo_config_path = Path.cwd() / ".claude" / "notify-config.json"
    if repo_config_path.exists():
        try:
            with open(repo_config_path) as f:
                repo_config = json.load(f)
                _merge_config(config, repo_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load repo config: {e}", file=sys.stderr)

    # Apply environment variable overrides
    env_topic = os.getenv("VIBE_GARDEN_NTFY_TOPIC")
    if env_topic:
        config["topic_template"] = env_topic

    env_discord_webhook = os.getenv("VIBE_GARDEN_NTFY_DISCORD_WEBHOOK")
    if env_discord_webhook:
        config["backends"]["discord"]["webhook_url"] = env_discord_webhook
        config["backends"]["discord"]["enabled"] = True

    env_slack_webhook = os.getenv("VIBE_GARDEN_NTFY_SLACK_WEBHOOK")
    if env_slack_webhook:
        config["backends"]["slack"]["webhook_url"] = env_slack_webhook
        config["backends"]["slack"]["enabled"] = True

    env_enabled = os.getenv("VIBE_GARDEN_NTFY_ENABLED")
    if env_enabled is not None:
        # Disable all backends if set to false
        if env_enabled.lower() in ("false", "0", "no"):
            for backend in config["backends"].values():
                backend["enabled"] = False

    return Config.from_dict(config)


def _merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """
    Recursively merge override config into base config.
    Modifies base in-place.
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_config(base[key], value)
        else:
            base[key] = value


def sanitize_message(message: str, config: Config) -> str:
    """
    Sanitize message according to privacy rules.

    Args:
        message: Raw message to sanitize
        config: Configuration with privacy settings

    Returns:
        Sanitized message
    """
    privacy = config.privacy
    sanitized = message

    # Strip file paths (absolute and relative)
    if privacy.get("strip_paths", True):
        # Match absolute paths (starting with / or ~)
        sanitized = re.sub(r"[/~][^\s:,;\'\"]+", "[path]", sanitized)
        # Match relative paths (./path or ../path)
        sanitized = re.sub(r"\./[^\s:,;\'\"]+", "[path]", sanitized)
        sanitized = re.sub(r"\.\./[^\s:,;\'\"]+", "[path]", sanitized)

    # Strip code blocks
    if privacy.get("strip_code", True):
        # Remove code blocks (```...```)
        sanitized = re.sub(r"```[^`]*```", "[code]", sanitized)
        # Remove inline code (`...`)
        sanitized = re.sub(r"`[^`]+`", "[code]", sanitized)
        # Remove common error traces (lines starting with "at " or "Traceback")
        sanitized = re.sub(
            r'(?m)^\s*(at |Traceback|File ")[^\n]*', "[trace]", sanitized
        )

    # Truncate to max length
    max_length = privacy.get("max_message_length", 100)
    if len(sanitized) > max_length:
        sanitized = sanitized[: max_length - 3] + "..."

    return sanitized.strip()


def should_filter_message(message: str, config: Config) -> bool:
    """
    Check if message should be filtered out.

    Args:
        message: Message to check
        config: Configuration with filtering rules

    Returns:
        True if message should be dropped, False if it should be sent
    """
    filtering = config.filtering

    # Check exclude patterns
    exclude_patterns = filtering.get("exclude_patterns", [])
    for pattern in exclude_patterns:
        if re.search(pattern, message):
            return True  # Drop this message

    # Check include patterns (if any are defined)
    include_patterns = filtering.get("include_patterns", [])
    if include_patterns:
        # If include patterns exist, message must match at least one
        for pattern in include_patterns:
            if re.search(pattern, message):
                return False  # Keep this message
        return True  # Drop if no include pattern matched

    return False  # Keep by default


def is_rate_limited(backend: str, config: Config) -> bool:
    """
    Check if backend is rate limited.

    Args:
        backend: Backend name (e.g., "ntfy", "discord", "slack")
        config: Configuration with rate limiting settings

    Returns:
        True if rate limited, False if allowed to send
    """
    rate_limiting = config.rate_limiting

    if not rate_limiting.get("enabled", True):
        return False

    max_per_minute = rate_limiting.get("max_per_minute", 1)
    now = datetime.now()

    # Check last send time for this backend
    if backend in _rate_limit_state:
        last_send = _rate_limit_state[backend]
        time_since_last = now - last_send
        cooldown = timedelta(seconds=60 / max_per_minute)

        if time_since_last < cooldown:
            return True  # Rate limited

    # Update timestamp
    _rate_limit_state[backend] = now
    return False
