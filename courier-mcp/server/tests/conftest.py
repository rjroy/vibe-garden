"""
Pytest configuration and shared fixtures for Courier MCP tests.
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import datetime

# Sample Gmail API responses (based on real Gmail API structure)

@pytest.fixture
def sample_label_list():
    """Sample labels.list() response from Gmail API."""
    return {
        "labels": [
            {
                "id": "INBOX",
                "name": "INBOX",
                "messageListVisibility": "show",
                "labelListVisibility": "labelShow",
                "type": "system",
                "messagesTotal": 1245,
                "messagesUnread": 42
            },
            {
                "id": "SENT",
                "name": "SENT",
                "messageListVisibility": "show",
                "labelListVisibility": "labelShow",
                "type": "system",
                "messagesTotal": 523,
                "messagesUnread": 0
            },
            {
                "id": "Label_789",
                "name": "Project Docs",
                "messageListVisibility": "show",
                "labelListVisibility": "labelShow",
                "type": "user",
                "messagesTotal": 89,
                "messagesUnread": 12
            }
        ]
    }


@pytest.fixture
def sample_messages_list():
    """Sample messages.list() response from Gmail API."""
    return {
        "messages": [
            {"id": "msg_001", "threadId": "thread_001"},
            {"id": "msg_002", "threadId": "thread_002"},
            {"id": "msg_003", "threadId": "thread_003"}
        ],
        "resultSizeEstimate": 3
    }


@pytest.fixture
def sample_message_full():
    """Sample messages.get() response with full message details."""
    return {
        "id": "msg_001",
        "threadId": "thread_001",
        "labelIds": ["INBOX", "Label_789"],
        "snippet": "This is a test email...",
        "internalDate": "1697385600000",  # Unix timestamp in ms
        "payload": {
            "headers": [
                {"name": "From", "value": "Alice Johnson <alice@example.com>"},
                {"name": "To", "value": "user@gmail.com"},
                {"name": "Cc", "value": "bob@example.com"},
                {"name": "Subject", "value": "Q4 Planning: [VOICE] Meeting Notes"},
                {"name": "Date", "value": "Mon, 15 Oct 2025 14:32:00 -0700"},
                {"name": "Message-ID", "value": "<CABcDEF1234567890@mail.gmail.com>"}
            ],
            "mimeType": "multipart/mixed",
            "body": {"size": 0},
            "parts": [
                {
                    "partId": "0",
                    "mimeType": "text/plain",
                    "body": {
                        "size": 245,
                        "data": "SGVyZSdzIHRoZSBlbWFpbCBib2R5IGluIHBsYWluIHRleHQu"  # base64url
                    }
                },
                {
                    "partId": "1",
                    "mimeType": "text/html",
                    "body": {
                        "size": 512,
                        "data": "PGh0bWw+PGJvZHk+SGVyZSdzIHRoZSBlbWFpbCBib2R5IGluIEhUTUwuPC9ib2R5PjwvaHRtbD4="
                    }
                },
                {
                    "partId": "2",
                    "mimeType": "application/pdf",
                    "filename": "meeting-notes.pdf",
                    "body": {
                        "size": 245678,
                        "attachmentId": "attach_123"
                    }
                }
            ]
        }
    }


@pytest.fixture
def sample_message_plain_text():
    """Sample message with plain text only (no HTML)."""
    return {
        "id": "msg_002",
        "threadId": "thread_002",
        "labelIds": ["INBOX"],
        "snippet": "Plain text email...",
        "internalDate": "1697385600000",
        "payload": {
            "headers": [
                {"name": "From", "value": "Bob Smith <bob@example.com>"},
                {"name": "To", "value": "user@gmail.com"},
                {"name": "Subject", "value": "Simple Test Email"},
                {"name": "Date", "value": "Mon, 15 Oct 2025 15:00:00 -0700"},
                {"name": "Message-ID", "value": "<XYZ123@mail.gmail.com>"}
            ],
            "mimeType": "text/plain",
            "body": {
                "size": 123,
                "data": "VGhpcyBpcyBhIHBsYWluIHRleHQgZW1haWwgd2l0aCBubyBIVE1MIGNvbnRlbnQu"
            }
        }
    }


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service object."""
    mock_service = MagicMock()

    # Mock labels() API
    mock_labels = MagicMock()
    mock_service.users().labels.return_value = mock_labels

    # Mock messages() API
    mock_messages = MagicMock()
    mock_service.users().messages.return_value = mock_messages

    return mock_service


@pytest.fixture
def mock_credentials():
    """Mock OAuth credentials."""
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.expired = False
    mock_creds.refresh_token = "mock_refresh_token"
    return mock_creds


@pytest.fixture
def temp_export_dir(tmp_path):
    """Temporary directory for markdown export tests."""
    export_dir = tmp_path / "emails"
    export_dir.mkdir()
    return export_dir


@pytest.fixture
def mock_config():
    """Mock configuration object."""
    return {
        "COURIER_TIMEOUT_SECONDS": 20,
        "COURIER_MAX_RESULTS_DEFAULT": 10,
        "COURIER_MAX_FILE_SIZE_KB": 10,
        "COURIER_NETWORK_RETRY_ATTEMPTS": 3,
        "COURIER_NETWORK_RETRY_BACKOFF_FACTOR": 2,
        "COURIER_CONCURRENT_FETCH_LIMIT": 5,
        "COURIER_LABEL_CACHE_TTL_SECONDS": 3600,
        "GMAIL_CREDENTIALS_PATH": "/fake/path/credentials.json"
    }


@pytest.fixture
def sample_markdown_output():
    """Expected markdown output for sample message."""
    return """---
from: Alice Johnson <alice@example.com>
to: user@gmail.com
cc:
  - bob@example.com
bcc: []
subject: 'Q4 Planning: [VOICE] Meeting Notes'
date: 2025-10-15T14:32:00-07:00
message-id: <CABcDEF1234567890@mail.gmail.com>
labels:
  - INBOX
  - Project Docs
attachments:
  - filename: meeting-notes.pdf
    size: 245678
    mime_type: application/pdf
---

# Email from Alice Johnson

Here's the email body in plain text.
"""


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch):
    """Reset environment variables for each test."""
    # Clear Gmail-related env vars
    monkeypatch.delenv("GMAIL_CREDENTIALS_PATH", raising=False)
    monkeypatch.delenv("COURIER_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("COURIER_MAX_RESULTS_DEFAULT", raising=False)


@pytest.fixture(autouse=True)
def load_config_for_tests(monkeypatch):
    """Load configuration before each test."""
    from courier_mcp.config import load_config

    # Set minimal required env vars
    monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")

    # Load config (this will use defaults from courier.config)
    load_config()
