"""Tests for configuration management."""

import os
import tempfile
import pytest
from pathlib import Path

# Ensure src directory is in path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from courier_mcp.config import Config, ConfigError


class TestConfigDefaults:
    """Test default configuration values."""

    def test_config_defaults(self):
        """Verify all default values are set correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty config to use defaults
            config = Config()

            assert config.get("COURIER_TIMEOUT_SECONDS") == 20
            assert config.get("COURIER_MAX_RESULTS_DEFAULT") == 10
            assert config.get("COURIER_MAX_FILE_SIZE_KB") == 10
            assert config.get("COURIER_NETWORK_RETRY_ATTEMPTS") == 3
            assert config.get("COURIER_NETWORK_RETRY_BACKOFF_FACTOR") == 2
            assert config.get("COURIER_LABEL_CACHE_TTL_SECONDS") == 3600


class TestConfigEnvironmentOverrides:
    """Test environment variable overrides."""

    def test_env_var_overrides_defaults(self, monkeypatch):
        """Verify environment variables override defaults."""
        monkeypatch.setenv("COURIER_TIMEOUT_SECONDS", "30")
        monkeypatch.setenv("COURIER_MAX_RESULTS_DEFAULT", "50")

        config = Config()

        assert config.get("COURIER_TIMEOUT_SECONDS") == 30
        assert config.get("COURIER_MAX_RESULTS_DEFAULT") == 50

    def test_env_var_type_conversion(self, monkeypatch):
        """Verify environment variables are converted to correct types."""
        monkeypatch.setenv("COURIER_TIMEOUT_SECONDS", "25")

        config = Config()
        value = config.get("COURIER_TIMEOUT_SECONDS")

        assert isinstance(value, int)
        assert value == 25

    def test_invalid_env_var_type(self, monkeypatch):
        """Verify invalid environment variable types raise errors."""
        monkeypatch.setenv("COURIER_TIMEOUT_SECONDS", "not_a_number")

        with pytest.raises(ConfigError):
            Config()


class TestConfigYAMLFile:
    """Test YAML configuration file loading."""

    def test_load_yaml_config(self):
        """Verify YAML config file is loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "courier.config"
            config_file.write_text("""
COURIER_TIMEOUT_SECONDS: 30
COURIER_MAX_RESULTS_DEFAULT: 20
""")

            config = Config(str(config_file))

            assert config.get("COURIER_TIMEOUT_SECONDS") == 30
            assert config.get("COURIER_MAX_RESULTS_DEFAULT") == 20

    def test_invalid_yaml_raises_error(self):
        """Verify invalid YAML raises ConfigError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "courier.config"
            config_file.write_text("invalid: yaml: content:")

            with pytest.raises(ConfigError):
                Config(str(config_file))

    def test_yaml_env_override_priority(self, monkeypatch):
        """Verify environment variables override YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "courier.config"
            config_file.write_text("COURIER_TIMEOUT_SECONDS: 30")

            monkeypatch.setenv("COURIER_TIMEOUT_SECONDS", "40")

            config = Config(str(config_file))

            assert config.get("COURIER_TIMEOUT_SECONDS") == 40


class TestConfigGetters:
    """Test configuration getter methods."""

    def test_get_int(self):
        """Test get_int() method."""
        config = Config()

        value = config.get_int("COURIER_TIMEOUT_SECONDS")
        assert isinstance(value, int)
        assert value == 20

    def test_get_str(self):
        """Test get_str() method."""
        config = Config()

        value = config.get_str("COURIER_LOG_LEVEL")
        assert isinstance(value, str)
        assert value == "DEBUG"

    def test_get_default(self):
        """Test get() with default value."""
        config = Config()

        value = config.get("NONEXISTENT_KEY", "default_value")
        assert value == "default_value"


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_passes_with_defaults(self):
        """Verify validation passes with default values."""
        config = Config()

        # Should not raise
        config.validate()

    def test_validate_timeout_positive(self, monkeypatch):
        """Verify timeout must be positive."""
        monkeypatch.setenv("COURIER_TIMEOUT_SECONDS", "0")

        config = Config()
        with pytest.raises(ConfigError):
            config.validate()

    def test_validate_max_results_range(self, monkeypatch):
        """Verify max_results must be 1-100."""
        monkeypatch.setenv("COURIER_MAX_RESULTS_DEFAULT", "150")

        config = Config()
        with pytest.raises(ConfigError):
            config.validate()

    def test_validate_log_level(self, monkeypatch):
        """Verify log_level must be valid."""
        monkeypatch.setenv("COURIER_LOG_LEVEL", "INVALID")

        config = Config()
        with pytest.raises(ConfigError):
            config.validate()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
