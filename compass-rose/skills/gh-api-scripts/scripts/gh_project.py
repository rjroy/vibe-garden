#!/usr/bin/env python3
"""GitHub Project API operations for Compass Rose.

This module provides CLI operations for interacting with GitHub Projects
via the gh CLI's GraphQL interface. All operations return JSON output
with consistent success/error envelope structure.

Usage:
    python3 gh_project.py list-issues
    python3 gh_project.py get-issue <number>
    python3 gh_project.py set-status <number> <status>
    python3 gh_project.py add-to-project <number>

All operations read configuration from .compass-rose/config.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Error codes as defined in TD-6
CONFIG_MISSING = "CONFIG_MISSING"
CONFIG_INVALID = "CONFIG_INVALID"
AUTH_REQUIRED = "AUTH_REQUIRED"
AUTH_SCOPE_MISSING = "AUTH_SCOPE_MISSING"
ISSUE_NOT_FOUND = "ISSUE_NOT_FOUND"
ISSUE_NOT_IN_PROJECT = "ISSUE_NOT_IN_PROJECT"
STATUS_INVALID = "STATUS_INVALID"
FIELD_NOT_FOUND = "FIELD_NOT_FOUND"
RATE_LIMITED = "RATE_LIMITED"
API_ERROR = "API_ERROR"

# Default config path relative to current working directory
DEFAULT_CONFIG_PATH = ".compass-rose/config.json"

# Valid owner types
VALID_OWNER_TYPES = ("user", "organization")


@dataclass
class ProjectConfig:
    """Configuration for GitHub Project operations.

    Attributes:
        owner: GitHub username or organization name
        owner_type: Either "user" or "organization"
        number: Project number (visible in project URL)
    """

    owner: str
    owner_type: str
    number: int


def output_success(data: dict[str, Any]) -> None:
    """Print success response to stdout and exit with code 0.

    Args:
        data: The response data to include in the envelope
    """
    response = {"success": True, "data": data}
    print(json.dumps(response, indent=2))
    sys.exit(0)


def output_error(code: str, message: str, details: str) -> None:
    """Print error response to stdout and exit with code 1.

    Args:
        code: Error code from the taxonomy (e.g., CONFIG_MISSING)
        message: Human-readable error message
        details: Actionable remediation guidance
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }
    print(json.dumps(response, indent=2))
    sys.exit(1)


def load_config(config_path: str | None = None) -> ProjectConfig:
    """Load and validate project configuration.

    Reads configuration from .compass-rose/config.json (or specified path)
    and validates all required fields.

    Args:
        config_path: Optional path to config file. Defaults to
                     .compass-rose/config.json in current directory.

    Returns:
        ProjectConfig with validated configuration values

    Raises:
        SystemExit: On missing or invalid configuration (via output_error)
    """
    path = Path(config_path) if config_path else Path(DEFAULT_CONFIG_PATH)

    # Check if config file exists
    if not path.exists():
        output_error(
            CONFIG_MISSING,
            "Configuration file not found",
            f"Expected config at {path}. "
            "Create .compass-rose/config.json with:\n\n"
            '{\n  "project": {\n    "owner": "<org-or-username>",\n'
            '    "owner_type": "user",\n    "number": <project-number>\n  }\n}\n\n'
            "Find your project number in the project URL:\n"
            "https://github.com/users/<owner>/projects/<number>",
        )

    # Try to parse JSON
    try:
        with open(path, encoding="utf-8") as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        output_error(
            CONFIG_INVALID,
            "Configuration file is not valid JSON",
            f"Parse error: {e}. Ensure .compass-rose/config.json contains valid JSON.",
        )

    # Validate project section exists
    if "project" not in config_data:
        output_error(
            CONFIG_INVALID,
            "Missing 'project' section in configuration",
            "Configuration must include a 'project' object with "
            "'owner', 'owner_type', and 'number' fields.\n\n"
            "Example:\n"
            '{\n  "project": {\n    "owner": "my-org",\n'
            '    "owner_type": "organization",\n    "number": 8\n  }\n}',
        )

    project = config_data["project"]

    # Validate required fields
    missing_fields = []
    if "owner" not in project:
        missing_fields.append("owner")
    if "owner_type" not in project:
        missing_fields.append("owner_type")
    if "number" not in project:
        missing_fields.append("number")

    if missing_fields:
        output_error(
            CONFIG_INVALID,
            f"Missing required fields: {', '.join(missing_fields)}",
            "Configuration 'project' section requires: owner, owner_type, number.\n\n"
            "Example:\n"
            '{\n  "project": {\n    "owner": "rjroy",\n'
            '    "owner_type": "user",\n    "number": 8\n  }\n}',
        )

    # Validate owner_type value
    owner_type = project["owner_type"]
    if owner_type not in VALID_OWNER_TYPES:
        output_error(
            CONFIG_INVALID,
            f"Invalid owner_type: '{owner_type}'",
            f"owner_type must be one of: {', '.join(VALID_OWNER_TYPES)}.\n\n"
            'Use "user" for personal projects (github.com/users/<name>/projects/<n>)\n'
            'Use "organization" for org projects (github.com/orgs/<name>/projects/<n>)',
        )

    # Validate number is an integer
    try:
        number = int(project["number"])
    except (ValueError, TypeError):
        output_error(
            CONFIG_INVALID,
            f"Invalid project number: '{project['number']}'",
            "project.number must be a positive integer.\n"
            "Find your project number in the project URL.",
        )

    if number <= 0:
        output_error(
            CONFIG_INVALID,
            f"Invalid project number: {number}",
            "project.number must be a positive integer.\n"
            "Find your project number in the project URL.",
        )

    return ProjectConfig(
        owner=project["owner"],
        owner_type=owner_type,
        number=number,
    )


