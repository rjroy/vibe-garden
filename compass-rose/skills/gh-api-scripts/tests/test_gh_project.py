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
    FIELD_NOT_FOUND,
    ISSUE_EXISTS_QUERY,
    ISSUE_NOT_FOUND,
    ISSUE_NOT_IN_PROJECT,
    LIST_ISSUES_QUERY,
    RATE_LIMITED,
    ExecutionResult,
    GhError,
    GraphQLResult,
    ProjectConfig,
    _check_issue_exists_in_repo,
    _execute_graphql,
    _execute_with_retry,
    _extract_field_value,
    _extract_retry_after,
    _is_retryable_error,
    _parse_gh_error,
    _parse_issue_from_node,
    cmd_get_issue,
    cmd_list_issues,
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


class TestExecuteGraphQL:
    """Tests for _execute_graphql function."""

    def test_successful_query(self) -> None:
        """Test successful GraphQL query execution."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"data": {"user": {"projectV2": {"items": []}}}}'
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _execute_graphql("query {}", {"owner": "test", "number": 1})

            assert result.success is True
            assert result.data == {"data": {"user": {"projectV2": {"items": []}}}}
            assert result.error is None

    def test_subprocess_failure(self) -> None:
        """Test GraphQL query with subprocess failure."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "To authenticate, run: gh auth login"

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _execute_graphql("query {}", {"owner": "test", "number": 1})

            assert result.success is False
            assert result.error is not None
            assert result.error.code == AUTH_REQUIRED

    def test_invalid_json_response(self) -> None:
        """Test GraphQL query with invalid JSON response."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "not valid json"
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _execute_graphql("query {}", {"owner": "test", "number": 1})

            assert result.success is False
            assert result.error is not None
            assert result.error.code == API_ERROR
            assert "JSON parse error" in result.error.details

    def test_graphql_errors_in_response(self) -> None:
        """Test GraphQL query with errors in response body."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "data": None,
            "errors": [{"message": "Field 'foo' not found"}],
        })
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _execute_graphql("query {}", {"owner": "test", "number": 1})

            assert result.success is False
            assert result.error is not None
            assert result.error.code == API_ERROR
            assert "Field 'foo' not found" in result.error.details

    def test_integer_variable_uses_dash_F(self) -> None:
        """Test that integer variables use -F flag for correct typing."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"data": {}}'
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            _execute_graphql("query {}", {"owner": "test", "number": 42})

            cmd = mock_run.call_args[0][0]
            # owner should use -f (string)
            assert "-f" in cmd
            assert "owner=test" in cmd
            # number should use -F (integer)
            assert "-F" in cmd
            assert "number=42" in cmd

    def test_none_variables_skipped(self) -> None:
        """Test that None variables are not included in command."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"data": {}}'
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            _execute_graphql("query {}", {"owner": "test", "cursor": None})

            cmd = mock_run.call_args[0][0]
            assert "cursor" not in " ".join(cmd)


class TestExtractFieldValue:
    """Tests for _extract_field_value function."""

    def test_extract_status_field(self) -> None:
        """Test extracting Status field value."""
        field_values = [
            {"name": "In Progress", "field": {"name": "Status"}},
            {"name": "P0", "field": {"name": "Priority"}},
        ]
        assert _extract_field_value(field_values, "Status") == "In Progress"

    def test_extract_priority_field(self) -> None:
        """Test extracting Priority field value."""
        field_values = [
            {"name": "Ready", "field": {"name": "Status"}},
            {"name": "P1", "field": {"name": "Priority"}},
        ]
        assert _extract_field_value(field_values, "Priority") == "P1"

    def test_field_not_present(self) -> None:
        """Test extracting field that doesn't exist."""
        field_values = [
            {"name": "Ready", "field": {"name": "Status"}},
        ]
        assert _extract_field_value(field_values, "Size") is None

    def test_empty_field_values(self) -> None:
        """Test extracting from empty field values."""
        assert _extract_field_value([], "Status") is None

    def test_missing_field_key(self) -> None:
        """Test handling nodes without 'field' key."""
        field_values = [
            {"name": "Something"},  # No 'field' key
        ]
        assert _extract_field_value(field_values, "Status") is None


