"""
Unit tests for backends.py (notification dispatchers).
"""

import json
import sys
import urllib.error
from http.client import HTTPResponse
from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from backends import send_ntfy, send_discord, send_slack, dispatch_all


class MockHTTPResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status=200, data=b""):
        self.status = status
        self.data = data

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class TestSendNtfy:
    """Test ntfy.sh dispatcher."""

    def test_send_ntfy_success(self, capsys):
        """Test successful ntfy.sh send."""
        config = {"ntfy": {"enabled": True, "priority": "high", "tags": ["test"]}}

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(200)):
            result = send_ntfy("Test message", config, "test-topic")

            assert result is True
            captured = capsys.readouterr()
            assert "✓ Sent to ntfy.sh: test-topic" in captured.err

    def test_send_ntfy_disabled(self):
        """Test ntfy.sh when disabled."""
        config = {"ntfy": {"enabled": False}}

        result = send_ntfy("Test message", config, "test-topic")
        assert result is False

    def test_send_ntfy_custom_config(self):
        """Test ntfy.sh with custom priority and tags."""
        config = {
            "ntfy": {
                "enabled": True,
                "priority": "urgent",
                "tags": ["custom", "tags"],
                "timeout": 10
            }
        }

        mock_urlopen = mock.Mock(return_value=MockHTTPResponse(200))

        with mock.patch('urllib.request.urlopen', mock_urlopen):
            with mock.patch('urllib.request.Request') as mock_request:
                send_ntfy("Test", config, "topic")

                # Verify request was created with correct headers
                call_args = mock_request.call_args
                headers = call_args.kwargs['headers']
                assert headers['Priority'] == 'urgent'
                assert headers['Tags'] == 'custom,tags'

    def test_send_ntfy_http_error(self, capsys):
        """Test ntfy.sh with HTTP error response."""
        config = {"ntfy": {"enabled": True}}

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(500)):
            result = send_ntfy("Test", config, "topic")

            assert result is False
            captured = capsys.readouterr()
            assert "✗ ntfy.sh error: HTTP 500" in captured.err

    def test_send_ntfy_network_error(self, capsys):
        """Test ntfy.sh with network error."""
        config = {"ntfy": {"enabled": True}}

        error = urllib.error.URLError("Network unreachable")
        with mock.patch('urllib.request.urlopen', side_effect=error):
            result = send_ntfy("Test", config, "topic")

            assert result is False
            captured = capsys.readouterr()
            assert "✗ ntfy.sh failed:" in captured.err

    def test_send_ntfy_timeout(self, capsys):
        """Test ntfy.sh with timeout."""
        config = {"ntfy": {"enabled": True, "timeout": 1}}

        with mock.patch('urllib.request.urlopen', side_effect=TimeoutError("Timeout")):
            result = send_ntfy("Test", config, "topic")

            assert result is False
            captured = capsys.readouterr()
            assert "✗ ntfy.sh error:" in captured.err


class TestSendDiscord:
    """Test Discord dispatcher."""

    def test_send_discord_success(self, capsys):
        """Test successful Discord send."""
        config = {
            "discord": {
                "enabled": True,
                "webhook_url": "https://discord.com/api/webhooks/test"
            }
        }

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(204)):
            result = send_discord("Test message", config)

            assert result is True
            captured = capsys.readouterr()
            assert "✓ Sent to Discord" in captured.err

    def test_send_discord_disabled(self):
        """Test Discord when disabled."""
        config = {"discord": {"enabled": False}}

        result = send_discord("Test", config)
        assert result is False

    def test_send_discord_missing_webhook(self, capsys):
        """Test Discord with missing webhook URL."""
        config = {"discord": {"enabled": True, "webhook_url": ""}}

        result = send_discord("Test", config)

        assert result is False
        captured = capsys.readouterr()
        assert "✗ Discord: Invalid or missing webhook URL" in captured.err

    def test_send_discord_invalid_webhook(self, capsys):
        """Test Discord with non-HTTPS webhook URL."""
        config = {
            "discord": {
                "enabled": True,
                "webhook_url": "http://insecure.com/webhook"
            }
        }

        result = send_discord("Test", config)

        assert result is False
        captured = capsys.readouterr()
        assert "✗ Discord: Invalid or missing webhook URL" in captured.err

    def test_send_discord_json_payload(self):
        """Test Discord sends correct JSON payload."""
        config = {
            "discord": {
                "enabled": True,
                "webhook_url": "https://discord.com/api/webhooks/test"
            }
        }

        mock_urlopen = mock.Mock(return_value=MockHTTPResponse(200))

        with mock.patch('urllib.request.urlopen', mock_urlopen):
            with mock.patch('urllib.request.Request') as mock_request:
                send_discord("Test message", config)

                # Verify JSON payload
                call_args = mock_request.call_args
                payload_bytes = call_args.kwargs['data']
                payload = json.loads(payload_bytes.decode('utf-8'))
                assert payload == {"content": "Test message"}

    def test_send_discord_http_error(self, capsys):
        """Test Discord with HTTP error."""
        config = {
            "discord": {
                "enabled": True,
                "webhook_url": "https://discord.com/api/webhooks/test"
            }
        }

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(400)):
            result = send_discord("Test", config)

            assert result is False
            captured = capsys.readouterr()
            assert "✗ Discord error: HTTP 400" in captured.err

    def test_send_discord_network_error(self, capsys):
        """Test Discord with network error."""
        config = {
            "discord": {
                "enabled": True,
                "webhook_url": "https://discord.com/api/webhooks/test"
            }
        }

        error = urllib.error.URLError("Connection refused")
        with mock.patch('urllib.request.urlopen', side_effect=error):
            result = send_discord("Test", config)

            assert result is False
            captured = capsys.readouterr()
            assert "✗ Discord failed:" in captured.err