def cmd_list_issues(args: argparse.Namespace) -> None:
    """List all open issues in the configured project.

    Placeholder implementation - will be completed in TASK-004.
    """
    config = load_config(args.config)
    # TODO: Implement in TASK-004 - List Issues Operation with Pagination
    output_success(
        {
            "message": "list-issues operation not yet implemented",
            "config": {
                "owner": config.owner,
                "owner_type": config.owner_type,
                "number": config.number,
            },
        }
    )


def cmd_get_issue(args: argparse.Namespace) -> None:
    """Get a single issue by number.

    Placeholder implementation - will be completed in TASK-005.
    """
    config = load_config(args.config)
    # TODO: Implement in TASK-005 - Get Issue Operation
    output_success(
        {
            "message": "get-issue operation not yet implemented",
            "issue_number": args.number,
            "config": {
                "owner": config.owner,
                "owner_type": config.owner_type,
                "number": config.number,
            },
        }
    )


def cmd_set_status(args: argparse.Namespace) -> None:
    """Update the status of an issue.

    Placeholder implementation - will be completed in TASK-006.
    """
    config = load_config(args.config)
    # TODO: Implement in TASK-006 - Set Status Operation
    output_success(
        {
            "message": "set-status operation not yet implemented",
            "issue_number": args.number,
            "status": args.status,
            "config": {
                "owner": config.owner,
                "owner_type": config.owner_type,
                "number": config.number,
            },
        }
    )


def cmd_add_to_project(args: argparse.Namespace) -> None:
    """Add an existing repository issue to the configured project.

    Placeholder implementation - will be completed in TASK-007.
    """
    config = load_config(args.config)
    # TODO: Implement in TASK-007 - Add to Project Operation
    output_success(
        {
            "message": "add-to-project operation not yet implemented",
            "issue_number": args.number,
            "config": {
                "owner": config.owner,
                "owner_type": config.owner_type,
                "number": config.number,
            },
        }
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands.

    Returns:
        Configured ArgumentParser with subcommands for all operations.
    """
    parser = argparse.ArgumentParser(
        prog="gh_project",
        description="GitHub Project API operations for Compass Rose",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s list-issues
    %(prog)s get-issue 42
    %(prog)s set-status 42 "In Progress"
    %(prog)s add-to-project 42

All operations read config from .compass-rose/config.json
All output is JSON to stdout
Exit codes: 0 = success, 1 = error (details in JSON)
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help=f"Path to config file (default: {DEFAULT_CONFIG_PATH})",
    )

    subparsers = parser.add_subparsers(
        title="operations",
        description="Available GitHub Project operations",
        dest="operation",
        required=True,
    )

    # list-issues subcommand
    parser_list = subparsers.add_parser(
        "list-issues",
        help="List all open issues in configured project",
        description="Fetches all open issues from the configured GitHub Project "
        "with automatic pagination. Returns issues with full details including "
        "status, priority, and size fields.",
    )
    parser_list.set_defaults(func=cmd_list_issues)

    # get-issue subcommand
    parser_get = subparsers.add_parser(
        "get-issue",
        help="Get single issue by number",
        description="Retrieves a single issue by its number with full project field values.",
    )
    parser_get.add_argument(
        "number",
        type=int,
        help="Issue number to retrieve",
    )
    parser_get.set_defaults(func=cmd_get_issue)

    # set-status subcommand
    parser_status = subparsers.add_parser(
        "set-status",
        help="Update issue status",
        description="Updates the Status field of an issue in the project.",
    )
    parser_status.add_argument(
        "number",
        type=int,
        help="Issue number to update",
    )
    parser_status.add_argument(
        "status",
        type=str,
        help='New status value (e.g., "In Progress", "Ready", "Done")',
    )
    parser_status.set_defaults(func=cmd_set_status)

    # add-to-project subcommand
    parser_add = subparsers.add_parser(
        "add-to-project",
        help="Add repository issue to project",
        description="Adds an existing repository issue to the configured GitHub Project.",
    )
    parser_add.add_argument(
        "number",
        type=int,
        help="Issue number to add to project",
    )
    parser_add.set_defaults(func=cmd_add_to_project)

    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Execute the command function
    args.func(args)


if __name__ == "__main__":
    main()
