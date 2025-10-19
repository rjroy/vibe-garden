"""
Integration tests with real Gmail API (optional).

These tests require valid Gmail credentials and are skipped by default.
Run with: pytest -m integration

Setup:
1. Create credentials.json (see docs/SETUP.md)
2. Set GMAIL_CREDENTIALS_PATH environment variable
3. Run: pytest -m integration

NOTE: These tests are placeholders for manual E2E testing.
Full integration testing is covered in TASK-017.
"""

import pytest
import os

# Skip all integration tests if credentials not available
pytestmark = pytest.mark.skipif(
    not os.environ.get("GMAIL_CREDENTIALS_PATH"),
    reason="Gmail credentials not available (set GMAIL_CREDENTIALS_PATH to run integration tests)"
)


@pytest.mark.integration
class TestGmailAPIIntegration:
    """Integration tests with real Gmail API."""

    def test_authentication_flow(self):
        """Test OAuth authentication with real credentials."""
        from courier_mcp.auth import get_authenticator

        auth = get_authenticator()
        service = auth.build_gmail_service()

        assert service is not None

    def test_label_fetching_real_api(self):
        """Test fetching real labels from Gmail."""
        from courier_mcp.auth import get_authenticator
        from courier_mcp.gmail_service import GmailService

        auth = get_authenticator()
        service = auth.build_gmail_service()
        gmail = GmailService(service)

        labels = gmail.fetch_labels()

        assert len(labels) > 0
        # Should have at least system labels
        label_names = [label["name"] for label in labels]
        assert "INBOX" in label_names

    def test_message_list_real_api(self):
        """Test fetching message list from real Gmail."""
        from courier_mcp.auth import get_authenticator
        from courier_mcp.gmail_service import GmailService

        auth = get_authenticator()
        service = auth.build_gmail_service()
        gmail = GmailService(service)

        # Fetch last 5 messages
        messages = gmail.fetch_messages(max_results=5)

        # Should get some messages (assuming inbox is not empty)
        assert isinstance(messages, list)
