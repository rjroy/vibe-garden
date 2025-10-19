"""Tests for logging infrastructure."""

import tempfile
import os
from pathlib import Path

# Ensure src directory is in path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from courier_mcp.logger import get_logger, sanitize_for_logging
from courier_mcp.errors import (
    AuthenticationError,
    GmailAPIError,
    ExportError,
    TimeoutError,
    RateLimitError,
    InvalidInputError,
    error_to_json,
)


def test_logger_creation():
    """Test logger can be created and used."""
    logger = get_logger("test")
    assert logger is not None
    assert logger.name == "test"


def test_logger_singleton():
    """Test logger is singleton (returns same instance)."""
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2


def test_sanitize_for_logging():
    """Test sensitive data is sanitized."""
    assert "***REDACTED***" in sanitize_for_logging("token=abc123")
    assert "***REDACTED***" in sanitize_for_logging("credentials=secret")

    # Normal strings should pass through
    normal = "normal message"
    sanitized = sanitize_for_logging(normal)
    assert normal in sanitized


def test_authentication_error():
    """Test AuthenticationError class."""
    error = AuthenticationError("OAuth token invalid")
    json_resp = error.to_json()

    assert json_resp["error"] == "AUTH_ERROR"
    assert json_resp["message"] == "OAuth token invalid"
    assert "guidance" in json_resp["details"]


def test_gmail_api_error():
    """Test GmailAPIError with status codes."""
    # Rate limit error
    error = GmailAPIError("Rate limited", status_code=429)
    json_resp = error.to_json()
    assert json_resp["error"] == "GMAIL_API_ERROR"
    assert 429 in json_resp["details"]["http_status"]

    # Permission error
    error = GmailAPIError("Permission denied", status_code=403)
    json_resp = error.to_json()
    assert "Permission denied" in json_resp["details"]["guidance"]


def test_timeout_error():
    """Test TimeoutError with partial results."""
    error = TimeoutError("Operation timed out", timeout_seconds=20, messages_processed=45)
    json_resp = error.to_json()

    assert json_resp["error"] == "TIMEOUT"
    assert json_resp["details"]["timeout_seconds"] == 20
    assert json_resp["details"]["messages_processed"] == 45


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError("Quota exhausted", retry_after_seconds=60)
    json_resp = error.to_json()

    assert json_resp["error"] == "RATE_LIMITED"
    assert json_resp["details"]["retry_after_seconds"] == 60


def test_invalid_input_error():
    """Test InvalidInputError."""
    error = InvalidInputError("max_results out of range", parameter="max_results")
    json_resp = error.to_json()

    assert json_resp["error"] == "INVALID_INPUT"
    assert json_resp["details"]["parameter"] == "max_results"


def test_error_to_json_courier_error():
    """Test error_to_json with CourierError."""
    error = ExportError("Cannot write to directory")
    json_resp = error_to_json(error)

    assert json_resp["error"] == "EXPORT_ERROR"
    assert "Cannot write" in json_resp["message"]


def test_error_to_json_generic_error():
    """Test error_to_json with generic exception."""
    error = ValueError("Some error")
    json_resp = error_to_json(error)

    assert json_resp["error"] == "INTERNAL_ERROR"
    assert error.__class__.__name__ in json_resp["details"]["type"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