class TestParseIssueFromNode:
    """Tests for _parse_issue_from_node function."""

    def test_parse_complete_issue(self) -> None:
        """Test parsing a complete issue node."""
        node = {
            "id": "item123",
            "content": {
                "number": 42,
                "title": "Fix login bug",
                "body": "Users cannot login",
                "state": "OPEN",
                "url": "https://github.com/owner/repo/issues/42",
                "labels": {"nodes": [{"name": "bug"}, {"name": "P0"}]},
            },
            "fieldValues": {
                "nodes": [
                    {"name": "In Progress", "field": {"name": "Status"}},
                    {"name": "P0", "field": {"name": "Priority"}},
                    {"name": "M", "field": {"name": "Size"}},
                ]
            },
        }

        issue = _parse_issue_from_node(node)

        assert issue is not None
        assert issue["number"] == 42
        assert issue["title"] == "Fix login bug"
        assert issue["body"] == "Users cannot login"
        assert issue["state"] == "OPEN"
        assert issue["url"] == "https://github.com/owner/repo/issues/42"
        assert issue["labels"] == ["bug", "P0"]
        assert issue["status"] == "In Progress"
        assert issue["priority"] == "P0"
        assert issue["size"] == "M"

    def test_parse_issue_without_labels(self) -> None:
        """Test parsing issue with no labels."""
        node = {
            "content": {
                "number": 1,
                "title": "Test",
                "body": "",
                "state": "OPEN",
                "url": "https://github.com/owner/repo/issues/1",
                "labels": {"nodes": []},
            },
            "fieldValues": {"nodes": []},
        }

        issue = _parse_issue_from_node(node)

        assert issue is not None
        assert issue["labels"] == []

    def test_parse_draft_item_returns_none(self) -> None:
        """Test that draft items (no content) return None."""
        node = {"id": "draft123", "content": None}

        assert _parse_issue_from_node(node) is None

    def test_parse_pull_request_returns_none(self) -> None:
        """Test that pull requests (no 'number' in content) return None."""
        node = {
            "content": {
                "title": "PR Title",
                # PRs might not have 'number' in the Issue fragment
            },
            "fieldValues": {"nodes": []},
        }

        assert _parse_issue_from_node(node) is None

    def test_parse_issue_missing_optional_fields(self) -> None:
        """Test parsing issue with missing optional field values."""
        node = {
            "content": {
                "number": 5,
                "title": "Minimal issue",
                "labels": {"nodes": []},
            },
            "fieldValues": {"nodes": []},
        }

        issue = _parse_issue_from_node(node)

        assert issue is not None
        assert issue["number"] == 5
        assert issue["body"] == ""
        assert issue["url"] == ""
        assert issue["state"] == ""
        assert issue["status"] is None
        assert issue["priority"] is None
        assert issue["size"] is None


class TestListIssuesQuery:
    """Tests for LIST_ISSUES_QUERY constant."""

    def test_query_user_format(self) -> None:
        """Test query formats correctly for user owner_type."""
        query = LIST_ISSUES_QUERY.format(owner_type="user")
        assert "user(login: $owner)" in query
        assert "organization" not in query

    def test_query_organization_format(self) -> None:
        """Test query formats correctly for organization owner_type."""
        query = LIST_ISSUES_QUERY.format(owner_type="organization")
        assert "organization(login: $owner)" in query
        assert "user(login:" not in query

    def test_query_includes_pagination(self) -> None:
        """Test query includes pagination fields."""
        query = LIST_ISSUES_QUERY.format(owner_type="user")
        assert "pageInfo" in query
        assert "hasNextPage" in query
        assert "endCursor" in query
        assert "$cursor" in query

    def test_query_includes_issue_fields(self) -> None:
        """Test query includes all required issue fields."""
        query = LIST_ISSUES_QUERY.format(owner_type="user")
        assert "number" in query
        assert "title" in query
        assert "body" in query
        assert "state" in query
        assert "url" in query
        assert "labels" in query

    def test_query_includes_status_field_check(self) -> None:
        """Test query includes Status field lookup."""
        query = LIST_ISSUES_QUERY.format(owner_type="user")
        assert 'field(name: "Status")' in query