class TestSendSlack:
    """Test Slack dispatcher."""

    def test_send_slack_success(self, capsys):
        """Test successful Slack send."""
        config = {
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/test"
            }
        }

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(200)):
            result = send_slack("Test message", config)

            assert result is True
            captured = capsys.readouterr()
            assert "✓ Sent to Slack" in captured.err

    def test_send_slack_disabled(self):
        """Test Slack when disabled."""
        config = {"slack": {"enabled": False}}

        result = send_slack("Test", config)
        assert result is False

    def test_send_slack_missing_webhook(self, capsys):
        """Test Slack with missing webhook URL."""
        config = {"slack": {"enabled": True, "webhook_url": ""}}

        result = send_slack("Test", config)

        assert result is False
        captured = capsys.readouterr()
        assert "✗ Slack: Invalid or missing webhook URL" in captured.err

    def test_send_slack_invalid_webhook(self, capsys):
        """Test Slack with non-HTTPS webhook URL."""
        config = {
            "slack": {
                "enabled": True,
                "webhook_url": "http://insecure.com/webhook"
            }
        }

        result = send_slack("Test", config)

        assert result is False
        captured = capsys.readouterr()
        assert "✗ Slack: Invalid or missing webhook URL" in captured.err

    def test_send_slack_json_payload(self):
        """Test Slack sends correct JSON payload."""
        config = {
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/test"
            }
        }

        mock_urlopen = mock.Mock(return_value=MockHTTPResponse(200))

        with mock.patch('urllib.request.urlopen', mock_urlopen):
            with mock.patch('urllib.request.Request') as mock_request:
                send_slack("Test message", config)

                # Verify JSON payload
                call_args = mock_request.call_args
                payload_bytes = call_args.kwargs['data']
                payload = json.loads(payload_bytes.decode('utf-8'))
                assert payload == {"text": "Test message"}

    def test_send_slack_http_error(self, capsys):
        """Test Slack with HTTP error."""
        config = {
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/test"
            }
        }

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(500)):
            result = send_slack("Test", config)

            assert result is False
            captured = capsys.readouterr()
            assert "✗ Slack error: HTTP 500" in captured.err

    def test_send_slack_network_error(self, capsys):
        """Test Slack with network error."""
        config = {
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/test"
            }
        }

        error = urllib.error.URLError("DNS lookup failed")
        with mock.patch('urllib.request.urlopen', side_effect=error):
            result = send_slack("Test", config)

            assert result is False
            captured = capsys.readouterr()
            assert "✗ Slack failed:" in captured.err


class TestDispatchAll:
    """Test dispatch orchestration."""

    def test_dispatch_all_backends(self):
        """Test dispatching to all backends."""
        config = {
            "ntfy": {"enabled": True},
            "discord": {"enabled": True, "webhook_url": "https://discord.com/webhook"},
            "slack": {"enabled": True, "webhook_url": "https://slack.com/webhook"}
        }

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(200)):
            results = dispatch_all("Test", config, "test-topic")

            assert "ntfy" in results
            assert "discord" in results
            assert "slack" in results

    def test_dispatch_error_isolation(self):
        """Test that one backend failure doesn't prevent others from sending."""
        config = {
            "ntfy": {"enabled": True},
            "discord": {"enabled": True, "webhook_url": "https://discord.com/webhook"},
            "slack": {"enabled": True, "webhook_url": "https://slack.com/webhook"}
        }

        # Make ntfy fail, but Discord and Slack succeed
        def mock_urlopen_selective(req, timeout=None):
            url = req.full_url if hasattr(req, 'full_url') else req.get_full_url()
            if "ntfy.sh" in url:
                raise urllib.error.URLError("ntfy failed")
            return MockHTTPResponse(200)

        with mock.patch('urllib.request.urlopen', side_effect=mock_urlopen_selective):
            results = dispatch_all("Test", config, "topic")

            # ntfy failed
            assert results.get("ntfy") is False

            # But Discord and Slack should still succeed
            assert results.get("discord") is True
            assert results.get("slack") is True

    def test_dispatch_only_enabled_backends(self):
        """Test that only enabled backends are dispatched to."""
        config = {
            "ntfy": {"enabled": False},
            "discord": {"enabled": True, "webhook_url": "https://discord.com/webhook"},
            "slack": {"enabled": False}
        }

        with mock.patch('urllib.request.urlopen', return_value=MockHTTPResponse(200)):
            results = dispatch_all("Test", config, "topic")

            # ntfy disabled - returns False
            assert results.get("ntfy") is False

            # Discord enabled
            assert results.get("discord") is True

            # Slack disabled
            assert results.get("slack") is False
