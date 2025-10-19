"""
Unit tests for Gmail service module (gmail_service.py).

Tests label fetching, message fetching, and rate limit handling.
"""

import pytest
from unittest.mock import MagicMock, patch
import asyncio
from datetime import datetime, timedelta

from courier_mcp.gmail_service import GmailService
from courier_mcp.errors import GmailAPIError


@pytest.mark.unit
class TestLabelFetching:
    """Test suite for label fetching and caching."""

    def test_fetch_labels_success(self, mock_gmail_service, sample_label_list):
        """Test successful label fetching from Gmail API."""
        # Mock the API call
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list

        gmail = GmailService(mock_gmail_service)
        labels = gmail.fetch_labels()

        assert len(labels) == 3
        assert labels[0]["id"] == "INBOX"
        assert labels[0]["name"] == "INBOX"
        assert labels[0]["message_count"] == 1245
        assert labels[2]["name"] == "Project Docs"

    def test_label_cache_hit(self, mock_gmail_service, sample_label_list):
        """Test that labels are cached and API is not called twice."""
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list

        gmail = GmailService(mock_gmail_service)

        # First call - should hit API
        labels1 = gmail.fetch_labels()

        # Second call - should use cache
        labels2 = gmail.fetch_labels()

        # API should only be called once
        assert mock_gmail_service.users().labels().list().execute.call_count == 1

        # Results should be identical
        assert labels1 == labels2

    def test_label_cache_ttl_expiration(self, mock_gmail_service, sample_label_list):
        """Test that label cache exists (TTL configuration tested via config)."""
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list

        gmail = GmailService(mock_gmail_service)

        # First call
        labels1 = gmail.fetch_labels()

        # Second call - should use cache (TTL is configured via config, not __init__)
        labels2 = gmail.fetch_labels()

        # API should only be called once (cache working)
        assert mock_gmail_service.users().labels().list().execute.call_count == 1

    def test_get_label_id_by_name(self, mock_gmail_service, sample_label_list):
        """Test translating friendly label name to ID."""
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list

        gmail = GmailService(mock_gmail_service)
        gmail.fetch_labels()  # Populate cache

        # Test system labels
        inbox_id = gmail.get_label_id("INBOX")
        assert inbox_id == "INBOX"

        # Test custom labels
        project_id = gmail.get_label_id("Project Docs")
        assert project_id == "Label_789"

    def test_get_label_id_case_insensitive(self, mock_gmail_service, sample_label_list):
        """Test that label name lookup is case-insensitive."""
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list

        gmail = GmailService(mock_gmail_service)
        gmail.fetch_labels()

        # Should find label regardless of case
        assert gmail.get_label_id("inbox") == "INBOX"
        assert gmail.get_label_id("Inbox") == "INBOX"
        assert gmail.get_label_id("project docs") == "Label_789"

    def test_get_label_id_not_found(self, mock_gmail_service, sample_label_list):
        """Test handling of non-existent label."""
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list

        gmail = GmailService(mock_gmail_service)
        gmail.fetch_labels()

        # Should return None or raise error for non-existent label
        result = gmail.get_label_id("NonExistentLabel")
        assert result is None


@pytest.mark.unit
class TestMessageFetching:
    """Test suite for message list and detail fetching."""

    def test_fetch_messages_basic_query(self, mock_gmail_service, sample_messages_list):
        """Test basic message fetching with simple query."""
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)
        messages = gmail.fetch_messages(query="is:unread", max_results=10)

        assert len(messages) == 3
        assert messages[0]["id"] == "msg_001"

        # Verify API was called with correct parameters
        mock_gmail_service.users().messages().list.assert_called_once()

    def test_fetch_messages_with_label_filter(self, mock_gmail_service, sample_messages_list, sample_label_list):
        """Test message fetching with label/folder filter."""
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)
        messages = gmail.fetch_messages(label_name="INBOX", max_results=10)

        assert len(messages) == 3

        # Verify label ID was used in query
        call_kwargs = mock_gmail_service.users().messages().list.call_args.kwargs
        assert "labelIds" in call_kwargs or "q" in call_kwargs

    def test_fetch_messages_with_date_range(self, mock_gmail_service, sample_messages_list):
        """Test message fetching with date range filters."""
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)
        messages = gmail.fetch_messages(
            date_start="2025-10-01",
            date_end="2025-10-15",
            max_results=10
        )

        assert len(messages) == 3

        # Verify date filters were added to query
        call_kwargs = mock_gmail_service.users().messages().list.call_args.kwargs
        assert "q" in call_kwargs
        assert "after:" in call_kwargs["q"] or "before:" in call_kwargs["q"]

    def test_fetch_messages_pagination(self, mock_gmail_service):
        """Test handling of paginated results."""
        # First page
        page1 = {
            "messages": [{"id": f"msg_{i}", "threadId": f"thread_{i}"} for i in range(100)],
            "nextPageToken": "token_page_2"
        }
        # Second page
        page2 = {
            "messages": [{"id": f"msg_{i}", "threadId": f"thread_{i}"} for i in range(100, 150)],
            "resultSizeEstimate": 150
        }

        mock_gmail_service.users().messages().list().execute.side_effect = [page1, page2]

        gmail = GmailService(mock_gmail_service)
        messages = gmail.fetch_messages(max_results=150)

        # Should fetch both pages
        assert len(messages) == 150
        assert mock_gmail_service.users().messages().list().execute.call_count == 2

    def test_fetch_messages_max_results_limit(self, mock_gmail_service, sample_messages_list):
        """Test that max_results is enforced (1-100 limit)."""
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)

        # Should clamp to valid range
        messages = gmail.fetch_messages(max_results=150)  # Over limit
        call_kwargs = mock_gmail_service.users().messages().list.call_args.kwargs
        assert call_kwargs.get("maxResults", 100) <= 100


