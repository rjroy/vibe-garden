"""Unit tests for gh_project.py config loading, CLI structure, and subprocess wrapper.

Tests cover:
- Valid configuration loading
- Missing configuration file
- Malformed JSON
- Missing required fields (owner, owner_type, number)
- Invalid owner_type values
- Invalid project number values
- CLI argument parsing
- Subprocess execution with retry logic
- Error code taxonomy (AUTH_REQUIRED, AUTH_SCOPE_MISSING, RATE_LIMITED, API_ERROR)
- Retryable vs non-retryable error detection
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

# Add the scripts directory to the path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from gh_project import (  # noqa: E402
    API_ERROR,
    AUTH_REQUIRED,
    AUTH_SCOPE_MISSING,
    CONFIG_INVALID,
    CONFIG_MISSING,
    RATE_LIMITED,
    ExecutionResult,
    GhError,
    ProjectConfig,
    _execute_with_retry,
    _extract_retry_after,
    _is_retryable_error,
    _parse_gh_error,
    create_parser,
    load_config,
)


class TestConfigLoading:
    """Tests for the load_config function."""

    def test_valid_config_user(self, tmp_path: Path) -> None:
        """Test loading a valid configuration with user owner_type."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                        "number": 8,
                    }
                }
            )
        )

        config = load_config(str(config_file))

        assert isinstance(config, ProjectConfig)
        assert config.owner == "rjroy"
        assert config.owner_type == "user"
        assert config.number == 8

    def test_valid_config_organization(self, tmp_path: Path) -> None:
        """Test loading a valid configuration with organization owner_type."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "anthropic",
                        "owner_type": "organization",
                        "number": 42,
                    }
                }
            )
        )

        config = load_config(str(config_file))

        assert config.owner == "anthropic"
        assert config.owner_type == "organization"
        assert config.number == 42

    def test_config_with_extra_fields(self, tmp_path: Path) -> None:
        """Test that extra fields in config are ignored."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                        "number": 8,
                    },
                    "preferences": {
                        "promptForLargeItems": True,
                    },
                }
            )
        )

        config = load_config(str(config_file))

        assert config.owner == "rjroy"
        assert config.owner_type == "user"
        assert config.number == 8

    def test_config_number_as_string(self, tmp_path: Path) -> None:
        """Test that number field as string is converted to int."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                        "number": "8",
                    }
                }
            )
        )

        config = load_config(str(config_file))

        assert config.number == 8
        assert isinstance(config.number, int)


class TestConfigMissing:
    """Tests for CONFIG_MISSING error scenarios."""

    def test_missing_config_file(self, tmp_path: Path) -> None:
        """Test error when config file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(SystemExit) as exc_info:
            with mock.patch("sys.stdout"):
                load_config(str(nonexistent))

        assert exc_info.value.code == 1

    def test_missing_config_file_output(self, tmp_path: Path, capsys) -> None:
        """Test that CONFIG_MISSING error includes proper output."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(SystemExit):
            load_config(str(nonexistent))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_MISSING
        assert "Configuration file not found" in output["error"]["message"]
        assert "config.json" in output["error"]["details"]


class TestConfigInvalid:
    """Tests for CONFIG_INVALID error scenarios."""

    def test_malformed_json(self, tmp_path: Path, capsys) -> None:
        """Test error when config file contains invalid JSON."""
        config_file = tmp_path / "config.json"
        config_file.write_text("{ not valid json }")

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "not valid JSON" in output["error"]["message"]

    def test_missing_project_section(self, tmp_path: Path, capsys) -> None:
        """Test error when 'project' section is missing."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"preferences": {}}))

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "project" in output["error"]["message"]

    def test_missing_owner_field(self, tmp_path: Path, capsys) -> None:
        """Test error when 'owner' field is missing."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner_type": "user",
                        "number": 8,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "owner" in output["error"]["message"]

    def test_missing_owner_type_field(self, tmp_path: Path, capsys) -> None:
        """Test error when 'owner_type' field is missing."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "number": 8,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "owner_type" in output["error"]["message"]

    def test_missing_number_field(self, tmp_path: Path, capsys) -> None:
        """Test error when 'number' field is missing."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "number" in output["error"]["message"]

    def test_missing_multiple_fields(self, tmp_path: Path, capsys) -> None:
        """Test error when multiple required fields are missing."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"project": {}}))

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        # All three fields should be mentioned
        assert "owner" in output["error"]["message"]
        assert "owner_type" in output["error"]["message"]
        assert "number" in output["error"]["message"]


