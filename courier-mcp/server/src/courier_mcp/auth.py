"""OAuth 2.0 authentication for Gmail API.

Handles credential loading, token refresh, and service authentication.
Supports OAuth 2.0 flow with refresh tokens for user delegation.

Security Notes:
- Credentials stored locally via env var GMAIL_CREDENTIALS_PATH
- Token.pickle cached for session to avoid repeated token calls
- Never logs authentication tokens
- Requires 'gmail.readonly' scope (read-only access)
"""

import os
import pickle
from pathlib import Path
from typing import final

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from courier_mcp.errors import AuthenticationError
from courier_mcp.logger import get_logger

# Gmail API scope (read-only)
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

logger = get_logger(__name__)


@final
class GmailAuthenticator:
    """Handles OAuth 2.0 authentication with Gmail API."""

    def __init__(self, credentials_path: str | None = None):
        """Initialize authenticator.

        Args:
            credentials_path: Path to credentials.json from Google Cloud.
                            If not provided, uses GMAIL_CREDENTIALS_PATH env var.

        Raises:
            AuthenticationError: If credentials path not found
        """
        self.credentials_path = credentials_path or os.getenv("GMAIL_CREDENTIALS_PATH")

        if not self.credentials_path:
            raise AuthenticationError(
                "Gmail credentials not configured",
                details={
                    "guidance": "Set GMAIL_CREDENTIALS_PATH environment variable to point to credentials.json from Google Cloud",
                },
            )

        credentials_file = Path(self.credentials_path)
        if not credentials_file.exists():
            raise AuthenticationError(
                f"Credentials file not found: {self.credentials_path}",
                details={
                    "guidance": "Create credentials.json via Google Cloud OAuth consent screen. See docs/SETUP.md",
                },
            )

        self.credentials_path = str(credentials_file)
        self.token_file = credentials_file.parent / "token.pickle"
        self._credentials: Credentials | None = None
        self._service = None

    def _load_or_refresh_credentials(self) -> Credentials:
        """Load credentials from pickle cache or refresh if needed.

        Returns:
            Valid Credentials object

        Raises:
            AuthenticationError: If credentials expired and cannot refresh
        """
        credentials = None

        # Try to load cached token
        if self.token_file.exists():
            try:
                with open(self.token_file, "rb") as token:
                    credentials = pickle.load(token)
                logger.debug("Loaded cached token")
            except Exception as e:
                logger.warning(f"Failed to load cached token: {e}")
                credentials = None

        # If no credentials or expired, run OAuth flow
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    logger.debug("Refreshing expired token")
                    credentials.refresh(Request())
                except RefreshError as e:
                    raise AuthenticationError(
                        f"Failed to refresh token: {e}",
                        details={
                            "guidance": "Re-authenticate by deleting token.pickle and restarting"
                        },
                    ) from e
            else:
                # Need to run full OAuth flow
                try:
                    logger.debug("Running OAuth flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        GMAIL_SCOPES,
                    )
                    credentials = flow.run_local_server(port=0)
                except Exception as e:
                    raise AuthenticationError(
                        f"OAuth flow failed: {e}",
                        details={
                            "guidance": "Ensure credentials.json is valid and from a Desktop/Native application. See docs/SETUP.md",
                        },
                    ) from e

        # Save token for next time
        try:
            with open(self.token_file, "wb") as token:
                pickle.dump(credentials, token)
            logger.debug("Saved credentials to token.pickle")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")

        return credentials

    def get_credentials(self) -> Credentials:
        """Get valid OAuth credentials.

        Returns:
            Valid Credentials object

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._credentials is None:
            self._credentials = self._load_or_refresh_credentials()

        return self._credentials

    def ensure_valid_token(self) -> None:
        """Ensure token is valid, refresh if needed.

        Raises:
            AuthenticationError: If token cannot be refreshed
        """
        credentials = self.get_credentials()

        if credentials.expired and credentials.refresh_token:
            try:
                logger.debug("Refreshing expired token")
                credentials.refresh(Request())
            except RefreshError as e:
                raise AuthenticationError(
                    f"Token refresh failed: {e}",
                    details={"guidance": "Re-authenticate by deleting token.pickle"},
                )

    def build_gmail_service(self):
        """Build authenticated Gmail API service.

        Returns:
            Gmail API service object

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._service is not None:
            return self._service

        try:
            self.ensure_valid_token()
            credentials = self.get_credentials()
            self._service = build("gmail", "v1", credentials=credentials)
            logger.info("Gmail API service built successfully")
            return self._service
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(
                f"Failed to build Gmail service: {e}",
                details={"guidance": "Check credentials and try again"},
            )

    def __repr__(self) -> str:
        """String representation (no sensitive data)."""
        return "GmailAuthenticator(credentials_path=***)"


# Global authenticator instance
_authenticator: GmailAuthenticator | None = None


def initialize_authenticator(credentials_path: str | None = None) -> GmailAuthenticator:
    """Initialize and return global authenticator instance.

    Args:
        credentials_path: Optional explicit path to credentials.json

    Returns:
        GmailAuthenticator instance

    Raises:
        AuthenticationError: If authentication setup fails
    """
    global _authenticator

    if _authenticator is None:
        _authenticator = GmailAuthenticator(credentials_path)

    return _authenticator


def get_authenticator() -> GmailAuthenticator:
    """Get global authenticator instance.

    Raises:
        RuntimeError: If authenticator not yet initialized
    """
    if _authenticator is None:
        raise RuntimeError("Authenticator not initialized. Call initialize_authenticator() first.")

    return _authenticator


if __name__ == "__main__":
    # Test authenticator
    try:
        authenticator = GmailAuthenticator()
        print("✓ Authenticator initialized")

        _ = authenticator.build_gmail_service()
        print("✓ Gmail service built")

    except AuthenticationError as e:
        print(f"✗ Authentication error: {e}")
