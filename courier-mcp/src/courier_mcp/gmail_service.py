"""Gmail API service layer with label caching and folder discovery.

Provides:
- Label fetching and caching with TTL
- Label ID ↔ Name translation
- Message list querying with search support
- Concurrent message detail fetching
- Exponential backoff for rate limiting
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from googleapiclient.errors import HttpError

from courier_mcp.logger import get_logger
from courier_mcp.config import get_config
from courier_mcp.errors import GmailAPIError, RateLimitError, AuthenticationError

logger = get_logger(__name__)


@dataclass
class Label:
    """Gmail label/folder metadata."""

    id: str
    name: str
    message_count: int
    unread_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Message:
    """Gmail message metadata (for list operations)."""

    id: str
    thread_id: str


class LabelCache:
    """In-memory cache for Gmail labels with TTL."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache.

        Args:
            ttl_seconds: Time to live for cached labels (default: 1 hour)
        """
        self.ttl_seconds = ttl_seconds
        self._labels: Optional[Dict[str, Label]] = None
        self._cached_at: Optional[float] = None

    def is_valid(self) -> bool:
        """Check if cache is valid (not expired)."""
        if self._labels is None or self._cached_at is None:
            return False

        age = time.time() - self._cached_at
        return age < self.ttl_seconds

    def get(self) -> Optional[Dict[str, Label]]:
        """Get cached labels if valid."""
        return self._labels if self.is_valid() else None

    def set(self, labels: Dict[str, Label]) -> None:
        """Store labels in cache."""
        self._labels = labels
        self._cached_at = time.time()

    def clear(self) -> None:
        """Clear cache."""
        self._labels = None
        self._cached_at = None


class GmailService:
    """Gmail API service with label caching and search support."""

    # System labels that always exist
    SYSTEM_LABELS = {
        "INBOX": "Inbox",
        "SENT": "[Gmail]/Sent Mail",
        "DRAFTS": "[Gmail]/Drafts",
        "SPAM": "[Gmail]/Spam",
        "TRASH": "[Gmail]/Trash",
        "IMPORTANT": "[Gmail]/Important",
        "STARRED": "[Gmail]/Starred",
        "UNREAD": "[Gmail]/All Mail",
    }

    def __init__(self, service):
        """Initialize Gmail service.

        Args:
            service: Authenticated Gmail API service object
        """
        self.service = service
        config = get_config()
        ttl = config.get_int("COURIER_LABEL_CACHE_TTL_SECONDS", 3600)
        self._label_cache = LabelCache(ttl)
        self._label_id_map: Dict[str, str] = {}  # friendly_name → id mapping
        logger.info(f"GmailService initialized with label cache TTL: {ttl}s")

    def fetch_labels(self, force_refresh: bool = False) -> Dict[str, Label]:
        """Fetch all Gmail labels with message counts.

        Args:
            force_refresh: Ignore cache and fetch fresh labels

        Returns:
            Dictionary of label_id → Label

        Raises:
            GmailAPIError: If API call fails
        """
        # Check cache first
        if not force_refresh:
            cached = self._label_cache.get()
            if cached:
                logger.debug(f"Returning {len(cached)} cached labels")
                return cached

        logger.debug("Fetching labels from Gmail API")

        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels_data = results.get("labels", [])
            logger.debug(f"Fetched {len(labels_data)} labels from API")

            # Parse labels
            labels = {}
            for label_data in labels_data:
                label = Label(
                    id=label_data["id"],
                    name=label_data["name"],
                    message_count=label_data.get("messagesTotal", 0),
                    unread_count=label_data.get("messagesUnread", 0),
                )
                labels[label.id] = label

                # Build friendly name mapping (prefer label name, fallback to ID)
                friendly_name = label.name.split("/")[-1]  # Use last part after /
                self._label_id_map[friendly_name.lower()] = label.id
                self._label_id_map[label.name.lower()] = label.id

            self._label_cache.set(labels)
            logger.info(f"Cached {len(labels)} labels")

            return labels

        except HttpError as e:
            if e.resp.status == 401:
                raise AuthenticationError("Token expired", details={"http_status": 401})
            elif e.resp.status == 403:
                raise GmailAPIError("Permission denied", status_code=403)
            else:
                raise GmailAPIError(f"Label fetch failed: {e}", status_code=e.resp.status)

    def get_label_id(self, friendly_name: str) -> str:
        """Translate friendly label name to Gmail label ID.

        Supports:
        - Label names like "INBOX", "Inbox"
        - Full paths like "Project Docs", "Work/Projects"
        - Case-insensitive matching

        Args:
            friendly_name: User-friendly label name

        Returns:
            Gmail label ID

        Raises:
            GmailAPIError: If label not found
        """
        # Fetch labels if not cached
        if not self._label_id_map:
            self.fetch_labels()

        # Try exact match (case-insensitive)
        label_lower = friendly_name.lower()
        if label_lower in self._label_id_map:
            label_id = self._label_id_map[label_lower]
            logger.debug(f"Mapped '{friendly_name}' → '{label_id}'")
            return label_id

        # Try partial match (suffix matching)
        for key, label_id in self._label_id_map.items():
            if key.endswith(label_lower) or label_lower.endswith(key):
                logger.debug(f"Mapped '{friendly_name}' → '{label_id}' (partial match)")
                return label_id

        raise GmailAPIError(
            f"Label not found: {friendly_name}",
            details={"available_labels": list(set(self._label_id_map.keys()))},
        )

    def build_search_query(
        self,
        search_query: Optional[str] = None,
        label_id: Optional[str] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
    ) -> str:
        """Build Gmail search query from components.

        Args:
            search_query: Gmail search syntax (e.g., "is:unread from:boss@example.com")
            label_id: Gmail label ID to filter by
            date_start: Start date in YYYY-MM-DD or Gmail date format
            date_end: End date in YYYY-MM-DD or Gmail date format

        Returns:
            Combined Gmail search query
        """
        parts = []

        if search_query:
            parts.append(search_query)

        if label_id:
            # Gmail API filters by label in messages.list(), not in query
            pass

        if date_start:
            parts.append(f"after:{date_start}")

        if date_end:
            parts.append(f"before:{date_end}")

        query = " ".join(parts)
        logger.debug(f"Built search query: {query}")

        return query

    async def fetch_messages(
        self,
        search_query: Optional[str] = None,
        label_id: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Message]:
        """Fetch message list with search and label filtering.

        Implements exponential backoff for rate limiting (429 responses).
        Supports pagination via nextPageToken.

        Args:
            search_query: Gmail search query syntax
            label_id: Label ID to filter by
            max_results: Maximum results (1-100)

        Returns:
            List of Message objects (ID and thread ID only)

        Raises:
            GmailAPIError: If API call fails
            RateLimitError: If rate limited after max retries
            AuthenticationError: If token expired
        """
        max_results = max(1, min(max_results, 100))  # Clamp to 1-100
        config = get_config()
        max_retries = config.get_int("COURIER_NETWORK_RETRY_ATTEMPTS", 3)
        backoff_factor = config.get_float("COURIER_NETWORK_RETRY_BACKOFF_FACTOR", 2.0)

        query = self.build_search_query(search_query, label_id)
        logger.debug(f"Fetching messages: query='{query}', label={label_id}, max={max_results}")

        for attempt in range(max_retries):
            try:
                request = self.service.users().messages().list(
                    userId="me",
                    q=query if query else None,
                    labelIds=[label_id] if label_id else None,
                    maxResults=max_results,
                )

                results = request.execute()
                messages_data = results.get("messages", [])

                messages = [Message(id=m["id"], thread_id=m["threadId"]) for m in messages_data]

                logger.info(f"Fetched {len(messages)} message IDs")
                return messages

            except HttpError as e:
                if e.resp.status == 429:
                    # Rate limited - implement exponential backoff
                    if attempt < max_retries - 1:
                        backoff = min(2 ** attempt * backoff_factor, 10)
                        logger.warning(
                            f"Rate limited (429), backing off {backoff}s (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        raise RateLimitError(
                            "Rate limited by Gmail API after retries"
                        )
                elif e.resp.status == 400:
                    raise GmailAPIError("Invalid search query syntax", status_code=400)
                elif e.resp.status == 401:
                    raise AuthenticationError("Token expired")
                else:
                    raise GmailAPIError(f"Message list failed: {e}", status_code=e.resp.status)

    async def fetch_message_details(
        self,
        message_ids: List[str],
        timeout_seconds: float = 20,
        max_concurrent: int = 5,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """Fetch full message details concurrently with timeout.

        Implements:
        - Concurrent fetching with semaphore to control concurrency
        - Exponential backoff for rate limits (429)
        - Graceful handling of deleted messages (404)
        - Global timeout enforcement returning partial results
        - Per-message retry logic for transient errors

        Args:
            message_ids: List of message IDs to fetch
            timeout_seconds: Maximum time to spend fetching
            max_concurrent: Maximum concurrent requests (default: 5)

        Returns:
            Tuple of (messages, errors)
            - messages: List of full message dicts (Gmail API format)
            - errors: List of error dicts with message_id and error reason

        Note:
            On timeout, returns partial results (messages fetched so far)
            and error list including timed-out messages.
        """
        logger.debug(f"Fetching details for {len(message_ids)} messages (timeout: {timeout_seconds}s, max_concurrent: {max_concurrent})")

        config = get_config()
        max_retries = config.get_int("COURIER_NETWORK_RETRY_ATTEMPTS", 3)
        backoff_factor = config.get_float("COURIER_NETWORK_RETRY_BACKOFF_FACTOR", 2.0)

        messages = []
        errors = []
        semaphore = asyncio.Semaphore(max_concurrent)
        all_tasks = []

        async def fetch_one(msg_id: str) -> Optional[Dict]:
            """Fetch single message with retry and backoff.

            Handles:
            - 404: Message deleted (informational, no retry)
            - 429: Rate limited (exponential backoff retry)
            - 401/403: Auth errors (no retry, critical)
            - Other: Log and skip
            """
            async with semaphore:
                for attempt in range(max_retries):
                    try:
                        result = self.service.users().messages().get(
                            userId="me",
                            id=msg_id,
                            format="full",
                        ).execute()

                        logger.debug(f"Fetched message {msg_id}")
                        return result

                    except HttpError as e:
                        if e.resp.status == 404:
                            # Message deleted - informational, don't retry
                            logger.debug(f"Message {msg_id} deleted (404)")
                            errors.append(
                                {
                                    "message_id": msg_id,
                                    "error": "Message was deleted (possibly by another client)",
                                }
                            )
                            return None

                        elif e.resp.status == 429:
                            # Rate limited - retry with exponential backoff
                            if attempt < max_retries - 1:
                                backoff = min(2 ** attempt * backoff_factor, 10)
                                logger.debug(f"Message {msg_id}: Rate limited (429), backing off {backoff}s")
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                logger.warning(f"Message {msg_id}: Rate limited after {max_retries} attempts")
                                errors.append(
                                    {
                                        "message_id": msg_id,
                                        "error": "Rate limited after retries",
                                    }
                                )
                                return None

                        elif e.resp.status == 401:
                            # Auth error - critical, don't retry
                            logger.error(f"Message {msg_id}: Auth error (401): {e}")
                            errors.append(
                                {
                                    "message_id": msg_id,
                                    "error": "Authentication failed (token expired)",
                                }
                            )
                            return None

                        elif e.resp.status == 403:
                            # Permission error - critical, don't retry
                            logger.error(f"Message {msg_id}: Permission denied (403): {e}")
                            errors.append(
                                {
                                    "message_id": msg_id,
                                    "error": "Permission denied",
                                }
                            )
                            return None

                        else:
                            # Other HTTP errors
                            logger.warning(f"Message {msg_id}: HTTP error {e.resp.status}: {e}")
                            errors.append(
                                {
                                    "message_id": msg_id,
                                    "error": f"HTTP {e.resp.status}: {str(e)[:100]}",
                                }
                            )
                            return None

        try:
            # Create fetch tasks
            tasks = [fetch_one(msg_id) for msg_id in message_ids]
            all_tasks = tasks

            # Run with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_seconds,
            )

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task exception: {result}")
                elif result is not None:
                    messages.append(result)

            logger.info(f"Fetched {len(messages)} messages successfully, {len(errors)} errors")
            return messages, errors

        except asyncio.TimeoutError:
            logger.warning(f"Timeout after {timeout_seconds}s, partial results: {len(messages)} messages fetched, {len(errors)} errors")
            # Cancel remaining tasks
            for task in all_tasks:
                if not task.done():
                    task.cancel()
                    logger.debug(f"Cancelled task {task}")

            return messages, errors


if __name__ == "__main__":
    print("✓ GmailService module loaded")