class TestCmdListIssues:
    """Integration tests for cmd_list_issues function."""

    def _make_graphql_response(
        self,
        items: list,
        has_next_page: bool = False,
        end_cursor: str | None = None,
        has_status_field: bool = True,
    ) -> str:
        """Helper to create a mock GraphQL response."""
        response = {
            "data": {
                "user": {
                    "projectV2": {
                        "items": {
                            "nodes": items,
                            "pageInfo": {
                                "hasNextPage": has_next_page,
                                "endCursor": end_cursor,
                            },
                        },
                        "field": {"id": "field123", "name": "Status"}
                        if has_status_field
                        else None,
                    }
                }
            }
        }
        return json.dumps(response)

    def _make_issue_node(
        self,
        number: int,
        title: str = "Test issue",
        status: str | None = "Ready",
    ) -> dict:
        """Helper to create a mock issue node."""
        node = {
            "id": f"item{number}",
            "content": {
                "number": number,
                "title": title,
                "body": f"Body for issue {number}",
                "state": "OPEN",
                "url": f"https://github.com/owner/repo/issues/{number}",
                "labels": {"nodes": [{"name": "bug"}]},
            },
            "fieldValues": {"nodes": []},
        }
        if status:
            node["fieldValues"]["nodes"].append(
                {"name": status, "field": {"name": "Status"}}
            )
        return node

    def test_list_issues_single_page(self, tmp_path: Path, capsys) -> None:
        """Test listing issues with single page of results."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        items = [
            self._make_issue_node(1, "First issue", "Ready"),
            self._make_issue_node(2, "Second issue", "In Progress"),
        ]
        mock_response = self._make_graphql_response(items, has_next_page=False)

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_response
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit) as exc_info:
                cmd_list_issues(args)

            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["data"]["count"] == 2
        assert len(output["data"]["issues"]) == 2
        assert output["data"]["issues"][0]["number"] == 1
        assert output["data"]["issues"][0]["title"] == "First issue"
        assert output["data"]["issues"][1]["number"] == 2

    def test_list_issues_pagination(self, tmp_path: Path, capsys) -> None:
        """Test listing issues with multiple pages."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        # First page
        page1_items = [self._make_issue_node(1)]
        page1_response = self._make_graphql_response(
            page1_items, has_next_page=True, end_cursor="cursor123"
        )

        # Second page
        page2_items = [self._make_issue_node(2)]
        page2_response = self._make_graphql_response(page2_items, has_next_page=False)

        mock_results = [
            mock.Mock(returncode=0, stdout=page1_response, stderr=""),
            mock.Mock(returncode=0, stdout=page2_response, stderr=""),
        ]

        with mock.patch("subprocess.run", side_effect=mock_results) as mock_run:
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit) as exc_info:
                cmd_list_issues(args)

            assert exc_info.value.code == 0

            # Verify two queries were made
            assert mock_run.call_count == 2

            # Verify second query included cursor
            second_call_args = mock_run.call_args_list[1][0][0]
            assert "cursor=cursor123" in " ".join(second_call_args)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["data"]["count"] == 2
        assert len(output["data"]["issues"]) == 2

    def test_list_issues_empty_project(self, tmp_path: Path, capsys) -> None:
        """Test listing issues from empty project."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        mock_response = self._make_graphql_response([], has_next_page=False)

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_response
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit) as exc_info:
                cmd_list_issues(args)

            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["data"]["count"] == 0
        assert output["data"]["issues"] == []

    def test_list_issues_organization_owner_type(self, tmp_path: Path) -> None:
        """Test that organization owner_type uses correct query root."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {
                    "owner": "testorg",
                    "owner_type": "organization",
                    "number": 5,
                }
            })
        )

        # Response with organization root
        response = {
            "data": {
                "organization": {
                    "projectV2": {
                        "items": {"nodes": [], "pageInfo": {"hasNextPage": False}},
                        "field": {"id": "f1", "name": "Status"},
                    }
                }
            }
        }

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response)
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit):
                cmd_list_issues(args)

            # Verify query used organization root
            cmd = mock_run.call_args[0][0]
            query_arg = next(arg for arg in cmd if "organization(login:" in arg)
            assert query_arg is not None

    def test_list_issues_status_field_missing(self, tmp_path: Path, capsys) -> None:
        """Test FIELD_NOT_FOUND error when Status field is missing."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        mock_response = self._make_graphql_response(
            [], has_next_page=False, has_status_field=False
        )

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_response
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit) as exc_info:
                cmd_list_issues(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == FIELD_NOT_FOUND
        assert "Status" in output["error"]["message"]

    def test_list_issues_api_error(self, tmp_path: Path, capsys) -> None:
        """Test handling of API errors."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "HTTP 404 Not Found"

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit) as exc_info:
                cmd_list_issues(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == API_ERROR

    def test_list_issues_filters_draft_items(self, tmp_path: Path, capsys) -> None:
        """Test that draft items are filtered out."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        items = [
            self._make_issue_node(1, "Real issue"),
            {"id": "draft1", "content": None, "fieldValues": {"nodes": []}},  # Draft
        ]
        mock_response = self._make_graphql_response(items, has_next_page=False)

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_response
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit):
                cmd_list_issues(args)

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["data"]["count"] == 1
        assert output["data"]["issues"][0]["number"] == 1

    def test_list_issues_handles_many_pages(self, tmp_path: Path, capsys) -> None:
        """Test handling of >100 items across multiple pages."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        # Create 3 pages with different issues
        pages = []
        for page_num in range(3):
            start = page_num * 100 + 1
            items = [self._make_issue_node(i) for i in range(start, start + 100)]
            has_next = page_num < 2
            cursor = f"cursor{page_num + 1}" if has_next else None
            pages.append(
                mock.Mock(
                    returncode=0,
                    stdout=self._make_graphql_response(items, has_next, cursor),
                    stderr="",
                )
            )

        with mock.patch("subprocess.run", side_effect=pages) as mock_run:
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit) as exc_info:
                cmd_list_issues(args)

            assert exc_info.value.code == 0
            assert mock_run.call_count == 3

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["data"]["count"] == 300

    def test_list_issues_project_not_found(self, tmp_path: Path, capsys) -> None:
        """Test handling when project doesn't exist."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 999}
            })
        )

        response = {"data": {"user": {"projectV2": None}}}

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response)
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)

            with pytest.raises(SystemExit) as exc_info:
                cmd_list_issues(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == API_ERROR
        assert "Project not found" in output["error"]["message"]


class TestGraphQLResultDataclass:
    """Tests for the GraphQLResult dataclass structure."""

    def test_graphql_result_success(self) -> None:
        """Test GraphQLResult for successful query."""
        result = GraphQLResult(
            success=True,
            data={"data": {"user": {}}},
        )
        assert result.success is True
        assert result.data is not None
        assert result.error is None

    def test_graphql_result_failure(self) -> None:
        """Test GraphQLResult for failed query."""
        error = GhError(code=API_ERROR, message="msg", details="det")
        result = GraphQLResult(
            success=False,
            error=error,
        )
        assert result.success is False
        assert result.data is None
        assert result.error == error


class TestCheckIssueExistsInRepo:
    """Tests for _check_issue_exists_in_repo function."""

    def test_issue_exists(self) -> None:
        """Test returns True when issue exists."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "data": {
                "repository": {
                    "issue": {"id": "I_123", "number": 42, "title": "Test"}
                }
            }
        })
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _check_issue_exists_in_repo("owner", "repo", 42)
            assert result is True

    def test_issue_not_found(self) -> None:
        """Test returns False when issue doesn't exist."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "data": {"repository": {"issue": None}}
        })
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _check_issue_exists_in_repo("owner", "repo", 999)
            assert result is False

    def test_repository_not_found(self) -> None:
        """Test returns None when repository doesn't exist."""
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"data": {"repository": None}})
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _check_issue_exists_in_repo("owner", "nonexistent", 42)
            assert result is None

    def test_api_failure(self) -> None:
        """Test returns None when API call fails."""
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "API error"

        with mock.patch("subprocess.run", return_value=mock_result):
            result = _check_issue_exists_in_repo("owner", "repo", 42)
            assert result is None


