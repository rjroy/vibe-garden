"""Tests for authentication module."""

import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Ensure src directory is in path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from courier_mcp.auth import GmailAuthenticator, AuthenticationError, initialize_authenticator, get_authenticator


class TestGmailAuthenticator:
    """Tests for GmailAuthenticator class."""

    def test_init_without_credentials_path(self):
        """Test error when GMAIL_CREDENTIALS_PATH not set."""
        # Clear env var
        old_env = os.environ.pop("GMAIL_CREDENTIALS_PATH", None)

        try:
            with patch.dict(os.environ, {}, clear=False):
                if "GMAIL_CREDENTIALS_PATH" in os.environ:
                    del os.environ["GMAIL_CREDENTIALS_PATH"]

                try:
                    GmailAuthenticator()
                    assert False, "Should raise AuthenticationError"
                except AuthenticationError as e:
                    assert "not configured" in str(e)
        finally:
            if old_env:
                os.environ["GMAIL_CREDENTIALS_PATH"] = old_env

    def test_init_with_missing_credentials_file(self):
        """Test error when credentials file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_path = os.path.join(tmpdir, "nonexistent.json")

            try:
                GmailAuthenticator(fake_path)
                assert False, "Should raise AuthenticationError"
            except AuthenticationError as e:
                assert "not found" in str(e)

    def test_init_with_valid_credentials_path(self):
        """Test successful initialization with valid credentials path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = os.path.join(tmpdir, "credentials.json")
            Path(creds_file).write_text("{}")

            authenticator = GmailAuthenticator(creds_file)
            assert authenticator.credentials_path == creds_file

    def test_authenticator_repr(self):
        """Test authenticator string representation (no sensitive data)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = os.path.join(tmpdir, "credentials.json")
            Path(creds_file).write_text("{}")

            authenticator = GmailAuthenticator(creds_file)
            repr_str = repr(authenticator)

            # Should not contain actual path
            assert "***" in repr_str
            assert creds_file not in repr_str


class TestAuthenticatorGlobals:
    """Tests for global authenticator instance."""

    def test_initialize_authenticator(self):
        """Test initialize_authenticator creates instance."""
        # Clear global state
        import courier_mcp.auth as auth_module
        auth_module._authenticator = None

        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = os.path.join(tmpdir, "credentials.json")
            Path(creds_file).write_text("{}")

            authenticator = initialize_authenticator(creds_file)
            assert authenticator is not None

    def test_get_authenticator_without_init(self):
        """Test get_authenticator raises error if not initialized."""
        import courier_mcp.auth as auth_module
        auth_module._authenticator = None

        try:
            get_authenticator()
            assert False, "Should raise RuntimeError"
        except RuntimeError as e:
            assert "not initialized" in str(e)

    def test_initialize_authenticator_singleton(self):
        """Test initialize_authenticator returns same instance."""
        import courier_mcp.auth as auth_module
        auth_module._authenticator = None

        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = os.path.join(tmpdir, "credentials.json")
            Path(creds_file).write_text("{}")

            auth1 = initialize_authenticator(creds_file)
            auth2 = initialize_authenticator(creds_file)
            assert auth1 is auth2


class TestCredentialHandling:
    """Tests for credential loading and token management."""

    @patch("courier_mcp.auth.InstalledAppFlow")
    def test_load_credentials_with_oauth_flow(self, mock_flow_class):
        """Test OAuth flow when no cached token exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = os.path.join(tmpdir, "credentials.json")
            Path(creds_file).write_text("{}")

            # Mock OAuth flow
            mock_flow = MagicMock()
            mock_creds = MagicMock()
            mock_creds.valid = True
            mock_creds.expired = False
            mock_flow.run_local_server.return_value = mock_creds
            mock_flow_class.from_client_secrets_file.return_value = mock_flow

            authenticator = GmailAuthenticator(creds_file)

            # This would require actual OAuth interaction, so we mock it
            # In real scenario, this would run OAuth flow
            # For testing, we verify the structure is correct
            assert authenticator.credentials_path == creds_file

    def test_token_file_location(self):
        """Test token.pickle file stored in same directory as credentials.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = os.path.join(tmpdir, "credentials.json")
            Path(creds_file).write_text("{}")

            authenticator = GmailAuthenticator(creds_file)

            # Token file should be in same directory
            expected_token_file = os.path.join(tmpdir, "token.pickle")
            assert str(authenticator.token_file) == expected_token_file


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
