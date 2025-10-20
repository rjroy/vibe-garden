"""
Unit tests for MCP server module (server.py).

Tests tool registration and server initialization.
"""

import pytest
from unittest.mock import MagicMock, patch

from courier_mcp.server import CourierServer, TOOLS


@pytest.mark.unit
class TestServerInitialization:
    """Test suite for server initialization and configuration."""

    @patch("courier_mcp.server.initialize_authenticator")
    def test_server_initialization_success(self, mock_init_auth):
        """Test successful server initialization."""
        mock_init_auth.return_value = MagicMock()

        server = CourierServer()

        assert server is not None
        mock_init_auth.assert_called_once()

    @patch("courier_mcp.server.initialize_authenticator")
    def test_server_initialization_fails_without_credentials(self, mock_init_auth):
        """Test that server fails to initialize without credentials."""
        mock_init_auth.side_effect = Exception("Credentials not found")

        with pytest.raises(Exception, match="Credentials not found"):
            CourierServer()

    def test_tools_are_defined(self):
        """Test that MCP tools are properly defined."""
        assert len(TOOLS) == 2

        tool_names = [tool.name for tool in TOOLS]
        assert "get-folders" in tool_names
        assert "get-messages" in tool_names

    def test_get_folders_tool_schema(self):
        """Test get-folders tool has correct schema."""
        get_folders_tool = next(t for t in TOOLS if t.name == "get-folders")

        assert get_folders_tool.description is not None
        assert get_folders_tool.inputSchema["type"] == "object"
        assert get_folders_tool.inputSchema["required"] == []

    def test_get_messages_tool_schema(self):
        """Test get-messages tool has correct schema."""
        get_messages_tool = next(t for t in TOOLS if t.name == "get-messages")

        assert get_messages_tool.description is not None
        assert get_messages_tool.inputSchema["type"] == "object"
        assert "export_directory" in get_messages_tool.inputSchema["required"]

        # Verify parameters
        props = get_messages_tool.inputSchema["properties"]
        assert "search_query" in props
        assert "folder" in props
        assert "export_directory" in props
        assert "date_start" in props
        assert "date_end" in props
        assert "max_results" in props

        # Verify max_results constraints
        assert props["max_results"]["minimum"] == 1
        assert props["max_results"]["maximum"] == 100
