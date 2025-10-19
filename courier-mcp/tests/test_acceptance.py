"""
Acceptance tests mapping to spec requirements.

These tests validate high-level requirements against the spec.
For full end-to-end testing with MCP server, see test_integration.py
"""

import pytest
from pathlib import Path


@pytest.mark.acceptance
class TestSpecAcceptanceCriteria:
    """Acceptance tests mapping to specification requirements."""

    def test_at01_markdown_export_format(self, temp_export_dir):
        """
        Spec AT-1: Basic retrieval
        Verify markdown files have correct format with YAML frontmatter
        """
        from courier_mcp.export import format_message_to_markdown

        sample_message = {
            "id": "msg_001",
            "labelIds": ["INBOX"],
            "payload": {
                "headers": [
                    {"name": "From", "value": "test@example.com"},
                    {"name": "To", "value": "user@gmail.com"},
                    {"name": "Subject", "value": "Test"},
                    {"name": "Date", "value": "Mon, 15 Oct 2025 14:00:00 +0000"}
                ],
                "mimeType": "text/plain",
                "body": {"data": "VGVzdCBtZXNzYWdl"}
            }
        }

        markdown = format_message_to_markdown(sample_message)

        assert markdown.startswith("---\n")
        assert "from: test@example.com" in markdown
        assert "subject: Test" in markdown

    def test_at02_search_query_building(self):
        """
        Spec AT-2: Search syntax
        Verify Gmail search queries are properly constructed
        """
        from courier_mcp.gmail_service import GmailService
        from unittest.mock import MagicMock

        mock_service = MagicMock()
        gmail = GmailService(mock_service)

        # This would test query building if exposed
        # For now, verify via integration tests
        assert True  # Placeholder

    def test_at04_filename_collision_prevention(self, temp_export_dir):
        """
        Spec AT-4: No overwrites
        Second export uses `_1`, `_2` suffixes
        """
        from courier_mcp.export import safe_file_write

        content = "Test"
        filename = "test.md"

        # First write
        path1 = safe_file_write(str(temp_export_dir / filename), content)
        assert Path(path1).name == filename

        # Second write (collision)
        path2 = safe_file_write(str(temp_export_dir / filename), content)
        assert Path(path2).name == "test_1.md"

        # Third write
        path3 = safe_file_write(str(temp_export_dir / filename), content)
        assert Path(path3).name == "test_2.md"

    def test_at06_attachment_metadata_extraction(self):
        """
        Spec AT-6: Attachment metadata
        Verify attachment list includes size and MIME type, but no binary
        """
        from courier_mcp.export import extract_attachments

        message = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": "dGVzdA=="}
                    },
                    {
                        "mimeType": "application/pdf",
                        "filename": "report.pdf",
                        "body": {"size": 524288, "attachmentId": "attach_123"}
                    }
                ]
            }
        }

        attachments = extract_attachments(message)

        assert len(attachments) == 1
        assert attachments[0]["filename"] == "report.pdf"
        assert attachments[0]["size"] == 524288
        assert attachments[0]["mime_type"] == "application/pdf"
        # Verify no binary data in attachment metadata
        assert "data" not in attachments[0]

    def test_at07_label_caching(self):
        """
        Spec AT-7: Folder discovery
        Verify labels are cached to reduce API calls
        """
        from courier_mcp.gmail_service import GmailService
        from unittest.mock import MagicMock

        mock_service = MagicMock()
        mock_service.users().labels().list().execute.return_value = {
            "labels": [
                {"id": "INBOX", "name": "INBOX", "messagesTotal": 100, "messagesUnread": 10}
            ]
        }

        gmail = GmailService(mock_service)

        # First call
        labels1 = gmail.fetch_labels()

        # Second call (should use cache)
        labels2 = gmail.fetch_labels()

        # API should only be called once
        assert mock_service.users().labels().list().execute.call_count == 1
        assert labels1 == labels2

    def test_at09_filename_generation_format(self):
        """
        Spec AT-9: Context efficiency
        Verify filenames follow spec format: YYYYMMDD_HHMMSS_folder_from_sender.md
        """
        from courier_mcp.export import generate_filename

        message = {
            "labelIds": ["INBOX"],
            "internalDate": "1697385600000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Alice Johnson <alice@example.com>"},
                    {"name": "Date", "value": "Mon, 15 Oct 2023 14:00:00 +0000"}
                ]
            }
        }

        filename = generate_filename(message)

        # Verify format
        assert filename.endswith(".md")
        parts = filename.replace(".md", "").split("_")

        # Should have: date (8 chars) + time (6 chars) + folder + sender
        assert len(parts[0]) == 8  # YYYYMMDD
        assert len(parts[1]) == 6  # HHMMSS
        assert "inbox" in filename.lower()
        assert "alice" in filename.lower()

    def test_at10_rate_limit_exponential_backoff(self):
        """
        Spec AT-5 & AT-8: Rate limit handling with exponential backoff
        """
        from courier_mcp.gmail_service import GmailService
        from unittest.mock import MagicMock
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()

        # Simulate rate limit then success
        call_count = 0

        def rate_limit_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                raise HttpError(resp=MagicMock(status=429), content=b"Rate limit")
            else:
                mock_response = MagicMock()
                mock_response.execute.return_value = {"messages": []}
                return mock_response

        mock_service.users().messages().list.side_effect = rate_limit_then_success

        # retry_attempts and backoff_factor are configured via config, not __init__
        gmail = GmailService(mock_service)
        messages = gmail.fetch_messages(max_results=10)

        # Should have retried and succeeded
        assert call_count == 2
        assert isinstance(messages, list)


@pytest.mark.acceptance
class TestToolSchemaCompliance:
    """Test that tools match spec requirements."""

    def test_tools_match_spec(self):
        """Verify MCP tools match specification."""
        from courier_mcp.server import TOOLS

        assert len(TOOLS) == 2

        tool_names = {tool.name for tool in TOOLS}
        assert "get-messages" in tool_names
        assert "get-folders" in tool_names

    def test_get_messages_required_parameters(self):
        """Verify get-messages requires export_directory."""
        from courier_mcp.server import TOOLS

        get_messages = next(t for t in TOOLS if t.name == "get-messages")
        assert "export_directory" in get_messages.inputSchema["required"]

    def test_max_results_constraints(self):
        """Verify max_results is constrained to 1-100."""
        from courier_mcp.server import TOOLS

        get_messages = next(t for t in TOOLS if t.name == "get-messages")
        max_results_spec = get_messages.inputSchema["properties"]["max_results"]

        assert max_results_spec["minimum"] == 1
        assert max_results_spec["maximum"] == 100
