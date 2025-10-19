"""
Unit tests for authentication module (auth.py).

Tests credential loading, token refresh, and Gmail service building.
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import os
import pickle

from courier_mcp.auth import GmailAuthenticator
from courier_mcp.errors import AuthenticationError


@pytest.mark.unit
class TestGmailAuthenticator:
    """Test suite for GmailAuthenticator class."""

    def test_init_missing_credentials_path(self, monkeypatch):
        """Test initialization fails when GMAIL_CREDENTIALS_PATH not set."""
        monkeypatch.delenv("GMAIL_CREDENTIALS_PATH", raising=False)

        with pytest.raises(AuthenticationError, match="GMAIL_CREDENTIALS_PATH"):
            GmailAuthenticator()

    def test_init_credentials_file_not_found(self, monkeypatch):
        """Test initialization fails when credentials file doesn't exist."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/nonexistent/credentials.json")

        with pytest.raises(AuthenticationError, match="not found"):
            GmailAuthenticator()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"installed": {}}')
    @patch("courier_mcp.auth.InstalledAppFlow")
    def test_init_success_with_valid_credentials(self, mock_flow, mock_file, mock_exists, monkeypatch):
        """Test successful initialization with valid credentials."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")
        mock_exists.return_value = True

        auth = GmailAuthenticator()

        assert auth.credentials_path == "/fake/credentials.json"
        mock_exists.assert_called()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("courier_mcp.auth.InstalledAppFlow")
    def test_load_cached_token(self, mock_flow, mock_pickle, mock_file, mock_exists, monkeypatch, mock_credentials):
        """Test loading cached token from token.pickle."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")

        # Credentials file exists
        def exists_side_effect(path):
            if "credentials.json" in path:
                return True
            if "token.pickle" in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect
        mock_pickle.return_value = mock_credentials

        auth = GmailAuthenticator()
        creds = auth._load_credentials()

        assert creds is not None
        assert creds.valid
        mock_pickle.assert_called_once()

    @patch("os.path.exists")
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
                    creds = auth._load_credentials()

                    # Should attempt refresh
                    mock_refresh.assert_called_once()

    @patch("os.path.exists")
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

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"installed": {}}')
    @patch("courier_mcp.auth.InstalledAppFlow")
    def test_authentication_error_on_invalid_credentials(self, mock_flow, mock_file, mock_exists, monkeypatch):
        """Test authentication error when credentials are invalid."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")
        mock_exists.return_value = True

        # Simulate invalid credentials (no refresh token)
        mock_credentials = MagicMock()
        mock_credentials.valid = False
        mock_credentials.expired = True
        mock_credentials.refresh_token = None

        with patch("pickle.load", return_value=mock_credentials):
            with pytest.raises(AuthenticationError):
                auth = GmailAuthenticator()
                auth._load_credentials()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"installed": {"client_id": "test", "client_secret": "secret"}}')
    @patch("courier_mcp.auth.InstalledAppFlow")
    @patch("pickle.dump")
    def test_new_token_generation_when_no_cache(self, mock_dump, mock_flow, mock_file, mock_exists, monkeypatch, mock_credentials):
        """Test generating new token when token.pickle doesn't exist."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/credentials.json")

        # Credentials file exists, but token.pickle doesn't
        def exists_side_effect(path):
            if "credentials.json" in path:
                return True
            if "token.pickle" in path:
                return False
            return False

        mock_exists.side_effect = exists_side_effect

        # Mock the flow
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_credentials
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        auth = GmailAuthenticator()
        creds = auth._load_credentials()

        # Should run OAuth flow
        mock_flow.from_client_secrets_file.assert_called_once()
        mock_flow_instance.run_local_server.assert_called_once()

        # Should save token
        mock_dump.assert_called_once()

    def test_token_pickle_path_computed_correctly(self, monkeypatch):
        """Test that token.pickle path is computed relative to credentials.json."""
        monkeypatch.setenv("GMAIL_CREDENTIALS_PATH", "/fake/dir/credentials.json")

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data='{"installed": {}}')):
                with patch("courier_mcp.auth.InstalledAppFlow"):
                    auth = GmailAuthenticator()

                    expected_token_path = "/fake/dir/token.pickle"
                    assert auth.token_path == expected_token_path
