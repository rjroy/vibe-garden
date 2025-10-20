"""Logging infrastructure for Courier MCP.

Provides centralized logging with file-based output and structured error logging.
Logs are written to courier-mcp.log by default (configurable via COURIER_LOG_PATH env var).

Security Note:
- Never logs authentication tokens or credentials
- Never logs personal email content
- Always sanitizes sensitive data before logging
"""

import logging
import logging.handlers
import os
from pathlib import Path

# Global logger instance
_logger: logging.Logger | None = None


def get_logger(name: str = "courier-mcp") -> logging.Logger:
    """Get or create the logger instance.

    Args:
        name: Logger name (default: "courier-mcp")

    Returns:
        Configured logger instance
    """
    global _logger

    if _logger is not None:
        return _logger

    # Get config for log path and level
    log_path = os.getenv("COURIER_LOG_PATH", "./courier-mcp.log")
    log_level = os.getenv("COURIER_LOG_LEVEL", "DEBUG").upper()

    # Create logger
    _logger = logging.getLogger(name)
    _logger.setLevel(getattr(logging, log_level, logging.DEBUG))

    # Create logs directory if needed
    log_file_path = Path(log_path)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create rotating file handler (max 10MB, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(getattr(logging, log_level, logging.DEBUG))

    # Create console handler (ERROR level only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    _logger.info(f"Logger initialized. Log file: {log_path}, Level: {log_level}")

    return _logger


def sanitize_for_logging(value: str, max_length: int = 100) -> str:
    """Sanitize values for logging (truncate, hide sensitive data).

    Args:
        value: Value to sanitize
        max_length: Maximum length for truncation

    Returns:
        Sanitized value safe for logging
    """
    if not value:
        return value

    # Hide common sensitive patterns
    if "token" in value.lower() or "credentials" in value.lower():
        return "***REDACTED***"

    # Truncate long values
    if len(value) > max_length:
        return f"{value[:max_length]}... (truncated)"

    return value


def log_api_call(logger: logging.Logger, method: str, endpoint: str, **kwargs) -> None:
    """Log API call with standard format.

    Args:
        logger: Logger instance
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint name
        **kwargs: Additional context (sanitized automatically)
    """
    sanitized_kwargs = {k: sanitize_for_logging(str(v)) for k, v in kwargs.items()}
    logger.debug(f"API Call: {method} {endpoint} {sanitized_kwargs}")


def log_quota_usage(logger: logging.Logger, units: int, total_seconds: float) -> None:
    """Log quota usage for monitoring.

    Args:
        logger: Logger instance
        units: Quota units consumed
        total_seconds: Time taken in seconds
    """
    units_per_second = units / total_seconds if total_seconds > 0 else 0
    logger.debug(
        f"Quota usage: {units} units in {total_seconds:.2f}s ({units_per_second:.1f} units/sec)"
    )


if __name__ == "__main__":
    # Test logging setup
    logger = get_logger()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    print("✓ Logger initialized successfully")
