"""Custom exceptions for Wyrd-Gen MCP Server.

This module defines exception classes that provide rich context for debugging
generation failures. Each exception includes:
- A human-readable message
- The operation that was being attempted
- Relevant parameters (model, prompt, paths, etc.)
- The original cause (if wrapping another exception)

Usage:
    try:
        result = await replicate_client.async_run(model, input=params)
    except Exception as e:
        raise GenerationError(
            message="Replicate API call failed",
            operation="image_generation",
            model=model,
            prompt=prompt,
            cause=e
        )
"""

from typing import Any


class WyrdGenError(Exception):
    """Base exception for all Wyrd-Gen errors.

    All custom exceptions inherit from this class, allowing callers to catch
    all Wyrd-Gen errors with a single except clause if desired.

    Attributes:
        message: Human-readable error description.
        context: Dictionary of contextual information for debugging.
        cause: The original exception that caused this error, if any.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Exception | None = None,
        **context: Any,
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            cause: The original exception that caused this error.
            **context: Additional context as keyword arguments.
        """
        self.message = message
        self.context = context
        self.cause = cause

        # Build detailed message for logging
        parts = [message]
        if context:
            context_str = ", ".join(f"{k}={v!r}" for k, v in context.items())
            parts.append(f"Context: {context_str}")
        if cause:
            parts.append(f"Caused by: {type(cause).__name__}: {cause}")

        super().__init__("\n".join(parts))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "error": self.message,
            "error_type": type(self).__name__,
        }
        if self.context:
            result["context"] = self.context
        if self.cause:
            result["cause"] = {
                "type": type(self.cause).__name__,
                "message": str(self.cause),
            }
        return result


class ValidationError(WyrdGenError):
    """Raised when input validation fails.

    Examples:
        - Missing required parameter (model, prompt, output_file_name)
        - Invalid file format
        - Model not found in catalog
    """

    def __init__(
        self,
        message: str,
        *,
        parameter: str | None = None,
        value: Any = None,
        **context: Any,
    ):
        """Initialize validation error.

        Args:
            message: Description of the validation failure.
            parameter: Name of the parameter that failed validation.
            value: The invalid value (will be truncated if too long).
            **context: Additional context.
        """
        if parameter:
            context["parameter"] = parameter
        if value is not None:
            # Truncate long values for readability
            str_value = str(value)
            if len(str_value) > 100:
                str_value = str_value[:100] + "..."
            context["value"] = str_value
        super().__init__(message, **context)


class GenerationError(WyrdGenError):
    """Raised when content generation fails.

    This covers failures during the actual generation process, including:
    - Replicate API errors
    - Local model loading failures
    - GPU/CUDA errors
    - Timeout during video generation
    """

    def __init__(
        self,
        message: str,
        *,
        operation: str | None = None,
        model: str | None = None,
        prompt: str | None = None,
        prediction_id: str | None = None,
        cause: Exception | None = None,
        **context: Any,
    ):
        """Initialize generation error.

        Args:
            message: Description of the generation failure.
            operation: The operation that failed (e.g., "image_generation", "video_polling").
            model: The model being used.
            prompt: The prompt (will be truncated if too long).
            prediction_id: Replicate prediction ID if available.
            cause: The original exception.
            **context: Additional context.
        """
        if operation:
            context["operation"] = operation
        if model:
            context["model"] = model
        if prompt:
            # Truncate long prompts for readability
            if len(prompt) > 200:
                prompt = prompt[:200] + "..."
            context["prompt"] = prompt
        if prediction_id:
            context["prediction_id"] = prediction_id
        super().__init__(message, cause=cause, **context)


class FileError(WyrdGenError):
    """Raised when file operations fail.

    This covers:
    - Input file not found
    - Output directory doesn't exist
    - Permission errors
    - Download failures
    """

    def __init__(
        self,
        message: str,
        *,
        path: str | None = None,
        operation: str | None = None,
        cause: Exception | None = None,
        **context: Any,
    ):
        """Initialize file error.

        Args:
            message: Description of the file operation failure.
            path: The file path involved.
            operation: The operation that failed (e.g., "read", "write", "download").
            cause: The original exception.
            **context: Additional context.
        """
        if path:
            context["path"] = path
        if operation:
            context["operation"] = operation
        super().__init__(message, cause=cause, **context)


class TimeoutError(GenerationError):
    """Raised when generation times out.

    Video generation can take several minutes. This exception is raised
    when the operation exceeds the configured timeout.
    """

    def __init__(
        self,
        message: str,
        *,
        timeout_seconds: int | None = None,
        elapsed_seconds: float | None = None,
        **context: Any,
    ):
        """Initialize timeout error.

        Args:
            message: Description of the timeout.
            timeout_seconds: The configured timeout limit.
            elapsed_seconds: How long the operation ran before timeout.
            **context: Additional context.
        """
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        if elapsed_seconds:
            context["elapsed_seconds"] = round(elapsed_seconds, 1)
        super().__init__(message, operation="timeout", **context)
