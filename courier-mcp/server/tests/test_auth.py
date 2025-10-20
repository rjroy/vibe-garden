"""
Unit tests for authentication module (auth.py).

Tests credential loading, token refresh, and Gmail service building.
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os
import pickle
from pathlib import Path

# Ensure src directory is in path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from courier_mcp.auth import GmailAuthenticator
from courier_mcp.errors import AuthenticationError


@pytest.mark.unit
class TestGmailAuthenticator:
    """Test suite for GmailAuthenticator class."""

    def test_init_missing_credentials_path(self, monkeypatch):
        """Test initialization fails when GMAIL_CREDENTIALS_PATH not set."""
        monkeypatch.delenv("GMAIL_CREDENTIALS_PATH", raising=False)

        # Error message is "Gmail credentials not configured"
        with pytest.raises(AuthenticationError, match="Gmail credentials not configured"):
            GmailAuthenticator()

    def test_init_credentials_file_not_found(self, monkeypatch):
        """Test initialization fails when credentials file doesn't exist."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/nonexistent/credentials.json")

        with pytest.raises(AuthenticationError, match="not found"):
            GmailAuthenticator()

    @patch("pathlib.Path.exists")
    def test_init_success_with_valid_credentials(self, mock_exists, monkeypatch):
        """Test successful initialization with valid credentials."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")
        mock_exists.return_value = True

        auth = GmailAuthenticator()

        assert auth.credentials_path == "/fake/credentials.json"
        mock_exists.assert_called()

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    def test_load_cached_token(self, mock_pickle, mock_file, mock_exists, monkeypatch, mock_credentials):
        """Test loading cached token from token.pickle."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")

        # Credentials file and token file both exist
        mock_exists.return_value = True
        mock_pickle.return_value = mock_credentials

        auth = GmailAuthenticator()
        # Method is _load_or_refresh_credentials not _load_credentials
        creds = auth._load_or_refresh_credentials()

        assert creds is not None
        assert creds.valid
        mock_pickle.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"installed": {}}')
    @patch("courier_mcp.auth.InstalledAppFlow")
    def test_token_refresh_on_expired(self, mock_flow, mock_file, mock_exists, monkeypatch, mock_credentials):
        """Test token refresh when credentials are expired."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")
        mock_exists.return_value = True

        # Simulate expired credentials
        mock_credentials.valid = False
        mock_credentials.expired = True
        mock_credentials.refresh_token = "valid_refresh_token"

        with patch("pickle.load", return_value=mock_credentials):
            with patch("pickle.dump") as mock_dump:
                with patch.object(mock_credentials, "refresh") as mock_refresh:
                    auth = GmailAuthenticator()
                    # Method is _load_or_refresh_credentials
                    creds = auth._load_or_refresh_credentials()

                    # Should attempt refresh
                    mock_refresh.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"installed": {}}')
    @patch("courier_mcp.auth.InstalledAppFlow")
    def test_build_gmail_service_success(self, mock_flow, mock_file, mock_exists, monkeypatch, mock_credentials):
        """Test building Gmail service with valid credentials."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")
        mock_exists.return_value = True

        with patch("pickle.load", return_value=mock_credentials):
            with patch("courier_mcp.auth.build") as mock_build:
                mock_service = MagicMock()
                mock_build.return_value = mock_service

                auth = GmailAuthenticator()
                service = auth.build_gmail_service()

                assert service is not None
                mock_build.assert_called_once_with("gmail", "v1", credentials=mock_credentials)

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"installed": {}}')
    @patch("courier_mcp.auth.InstalledAppFlow")
    def test_authentication_error_on_invalid_credentials(self, mock_flow, mock_file, mock_exists, monkeypatch):
        """Test that invalid credentials trigger OAuth flow (not an error)."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")
        mock_exists.return_value = True

        # Simulate invalid credentials (no refresh token)
        mock_credentials = MagicMock()
        mock_credentials.valid = False
        mock_credentials.expired = True
        mock_credentials.refresh_token = None

        # Mock OAuth flow
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_credentials
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        with patch("pickle.load", return_value=mock_credentials):
            with patch("pickle.dump"):
                auth = GmailAuthenticator()
                # Should run OAuth flow, not raise error
                creds = auth._load_or_refresh_credentials()
                assert creds is not None

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"installed": {"client_id": "test"}}')
    @patch("courier_mcp.auth.InstalledAppFlow")
    @patch("pickle.dump")
    def test_new_token_generation_when_no_cache(self, mock_dump, mock_flow, mock_file, mock_path_exists, monkeypatch, mock_credentials):
        """Test generating new token when token.pickle doesn't exist."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")

        # credentials.json exists, token.pickle doesn't
        # Path.exists() is called twice: once for credentials, once for token
        mock_path_exists.side_effect = [True, False]  # First call True, second False

        # Mock the OAuth flow
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_credentials
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        auth = GmailAuthenticator()
        # Method is _load_or_refresh_credentials
        creds = auth._load_or_refresh_credentials()

        # Should run OAuth flow
        mock_flow.from_client_secrets_file.assert_called_once()
        mock_flow_instance.run_local_server.assert_called_once()

        # Should save token
        mock_dump.assert_called_once()

    def test_token_pickle_path_computed_correctly(self, monkeypatch):
        """Test that token.pickle path is computed relative to credentials.json."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/dir/credentials.json")

        with patch("pathlib.Path.exists", return_value=True):
            auth = GmailAuthenticator()

            # token_file is a Path object
            expected_token_path = "/fake/dir/token.pickle"
            assert str(auth.token_file) == expected_token_path
