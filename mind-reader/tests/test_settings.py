"""
Unit tests for settings.py (settings loading and merging).
"""

import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from core.settings import (
    Settings,
    _deep_merge,
    load_settings,
)


class TestDeepMerge:
    """Test _deep_merge function."""

    def test_merge_flat_keys(self):
        """Test merging non-nested keys."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}
        # Original should not be modified
        assert base == {"a": 1, "b": 2}

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {"temporal": {"enabled": True, "duration_threshold": "p95"}}
        override = {"temporal": {"duration_threshold": "p75"}}
        result = _deep_merge(base, override)
        assert result["temporal"]["enabled"] is True
        assert result["temporal"]["duration_threshold"] == "p75"

    def test_merge_deep_nesting(self):
        """Test merging deeply nested structures."""
        base = {"a": {"b": {"c": 1, "d": 2}}}
        override = {"a": {"b": {"c": 10}}}
        result = _deep_merge(base, override)
        assert result["a"]["b"]["c"] == 10
        assert result["a"]["b"]["d"] == 2


class TestSettings:
    """Test Settings data class."""

    def test_from_dict_with_empty(self):
        """Test creating Settings from empty dict uses defaults."""
        settings = Settings.from_dict({})
        assert settings.enabled is True
        assert settings.temporal.enabled is True
        assert settings.temporal.duration_threshold == "p95"
        assert settings.sentiment.window_size == 5
        assert settings.sentiment.threshold == -0.2
        assert settings.quiet_until is None

    def test_from_dict_with_partial_temporal(self):
        """Test partial temporal settings merge correctly."""
        data = {"temporal": {"duration_threshold": "p75"}}
        settings = Settings.from_dict(data)
        assert settings.temporal.enabled is True  # Default preserved
        assert settings.temporal.duration_threshold == "p75"  # Overridden
        assert settings.temporal.prompt_threshold == "p95"  # Default preserved

    def test_from_dict_with_partial_sentiment(self):
        """Test partial sentiment settings merge correctly."""
        data = {"sentiment": {"threshold": -0.5, "cooldown_prompts": 20}}
        settings = Settings.from_dict(data)
        assert settings.sentiment.enabled is True  # Default
        assert settings.sentiment.threshold == -0.5  # Overridden
        assert settings.sentiment.cooldown_prompts == 20  # Overridden
        assert settings.sentiment.window_size == 5  # Default

    def test_from_dict_with_quiet_until(self):
        """Test parsing quiet_until timestamp."""
        future = datetime.now() + timedelta(hours=1)
        data = {"quiet_until": future.isoformat()}
        settings = Settings.from_dict(data)
        assert settings.quiet_until is not None
        assert settings.quiet_until.hour == future.hour

    def test_from_dict_with_invalid_quiet_until(self):
        """Test invalid quiet_until is ignored."""
        data = {"quiet_until": "not-a-timestamp"}
        settings = Settings.from_dict(data)
        assert settings.quiet_until is None

    def test_from_dict_disabled(self):
        """Test disabled plugin."""
        data = {"enabled": False}
        settings = Settings.from_dict(data)
        assert settings.enabled is False


class TestIsQuiet:
    """Test Settings.is_quiet() method."""

    def test_is_quiet_when_none(self):
        """Test not quiet when quiet_until is None."""
        settings = Settings.from_dict({})
        assert settings.is_quiet() is False

    def test_is_quiet_when_future(self):
        """Test is quiet when quiet_until is in future."""
        future = datetime.now() + timedelta(hours=1)
        settings = Settings.from_dict({"quiet_until": future.isoformat()})
        assert settings.is_quiet() is True

    def test_is_quiet_when_past(self):
        """Test not quiet when quiet_until is in past."""
        past = datetime.now() - timedelta(hours=1)
        settings = Settings.from_dict({"quiet_until": past.isoformat()})
        assert settings.is_quiet() is False


class TestLoadSettings:
    """Test load_settings function."""

    def test_load_missing_file(self, tmp_path):
        """Test loading from non-existent file returns defaults."""
        settings = load_settings(tmp_path / "nonexistent.json")
        assert settings.enabled is True
        assert settings.temporal.enabled is True

    def test_load_valid_file(self, tmp_path):
        """Test loading from valid settings file."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(
            json.dumps(
                {
                    "enabled": False,
                    "temporal": {"duration_threshold": "p75"},
                }
            )
        )
        settings = load_settings(settings_file)
        assert settings.enabled is False
        assert settings.temporal.duration_threshold == "p75"

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON returns defaults."""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("not valid json {")
        settings = load_settings(settings_file)
        assert settings.enabled is True  # Fallback to defaults

    def test_load_default_path(self):
        """Test loading from default path when not specified."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            mock.patch("pathlib.Path.home", return_value=Path(tmpdir)),
        ):
            settings = load_settings()
            # Should return defaults since file doesn't exist
            assert settings.enabled is True
