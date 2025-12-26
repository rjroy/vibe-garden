"""Unit tests for gh_project.py config loading and CLI structure.

Tests cover:
- Valid configuration loading
- Missing configuration file
- Malformed JSON
- Missing required fields (owner, owner_type, number)
- Invalid owner_type values
- Invalid project number values
- CLI argument parsing
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
    CONFIG_INVALID,
    CONFIG_MISSING,
    ProjectConfig,
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
