"""
Integration tests for notify.py (main hook script).
Tests the full pipeline: stdin → filter → sanitize → rate limit → dispatch.
"""

import io
import json
import sys
from pathlib import Path
from unittest import mock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import notify
from lib import _rate_limit_state


class TestMain:
    """Test main notification pipeline."""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        """Clear rate limit state before and after each test."""
        _rate_limit_state.clear()
        yield
        _rate_limit_state.clear()

    def test_full_pipeline_success(self, capsys):
        """Test successful end-to-end notification."""
        hook_input = {"message": "Task complete"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                with mock.patch('notify.is_rate_limited', return_value=False):  # Not rate limited
                    with mock.patch('notify.dispatch_all') as mock_dispatch:
                        with mock.patch('notify.generate_topic', return_value='test-topic'):
                            # Setup mock config
                            from lib import Config, DEFAULT_CONFIG
                            mock_config.return_value = Config.from_dict(DEFAULT_CONFIG)
                            mock_dispatch.return_value = {"ntfy": True}

                            # Run
                            with pytest.raises(SystemExit) as exc_info:
                                notify.main()

                            # Should exit 0
                            assert exc_info.value.code == 0

                            # Should have dispatched
                            mock_dispatch.assert_called_once()

    def test_invalid_json_input(self, capsys):
        """Test handling of invalid JSON input."""
        stdin_mock = io.StringIO("not valid json")

        with mock.patch('sys.stdin', stdin_mock):
            with pytest.raises(SystemExit) as exc_info:
                notify.main()

            # Should exit gracefully
            assert exc_info.value.code == 0

            # Should log warning
            captured = capsys.readouterr()
            assert "Invalid JSON input" in captured.err

    def test_empty_message(self, capsys):
        """Test handling of empty message."""
        hook_input = {"message": ""}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with pytest.raises(SystemExit) as exc_info:
                notify.main()

            # Should exit gracefully
            assert exc_info.value.code == 0

            # Should log warning
            captured = capsys.readouterr()
            assert "No message" in captured.err

    def test_filtered_message(self, capsys):
        """Test message filtering."""
        hook_input = {"message": "Debug: some debug message"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                # Setup config with Debug filter
                from lib import Config
                config_data = {
                    "backends": {"ntfy": {"enabled": True}},
                    "filtering": {"exclude_patterns": ["^Debug:"], "include_patterns": []},
                    "privacy": {"max_message_length": 100, "strip_paths": True, "strip_code": True},
                    "rate_limiting": {"enabled": True, "max_per_minute": 1}
                }
                mock_config.return_value = Config.from_dict(config_data)

                with pytest.raises(SystemExit) as exc_info:
                    notify.main()

                # Should exit gracefully
                assert exc_info.value.code == 0

                # Should log that message was filtered
                captured = capsys.readouterr()
                assert "Filtered out" in captured.err

    def test_message_sanitization(self):
        """Test message sanitization."""
        hook_input = {"message": "Error in /home/user/project/file.py with `code` snippet"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                with mock.patch('notify.is_rate_limited', return_value=False):  # Not rate limited
                    with mock.patch('notify.dispatch_all') as mock_dispatch:
                        with mock.patch('notify.generate_topic', return_value='test-topic'):
                            from lib import Config, DEFAULT_CONFIG
                            mock_config.return_value = Config.from_dict(DEFAULT_CONFIG)
                            mock_dispatch.return_value = {"ntfy": True}

                            with pytest.raises(SystemExit):
                                notify.main()

                            # Check that dispatch was called with sanitized message
                            call_args = mock_dispatch.call_args
                            sanitized_message = call_args[0][0]

                            # Should not contain file path or code
                            assert "/home/user/project/file.py" not in sanitized_message
                            assert "`code`" not in sanitized_message

    def test_rate_limiting(self, capsys):
        """Test rate limiting prevents repeated notifications."""
        hook_input = {"message": "Test message"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                with mock.patch('notify.is_rate_limited') as mock_rate_limit:
                    with mock.patch('notify.generate_topic', return_value='test-topic'):
                        from lib import Config, DEFAULT_CONFIG
                        mock_config.return_value = Config.from_dict(DEFAULT_CONFIG)

                        # Simulate rate limiting
                        mock_rate_limit.return_value = True

                        with pytest.raises(SystemExit) as exc_info:
                            notify.main()

                        # Should exit gracefully
                        assert exc_info.value.code == 0

                        # Should log rate limit
                        captured = capsys.readouterr()
                        assert "Rate limited" in captured.err or "No backends available" in captured.err

    def test_all_backends_disabled(self, capsys):
        """Test behavior when all backends disabled."""
        hook_input = {"message": "Test message"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                # All backends disabled
                from lib import Config
                config_data = {
                    "backends": {
                        "ntfy": {"enabled": False},
                        "discord": {"enabled": False},
                        "slack": {"enabled": False}
                    },
                    "filtering": {"exclude_patterns": [], "include_patterns": []},
                    "privacy": {"max_message_length": 100, "strip_paths": True, "strip_code": True},
                    "rate_limiting": {"enabled": True, "max_per_minute": 1}
                }
                mock_config.return_value = Config.from_dict(config_data)

                with pytest.raises(SystemExit) as exc_info:
                    notify.main()

                # Should exit gracefully
                assert exc_info.value.code == 0

                # Should log that backends are disabled
                captured = capsys.readouterr()
                assert "disabled" in captured.err.lower()

    def test_config_load_failure_uses_defaults(self, capsys):
        """Test that config load failure falls back to defaults."""
        hook_input = {"message": "Test message"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config', side_effect=Exception("Config error")):
                with mock.patch('notify.is_rate_limited', return_value=False):  # Not rate limited
                    with mock.patch('notify.dispatch_all') as mock_dispatch:
                        with mock.patch('notify.generate_topic', return_value='test-topic'):
                            mock_dispatch.return_value = {"ntfy": True}

                            with pytest.raises(SystemExit) as exc_info:
                                notify.main()

                            # Should exit gracefully
                            assert exc_info.value.code == 0

                            # Should log warning about config failure
                            captured = capsys.readouterr()
                            assert "Failed to load config" in captured.err

                            # Should still dispatch (using defaults)
                            assert mock_dispatch.called

    def test_topic_generation_failure_uses_fallback(self, capsys):
        """Test that topic generation failure uses fallback topic."""
        hook_input = {"message": "Test message"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                with mock.patch('notify.is_rate_limited', return_value=False):  # Not rate limited
                    with mock.patch('notify.generate_topic', side_effect=Exception("Git error")):
                        with mock.patch('notify.dispatch_all') as mock_dispatch:
                            from lib import Config, DEFAULT_CONFIG
                            mock_config.return_value = Config.from_dict(DEFAULT_CONFIG)
                            mock_dispatch.return_value = {"ntfy": True}

                            with pytest.raises(SystemExit) as exc_info:
                                notify.main()

                            # Should exit gracefully
                            assert exc_info.value.code == 0

                            # Should use fallback topic
                            call_args = mock_dispatch.call_args
                            topic = call_args[0][2]
                            assert topic == "claude-unknown-unknown"

    def test_dispatch_failure_exits_gracefully(self, capsys):
        """Test that dispatch failure doesn't block Claude."""
        hook_input = {"message": "Test message"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                with mock.patch('notify.is_rate_limited', return_value=False):  # Not rate limited
                    with mock.patch('notify.dispatch_all', side_effect=Exception("Dispatch error")):
                        with mock.patch('notify.generate_topic', return_value='test-topic'):
                            from lib import Config, DEFAULT_CONFIG
                            mock_config.return_value = Config.from_dict(DEFAULT_CONFIG)

                            with pytest.raises(SystemExit) as exc_info:
                                notify.main()

                            # Should exit gracefully (code 0)
                            assert exc_info.value.code == 0

                            # Should log warning
                            captured = capsys.readouterr()
                            assert "Dispatch failed" in captured.err

    def test_unexpected_exception_exits_gracefully(self, capsys):
        """Test that unexpected exceptions don't block Claude."""
        hook_input = {"message": "Test message"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config', side_effect=RuntimeError("Unexpected error")):
                with pytest.raises(SystemExit) as exc_info:
                    notify.main()

                # Should ALWAYS exit 0
                assert exc_info.value.code == 0

                # Should log error
                captured = capsys.readouterr()
                assert "Error in notify hook" in captured.err or "Failed to load config" in captured.err

    def test_successful_dispatch_logs_summary(self, capsys):
        """Test that successful dispatch logs summary."""
        hook_input = {"message": "Task complete"}
        stdin_mock = io.StringIO(json.dumps(hook_input))

        with mock.patch('sys.stdin', stdin_mock):
            with mock.patch('notify.load_config') as mock_config:
                with mock.patch('notify.is_rate_limited', return_value=False):  # Not rate limited
                    with mock.patch('notify.dispatch_all') as mock_dispatch:
                        with mock.patch('notify.generate_topic', return_value='test-topic'):
                            from lib import Config, DEFAULT_CONFIG
                            mock_config.return_value = Config.from_dict(DEFAULT_CONFIG)
                            mock_dispatch.return_value = {"ntfy": True, "discord": False, "slack": True}

                            with pytest.raises(SystemExit):
                                notify.main()

                            # Should log summary
                            captured = capsys.readouterr()
                            assert "Dispatched" in captured.err
                            # 2 successful out of attempted backends
                            assert "2/" in captured.err or "backends" in captured.err
