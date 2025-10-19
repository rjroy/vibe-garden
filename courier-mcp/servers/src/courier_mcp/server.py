"""MCP Server for Courier - Gmail export tool.

Implements two tools:
1. get-messages: Query Gmail and export to markdown files
2. get-folders: List available Gmail labels/folders

Runs as stdio-based MCP server for integration with Claude Code.
"""

import asyncio
import json
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .auth import get_authenticator, initialize_authenticator
from .config import get_config
from .errors import (
    CourierError,
    InvalidInputError,
    error_to_json,
)
from .export import (
    format_message_to_markdown,
    generate_filename,
    safe_file_write,
    truncate_markdown,
)
from .gmail_service import GmailService
from .logger import get_logger

logger = get_logger(__name__)

# Tool definitions
TOOLS = [
    Tool(
        name="get-folders",
        description="List all available Gmail labels/folders with message counts",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="get-messages",
        description="Query Gmail inbox, filter by criteria, and export matching messages to directory",
        inputSchema={
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Gmail search query syntax (e.g., 'is:unread from:boss@example.com')",
                },
                "folder": {
                    "type": "string",
                    "description": "Friendly folder/label name (e.g., 'INBOX', 'Project Docs'). Get list from get-folders tool.",
                },
                "export_directory": {
                    "type": "string",
                    "description": "Directory path where markdown files will be saved (absolute or relative)",
                },
                "date_start": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format (optional)",
                },
                "date_end": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format (optional)",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum messages to retrieve (1-100, default from config)",
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["export_directory"],
        },
    ),
]