class TestIssueExistsQuery:
    """Tests for ISSUE_EXISTS_QUERY constant."""

    def test_query_structure(self) -> None:
        """Test query has correct structure."""
        assert "repository(owner: $owner, name: $repo)" in ISSUE_EXISTS_QUERY
        assert "issue(number: $number)" in ISSUE_EXISTS_QUERY
        assert "$owner: String!" in ISSUE_EXISTS_QUERY
        assert "$repo: String!" in ISSUE_EXISTS_QUERY
        assert "$number: Int!" in ISSUE_EXISTS_QUERY


class TestCmdGetIssue:
    """Tests for cmd_get_issue function."""

    def _make_graphql_response(
        self,
        items: list,
        has_next_page: bool = False,
        end_cursor: str | None = None,
        has_status_field: bool = True,
    ) -> str:
        """Helper to create a mock GraphQL response."""
        response = {
            "data": {
                "user": {
                    "projectV2": {
                        "items": {
                            "nodes": items,
                            "pageInfo": {
                                "hasNextPage": has_next_page,
                                "endCursor": end_cursor,
                            },
                        },
                        "field": {"id": "field123", "name": "Status"}
                        if has_status_field
                        else None,
                    }
                }
            }
        }
        return json.dumps(response)

    def _make_issue_node(
        self,
        number: int,
        title: str = "Test issue",
        status: str | None = "Ready",
        priority: str | None = "P1",
        size: str | None = "M",
    ) -> dict:
        """Helper to create a mock issue node."""
        node = {
            "id": f"item{number}",
            "content": {
                "number": number,
                "title": title,
                "body": f"Body for issue {number}",
                "state": "OPEN",
                "url": f"https://github.com/owner/repo/issues/{number}",
                "labels": {"nodes": [{"name": "bug"}]},
            },
            "fieldValues": {"nodes": []},
        }
        if status:
            node["fieldValues"]["nodes"].append(
                {"name": status, "field": {"name": "Status"}}
            )
        if priority:
            node["fieldValues"]["nodes"].append(
                {"name": priority, "field": {"name": "Priority"}}
            )
        if size:
            node["fieldValues"]["nodes"].append(
                {"name": size, "field": {"name": "Size"}}
            )
        return node

    def test_get_issue_found(self, tmp_path: Path, capsys) -> None:
        """Test getting an issue that exists in the project."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        items = [
            self._make_issue_node(42, "Found issue", "In Progress", "P0", "L"),
        ]
        mock_response = self._make_graphql_response(items, has_next_page=False)

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_response
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 42

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["data"]["number"] == 42
        assert output["data"]["title"] == "Found issue"
        assert output["data"]["status"] == "In Progress"
        assert output["data"]["priority"] == "P0"
        assert output["data"]["size"] == "L"
        assert output["data"]["labels"] == ["bug"]
        assert output["data"]["state"] == "OPEN"

    def test_get_issue_found_on_second_page(self, tmp_path: Path, capsys) -> None:
        """Test getting an issue that exists on second page of results."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        # First page - doesn't have the issue
        page1_items = [self._make_issue_node(1)]
        page1_response = self._make_graphql_response(
            page1_items, has_next_page=True, end_cursor="cursor123"
        )

        # Second page - has the issue
        page2_items = [self._make_issue_node(42, "Found on page 2")]
        page2_response = self._make_graphql_response(page2_items, has_next_page=False)

        mock_results = [
            mock.Mock(returncode=0, stdout=page1_response, stderr=""),
            mock.Mock(returncode=0, stdout=page2_response, stderr=""),
        ]

        with mock.patch("subprocess.run", side_effect=mock_results):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 42

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is True
        assert output["data"]["number"] == 42
        assert output["data"]["title"] == "Found on page 2"

    def test_get_issue_not_in_project_no_repo_config(
        self, tmp_path: Path, capsys
    ) -> None:
        """Test ISSUE_NOT_IN_PROJECT when issue not found and no repository configured."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        # Project has different issues, not the one we're looking for
        items = [self._make_issue_node(1), self._make_issue_node(2)]
        mock_response = self._make_graphql_response(items, has_next_page=False)

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_response
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 999

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == ISSUE_NOT_IN_PROJECT
        assert "999" in output["error"]["message"]
        assert "add-to-project" in output["error"]["details"]

    def test_get_issue_not_found_with_repo_config(
        self, tmp_path: Path, capsys
    ) -> None:
        """Test ISSUE_NOT_FOUND when issue doesn't exist in repository."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {
                    "owner": "testuser",
                    "owner_type": "user",
                    "number": 1,
                    "repository": "testrepo",
                }
            })
        )

        # Project listing response - issue not in project
        project_items = [self._make_issue_node(1)]
        project_response = self._make_graphql_response(
            project_items, has_next_page=False
        )

        # Repository check response - issue doesn't exist
        repo_response = json.dumps({"data": {"repository": {"issue": None}}})

        mock_results = [
            mock.Mock(returncode=0, stdout=project_response, stderr=""),
            mock.Mock(returncode=0, stdout=repo_response, stderr=""),
        ]

        with mock.patch("subprocess.run", side_effect=mock_results):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 999

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == ISSUE_NOT_FOUND
        assert "999" in output["error"]["message"]
        assert "testuser/testrepo" in output["error"]["details"]

    def test_get_issue_exists_but_not_in_project(
        self, tmp_path: Path, capsys
    ) -> None:
        """Test ISSUE_NOT_IN_PROJECT when issue exists but not linked to project."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {
                    "owner": "testuser",
                    "owner_type": "user",
                    "number": 1,
                    "repository": "testrepo",
                }
            })
        )

        # Project listing response - issue not in project
        project_items = [self._make_issue_node(1)]
        project_response = self._make_graphql_response(
            project_items, has_next_page=False
        )

        # Repository check response - issue exists
        repo_response = json.dumps({
            "data": {
                "repository": {
                    "issue": {"id": "I_999", "number": 999, "title": "Exists"}
                }
            }
        })

        mock_results = [
            mock.Mock(returncode=0, stdout=project_response, stderr=""),
            mock.Mock(returncode=0, stdout=repo_response, stderr=""),
        ]

        with mock.patch("subprocess.run", side_effect=mock_results):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 999

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == ISSUE_NOT_IN_PROJECT
        assert "999" in output["error"]["message"]
        assert "add-to-project" in output["error"]["details"]

    def test_get_issue_invalid_number_zero(self, tmp_path: Path, capsys) -> None:
        """Test error for invalid issue number (zero)."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        args = mock.Mock()
        args.config = str(config_file)
        args.number = 0

        with pytest.raises(SystemExit) as exc_info:
            cmd_get_issue(args)

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "0" in output["error"]["message"]

    def test_get_issue_invalid_number_negative(self, tmp_path: Path, capsys) -> None:
        """Test error for invalid issue number (negative)."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        args = mock.Mock()
        args.config = str(config_file)
        args.number = -5

        with pytest.raises(SystemExit) as exc_info:
            cmd_get_issue(args)

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == CONFIG_INVALID
        assert "-5" in output["error"]["message"]

    def test_get_issue_organization_owner_type(self, tmp_path: Path, capsys) -> None:
        """Test that organization owner_type uses correct query root."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {
                    "owner": "testorg",
                    "owner_type": "organization",
                    "number": 5,
                }
            })
        )

        # Response with organization root
        response = {
            "data": {
                "organization": {
                    "projectV2": {
                        "items": {
                            "nodes": [self._make_issue_node(42)],
                            "pageInfo": {"hasNextPage": False},
                        },
                        "field": {"id": "f1", "name": "Status"},
                    }
                }
            }
        }

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response)
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result) as mock_run:
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 42

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 0

            # Verify query used organization root
            cmd = mock_run.call_args[0][0]
            query_arg = next(arg for arg in cmd if "organization(login:" in arg)
            assert query_arg is not None

    def test_get_issue_project_not_found(self, tmp_path: Path, capsys) -> None:
        """Test handling when project doesn't exist."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 999}
            })
        )

        response = {"data": {"user": {"projectV2": None}}}

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response)
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 42

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == API_ERROR
        assert "Project not found" in output["error"]["message"]

    def test_get_issue_api_error(self, tmp_path: Path, capsys) -> None:
        """Test handling of API errors."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "HTTP 500 Internal Server Error"

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 42

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False

    def test_get_issue_empty_project(self, tmp_path: Path, capsys) -> None:
        """Test getting issue from empty project returns ISSUE_NOT_IN_PROJECT."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {"owner": "testuser", "owner_type": "user", "number": 1}
            })
        )

        mock_response = self._make_graphql_response([], has_next_page=False)

        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_response
        mock_result.stderr = ""

        with mock.patch("subprocess.run", return_value=mock_result):
            args = mock.Mock()
            args.config = str(config_file)
            args.number = 42

            with pytest.raises(SystemExit) as exc_info:
                cmd_get_issue(args)

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["success"] is False
        assert output["error"]["code"] == ISSUE_NOT_IN_PROJECT


class TestConfigWithRepository:
    """Tests for config with repository field."""

    def test_config_with_repository(self, tmp_path: Path) -> None:
        """Test loading config with repository field."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {
                    "owner": "rjroy",
                    "owner_type": "user",
                    "number": 8,
                    "repository": "vibe-garden",
                }
            })
        )

        config = load_config(str(config_file))

        assert config.repository == "vibe-garden"

    def test_config_without_repository(self, tmp_path: Path) -> None:
        """Test loading config without repository field."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({
                "project": {
                    "owner": "rjroy",
                    "owner_type": "user",
                    "number": 8,
                }
            })
        )

        config = load_config(str(config_file))

        assert config.repository is None