class TestInvalidOwnerType:
    """Tests for invalid owner_type values."""

    def test_invalid_owner_type_team(self, tmp_path: Path, capsys) -> None:
        """Test error when owner_type is 'team' (invalid)."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "team",
                        "number": 8,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "team" in output["error"]["message"]
        assert "user" in output["error"]["details"]
        assert "organization" in output["error"]["details"]

    def test_invalid_owner_type_org(self, tmp_path: Path, capsys) -> None:
        """Test error when owner_type is 'org' (must be 'organization')."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "anthropic",
                        "owner_type": "org",
                        "number": 42,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "org" in output["error"]["message"]

    def test_invalid_owner_type_empty(self, tmp_path: Path, capsys) -> None:
        """Test error when owner_type is empty string."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "",
                        "number": 8,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID

    def test_invalid_owner_type_case_sensitive(self, tmp_path: Path, capsys) -> None:
        """Test that owner_type is case-sensitive ('User' is invalid)."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "User",
                        "number": 8,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID


class TestInvalidProjectNumber:
    """Tests for invalid project number values."""

    def test_invalid_number_string(self, tmp_path: Path, capsys) -> None:
        """Test error when number is a non-numeric string."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                        "number": "not-a-number",
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "number" in output["error"]["message"].lower()

    def test_invalid_number_zero(self, tmp_path: Path, capsys) -> None:
        """Test error when number is zero."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                        "number": 0,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID

    def test_invalid_number_negative(self, tmp_path: Path, capsys) -> None:
        """Test error when number is negative."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                        "number": -5,
                    }
                }
            )
        )

        with pytest.raises(SystemExit):
            load_config(str(config_file))

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID


class TestCLIParser:
    """Tests for the argparse CLI structure."""

    def test_parser_creation(self) -> None:
        """Test that the parser is created successfully."""
        parser = create_parser()
        assert parser is not None

    def test_list_issues_subcommand(self) -> None:
        """Test parsing list-issues subcommand."""
        parser = create_parser()
        args = parser.parse_args(["list-issues"])

        assert args.operation == "list-issues"
        assert hasattr(args, "func")

    def test_get_issue_subcommand(self) -> None:
        """Test parsing get-issue subcommand with number."""
        parser = create_parser()
        args = parser.parse_args(["get-issue", "42"])

        assert args.operation == "get-issue"
        assert args.number == 42

    def test_set_status_subcommand(self) -> None:
        """Test parsing set-status subcommand with number and status."""
        parser = create_parser()
        args = parser.parse_args(["set-status", "42", "In Progress"])

        assert args.operation == "set-status"
        assert args.number == 42
        assert args.status == "In Progress"

    def test_add_to_project_subcommand(self) -> None:
        """Test parsing add-to-project subcommand with number."""
        parser = create_parser()
        args = parser.parse_args(["add-to-project", "42"])

        assert args.operation == "add-to-project"
        assert args.number == 42

    def test_config_flag(self) -> None:
        """Test that --config flag is parsed correctly."""
        parser = create_parser()
        args = parser.parse_args(["--config", "/custom/path.json", "list-issues"])

        assert args.config == "/custom/path.json"

    def test_config_short_flag(self) -> None:
        """Test that -c short flag works for config."""
        parser = create_parser()
        args = parser.parse_args(["-c", "/custom/path.json", "list-issues"])

        assert args.config == "/custom/path.json"

    def test_missing_operation(self) -> None:
        """Test that missing operation causes error."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_get_issue_missing_number(self) -> None:
        """Test that get-issue without number causes error."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["get-issue"])

    def test_set_status_missing_status(self) -> None:
        """Test that set-status without status causes error."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["set-status", "42"])


class TestCLIIntegration:
    """Integration tests for CLI invocation."""

    def test_cli_list_issues_with_valid_config(self, tmp_path: Path) -> None:
        """Test CLI invocation with valid config returns success."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "user",
                        "number": 8,
                    }
                }
            )
        )

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "gh_project.py"),
                "--config",
                str(config_file),
                "list-issues",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["success"] is True

    def test_cli_missing_config(self, tmp_path: Path) -> None:
        """Test CLI invocation with missing config returns error."""
        nonexistent = tmp_path / "nonexistent.json"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "gh_project.py"),
                "--config",
                str(nonexistent),
                "list-issues",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_MISSING

    def test_cli_invalid_owner_type(self, tmp_path: Path) -> None:
        """Test CLI invocation with invalid owner_type returns error."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "project": {
                        "owner": "rjroy",
                        "owner_type": "invalid",
                        "number": 8,
                    }
                }
            )
        )

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "gh_project.py"),
                "--config",
                str(config_file),
                "list-issues",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID


