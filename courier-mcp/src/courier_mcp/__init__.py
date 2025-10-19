"""Courier MCP - Gmail message export tool for Claude Code.

A Model Context Protocol server that enables Claude Code users to retrieve
and export Gmail messages as markdown files with YAML frontmatter.

Main exports:
- config: Configuration management
- logger: Logging infrastructure
- errors: Error classes
- server: MCP server and tool handlers (created in TASK-011)
"""

__version__ = "1.0.0"
__author__ = "Anthropic"

# Export main components for easy access
from courier_mcp.config import Config, load_config, get_config  # noqa: F401
from courier_mcp.logger import get_logger  # noqa: F401
from courier_mcp.errors import (  # noqa: F401
    CourierError,
    AuthenticationError,
    GmailAPIError,
    ExportError,
    TimeoutError,
    RateLimitError,
    ConfigError,
    InvalidInputError,
    error_to_json,
)

__all__ = [
    "Config",
    "load_config",
    "get_config",
    "get_logger",
    "CourierError",
    "AuthenticationError",
    "GmailAPIError",
    "ExportError",
    "TimeoutError",
    "RateLimitError",
    "ConfigError",
    "InvalidInputError",
    "error_to_json",
]
