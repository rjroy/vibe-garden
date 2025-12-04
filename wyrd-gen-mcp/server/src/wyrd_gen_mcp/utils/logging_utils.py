"""Logging utilities for Wyrd-Gen MCP Server.

This module provides utilities for consistent, context-rich logging:
- Request ID generation and tracking
- Structured log context management
- Helper functions for common logging patterns

The request ID allows correlating all log messages for a single generation
request, making it easy to trace issues in the logs.

Usage:
    from wyrd_gen_mcp.utils.logging_utils import RequestContext, get_logger

    logger = get_logger(__name__)

    async def generate_image(...):
        with RequestContext(model=model, operation="image_generation") as ctx:
            ctx.log_start(prompt=prompt)
            try:
                result = await do_generation()
                ctx.log_success(saved_files=result.saved_files)
                return result
            except Exception as e:
                ctx.log_error(e)
                raise
"""

import logging
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Generator

# Context variable to store current request ID
# This allows nested functions to access the same request ID
_current_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    All loggers are children of the 'wyrd-gen-mcp' logger to ensure
    consistent configuration.

    Args:
        name: The logger name (typically __name__).

    Returns:
        A configured logger instance.
    """
    # Ensure all loggers are under the wyrd-gen-mcp namespace
    if not name.startswith("wyrd-gen-mcp"):
        if name.startswith("wyrd_gen_mcp"):
            # Convert module path to logger path
            name = name.replace("wyrd_gen_mcp", "wyrd-gen-mcp", 1)
        else:
            name = f"wyrd-gen-mcp.{name}"
    return logging.getLogger(name)


def get_current_request_id() -> str | None:
    """Get the current request ID from context.

    Returns:
        The current request ID, or None if not in a request context.
    """
    return _current_request_id.get()


def generate_request_id() -> str:
    """Generate a short, unique request ID.

    Uses UUID4 but truncates to 8 characters for readability in logs.
    This provides sufficient uniqueness for log correlation while
    keeping log lines compact.

    Returns:
        An 8-character hex string (e.g., "a1b2c3d4").
    """
    return uuid.uuid4().hex[:8]


class RequestContext:
    """Context manager for tracking a generation request through logs.

    Provides a consistent way to:
    - Generate and track a request ID
    - Log operation start, success, and failure
    - Include relevant context in all log messages

    The request ID is stored in a context variable, so nested function calls
    can access it via get_current_request_id().

    Example:
        with RequestContext(model="flux-schnell", operation="image_gen") as ctx:
            ctx.log_start(prompt="A cat")
            result = await generate()
            ctx.log_success(file="/path/to/output.png")
    """

    def __init__(
        self,
        operation: str,
        logger: logging.Logger | None = None,
        **context: Any,
    ):
        """Initialize request context.

        Args:
            operation: Name of the operation (e.g., "image_generation", "video_generation").
            logger: Logger to use. If None, uses the default wyrd-gen-mcp logger.
            **context: Additional context to include in all log messages.
        """
        self.operation = operation
        self.logger = logger or logging.getLogger("wyrd-gen-mcp")
        self.context = context
        self.request_id = generate_request_id()
        self._token: Any = None

    def __enter__(self) -> "RequestContext":
        """Enter the context, setting the request ID."""
        self._token = _current_request_id.set(self.request_id)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context, restoring the previous request ID."""
        _current_request_id.reset(self._token)

    def _format_message(self, message: str, **extra: Any) -> str:
        """Format a log message with request ID and context.

        Args:
            message: The base message.
            **extra: Additional key-value pairs to include.

        Returns:
            Formatted message with context.
        """
        parts = [f"[{self.request_id}]", f"[{self.operation}]", message]

        # Combine base context with extra context
        all_context = {**self.context, **extra}
        if all_context:
            context_items = []
            for k, v in all_context.items():
                # Truncate long values
                str_v = str(v)
                if len(str_v) > 100:
                    str_v = str_v[:100] + "..."
                context_items.append(f"{k}={str_v}")
            parts.append(f"({', '.join(context_items)})")

        return " ".join(parts)

    def log_start(self, **extra: Any) -> None:
        """Log the start of an operation.

        Args:
            **extra: Additional context for this specific log message.
        """
        self.logger.info(self._format_message("Starting", **extra))

    def log_progress(self, message: str, **extra: Any) -> None:
        """Log progress during an operation.

        Args:
            message: Progress description.
            **extra: Additional context for this specific log message.
        """
        self.logger.info(self._format_message(message, **extra))

    def log_debug(self, message: str, **extra: Any) -> None:
        """Log debug information.

        Args:
            message: Debug information.
            **extra: Additional context for this specific log message.
        """
        self.logger.debug(self._format_message(message, **extra))

    def log_warning(self, message: str, **extra: Any) -> None:
        """Log a warning.

        Args:
            message: Warning description.
            **extra: Additional context for this specific log message.
        """
        self.logger.warning(self._format_message(message, **extra))

    def log_success(self, **extra: Any) -> None:
        """Log successful completion of an operation.

        Args:
            **extra: Additional context (e.g., output paths, stats).
        """
        self.logger.info(self._format_message("Completed successfully", **extra))

    def log_error(self, error: Exception, **extra: Any) -> None:
        """Log an error with full exception details.

        Uses logger.exception() to include the traceback.

        Args:
            error: The exception that occurred.
            **extra: Additional context for this specific log message.
        """
        extra["error_type"] = type(error).__name__
        extra["error_message"] = str(error)
        self.logger.exception(self._format_message("Failed", **extra))


@contextmanager
def log_operation(
    logger: logging.Logger,
    operation: str,
    **context: Any,
) -> Generator[RequestContext, None, None]:
    """Convenience function for logging an operation with context.

    This is a wrapper around RequestContext that can be used as a
    context manager or decorator.

    Args:
        logger: The logger to use.
        operation: Name of the operation.
        **context: Context to include in log messages.

    Yields:
        A RequestContext instance for logging.

    Example:
        with log_operation(logger, "download", url=url, dest=path) as ctx:
            ctx.log_start()
            bytes_written = await do_download()
            ctx.log_success(bytes=bytes_written)
    """
    with RequestContext(operation, logger=logger, **context) as ctx:
        yield ctx