class TestIsRetryableError:
    """Tests for _is_retryable_error function."""

    def test_502_is_retryable(self) -> None:
        """Test that HTTP 502 errors are retryable."""
        assert _is_retryable_error("HTTP 502 Bad Gateway") is True
        assert _is_retryable_error("error: 502") is True

    def test_503_is_retryable(self) -> None:
        """Test that HTTP 503 errors are retryable."""
        assert _is_retryable_error("HTTP 503 Service Unavailable") is True
        assert _is_retryable_error("error: 503") is True

    def test_bad_gateway_is_retryable(self) -> None:
        """Test that 'Bad Gateway' text is retryable."""
        assert _is_retryable_error("Server returned Bad Gateway") is True

    def test_service_unavailable_is_retryable(self) -> None:
        """Test that 'Service Unavailable' text is retryable."""
        assert _is_retryable_error("Service Unavailable") is True

    def test_connection_reset_is_retryable(self) -> None:
        """Test that connection reset errors are retryable."""
        assert _is_retryable_error("connection reset by peer") is True

    def test_connection_refused_is_retryable(self) -> None:
        """Test that connection refused errors are retryable."""
        assert _is_retryable_error("connection refused") is True

    def test_network_unreachable_is_retryable(self) -> None:
        """Test that network unreachable errors are retryable."""
        assert _is_retryable_error("network is unreachable") is True

    def test_404_is_not_retryable(self) -> None:
        """Test that HTTP 404 errors are NOT retryable."""
        assert _is_retryable_error("HTTP 404 Not Found") is False
        assert _is_retryable_error("error: 404") is False
        assert _is_retryable_error("not found") is False

    def test_401_is_not_retryable(self) -> None:
        """Test that HTTP 401 errors are NOT retryable."""
        assert _is_retryable_error("HTTP 401 Unauthorized") is False
        assert _is_retryable_error("error: 401") is False

    def test_400_is_not_retryable(self) -> None:
        """Test that HTTP 400 errors are NOT retryable."""
        assert _is_retryable_error("HTTP 400 Bad Request") is False
        assert _is_retryable_error("error: 400") is False
        assert _is_retryable_error("bad request") is False

    def test_429_is_not_retryable(self) -> None:
        """Test that HTTP 429 rate limit errors are NOT retryable (handled specially)."""
        assert _is_retryable_error("HTTP 429 Too Many Requests") is False
        assert _is_retryable_error("rate limit exceeded") is False

    def test_auth_errors_not_retryable(self) -> None:
        """Test that authentication errors are NOT retryable."""
        assert _is_retryable_error("To authenticate, run: gh auth login") is False
        assert _is_retryable_error("not logged in") is False

    def test_scope_errors_not_retryable(self) -> None:
        """Test that scope errors are NOT retryable."""
        assert _is_retryable_error("missing project scope") is False
        assert _is_retryable_error("insufficient permissions") is False

    def test_unknown_error_not_retryable(self) -> None:
        """Test that unknown errors are NOT retryable by default."""
        assert _is_retryable_error("some random error message") is False
        assert _is_retryable_error("") is False


class TestExtractRetryAfter:
    """Tests for _extract_retry_after function."""

    def test_retry_after_header_format(self) -> None:
        """Test extracting retry-after from header format."""
        assert _extract_retry_after("Retry-After: 60") == 60
        assert _extract_retry_after("retry-after: 120") == 120

    def test_retry_after_in_message(self) -> None:
        """Test extracting retry-after from message text."""
        assert _extract_retry_after("Please retry after 30 seconds") == 30
        assert _extract_retry_after("retry after 45") == 45

    def test_wait_seconds_format(self) -> None:
        """Test extracting from 'wait X seconds' format."""
        assert _extract_retry_after("Please wait 90 seconds before trying again") == 90

    def test_try_again_format(self) -> None:
        """Test extracting from 'try again in X' format."""
        assert _extract_retry_after("try again in 120 seconds") == 120

    def test_no_retry_after(self) -> None:
        """Test that None is returned when no retry-after found."""
        assert _extract_retry_after("Rate limit exceeded") is None
        assert _extract_retry_after("Too many requests") is None
        assert _extract_retry_after("") is None


