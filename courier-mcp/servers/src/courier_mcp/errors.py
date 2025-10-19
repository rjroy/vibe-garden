"""Error classes and exception hierarchy for Courier MCP.

All exceptions inherit from CourierError and include proper logging
before JSON response is sent to MCP client.
"""

from typing import Any


class CourierError(Exception):
    """Base exception class for all Courier MCP errors.

    Attributes:
        code: Error code (e.g., "AUTH_ERROR", "RATE_LIMITED")
        message: Human-readable error message
        details: Optional additional error context
    """

    error_code = "UNKNOWN_ERROR"
    http_status = 500

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize error.

        Args:
            message: Error message
            details: Optional additional context
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_json(self) -> dict[str, Any]:
        """Convert error to JSON response format.

        Returns:
            Dictionary suitable for JSON response
        """
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details if self.details else None,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message})"


class AuthenticationError(CourierError):
    """OAuth authentication or credential-related error."""

    error_code = "AUTH_ERROR"
    http_status = 401

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        if details is None:
            details = {}
        details.setdefault(
            "guidance",
            "Check that GMAIL_CREDENTIALS_PATH is set correctly and credentials.json exists",
        )
        super().__init__(message, details)


class GmailAPIError(CourierError):
    """Gmail API call failed.

    May include rate limiting (429), permission errors (403), or other API failures.
    """

    error_code = "GMAIL_API_ERROR"
    http_status = 502

    def __init__(
        self, message: str, status_code: int | None = None, details: dict[str, Any] | None = None
    ):
        if details is None:
            details = {}

        # Map common status codes to guidance
        guidance_map = {
            401: "Token expired or invalid. Try authenticating again.",
            403: "Permission denied. Check that you granted 'gmail.readonly' scope.",
            429: "Rate limited by Gmail API. Try again in a few moments.",
            404: "Message not found (possibly deleted by another client).",
            400: "Invalid Gmail search query syntax.",
            503: "Gmail API temporarily unavailable. Retrying...",
        }

        if status_code:
            details["http_status"] = status_code
            if status_code in guidance_map:
                details.setdefault("guidance", guidance_map[status_code])

        super().__init__(message, details)


class ExportError(CourierError):
    """File export or markdown formatting error."""

    error_code = "EXPORT_ERROR"
    http_status = 500

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        if details is None:
            details = {}
        details.setdefault("guidance", "Check export directory path and write permissions")
        super().__init__(message, details)


class TimeoutError(CourierError):
    """Operation exceeded timeout deadline.

    Includes information about partial results if available.
    """

    error_code = "TIMEOUT"
    http_status = 504

    def __init__(
        self,
        message: str,
        timeout_seconds: int,
        messages_processed: int = 0,
        details: dict[str, Any] | None = None,
    ):
        if details is None:
            details = {}
        details["timeout_seconds"] = timeout_seconds
        details["messages_processed"] = messages_processed
        details.setdefault(
            "guidance",
            f"Operation exceeded {timeout_seconds}s timeout. Partial results saved if available.",
        )
        super().__init__(message, details)


class RateLimitError(GmailAPIError):
    """Gmail API rate limit exceeded (429 response).

    This is handled transparently with exponential backoff in normal operation.
    This exception is only raised if backoff exhausted or max retries exceeded.
    """

    error_code = "RATE_LIMITED"

    def __init__(self, message: str, retry_after_seconds: int | None = None):
        details = {}
        if retry_after_seconds:
            details["retry_after_seconds"] = retry_after_seconds
        details.setdefault("guidance", "Gmail API quota exhausted. Please wait before retrying.")

        super().__init__(message, status_code=429, details=details)


class ConfigError(CourierError):
    """Configuration loading or validation error."""

    error_code = "CONFIG_ERROR"
    http_status = 500

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        if details is None:
            details = {}
        details.setdefault("guidance", "Check courier.config and environment variables (COURIER_*)")
        super().__init__(message, details)


class InvalidInputError(CourierError):
    """Invalid input parameters to MCP tool.

    Validation failed for required or constrained parameters.
    """

    error_code = "INVALID_INPUT"
    http_status = 400

    def __init__(
        self, message: str, parameter: str | None = None, details: dict[str, Any] | None = None
    ):
        if details is None:
            details = {}
        if parameter:
            details["parameter"] = parameter
        details.setdefault("guidance", "Check input parameters against tool specification")
        super().__init__(message, details)


def error_to_json(error: Exception) -> dict[str, Any]:
    """Convert any exception to JSON response format.

    Args:
        error: Exception to convert

    Returns:
        Dictionary suitable for MCP JSON error response
    """
    if isinstance(error, CourierError):
        return error.to_json()

    # For non-Courier exceptions, wrap them
    return {
        "error": "INTERNAL_ERROR",
        "message": str(error),
        "details": {
            "type": error.__class__.__name__,
            "guidance": "An unexpected error occurred. Check logs for details.",
        },
    }


if __name__ == "__main__":
    # Test error classes
    errors = [
        AuthenticationError("Invalid OAuth token"),
        GmailAPIError("Rate limited", status_code=429),
        ExportError("Cannot write to directory /invalid/path"),
        TimeoutError("Operation exceeded timeout", timeout_seconds=20, messages_processed=45),
        RateLimitError("Quota exhausted", retry_after_seconds=60),
        InvalidInputError("Invalid max_results", parameter="max_results"),
    ]

    for error in errors:
        print(f"✓ {error.__class__.__name__}: {error.to_json()}")