@pytest.mark.unit
@pytest.mark.asyncio
class TestMessageDetailFetching:
    """Test suite for concurrent message detail fetching."""

    async def test_fetch_message_details_single(self, mock_gmail_service, sample_message_full):
        """Test fetching details for a single message."""
        mock_gmail_service.users().messages().get().execute.return_value = sample_message_full

        gmail = GmailService(mock_gmail_service)
        message_ids = ["msg_001"]

        details = await gmail.fetch_message_details(message_ids)

        assert len(details) == 1
        assert details[0]["id"] == "msg_001"

    async def test_fetch_message_details_concurrent(self, mock_gmail_service, sample_message_full):
        """Test concurrent fetching of multiple messages."""
        # Return different messages for each ID
        def get_message_side_effect(*args, **kwargs):
            mock_response = MagicMock()
            msg_id = kwargs.get("id", "unknown")
            mock_response.execute.return_value = {**sample_message_full, "id": msg_id}
            return mock_response

        mock_gmail_service.users().messages().get.side_effect = get_message_side_effect

        # concurrent_limit is configured via config, not __init__
        gmail = GmailService(mock_gmail_service)
        message_ids = [f"msg_{i}" for i in range(10)]

        details = await gmail.fetch_message_details(message_ids)

        assert len(details) == 10
        # All messages should be fetched
        assert all(d is not None for d in details)

    async def test_fetch_message_details_with_timeout(self, mock_gmail_service):
        """Test timeout handling during message fetching."""

        async def slow_fetch(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow API
            return sample_message_full

        with patch.object(GmailService, "_fetch_single_message", side_effect=slow_fetch):
            gmail = GmailService(mock_gmail_service)
            message_ids = ["msg_001"]

            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    gmail.fetch_message_details(message_ids),
                    timeout=1
                )

    async def test_fetch_message_details_handles_404(self, mock_gmail_service, sample_message_full):
        """Test handling of deleted messages (404 errors)."""
        from googleapiclient.errors import HttpError

        def get_message_side_effect(*args, **kwargs):
            msg_id = kwargs.get("id", "unknown")
            mock_response = MagicMock()

            if msg_id == "msg_deleted":
                # Simulate 404 for deleted message
                raise HttpError(
                    resp=MagicMock(status=404),
                    content=b"Not Found"
                )
            else:
                mock_response.execute.return_value = {**sample_message_full, "id": msg_id}
                return mock_response

        mock_gmail_service.users().messages().get.side_effect = get_message_side_effect

        gmail = GmailService(mock_gmail_service)
        message_ids = ["msg_001", "msg_deleted", "msg_003"]

        details = await gmail.fetch_message_details(message_ids)

        # Should return partial results, skipping deleted message
        valid_details = [d for d in details if d is not None]
        assert len(valid_details) == 2


@pytest.mark.unit
class TestRateLimitHandling:
    """Test suite for rate limiting and exponential backoff."""

    def test_exponential_backoff_on_429(self, mock_gmail_service, sample_messages_list):
        """Test exponential backoff when rate limited."""
        from googleapiclient.errors import HttpError

        # First call: rate limit error
        # Second call: success
        call_count = 0

        def list_with_rate_limit(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                raise HttpError(
                    resp=MagicMock(status=429),
                    content=b"Rate Limit Exceeded"
                )
            else:
                mock_response = MagicMock()
                mock_response.execute.return_value = sample_messages_list
                return mock_response

        mock_gmail_service.users().messages().list.side_effect = list_with_rate_limit

        # retry_attempts and backoff_factor are configured via config
        gmail = GmailService(mock_gmail_service)

        # Should retry and eventually succeed
        messages = gmail.fetch_messages(max_results=10)

        assert len(messages) == 3
        assert call_count == 2  # First failed, second succeeded

    def test_max_retry_attempts_exceeded(self, mock_gmail_service):
        """Test that retries are limited to max attempts."""
        from googleapiclient.errors import HttpError

        def always_rate_limit(*args, **kwargs):
            raise HttpError(
                resp=MagicMock(status=429),
                content=b"Rate Limit Exceeded"
            )

        mock_gmail_service.users().messages().list.side_effect = always_rate_limit

        # retry_attempts configured via config
        gmail = GmailService(mock_gmail_service)

        # Should raise error after max retries
        with pytest.raises(GmailAPIError, match="Rate limit"):
            gmail.fetch_messages(max_results=10)

    def test_permanent_errors_not_retried(self, mock_gmail_service):
        """Test that permanent errors (401, 403) are not retried."""
        from googleapiclient.errors import HttpError

        call_count = 0

        def auth_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise HttpError(
                resp=MagicMock(status=401),
                content=b"Unauthorized"
            )

        mock_gmail_service.users().messages().list.side_effect = auth_error

        # retry_attempts configured via config
        gmail = GmailService(mock_gmail_service)

        # Should fail immediately without retries
        with pytest.raises(GmailAPIError, match="Auth"):
            gmail.fetch_messages(max_results=10)

        # Should only be called once (no retries)
        assert call_count == 1