class TestParseGhError:
    """Tests for _parse_gh_error function."""

    def test_auth_required_gh_auth_login(self) -> None:
        """Test AUTH_REQUIRED detection from 'gh auth login' message."""
        error = _parse_gh_error("To authenticate, run: gh auth login", 1)
        assert error.code == AUTH_REQUIRED
        assert "gh auth login" in error.details

    def test_auth_required_not_logged_in(self) -> None:
        """Test AUTH_REQUIRED detection from 'not logged in' message."""
        error = _parse_gh_error("error: not logged in", 1)
        assert error.code == AUTH_REQUIRED

    def test_auth_required_401(self) -> None:
        """Test AUTH_REQUIRED detection from HTTP 401."""
        error = _parse_gh_error("HTTP 401 Unauthorized", 1)
        assert error.code == AUTH_REQUIRED

    def test_auth_scope_missing_project_scope(self) -> None:
        """Test AUTH_SCOPE_MISSING detection from project scope message."""
        error = _parse_gh_error("missing project scope for this operation", 1)
        assert error.code == AUTH_SCOPE_MISSING
        assert "gh auth refresh -s project" in error.details

    def test_auth_scope_missing_insufficient_permissions(self) -> None:
        """Test AUTH_SCOPE_MISSING detection from permissions message."""
        error = _parse_gh_error("insufficient permissions for projects", 1)
        assert error.code == AUTH_SCOPE_MISSING

    def test_rate_limited_429(self) -> None:
        """Test RATE_LIMITED detection from HTTP 429."""
        error = _parse_gh_error("HTTP 429 Too Many Requests", 1)
        assert error.code == RATE_LIMITED

    def test_rate_limited_with_retry_after(self) -> None:
        """Test RATE_LIMITED includes retry_after when available."""
        error = _parse_gh_error("rate limit exceeded, retry after 60 seconds", 1)
        assert error.code == RATE_LIMITED
        assert error.retry_after == 60
        assert "60" in error.details

    def test_rate_limited_without_retry_after(self) -> None:
        """Test RATE_LIMITED without retry_after has helpful message."""
        error = _parse_gh_error("API rate limit exceeded", 1)
        assert error.code == RATE_LIMITED
        assert error.retry_after is None
        assert "rate_limit" in error.details

    def test_api_error_fallback(self) -> None:
        """Test API_ERROR as fallback for unrecognized errors."""
        error = _parse_gh_error("Some random API error occurred", 1)
        assert error.code == API_ERROR
        assert "Some random API error occurred" in error.details

    def test_api_error_empty_stderr(self) -> None:
        """Test API_ERROR with empty stderr includes exit code."""
        error = _parse_gh_error("", 42)
        assert error.code == API_ERROR
        assert "42" in error.details

    def test_api_error_whitespace_stderr(self) -> None:
        """Test API_ERROR with whitespace-only stderr."""
        error = _parse_gh_error("   \n  ", 1)
        assert error.code == API_ERROR
        assert "exit code 1" in error.details