class CourierServer:
    """MCP Server for Courier Gmail export tool."""

    def __init__(self):
        """Initialize server."""
        self.gmail_service: GmailService | None = None

        # Initialize authenticator (will raise if credentials not configured)
        try:
            _ = initialize_authenticator()
            logger.info("Authenticator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize authenticator: {e}")
            raise

        logger.info("CourierServer initialized")

    async def _handle_get_folders(self) -> list[TextContent]:
        """Handle get-folders tool call.

        Lists all Gmail labels/folders with message counts.

        Returns:
            List with single TextContent containing JSON results
        """
        try:
            logger.info("get-folders called")

            # Ensure Gmail service is ready
            if not self.gmail_service:
                await self._initialize_gmail_service()

            if not self.gmail_service:
                raise CourierError("Gmail service not initialized")

            # Fetch labels
            labels = self.gmail_service.fetch_labels()

            # Format response
            folders: list[dict[str, str | int]] = []
            for label_id, label in labels.items():
                folders.append(
                    {
                        "id": label_id,
                        "name": label.name,
                        "message_count": label.message_count,
                        "unread_count": label.unread_count,
                    }
                )

            result = {"folders": folders}
            logger.info(f"get-folders: Returning {len(folders)} folders")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except CourierError as e:
            logger.error(f"get-folders error: {e}")
            return [TextContent(type="text", text=json.dumps(error_to_json(e), indent=2))]
        except Exception as e:
            logger.error(f"get-folders unexpected error: {e}")
            return [TextContent(type="text", text=json.dumps(error_to_json(e), indent=2))]

    async def _handle_get_messages(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle get-messages tool call.

        Queries Gmail, retrieves messages, and exports to markdown files.

        Args:
            arguments: Tool input with search criteria and export path

        Returns:
            List with single TextContent containing JSON results
        """

        timeout_seconds: float | None = None
        try:
            config = get_config()
            timeout_seconds = config.get_float("COURIER_TIMEOUT_SECONDS", 20)

            logger.info(f"get-messages called with args: {arguments}")

            # Validate inputs
            export_directory: str | None = arguments.get("export_directory")
            if not export_directory:
                raise InvalidInputError(
                    "export_directory is required", parameter="export_directory"
                )

            search_query: str = arguments.get("search_query", "")
            folder: str = arguments.get("folder", "INBOX")
            date_start: str | None = arguments.get("date_start")
            date_end: str | None = arguments.get("date_end")
            max_results: int | None = arguments.get("max_results")

            if max_results is None:
                max_results = config.get_int("COURIER_MAX_RESULTS_DEFAULT", 10)

            max_results = max(1, min(int(max_results), 100))

            # Ensure Gmail service is ready
            if not self.gmail_service:
                await self._initialize_gmail_service()

            # Run with timeout
            result = await asyncio.wait_for(
                self._export_messages(
                    search_query,
                    folder,
                    export_directory,
                    date_start,
                    date_end,
                    max_results,
                ),
                timeout=timeout_seconds,
            )

            logger.info(
                f"get-messages: Successfully exported {len(result.get('files_saved', []))} messages"
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except asyncio.TimeoutError:
            logger.error(f"get-messages timeout after {timeout_seconds}s")
            error_result = {
                "error": "TIMEOUT",
                "message": f"Operation exceeded {timeout_seconds}s timeout",
                "details": {"timeout_seconds": timeout_seconds},
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

        except CourierError as e:
            logger.error(f"get-messages error: {e}")
            return [TextContent(type="text", text=json.dumps(error_to_json(e), indent=2))]
        except Exception as e:
            logger.error(f"get-messages unexpected error: {e}")
            return [TextContent(type="text", text=json.dumps(error_to_json(e), indent=2))]

    async def _initialize_gmail_service(self):
        """Initialize Gmail service with authentication.

        Raises:
            CourierError: If authentication fails
        """
        try:
            authenticator = get_authenticator()
            authenticator.ensure_valid_token()
            service = authenticator.build_gmail_service()
            self.gmail_service = GmailService(service)
            logger.info("Gmail service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            raise

    async def _export_messages(
        self,
        search_query: str,
        folder: str,
        export_directory: str,
        date_start: str | None,
        date_end: str | None,
        max_results: int,
    ) -> dict[str, Any]:
        """Export messages to markdown files.

        Orchestrates the full workflow:
        1. Translate folder name to ID
        2. Search for messages
        3. Fetch message details
        4. Format to markdown
        5. Write files

        Args:
            search_query: Gmail search query
            folder: Folder/label name
            export_directory: Directory to export to
            date_start: Start date (optional)
            date_end: End date (optional)
            max_results: Maximum messages to retrieve

        Returns:
            dict with files_saved, summary, and errors
        """
        files_saved = []
        errors = []

        try:
            # Step 1: Get label ID
            label_id = None
            if folder and folder.upper() != "INBOX":
                label_id = self.gmail_service.get_label_id(folder)
            elif folder.upper() == "INBOX":
                label_id = "INBOX"

            logger.debug(f"Folder '{folder}' mapped to label_id '{label_id}'")

            # Step 2: Fetch message list
            message_list = await self.gmail_service.fetch_messages(
                search_query=search_query,
                label_id=label_id,
                max_results=max_results,
            )

            logger.info(f"Found {len(message_list)} messages matching query")

            if not message_list:
                return {
                    "files_saved": [],
                    "summary": "Query returned no messages",
                    "errors": [],
                }

            # Step 3: Fetch message details (with timeout budget)
            config = get_config()
            timeout_seconds = config.get_float("COURIER_TIMEOUT_SECONDS", 20)
            # Allocate 80% of timeout for fetching, 20% for export
            fetch_timeout = timeout_seconds * 0.8

            message_ids = [m.id for m in message_list]
            (
                detailed_messages,
                fetch_errors,
            ) = await self.gmail_service.fetch_message_details(
                message_ids,
                timeout_seconds=fetch_timeout,
            )

            errors.extend(fetch_errors)
            logger.info(f"Fetched {len(detailed_messages)} message details")

            # Step 4: Format and write files
            for message in detailed_messages:
                try:
                    # Format to markdown
                    markdown = format_message_to_markdown(message)

                    # Apply file size limit
                    max_file_size_kb = config.get_int("COURIER_MAX_FILE_SIZE_KB", 10)
                    markdown = truncate_markdown(markdown, max_size_kb=max_file_size_kb)

                    # Generate filename
                    filename = generate_filename(message, folder=folder)

                    # Write file
                    filepath = f"{export_directory}/{filename}"
                    saved_path = safe_file_write(filepath, markdown)

                    files_saved.append(saved_path)
                    logger.debug(f"Exported message {message['id']} to {saved_path}")

                except Exception as e:
                    logger.warning(f"Failed to export message {message['id']}: {e}")
                    errors.append(
                        {
                            "message_id": message["id"],
                            "error": str(e)[:100],
                        }
                    )

            # Build response
            summary = f"Retrieved and exported {len(files_saved)} messages in {len(detailed_messages)} fetches"
            if errors:
                summary += f" ({len(errors)} errors)"

            return {
                "files_saved": files_saved,
                "summary": summary,
                "errors": errors if errors else [],
            }

        except CourierError:
            raise
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise


async def main():
    """Entry point for MCP server."""
    # Initialize CourierServer instance (validates auth)
    courier_server = CourierServer()

    # Create MCP Server instance
    server = Server("courier-mcp")

    # Register list_tools handler
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return TOOLS

    # Register call_tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        logger.info(f"Tool called: {name}")
        logger.debug(f"Tool arguments: {arguments}")
        try:
            if name == "get-folders":
                return await courier_server._handle_get_folders(arguments)
            elif name == "get-messages":
                return await courier_server._handle_get_messages(arguments)
            else:
                logger.error(f"Unknown tool: {name}")
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.exception(f"Error in tool {name}: {e}")
            error_result = {
                "success": False,
                "error": str(e),
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    # Run the server
    logger.info("Starting Courier MCP Server")
    print("Courier MCP Server running on stdio", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        logger.info("stdio_server started, beginning server.run")
        await server.run(read_stream, write_stream, server.create_initialization_options())
        logger.info("Server run completed")


if __name__ == "__main__":
    try:
        logger.info("Main entry point - starting asyncio.run(main())")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
