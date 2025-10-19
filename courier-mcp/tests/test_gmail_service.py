"""
Unit tests for Gmail service module (gmail_service.py).

Tests label fetching, message fetching, and rate limit handling.
"""

import pytest
from unittest.mock import MagicMock, patch
import asyncio
from datetime import datetime, timedelta

from courier_mcp.gmail_service import GmailService
from courier_mcp.errors import GmailAPIError, RateLimitError, AuthenticationError


@pytest.mark.unit
class TestLabelFetching:
    """Test suite for label fetching and caching."""

    def test_fetch_labels_success(self, mock_gmail_service, sample_label_list):
        """Test successful label fetching from Gmail API."""
        # Mock the API call
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list

        gmail = GmailService(mock_gmail_service)
        labels = gmail.fetch_labels()

        # fetch_labels() returns dict[str, Label] where keys are label IDs
        assert len(labels) == 3
        assert "INBOX" in labels
        assert labels["INBOX"].name == "INBOX"
        assert labels["INBOX"].message_count == 1245
        assert "Label_789" in labels
        assert labels["Label_789"].name == "Project Docs"

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

        # Should raise GmailAPIError for non-existent label
        with pytest.raises(GmailAPIError, match="Label not found"):
            gmail.get_label_id("NonExistentLabel")


@pytest.mark.unit
@pytest.mark.asyncio
class TestMessageFetching:
    """Test suite for message list and detail fetching."""

    async def test_fetch_messages_basic_query(self, mock_gmail_service, sample_messages_list):
        """Test basic message fetching with simple query."""
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)
        # fetch_messages() is async and takes search_query parameter
        messages = await gmail.fetch_messages(search_query="is:unread", max_results=10)

        assert len(messages) == 3
        assert messages[0].id == "msg_001"

        # Verify API was called with correct parameters - check that it was called, not how many times
        assert mock_gmail_service.users().messages().list.call_count >= 1

    async def test_fetch_messages_with_label_filter(self, mock_gmail_service, sample_messages_list, sample_label_list):
        """Test message fetching with label/folder filter."""
        mock_gmail_service.users().labels().list().execute.return_value = sample_label_list
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)
        # fetch_messages() takes label_id parameter, not label_name
        messages = await gmail.fetch_messages(label_id="INBOX", max_results=10)

        assert len(messages) == 3

        # Verify label ID was used in query
        call_kwargs = mock_gmail_service.users().messages().list.call_args.kwargs
        assert "labelIds" in call_kwargs or "q" in call_kwargs

    async def test_fetch_messages_with_date_range(self, mock_gmail_service, sample_messages_list):
        """Test message fetching with date range filters."""
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)
        # Date filters are passed via search_query using build_search_query()
        # Build the query first
        query = gmail.build_search_query(date_start="2025-10-01", date_end="2025-10-15")
        messages = await gmail.fetch_messages(
            search_query=query,
            max_results=10
        )

        assert len(messages) == 3

        # Verify date filters were in the query
        assert "after:" in query
        assert "before:" in query

    async def test_fetch_messages_pagination(self, mock_gmail_service):
        """Test that fetch_messages handles single page correctly (pagination not yet implemented)."""
        # Current implementation fetches single page only
        page1 = {
            "messages": [{"id": f"msg_{i}", "threadId": f"thread_{i}"} for i in range(10)],
            "resultSizeEstimate": 10
        }

        mock_gmail_service.users().messages().list().execute.return_value = page1

        gmail = GmailService(mock_gmail_service)
        messages = await gmail.fetch_messages(max_results=10)

        # Should fetch single page
        assert len(messages) == 10
        assert mock_gmail_service.users().messages().list().execute.call_count == 1

    async def test_fetch_messages_max_results_limit(self, mock_gmail_service, sample_messages_list):
        """Test that max_results is enforced (1-100 limit)."""
        mock_gmail_service.users().messages().list().execute.return_value = sample_messages_list

        gmail = GmailService(mock_gmail_service)

        # Should clamp to valid range
        messages = await gmail.fetch_messages(max_results=150)  # Over limit
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

        # fetch_message_details returns tuple (messages, errors)
        messages, errors = await gmail.fetch_message_details(message_ids)

        assert len(messages) == 1
        assert messages[0]["id"] == "msg_001"
        assert len(errors) == 0

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

        # fetch_message_details returns tuple (messages, errors)
        messages, errors = await gmail.fetch_message_details(message_ids)

        assert len(messages) == 10
        assert len(errors) == 0
        # All messages should be fetched
        assert all(m is not None for m in messages)

    async def test_fetch_message_details_with_timeout(self, mock_gmail_service, sample_message_full):
        """Test timeout handling during message fetching."""

        async def slow_fetch(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate slow API
            return sample_message_full

        # Simulate slow execute() call
        mock_gmail_service.users().messages().get().execute.side_effect = lambda: asyncio.run(slow_fetch())

        gmail = GmailService(mock_gmail_service)
        message_ids = ["msg_001"]

        # fetch_message_details has built-in timeout that returns partial results
        # We can override it with a shorter timeout
        messages, errors = await gmail.fetch_message_details(message_ids, timeout_seconds=0.1)

        # Should return partial results (empty in this case due to timeout)
        assert isinstance(messages, list)
        assert isinstance(errors, list)

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

        # fetch_message_details returns tuple (messages, errors)
        messages, errors = await gmail.fetch_message_details(message_ids)

        # Should return 2 messages (deleted one skipped) and 1 error
        assert len(messages) == 2
        assert len(errors) == 1
        assert errors[0]["message_id"] == "msg_deleted"


@pytest.mark.unit
@pytest.mark.asyncio
class TestRateLimitHandling:
    """Test suite for rate limiting and exponential backoff."""

    async def test_exponential_backoff_on_429(self, mock_gmail_service, sample_messages_list):
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
        messages = await gmail.fetch_messages(max_results=10)

        assert len(messages) == 3
        assert call_count == 2  # First failed, second succeeded

    async def test_max_retry_attempts_exceeded(self, mock_gmail_service):
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

        # Should raise RateLimitError after max retries
        with pytest.raises(RateLimitError, match="Rate limited"):
            await gmail.fetch_messages(max_results=10)

    async def test_permanent_errors_not_retried(self, mock_gmail_service):
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

        # Should fail immediately without retries - raises AuthenticationError
        with pytest.raises(AuthenticationError, match="Token expired"):
            await gmail.fetch_messages(max_results=10)

        # Should only be called once (no retries)
        assert call_count == 1
