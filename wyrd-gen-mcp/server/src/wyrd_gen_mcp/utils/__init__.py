"""Utility functions for Wyrd-Gen MCP Server.

This module provides common utilities used across generators:

File utilities (from file_utils):
    - download_file: Async download from URL to local file
    - get_next_available_path: Find non-colliding filename with index suffix
    - resolve_output_path: Convert relative paths to absolute using invoke directory

Image utilities (from image_utils):
    - image_to_data_uri: Convert local image to base64 data URI for API submission

Logging utilities (from logging_utils):
    - get_logger: Get a configured logger instance
    - RequestContext: Context manager for request-scoped logging with correlation IDs
    - log_operation: Convenience function for logging operations

Example usage:
    from wyrd_gen_mcp.utils import resolve_output_path, image_to_data_uri

    # Resolve relative path
    abs_path = resolve_output_path("output.png", "/home/user/project")
    # Result: "/home/user/project/output.png"

    # Convert image for API submission
    data_uri = image_to_data_uri("/path/to/image.png")
    # Result: "data:image/png;base64,iVBORw0KGgo..."

    # Use request context for correlated logging
    from wyrd_gen_mcp.utils import RequestContext, get_logger

    logger = get_logger(__name__)
    with RequestContext(operation="image_gen", model="flux") as ctx:
        ctx.log_start(prompt="A cat")
        # All logs will include the same request ID
        ctx.log_success(file="output.png")
"""

from wyrd_gen_mcp.utils.file_utils import (
    download_file,
    get_next_available_path,
    resolve_output_path,
)
from wyrd_gen_mcp.utils.image_utils import image_to_data_uri
from wyrd_gen_mcp.utils.logging_utils import (
    RequestContext,
    get_current_request_id,
    get_logger,
    log_operation,
)

__all__ = [
    "RequestContext",
    "download_file",
    "get_current_request_id",
    "get_logger",
    "get_next_available_path",
    "image_to_data_uri",
    "log_operation",
    "resolve_output_path",
]
