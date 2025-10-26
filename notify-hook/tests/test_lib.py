"""
Unit tests for lib.py (config, sanitization, filtering, rate limiting).
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import (
    Config,
    DEFAULT_CONFIG,
    load_config,
    sanitize_message,
    should_filter_message,
    is_rate_limited,
    _merge_config,
    _rate_limit_state
)


class TestConfig:
    """Test Config data class."""

    def test_from_dict_with_defaults(self):
        """Test creating Config with default values."""
        config = Config.from_dict({})
        assert config.backends == DEFAULT_CONFIG["backends"]
        assert config.filtering == DEFAULT_CONFIG["filtering"]
        assert config.privacy == DEFAULT_CONFIG["privacy"]
        assert config.rate_limiting == DEFAULT_CONFIG["rate_limiting"]

    def test_from_dict_with_custom_values(self):
        """Test creating Config with custom values."""
        custom = {
            "backends": {"ntfy": {"enabled": False}},
            "filtering": {"exclude_patterns": ["^Test:"]},
            "privacy": {"max_message_length": 50},
            "rate_limiting": {"max_per_minute": 2}
        }
        config = Config.from_dict(custom)
        assert config.backends == custom["backends"]
        assert config.filtering == custom["filtering"]
        assert config.privacy == custom["privacy"]
        assert config.rate_limiting == custom["rate_limiting"]


class TestMergeConfig:
    """Test config merging logic."""

    def test_merge_flat_keys(self):
        """Test merging non-nested keys."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        _merge_config(base, override)
        assert base == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {"backends": {"ntfy": {"enabled": True, "topic": "default"}}}
        override = {"backends": {"ntfy": {"topic": "custom"}}}
        _merge_config(base, override)
        assert base["backends"]["ntfy"]["enabled"] is True
        assert base["backends"]["ntfy"]["topic"] == "custom"


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_config_defaults(self):
        """Test loading config with no files or env vars."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                with mock.patch("pathlib.Path.home", return_value=Path(tmpdir)):
                    with mock.patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                        config = load_config()
                        assert config.backends["ntfy"]["enabled"] is True
                        assert config.backends["ntfy"]["topic"] == "claude-{owner}-{repo}"

    def test_load_config_from_user_file(self, tmp_path):
        """Test loading config from user config file."""
        user_config = tmp_path / ".claude"
        user_config.mkdir()
        config_file = user_config / "notify-config.json"
        config_file.write_text(json.dumps({
            "backends": {"ntfy": {"topic": "user-topic"}}
        }))

        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("pathlib.Path.home", return_value=tmp_path):
                with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
                    config = load_config()
                    assert config.backends["ntfy"]["topic"] == "user-topic"

    def test_load_config_from_repo_file(self, tmp_path):
        """Test loading config from repo config file."""
        repo_config = tmp_path / ".claude"
        repo_config.mkdir()
        config_file = repo_config / "notify-config.json"
        config_file.write_text(json.dumps({
            "backends": {"ntfy": {"topic": "repo-topic"}}
        }))

        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("pathlib.Path.home", return_value=Path("/nonexistent")):
                with mock.patch("pathlib.Path.cwd", return_value=tmp_path):
                    config = load_config()
                    assert config.backends["ntfy"]["topic"] == "repo-topic"

    def test_load_config_hierarchy(self, tmp_path):
        """Test config hierarchy: env vars > repo config > user config > defaults."""
        # User config
        user_config_dir = tmp_path / "user" / ".claude"
        user_config_dir.mkdir(parents=True)
        (user_config_dir / "notify-config.json").write_text(json.dumps({
            "backends": {"ntfy": {"topic": "user-topic"}}
        }))

        # Repo config
        repo_config_dir = tmp_path / "repo" / ".claude"
        repo_config_dir.mkdir(parents=True)
        (repo_config_dir / "notify-config.json").write_text(json.dumps({
            "backends": {"ntfy": {"topic": "repo-topic"}}
        }))

        # Env var should override everything
        with mock.patch.dict(os.environ, {"VIBE_GARDEN_NTFY_TOPIC": "env-topic"}):
            with mock.patch("pathlib.Path.home", return_value=tmp_path / "user"):
                with mock.patch("pathlib.Path.cwd", return_value=tmp_path / "repo"):
                    config = load_config()
                    assert config.backends["ntfy"]["topic"] == "env-topic"

    def test_load_config_env_vars(self):
        """Test environment variable overrides."""
        env_vars = {
            "VIBE_GARDEN_NTFY_TOPIC": "custom-topic",
            "VIBE_GARDEN_NTFY_DISCORD_WEBHOOK": "https://discord.webhook",
            "VIBE_GARDEN_NTFY_SLACK_WEBHOOK": "https://slack.webhook"
        }
        with mock.patch.dict(os.environ, env_vars):
            with tempfile.TemporaryDirectory() as tmpdir:
                with mock.patch("pathlib.Path.home", return_value=Path(tmpdir)):
                    with mock.patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                        config = load_config()
                        assert config.backends["ntfy"]["topic"] == "custom-topic"
                        assert config.backends["discord"]["webhook_url"] == "https://discord.webhook"
                        assert config.backends["discord"]["enabled"] is True
                        assert config.backends["slack"]["webhook_url"] == "https://slack.webhook"
                        assert config.backends["slack"]["enabled"] is True

    def test_load_config_global_disable(self):
        """Test global disable via VIBE_GARDEN_NTFY_ENABLED=false."""
        with mock.patch.dict(os.environ, {"VIBE_GARDEN_NTFY_ENABLED": "false"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with mock.patch("pathlib.Path.home", return_value=Path(tmpdir)):
                    with mock.patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                        config = load_config()
                        assert config.backends["ntfy"]["enabled"] is False
                        assert config.backends["discord"]["enabled"] is False
                        assert config.backends["slack"]["enabled"] is False


class TestSanitizeMessage:
    """Test message sanitization."""

    def test_sanitize_absolute_paths(self):
        """Test removal of absolute paths."""
        config = Config.from_dict(DEFAULT_CONFIG)
        message = "Error in /home/user/project/file.py at line 42"
        sanitized = sanitize_message(message, config)
        assert "/home/user/project/file.py" not in sanitized
        assert "[path]" in sanitized

    def test_sanitize_relative_paths(self):
        """Test removal of relative paths."""
        config = Config.from_dict(DEFAULT_CONFIG)
        message = "Check ./src/main.py and ../lib/utils.py"
        sanitized = sanitize_message(message, config)
        assert "./src/main.py" not in sanitized
        assert "../lib/utils.py" not in sanitized
        assert "[path]" in sanitized

    def test_sanitize_code_blocks(self):
        """Test removal of code blocks."""
        config = Config.from_dict(DEFAULT_CONFIG)
        message = "Error: ```python\ndef foo(): pass\n```"
        sanitized = sanitize_message(message, config)
        assert "```" not in sanitized
        assert "def foo()" not in sanitized
        assert "[code]" in sanitized

    def test_sanitize_inline_code(self):
        """Test removal of inline code."""
        config = Config.from_dict(DEFAULT_CONFIG)
        message = "Call `function()` with `arg=value`"
        sanitized = sanitize_message(message, config)
        assert "function()" not in sanitized
        assert "[code]" in sanitized

    def test_sanitize_truncate(self):
        """Test message truncation."""
        config = Config.from_dict({
            "privacy": {"max_message_length": 20, "strip_paths": False, "strip_code": False}
        })
        message = "This is a very long message that exceeds the maximum length"
        sanitized = sanitize_message(message, config)
        assert len(sanitized) <= 20
        assert sanitized.endswith("...")

    def test_sanitize_no_strip_paths(self):
        """Test sanitization with strip_paths disabled."""
        config = Config.from_dict({
            "privacy": {"strip_paths": False, "strip_code": True, "max_message_length": 100}
        })
        message = "File at /home/user/file.py"
        sanitized = sanitize_message(message, config)
        assert "/home/user/file.py" in sanitized

    def test_sanitize_no_strip_code(self):
        """Test sanitization with strip_code disabled."""
        config = Config.from_dict({
            "privacy": {"strip_paths": True, "strip_code": False, "max_message_length": 100}
        })
        message = "Run `command` to fix"
        sanitized = sanitize_message(message, config)
        assert "`command`" in sanitized


class TestShouldFilterMessage:
    """Test message filtering."""

    def test_filter_exclude_pattern_match(self):
        """Test filtering with matching exclude pattern."""
        config = Config.from_dict({
            "filtering": {"exclude_patterns": ["^Debug:", "^Trace:"], "include_patterns": []}
        })
        assert should_filter_message("Debug: some message", config) is True
        assert should_filter_message("Trace: stack trace", config) is True

    def test_filter_exclude_pattern_no_match(self):
        """Test no filtering when exclude pattern doesn't match."""
        config = Config.from_dict({
            "filtering": {"exclude_patterns": ["^Debug:"], "include_patterns": []}
        })
        assert should_filter_message("Info: important message", config) is False

    def test_filter_include_pattern_match(self):
        """Test filtering with matching include pattern."""
        config = Config.from_dict({
            "filtering": {"exclude_patterns": [], "include_patterns": ["^Task"]}
        })
        assert should_filter_message("Task complete", config) is False
        assert should_filter_message("Info: ready", config) is True

    def test_filter_include_and_exclude(self):
        """Test exclude patterns take precedence over include patterns."""
        config = Config.from_dict({
            "filtering": {
                "exclude_patterns": ["^Debug:"],
                "include_patterns": ["Debug"]
            }
        })
        # Even though "Debug" matches include pattern, exclude takes precedence
        assert should_filter_message("Debug: test", config) is True

    def test_filter_no_patterns(self):
        """Test no filtering when no patterns defined."""
        config = Config.from_dict({
            "filtering": {"exclude_patterns": [], "include_patterns": []}
        })
        assert should_filter_message("Any message", config) is False