class TestExecuteWithRetry:
    """Tests for _execute_with_retry function with mocked subprocess."""

    def test_success_first_attempt(self) -> None:
        """Test successful execution on first attempt."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"data": "success"}'
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            result = _execute_with_retry(["gh", "api", "test"])

            assert result.success is True
            assert result.stdout == '{"data": "success"}'
            assert result.attempts == 1
            assert mock_run.call_count == 1

    def test_retryable_error_then_success(self) -> None:
        """Test retry on transient error followed by success."""
        fail_result = mock.Mock()
        fail_result.returncode = 1
        fail_result.stdout = ""
        fail_result.stderr = "HTTP 502 Bad Gateway"

        success_result = mock.Mock()
        success_result.returncode = 0
        success_result.stdout = '{"data": "success"}'
        success_result.stderr = ""

        with mock.patch("subprocess.run", side_effect=[fail_result, success_result]):
            with mock.patch("time.sleep"):
                result = _execute_with_retry(["gh", "api", "test"])

                assert result.success is True
                assert result.attempts == 2

    def test_non_retryable_error_no_retry(self) -> None:
        """Test that non-retryable errors don't trigger retry."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "HTTP 404 Not Found"

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            result = _execute_with_retry(["gh", "api", "test"])

            assert result.success is False
            assert result.attempts == 1
            assert result.error is not None
            assert mock_run.call_count == 1

    def test_auth_error_no_retry(self) -> None:
        """Test that auth errors don't trigger retry."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "To authenticate, run: gh auth login"

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            result = _execute_with_retry(["gh", "api", "test"])

            assert result.success is False
            assert result.error.code == AUTH_REQUIRED
            assert mock_run.call_count == 1

    def test_rate_limit_no_retry(self) -> None:
        """Test that rate limit errors don't trigger automatic retry."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "API rate limit exceeded, retry after 60 seconds"

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            result = _execute_with_retry(["gh", "api", "test"])

            assert result.success is False
            assert result.error.code == RATE_LIMITED
            assert result.error.retry_after == 60
            assert mock_run.call_count == 1

    def test_max_retries_exhausted(self) -> None:
        """Test that all retries are exhausted on persistent retryable error."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "HTTP 502 Bad Gateway"

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            with mock.patch("time.sleep") as mock_sleep:
                result = _execute_with_retry(["gh", "api", "test"], max_attempts=3)

                assert result.success is False
                assert result.attempts == 3
                assert mock_run.call_count == 3
                # Should have slept twice (after attempt 1 and 2)
                assert mock_sleep.call_count == 2

    def test_exponential_backoff_delays(self) -> None:
        """Test that exponential backoff uses correct delays."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "HTTP 503 Service Unavailable"

        with mock.patch("subprocess.run", return_value=mock_result):
            with mock.patch("time.sleep") as mock_sleep:
                _execute_with_retry(["gh", "api", "test"], max_attempts=3)

                # Verify delays: 1s after first failure, 2s after second
                mock_sleep.assert_any_call(1)
                mock_sleep.assert_any_call(2)

    def test_timeout_is_retryable(self) -> None:
        """Test that subprocess timeout triggers retry."""
        with mock.patch(
            "subprocess.run",
            side_effect=[
                subprocess.TimeoutExpired(cmd="gh", timeout=30),
                mock.Mock(returncode=0, stdout='{"data": "success"}', stderr=""),
            ],
        ):
            with mock.patch("time.sleep"):
                result = _execute_with_retry(["gh", "api", "test"])

                assert result.success is True
                assert result.attempts == 2

    def test_all_timeouts_fail(self) -> None:
        """Test that persistent timeouts exhaust retries."""
        with mock.patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="gh", timeout=30),
        ):
            with mock.patch("time.sleep"):
                result = _execute_with_retry(["gh", "api", "test"], max_attempts=3)

                assert result.success is False
                assert result.attempts == 3
                assert result.error is not None

    def test_timeout_parameter_passed(self) -> None:
        """Test that timeout parameter is passed to subprocess.run."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"data": "success"}'
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            _execute_with_retry(["gh", "api", "test"], timeout=45)

            mock_run.assert_called_once()
            _, kwargs = mock_run.call_args
            assert kwargs["timeout"] == 45

    def test_custom_max_attempts(self) -> None:
        """Test custom max_attempts parameter."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "HTTP 502 Bad Gateway"

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            with mock.patch("time.sleep"):
                result = _execute_with_retry(["gh", "api", "test"], max_attempts=5)

                assert result.attempts == 5
                assert mock_run.call_count == 5


class TestGhErrorDataclass:
    """Tests for the GhError dataclass structure."""

    def test_gh_error_basic_fields(self) -> None:
        """Test GhError has correct basic fields."""
        error = GhError(
            code="TEST_ERROR",
            message="Test message",
            details="Test details",
        )
        assert error.code == "TEST_ERROR"
        assert error.message == "Test message"
        assert error.details == "Test details"
        assert error.retry_after is None

    def test_gh_error_with_retry_after(self) -> None:
        """Test GhError with retry_after field."""
        error = GhError(
            code=RATE_LIMITED,
            message="Rate limited",
            details="Wait 60 seconds",
            retry_after=60,
        )
        assert error.retry_after == 60


class TestExecutionResultDataclass:
    """Tests for the ExecutionResult dataclass structure."""

    def test_execution_result_success(self) -> None:
        """Test ExecutionResult for successful execution."""
        result = ExecutionResult(
            success=True,
            stdout='{"data": "value"}',
            attempts=1,
        )
        assert result.success is True
        assert result.stdout == '{"data": "value"}'
        assert result.error is None
        assert result.attempts == 1

    def test_execution_result_failure(self) -> None:
        """Test ExecutionResult for failed execution."""
        error = GhError(code="TEST", message="msg", details="det")
        result = ExecutionResult(
            success=False,
            error=error,
            attempts=3,
        )
        assert result.success is False
        assert result.stdout == ""
        assert result.error == error
        assert result.attempts == 3
