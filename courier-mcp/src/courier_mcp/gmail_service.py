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

        Args:
            search_query: Gmail search query syntax
            label_id: Label ID to filter by
            max_results: Maximum results (1-100)

        Returns:
            List of Message objects (ID and thread ID only)

        Raises:
            GmailAPIError: If API call fails
        """
        max_results = max(1, min(max_results, 100))  # Clamp to 1-100

        query = self.build_search_query(search_query, label_id)

        logger.debug(f"Fetching messages: query='{query}', label={label_id}, max={max_results}")

        try:
            request = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results,
            )

            if label_id:
                # Note: labelIds is separate parameter
                request = self.service.users().messages().list(
                    userId="me",
                    q=query,
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
                raise RateLimitError("Rate limited by Gmail API")
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

        Args:
            message_ids: List of message IDs to fetch
            timeout_seconds: Maximum time to spend fetching
            max_concurrent: Maximum concurrent requests

        Returns:
            Tuple of (messages, errors)
            - messages: List of full message dicts
            - errors: List of error dicts with message_id and reason

        Raises:
            GmailAPIError: If critical error occurs
        """
        logger.debug(f"Fetching details for {len(message_ids)} messages (timeout: {timeout_seconds}s)")

        messages = []
        errors = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_one(msg_id: str) -> Optional[Dict]:
            """Fetch single message with backoff."""
            async with semaphore:
                for attempt in range(3):
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
                            # Message deleted
                            logger.debug(f"Message {msg_id} deleted (404)")
                            errors.append(
                                {
                                    "message_id": msg_id,
                                    "error": "Message was deleted (possibly by another client)",
                                }
                            )
                            return None
                        elif e.resp.status == 429:
                            # Rate limit
                            if attempt < 2:
                                backoff = min(2 ** attempt, 10)
                                logger.debug(f"Rate limited, backing off {backoff}s")
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                errors.append(
                                    {
                                        "message_id": msg_id,
                                        "error": "Rate limited after retries",
                                    }
                                )
                                return None
                        else:
                            logger.warning(f"Error fetching {msg_id}: {e}")
                            errors.append(
                                {
                                    "message_id": msg_id,
                                    "error": str(e),
                                }
                            )
                            return None

        try:
            # Create fetch tasks
            tasks = [fetch_one(msg_id) for msg_id in message_ids]

            # Run with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_seconds,
            )

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task failed: {result}")
                elif result is not None:
                    messages.append(result)

            logger.info(f"Fetched {len(messages)} messages successfully, {len(errors)} errors")

            return messages, errors

        except asyncio.TimeoutError:
            logger.warning(f"Timeout after {timeout_seconds}s, partial results: {len(messages)} messages")
            # Cancel remaining tasks
            for task in asyncio.all_tasks():
                task.cancel()

            return messages, errors


if __name__ == "__main__":
    print("✓ GmailService module loaded")
