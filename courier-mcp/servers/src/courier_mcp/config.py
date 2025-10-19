"""Configuration management for Courier MCP.

Loads configuration from:
1. courier.config (YAML file in repository)
2. Environment variables (overrides YAML)
3. Hardcoded defaults (if neither file nor env var exists)

Environment variable naming convention: COURIER_<SETTING_NAME>
Example: COURIER_TIMEOUT_SECONDS=30 overrides courier.config value
"""

import os
import yaml
from pathlib import Path
from typing import Any, final, override


class ConfigError(Exception):
    """Configuration loading or validation error."""

    pass


@final
class Config:
    """Configuration manager for Courier MCP server."""

    # Hardcoded defaults (fallback if config file missing)
    _DEFAULTS = {
        "COURIER_TIMEOUT_SECONDS": 20,
        "COURIER_MAX_RESULTS_DEFAULT": 10,
        "COURIER_MAX_FILE_SIZE_KB": 10,
        "COURIER_NETWORK_RETRY_ATTEMPTS": 3,
        "COURIER_NETWORK_RETRY_BACKOFF_FACTOR": 2,
        "COURIER_LABEL_CACHE_TTL_SECONDS": 3600,
        "COURIER_LOG_PATH": "./courier-mcp.log",
        "COURIER_LOG_LEVEL": "DEBUG",
        "GMAIL_API_QUOTA_UNITS_PER_SECOND": 250,
    }

    def __init__(self, config_file: str | None = None):
        """Initialize configuration.

        Args:
            config_file: Path to courier.config file. If None, looks for
                        courier.config in current directory or parent directories.

        Raises:
            ConfigError: If configuration is invalid or missing required values.
        """
        self._config: dict[str, Any] = {}
        self._load_config(config_file)

    def _load_config(self, config_file: str | None) -> None:
        """Load configuration from file, environment, and defaults.

        Priority (lowest to highest):
        1. Hardcoded defaults
        2. courier.config file (YAML)
        3. Environment variables

        Args:
            config_file: Optional explicit path to config file.

        Raises:
            ConfigError: If config file exists but is invalid YAML.
        """
        # Start with defaults
        self._config = self._DEFAULTS.copy()

        # Load from courier.config file if it exists
        config_path = config_file or self._find_config_file()
        if config_path:
            try:
                with open(config_path, "r") as f:
                    yaml_config = yaml.safe_load(f) or {}
                    self._config.update(yaml_config)
            except yaml.YAMLError as e:
                raise ConfigError(f"Invalid YAML in {config_path}: {e}")
            except IOError as e:
                raise ConfigError(f"Cannot read config file {config_path}: {e}")

        # Override with environment variables
        for key in self._DEFAULTS:
            env_value = os.getenv(key)
            if env_value is not None:
                # Try to convert to appropriate type (int or str)
                try:
                    # If default is int, try to parse env value as int
                    if isinstance(self._DEFAULTS[key], int):
                        self._config[key] = int(env_value)
                    else:
                        self._config[key] = env_value
                except ValueError:
                    raise ConfigError(
                        f"Invalid value for {key}: {env_value} (expected {type(self._DEFAULTS[key]).__name__})"
                    )

    def _find_config_file(self) -> str | None:
        """Find courier.config file in current or parent directories.

        Returns:
            Path to courier.config if found, None otherwise.
        """
        # Check current directory and up to 3 parent directories
        current = Path.cwd()
        for _ in range(4):
            config_path = current / "courier.config"
            if config_path.exists():
                return str(config_path)
            if current.parent == current:  # reached root
                break
            current = current.parent

        return None

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (e.g., "COURIER_TIMEOUT_SECONDS")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get configuration value as integer.

        Args:
            key: Configuration key
            default: Default integer value

        Returns:
            Configuration value as integer

        Raises:
            ConfigError: If value cannot be converted to integer
        """
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ConfigError(f"Configuration {key} is not a valid integer: {value}")

    def get_float(self, key: str, default: float = 0) -> float:
        """Get configuration value as float.

        Args:
            key: Configuration key
            default: Default float value

        Returns:
            Configuration value as float

        Raises:
            ConfigError: If value cannot be converted to float
        """
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ConfigError(f"Configuration {key} is not a valid float: {value}")

    def get_str(self, key: str, default: str = "") -> str:
        """Get configuration value as string.

        Args:
            key: Configuration key
            default: Default string value

        Returns:
            Configuration value as string
        """
        value = self.get(key, default)
        return str(value)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get configuration value as boolean.

        Args:
            key: Configuration key
            default: Default boolean value

        Returns:
            Configuration value as boolean
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)

    def validate(self) -> None:
        """Validate configuration values.

        Raises:
            ConfigError: If configuration is invalid
        """
        # Validate timeout is positive
        timeout = self.get_int("COURIER_TIMEOUT_SECONDS")
        if timeout <= 0:
            raise ConfigError("COURIER_TIMEOUT_SECONDS must be positive")

        # Validate max results is in valid range
        max_results = self.get_int("COURIER_MAX_RESULTS_DEFAULT")
        if not 1 <= max_results <= 100:
            raise ConfigError("COURIER_MAX_RESULTS_DEFAULT must be 1-100")

        # Validate max file size is positive
        max_file_size = self.get_int("COURIER_MAX_FILE_SIZE_KB")
        if max_file_size <= 0:
            raise ConfigError("COURIER_MAX_FILE_SIZE_KB must be positive")

        # Validate retry attempts
        retry_attempts = self.get_int("COURIER_NETWORK_RETRY_ATTEMPTS")
        if retry_attempts < 0:
            raise ConfigError("COURIER_NETWORK_RETRY_ATTEMPTS must be >= 0")

        # Validate backoff factor
        backoff_factor = self.get_int("COURIER_NETWORK_RETRY_BACKOFF_FACTOR")
        if backoff_factor < 1:
            raise ConfigError("COURIER_NETWORK_RETRY_BACKOFF_FACTOR must be >= 1")

        # Validate log level
        log_level = self.get_str("COURIER_LOG_LEVEL").upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            raise ConfigError(
                f"COURIER_LOG_LEVEL must be one of: {', '.join(valid_levels)}"
            )

    @override
    def __repr__(self) -> str:
        """String representation (excludes sensitive values)."""
        # Don't include credentials path in repr
        safe_config = {k: v for k, v in self._config.items() if "CREDENTIAL" not in k}
        return f"Config({safe_config})"


# Global config instance (lazy-loaded)
_config: Config | None = None


def load_config(config_file: str | None = None) -> Config:
    """Load and return global configuration instance.

    Args:
        config_file: Optional explicit path to config file

    Returns:
        Config instance

    Raises:
        ConfigError: If configuration is invalid
    """
    global _config
    if _config is None:
        _config = Config(config_file)
        _config.validate()
    return _config


def get_config() -> Config:
    """Get global configuration instance.

    Raises:
        RuntimeError: If config not yet loaded
    """
    if _config is None:
        raise RuntimeError("Configuration not yet loaded. Call load_config() first.")
    return _config