class TestIsRateLimited:
    """Test rate limiting."""

    def setup_method(self):
        """Clear rate limit state before each test."""
        _rate_limit_state.clear()

    def test_rate_limit_first_send(self):
        """Test first send is not rate limited."""
        config = Config.from_dict(DEFAULT_CONFIG)
        assert is_rate_limited("ntfy", config) is False

    def test_rate_limit_subsequent_send(self):
        """Test subsequent send within cooldown is rate limited."""
        config = Config.from_dict({"rate_limiting": {"enabled": True, "max_per_minute": 1}})

        # First send
        assert is_rate_limited("ntfy", config) is False

        # Immediate second send should be rate limited
        assert is_rate_limited("ntfy", config) is True

    def test_rate_limit_after_cooldown(self):
        """Test send after cooldown is not rate limited."""
        config = Config.from_dict({"rate_limiting": {"enabled": True, "max_per_minute": 1}})

        # First send
        is_rate_limited("ntfy", config)

        # Simulate time passing (61 seconds)
        _rate_limit_state["ntfy"] = datetime.now() - timedelta(seconds=61)

        # Should not be rate limited anymore
        assert is_rate_limited("ntfy", config) is False

    def test_rate_limit_disabled(self):
        """Test rate limiting can be disabled."""
        config = Config.from_dict({"rate_limiting": {"enabled": False}})

        # Multiple sends should all succeed
        assert is_rate_limited("ntfy", config) is False
        assert is_rate_limited("ntfy", config) is False
        assert is_rate_limited("ntfy", config) is False

    def test_rate_limit_per_backend(self):
        """Test rate limiting is tracked per backend."""
        config = Config.from_dict(DEFAULT_CONFIG)

        # Send to ntfy
        assert is_rate_limited("ntfy", config) is False

        # Immediate send to discord should not be rate limited (different backend)
        assert is_rate_limited("discord", config) is False

        # But second send to ntfy should be rate limited
        assert is_rate_limited("ntfy", config) is True

    def test_rate_limit_higher_rate(self):
        """Test higher rate limit (2 per minute)."""
        config = Config.from_dict({"rate_limiting": {"enabled": True, "max_per_minute": 2}})

        # First two sends should succeed
        assert is_rate_limited("ntfy", config) is False

        # Simulate 30 seconds passing (should allow one more)
        _rate_limit_state["ntfy"] = datetime.now() - timedelta(seconds=30)
        assert is_rate_limited("ntfy", config) is False

        # Immediate third send should be rate limited
        assert is_rate_limited("ntfy", config) is True
