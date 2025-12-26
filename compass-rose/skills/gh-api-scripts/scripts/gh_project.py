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
import re
import subprocess
import sys
import time
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

# GraphQL query for listing issues with pagination
# Uses {owner_type} placeholder for user vs organization
LIST_ISSUES_QUERY = """
query($owner: String!, $number: Int!, $cursor: String) {{
  {owner_type}(login: $owner) {{
    projectV2(number: $number) {{
      items(first: 100, after: $cursor) {{
        pageInfo {{ hasNextPage endCursor }}
        nodes {{
          id
          content {{
            ... on Issue {{
              number
              title
              body
              state
              url
              labels(first: 20) {{ nodes {{ name }} }}
            }}
          }}
          fieldValues(first: 20) {{
            nodes {{
              ... on ProjectV2ItemFieldSingleSelectValue {{
                name
                field {{ ... on ProjectV2SingleSelectField {{ name }} }}
              }}
            }}
          }}
        }}
      }}
      field(name: "Status") {{
        ... on ProjectV2SingleSelectField {{
          id
          name
        }}
      }}
    }}
  }}
}}
"""


@dataclass
class ProjectConfig:
    """Configuration for GitHub Project operations.

    Attributes:
        owner: GitHub username or organization name
        owner_type: Either "user" or "organization"
        number: Project number (visible in project URL)
        repository: Repository name (for issue existence checks)
    """

    owner: str
    owner_type: str
    number: int
    repository: str | None = None


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

    # Repository is optional - used for issue existence checks
    repository = project.get("repository")

    return ProjectConfig(
        owner=project["owner"],
        owner_type=owner_type,
        number=number,
        repository=repository,
    )


# Patterns for detecting error types from gh CLI output
_RETRYABLE_PATTERNS = [
    r"502",
    r"503",
    r"Bad Gateway",
    r"Service Unavailable",
    r"connection reset",
    r"connection refused",
    r"network is unreachable",
    r"temporary failure",
]

_AUTH_REQUIRED_PATTERNS = [
    r"gh auth login",
    r"not logged in",
    r"authentication required",
    r"401",
    r"Unauthorized",
]

_AUTH_SCOPE_PATTERNS = [
    r"project.*scope",
    r"scope.*project",
    r"scopes",
    r"insufficient permissions",
    r"permission denied.*project",
]

_RATE_LIMIT_PATTERNS = [
    r"rate limit",
    r"429",
    r"Too Many Requests",
    r"API rate limit exceeded",
]


def _is_retryable_error(stderr: str) -> bool:
    """Determine if an error is retryable (transient) or permanent.

    Retryable errors include:
    - HTTP 502 Bad Gateway
    - HTTP 503 Service Unavailable
    - Connection errors (reset, refused, unreachable)
    - Temporary failures

    Non-retryable errors include:
    - HTTP 404 Not Found
    - HTTP 401 Unauthorized
    - HTTP 400 Bad Request
    - HTTP 429 Rate Limited (handled specially with retry-after)

    Args:
        stderr: The stderr output from the subprocess

    Returns:
        True if the error is retryable, False otherwise
    """
    stderr_lower = stderr.lower()

    # Check for non-retryable errors first
    non_retryable = ["404", "not found", "400", "bad request"]
    for pattern in non_retryable:
        if pattern in stderr_lower:
            return False

    # Rate limiting is handled specially, not retried automatically
    for pattern in _RATE_LIMIT_PATTERNS:
        if re.search(pattern, stderr, re.IGNORECASE):
            return False

    # Auth errors are not retryable
    for pattern in _AUTH_REQUIRED_PATTERNS + _AUTH_SCOPE_PATTERNS:
        if re.search(pattern, stderr, re.IGNORECASE):
            return False

    # Check for retryable patterns
    for pattern in _RETRYABLE_PATTERNS:
        if re.search(pattern, stderr, re.IGNORECASE):
            return True

    return False


def _extract_retry_after(stderr: str) -> int | None:
    """Extract retry-after seconds from rate limit response.

    Looks for patterns like:
    - "retry after X seconds"
    - "Retry-After: X"
    - "wait X seconds"

    Args:
        stderr: The stderr output from the subprocess

    Returns:
        Number of seconds to wait, or None if not found
    """
    # Look for explicit retry-after header or message
    patterns = [
        r"retry[- ]after[:\s]+(\d+)",
        r"wait\s+(\d+)\s+second",
        r"try again in\s+(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, stderr, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None


@dataclass
class GhError:
    """Categorized error from gh CLI execution.

    Attributes:
        code: Error code from the taxonomy (AUTH_REQUIRED, RATE_LIMITED, etc.)
        message: Human-readable error message
        details: Actionable remediation guidance
        retry_after: Seconds to wait before retry (only for RATE_LIMITED)
    """

    code: str
    message: str
    details: str
    retry_after: int | None = None


def _parse_gh_error(stderr: str, returncode: int) -> GhError:
    """Parse gh CLI error output and categorize into error taxonomy.

    Args:
        stderr: The stderr output from the subprocess
        returncode: The exit code from the subprocess

    Returns:
        GhError with appropriate code, message, and remediation details
    """
    # Check for authentication required
    for pattern in _AUTH_REQUIRED_PATTERNS:
        if re.search(pattern, stderr, re.IGNORECASE):
            return GhError(
                code=AUTH_REQUIRED,
                message="GitHub CLI authentication required",
                details="Run `gh auth login` to authenticate with GitHub.",
            )

    # Check for missing project scope
    for pattern in _AUTH_SCOPE_PATTERNS:
        if re.search(pattern, stderr, re.IGNORECASE):
            return GhError(
                code=AUTH_SCOPE_MISSING,
                message="GitHub CLI missing 'project' scope",
                details="Run `gh auth refresh -s project` to add the required scope.",
            )

    # Check for rate limiting
    for pattern in _RATE_LIMIT_PATTERNS:
        if re.search(pattern, stderr, re.IGNORECASE):
            retry_after = _extract_retry_after(stderr)
            retry_msg = (
                f"Wait {retry_after} seconds before retrying."
                if retry_after
                else "Wait before retrying. Check rate limit status with `gh api rate_limit`."
            )
            return GhError(
                code=RATE_LIMITED,
                message="GitHub API rate limit exceeded",
                details=retry_msg,
                retry_after=retry_after,
            )

    # Fallback: generic API error with raw message
    # Clean up the stderr for display
    cleaned_stderr = stderr.strip()
    if not cleaned_stderr:
        cleaned_stderr = f"Command failed with exit code {returncode}"

    return GhError(
        code=API_ERROR,
        message="GitHub API error",
        details=cleaned_stderr,
    )


@dataclass
class ExecutionResult:
    """Result of subprocess execution with retry handling.

    Attributes:
        success: True if command succeeded
        stdout: Standard output from successful command
        error: Parsed error if command failed
        attempts: Number of attempts made
    """

    success: bool
    stdout: str = ""
    error: GhError | None = None
    attempts: int = 1


def _execute_with_retry(
    cmd: list[str],
    max_attempts: int = 3,
    timeout: int = 30,
) -> ExecutionResult:
    """Execute a subprocess command with exponential backoff retry.

    Implements retry logic for transient errors:
    - Retryable: Network timeout, connection error, HTTP 502, 503
    - Non-retryable: HTTP 404, 401, 400, rate limit 429

    Args:
        cmd: Command and arguments to execute
        max_attempts: Maximum number of attempts (default 3)
        timeout: Timeout per attempt in seconds (default 30)

    Returns:
        ExecutionResult with success status and stdout or error details
    """
    # Generate delays for exponential backoff: 1s, 2s, 4s, 8s, ...
    # We need (max_attempts - 1) delays (no delay after last attempt)
    delays = [2**i for i in range(max_attempts - 1)]
    last_error: GhError | None = None
    last_stderr = ""
    last_returncode = 1

    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return ExecutionResult(
                    success=True,
                    stdout=result.stdout,
                    attempts=attempt + 1,
                )

            # Command failed - check if retryable
            last_stderr = result.stderr
            last_returncode = result.returncode

            if not _is_retryable_error(result.stderr):
                # Permanent error - don't retry
                error = _parse_gh_error(result.stderr, result.returncode)
                return ExecutionResult(
                    success=False,
                    error=error,
                    attempts=attempt + 1,
                )

            # Retryable error - continue to retry logic

        except subprocess.TimeoutExpired:
            # Timeout is retryable
            last_stderr = f"Command timed out after {timeout} seconds"
            last_returncode = -1

        # Wait before retrying (unless this was the last attempt)
        if attempt < max_attempts - 1:
            time.sleep(delays[attempt])

    # All attempts exhausted - return last error
    last_error = _parse_gh_error(last_stderr, last_returncode)
    return ExecutionResult(
        success=False,
        error=last_error,
        attempts=max_attempts,
    )


@dataclass
class GraphQLResult:
    """Result of a GraphQL query execution.

    Attributes:
        success: True if query executed successfully
        data: Parsed JSON response data (if successful)
        error: GhError if query failed
    """

    success: bool
    data: dict[str, Any] | None = None
    error: GhError | None = None


def _execute_graphql(
    query: str,
    variables: dict[str, Any],
    max_attempts: int = 3,
    timeout: int = 30,
) -> GraphQLResult:
    """Execute a GraphQL query via gh api graphql.

    Args:
        query: The GraphQL query string
        variables: Variables to pass to the query
        max_attempts: Maximum number of retry attempts
        timeout: Timeout per attempt in seconds

    Returns:
        GraphQLResult with parsed data or error details
    """
    # Build command with query and variables
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        if value is None:
            continue
        if isinstance(value, int):
            cmd.extend(["-F", f"{name}={value}"])
        else:
            cmd.extend(["-f", f"{name}={value}"])

    result = _execute_with_retry(cmd, max_attempts=max_attempts, timeout=timeout)

    if not result.success:
        return GraphQLResult(success=False, error=result.error)

    # Parse JSON response
    try:
        response_data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return GraphQLResult(
            success=False,
            error=GhError(
                code=API_ERROR,
                message="Failed to parse GraphQL response",
                details=f"JSON parse error: {e}. Response: {result.stdout[:200]}",
            ),
        )

    # Check for GraphQL errors in response
    if "errors" in response_data:
        error_msgs = [e.get("message", str(e)) for e in response_data["errors"]]
        return GraphQLResult(
            success=False,
            error=GhError(
                code=API_ERROR,
                message="GraphQL query returned errors",
                details="; ".join(error_msgs),
            ),
        )

    return GraphQLResult(success=True, data=response_data)


def _extract_field_value(field_values: list[dict], field_name: str) -> str | None:
    """Extract a specific field value from project item field values.

    Args:
        field_values: List of field value nodes from GraphQL response
        field_name: Name of the field to extract (e.g., "Status", "Priority")

    Returns:
        The field value if found, None otherwise
    """
    for fv in field_values:
        # Check if this is a single select field with the right name
        field = fv.get("field", {})
        if field.get("name") == field_name:
            return fv.get("name")
    return None


def _parse_issue_from_node(node: dict) -> dict[str, Any] | None:
    """Parse a project item node into issue data.

    Args:
        node: A project item node from GraphQL response

    Returns:
        Issue dictionary with normalized fields, or None if not an issue
    """
    content = node.get("content")
    if not content:
        # Draft items or non-issue content
        return None

    # Only process issues (not pull requests or draft items)
    if "number" not in content:
        return None

    # Extract labels
    labels_data = content.get("labels", {}).get("nodes", [])
    labels = [label.get("name") for label in labels_data if label.get("name")]

    # Extract project field values
    field_values = node.get("fieldValues", {}).get("nodes", [])
    status = _extract_field_value(field_values, "Status")
    priority = _extract_field_value(field_values, "Priority")
    size = _extract_field_value(field_values, "Size")

    return {
        "number": content.get("number"),
        "title": content.get("title", ""),
        "body": content.get("body", ""),
        "url": content.get("url", ""),
        "state": content.get("state", ""),
        "labels": labels,
        "status": status,
        "priority": priority,
        "size": size,
    }


def cmd_list_issues(args: argparse.Namespace) -> None:
    """List all open issues in the configured project.

    Fetches all issues from the project with automatic pagination.
    Returns issues with: number, title, body, url, state, labels, status, priority, size.
    """
    config = load_config(args.config)

    # Format query with correct owner_type (user vs organization)
    query = LIST_ISSUES_QUERY.format(owner_type=config.owner_type)

    all_issues: list[dict[str, Any]] = []
    cursor: str | None = None
    status_field_checked = False
    status_field_exists = False

    while True:
        # Execute paginated query
        variables = {
            "owner": config.owner,
            "number": config.number,
            "cursor": cursor,
        }
        result = _execute_graphql(query, variables)

        if not result.success:
            assert result.error is not None
            output_error(result.error.code, result.error.message, result.error.details)

        assert result.data is not None
        data = result.data.get("data", {})

        # Navigate to project data (user or organization)
        owner_data = data.get(config.owner_type, {})
        project_data = owner_data.get("projectV2")

        if not project_data:
            output_error(
                API_ERROR,
                "Project not found",
                f"Could not find project #{config.number} for {config.owner_type} "
                f"'{config.owner}'. Verify the project exists and you have access.",
            )

        # Check for Status field on first iteration
        if not status_field_checked:
            status_field_checked = True
            status_field = project_data.get("field")
            if status_field and status_field.get("name") == "Status":
                status_field_exists = True

        # Extract items from this page
        items_data = project_data.get("items", {})
        nodes = items_data.get("nodes", [])

        for node in nodes:
            issue = _parse_issue_from_node(node)
            if issue is not None:
                all_issues.append(issue)

        # Check for more pages
        page_info = items_data.get("pageInfo", {})
        if not page_info.get("hasNextPage", False):
            break
        cursor = page_info.get("endCursor")

    # Check if Status field was missing (only if we got items to check)
    if not status_field_exists and not status_field_checked:
        # We never even made a query - this shouldn't happen, but handle it
        pass
    elif not status_field_exists:
        output_error(
            FIELD_NOT_FOUND,
            "Status field not found in project",
            "The project does not have a 'Status' field configured. "
            "Add a Status single-select field to the project in GitHub.",
        )

    output_success({"issues": all_issues, "count": len(all_issues)})


# GraphQL query to check if an issue exists in the repository
ISSUE_EXISTS_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    issue(number: $number) {
      id
      number
      title
    }
  }
}
"""

# GraphQL query to get project Status field with options
# Uses {owner_type} placeholder for user vs organization
GET_STATUS_FIELD_QUERY = """
query($owner: String!, $number: Int!) {{
  {owner_type}(login: $owner) {{
    projectV2(number: $number) {{
      id
      field(name: "Status") {{
        ... on ProjectV2SingleSelectField {{
          id
          name
          options {{
            id
            name
          }}
        }}
      }}
    }}
  }}
}}
"""

# GraphQL query to find a project item by issue number
# Returns the project item ID and current field values for the issue
# Uses {owner_type} placeholder for user vs organization
FIND_PROJECT_ITEM_QUERY = """
query($owner: String!, $number: Int!, $cursor: String) {{
  {owner_type}(login: $owner) {{
    projectV2(number: $number) {{
      id
      items(first: 100, after: $cursor) {{
        pageInfo {{ hasNextPage endCursor }}
        nodes {{
          id
          content {{
            ... on Issue {{
              number
            }}
          }}
          fieldValues(first: 20) {{
            nodes {{
              ... on ProjectV2ItemFieldSingleSelectValue {{
                name
                field {{ ... on ProjectV2SingleSelectField {{ name }} }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""

# GraphQL mutation to update a project item field value
UPDATE_PROJECT_ITEM_FIELD_MUTATION = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }
  ) {
    projectV2Item {
      id
    }
  }
}
"""

# GraphQL mutation to add an issue to a project
ADD_TO_PROJECT_MUTATION = """
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item {
      id
    }
  }
}
"""

# GraphQL query to get project ID
# Uses {owner_type} placeholder for user vs organization
GET_PROJECT_ID_QUERY = """
query($owner: String!, $number: Int!) {{
  {owner_type}(login: $owner) {{
    projectV2(number: $number) {{
      id
    }}
  }}
}}
"""


def _check_issue_exists_in_repo(
    owner: str, repo: str, issue_number: int
) -> bool | None:
    """Check if an issue exists in a repository.

    Args:
        owner: Repository owner (user or organization)
        repo: Repository name
        issue_number: Issue number to check

    Returns:
        True if issue exists, False if not found, None if check failed
    """
    variables = {
        "owner": owner,
        "repo": repo,
        "number": issue_number,
    }
    result = _execute_graphql(ISSUE_EXISTS_QUERY, variables)

    if not result.success:
        # Check failed - return None to indicate uncertainty
        return None

    assert result.data is not None
    data = result.data.get("data", {})
    repo_data = data.get("repository")

    if repo_data is None:
        # Repository doesn't exist or no access
        return None

    issue_data = repo_data.get("issue")
    return issue_data is not None


@dataclass
class IssueNodeInfo:
    """Information about an issue from the repository.

    Attributes:
        node_id: The GraphQL node ID of the issue
        number: The issue number
        title: The issue title
    """

    node_id: str
    number: int
    title: str


def _get_issue_node_id(
    owner: str, repo: str, issue_number: int
) -> IssueNodeInfo | GhError:
    """Get the node ID for an issue in a repository.

    Args:
        owner: Repository owner (user or organization)
        repo: Repository name
        issue_number: Issue number to look up

    Returns:
        IssueNodeInfo if issue found, GhError if not found or API error
    """
    variables = {
        "owner": owner,
        "repo": repo,
        "number": issue_number,
    }
    result = _execute_graphql(ISSUE_EXISTS_QUERY, variables)

    if not result.success:
        assert result.error is not None
        return result.error

    assert result.data is not None
    data = result.data.get("data", {})
    repo_data = data.get("repository")

    if repo_data is None:
        return GhError(
            code=API_ERROR,
            message=f"Repository '{owner}/{repo}' not found",
            details=f"Could not access repository '{owner}/{repo}'. "
            "Verify the repository exists and you have access.",
        )

    issue_data = repo_data.get("issue")
    if issue_data is None:
        return GhError(
            code=ISSUE_NOT_FOUND,
            message=f"Issue #{issue_number} not found",
            details=f"Issue #{issue_number} does not exist in repository "
            f"'{owner}/{repo}'. Verify the issue number with: gh issue view {issue_number}",
        )

    return IssueNodeInfo(
        node_id=issue_data["id"],
        number=issue_data["number"],
        title=issue_data.get("title", ""),
    )


def _get_project_id(config: ProjectConfig) -> str | GhError:
    """Get the GraphQL node ID for a project.

    Args:
        config: Project configuration

    Returns:
        Project node ID string if successful, GhError if project not found or API error
    """
    query = GET_PROJECT_ID_QUERY.format(owner_type=config.owner_type)

    result = _execute_graphql(
        query,
        {"owner": config.owner, "number": config.number},
    )

    if not result.success:
        assert result.error is not None
        return result.error

    assert result.data is not None
    data = result.data.get("data", {})

    # Navigate to project data (user or organization)
    owner_data = data.get(config.owner_type, {})
    project_data = owner_data.get("projectV2")

    if not project_data:
        return GhError(
            code=API_ERROR,
            message="Project not found",
            details=f"Could not find project #{config.number} for {config.owner_type} "
            f"'{config.owner}'. Verify the project exists and you have access.",
        )

    project_id = project_data.get("id")
    if not project_id:
        return GhError(
            code=API_ERROR,
            message="Project ID not found in response",
            details="Unexpected API response format. The project exists but no ID was returned.",
        )

    return project_id


def _add_issue_to_project(project_id: str, issue_node_id: str) -> GraphQLResult:
    """Add an issue to a project via GraphQL mutation.

    Args:
        project_id: GraphQL node ID of the project
        issue_node_id: GraphQL node ID of the issue to add

    Returns:
        GraphQLResult with mutation response
    """
    return _execute_graphql(
        ADD_TO_PROJECT_MUTATION,
        {
            "projectId": project_id,
            "contentId": issue_node_id,
        },
    )


def cmd_get_issue(args: argparse.Namespace) -> None:
    """Get a single issue by number with full project field values.

    Fetches the issue from the configured project, including all project
    field values (status, priority, size). Returns appropriate error codes
    if the issue doesn't exist or isn't linked to the project.

    Args:
        args: Parsed CLI arguments including:
            - number: Issue number to retrieve
            - config: Optional path to config file
    """
    # Validate issue number is positive (argparse ensures it's an int)
    if args.number <= 0:
        output_error(
            CONFIG_INVALID,
            f"Invalid issue number: {args.number}",
            "Issue number must be a positive integer.",
        )

    config = load_config(args.config)

    # Strategy: Query project items and find matching issue number.
    # This reuses the list-issues infrastructure and is simpler than
    # doing separate queries for issue existence and project membership.

    # Format query with correct owner_type (user vs organization)
    query = LIST_ISSUES_QUERY.format(owner_type=config.owner_type)

    # We'll paginate through all items to find the matching issue
    cursor: str | None = None
    target_issue: dict[str, Any] | None = None

    while True:
        variables = {
            "owner": config.owner,
            "number": config.number,
            "cursor": cursor,
        }
        result = _execute_graphql(query, variables)

        if not result.success:
            assert result.error is not None
            output_error(result.error.code, result.error.message, result.error.details)

        assert result.data is not None
        data = result.data.get("data", {})

        # Navigate to project data (user or organization)
        owner_data = data.get(config.owner_type, {})
        project_data = owner_data.get("projectV2")

        if not project_data:
            output_error(
                API_ERROR,
                "Project not found",
                f"Could not find project #{config.number} for {config.owner_type} "
                f"'{config.owner}'. Verify the project exists and you have access.",
            )

        # Search through items for matching issue number
        items_data = project_data.get("items", {})
        nodes = items_data.get("nodes", [])

        for node in nodes:
            issue = _parse_issue_from_node(node)
            if issue is not None and issue["number"] == args.number:
                target_issue = issue
                break

        # If we found the issue, stop searching
        if target_issue is not None:
            break

        # Check for more pages
        page_info = items_data.get("pageInfo", {})
        if not page_info.get("hasNextPage", False):
            break
        cursor = page_info.get("endCursor")

    # If we found the issue in the project, return it
    if target_issue is not None:
        output_success(target_issue)

    # Issue not found in project - determine if it doesn't exist or isn't linked
    # We need repository info to check issue existence
    if config.repository:
        issue_exists = _check_issue_exists_in_repo(
            config.owner, config.repository, args.number
        )

        if issue_exists is False:
            # Issue definitely doesn't exist in the repository
            output_error(
                ISSUE_NOT_FOUND,
                f"Issue #{args.number} not found",
                f"Issue #{args.number} does not exist in repository "
                f"'{config.owner}/{config.repository}'. "
                f"Verify the issue number with: gh issue view {args.number}",
            )
        elif issue_exists is True:
            # Issue exists but not in project
            output_error(
                ISSUE_NOT_IN_PROJECT,
                f"Issue #{args.number} not linked to project",
                f"Issue #{args.number} exists but is not linked to project "
                f"#{config.number}. Use 'add-to-project {args.number}' to add it.",
            )
        # If issue_exists is None, we couldn't determine - fall through

    # Without repository info or if the check failed, return ISSUE_NOT_IN_PROJECT
    # as the more actionable error (user can try adding it)
    output_error(
        ISSUE_NOT_IN_PROJECT,
        f"Issue #{args.number} not found in project",
        f"Issue #{args.number} is not linked to project #{config.number}. "
        f"Use 'add-to-project {args.number}' to add it to the project, "
        f"or verify the issue number is correct.",
    )


@dataclass
class StatusFieldInfo:
    """Information about a project's Status field.

    Attributes:
        project_id: The GraphQL ID of the project
        field_id: The GraphQL ID of the Status field
        options: Mapping of status option names to their IDs
    """

    project_id: str
    field_id: str
    options: dict[str, str]  # option_name -> option_id


def _get_status_field_info(config: ProjectConfig) -> StatusFieldInfo | GhError:
    """Get the Status field ID and valid options for a project.

    Args:
        config: Project configuration

    Returns:
        StatusFieldInfo if successful, GhError if field not found or API error
    """
    query = GET_STATUS_FIELD_QUERY.format(owner_type=config.owner_type)

    result = _execute_graphql(
        query,
        {"owner": config.owner, "number": config.number},
    )

    if not result.success:
        assert result.error is not None
        return result.error

    assert result.data is not None
    data = result.data.get("data", {})

    # Navigate to project data (user or organization)
    owner_data = data.get(config.owner_type, {})
    project_data = owner_data.get("projectV2")

    if not project_data:
        return GhError(
            code=API_ERROR,
            message="Project not found",
            details=f"Could not find project #{config.number} for {config.owner_type} "
            f"'{config.owner}'. Verify the project exists and you have access.",
        )

    project_id = project_data.get("id")
    field_data = project_data.get("field")

    if not field_data or not field_data.get("id"):
        return GhError(
            code=FIELD_NOT_FOUND,
            message="Status field not found in project",
            details="The project does not have a 'Status' field configured. "
            "Add a Status single-select field to the project in GitHub.",
        )

    field_id = field_data.get("id")
    options_list = field_data.get("options", [])

    # Build options mapping: name -> id
    options = {}
    for opt in options_list:
        opt_name = opt.get("name")
        opt_id = opt.get("id")
        if opt_name and opt_id:
            options[opt_name] = opt_id

    return StatusFieldInfo(
        project_id=project_id,
        field_id=field_id,
        options=options,
    )


@dataclass
class ProjectItemInfo:
    """Information about a project item (issue linked to project).

    Attributes:
        item_id: The GraphQL ID of the project item
        issue_number: The issue number
        current_status: The current Status field value, if set
    """

    item_id: str
    issue_number: int
    current_status: str | None


def _find_project_item(
    config: ProjectConfig, issue_number: int
) -> ProjectItemInfo | GhError:
    """Find the project item ID for a given issue number.

    Args:
        config: Project configuration
        issue_number: Issue number to find

    Returns:
        ProjectItemInfo if found, GhError if not found or API error
    """
    query = FIND_PROJECT_ITEM_QUERY.format(owner_type=config.owner_type)
    cursor: str | None = None

    while True:
        result = _execute_graphql(
            query,
            {"owner": config.owner, "number": config.number, "cursor": cursor},
        )

        if not result.success:
            assert result.error is not None
            return result.error

        assert result.data is not None
        data = result.data.get("data", {})

        # Navigate to project data
        owner_data = data.get(config.owner_type, {})
        project_data = owner_data.get("projectV2")

        if not project_data:
            return GhError(
                code=API_ERROR,
                message="Project not found",
                details=f"Could not find project #{config.number} for "
                f"{config.owner_type} '{config.owner}'.",
            )

        items_data = project_data.get("items", {})
        nodes = items_data.get("nodes", [])

        for node in nodes:
            content = node.get("content")
            if not content:
                continue

            node_issue_number = content.get("number")
            if node_issue_number == issue_number:
                # Found the issue - extract current status
                item_id = node.get("id")
                field_values = node.get("fieldValues", {}).get("nodes", [])
                current_status = _extract_field_value(field_values, "Status")

                return ProjectItemInfo(
                    item_id=item_id,
                    issue_number=issue_number,
                    current_status=current_status,
                )

        # Check for more pages
        page_info = items_data.get("pageInfo", {})
        if not page_info.get("hasNextPage", False):
            break
        cursor = page_info.get("endCursor")

    # Issue not found in project
    return GhError(
        code=ISSUE_NOT_IN_PROJECT,
        message=f"Issue #{issue_number} not linked to project",
        details=f"Issue #{issue_number} is not linked to project #{config.number}. "
        f"Use 'add-to-project {issue_number}' to add it first.",
    )


def _update_project_item_status(
    project_id: str, item_id: str, field_id: str, option_id: str
) -> GraphQLResult:
    """Update the status field of a project item.

    Args:
        project_id: GraphQL ID of the project
        item_id: GraphQL ID of the project item
        field_id: GraphQL ID of the Status field
        option_id: GraphQL ID of the status option to set

    Returns:
        GraphQLResult with mutation response
    """
    return _execute_graphql(
        UPDATE_PROJECT_ITEM_FIELD_MUTATION,
        {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "optionId": option_id,
        },
    )


def cmd_set_status(args: argparse.Namespace) -> None:
    """Update the Status field of an issue in the project.

    Sets the issue's Status field to the specified value. The status must
    be a valid option defined in the project's Status field configuration.

    Args:
        args: Parsed CLI arguments including:
            - number: Issue number to update
            - status: New status value to set
            - config: Optional path to config file

    Output (success):
        {
            "success": true,
            "data": {
                "number": 42,
                "previous_status": "Ready",
                "new_status": "In Progress"
            }
        }

    Error codes:
        - CONFIG_INVALID: Invalid issue number (zero or negative)
        - FIELD_NOT_FOUND: Status field doesn't exist in project
        - STATUS_INVALID: Requested status value not in field options
        - ISSUE_NOT_IN_PROJECT: Issue not linked to the project
    """
    # Validate issue number is positive
    if args.number <= 0:
        output_error(
            CONFIG_INVALID,
            f"Invalid issue number: {args.number}",
            "Issue number must be a positive integer.",
        )

    config = load_config(args.config)
    new_status = args.status

    # Step 1: Get Status field info and validate the requested status
    status_info = _get_status_field_info(config)
    if isinstance(status_info, GhError):
        output_error(status_info.code, status_info.message, status_info.details)

    # Validate requested status exists in field options
    if new_status not in status_info.options:
        valid_options = ", ".join(sorted(status_info.options.keys()))
        output_error(
            STATUS_INVALID,
            f"Invalid status value: '{new_status}'",
            f"Status must be one of: {valid_options}",
        )

    option_id = status_info.options[new_status]

    # Step 2: Find the project item for this issue
    item_info = _find_project_item(config, args.number)
    if isinstance(item_info, GhError):
        output_error(item_info.code, item_info.message, item_info.details)

    previous_status = item_info.current_status

    # Step 3: Update the status
    result = _update_project_item_status(
        status_info.project_id,
        item_info.item_id,
        status_info.field_id,
        option_id,
    )

    if not result.success:
        assert result.error is not None
        output_error(result.error.code, result.error.message, result.error.details)

    # Success - return previous and new status
    output_success(
        {
            "number": args.number,
            "previous_status": previous_status,
            "new_status": new_status,
        }
    )


def cmd_add_to_project(args: argparse.Namespace) -> None:
    """Add an existing repository issue to the configured project.

    Looks up the issue in the repository, then adds it to the project
    via GraphQL mutation. Requires the repository field in config.

    Args:
        args: Parsed CLI arguments including:
            - number: Issue number to add to the project
            - config: Optional path to config file

    Output (success):
        {
            "success": true,
            "data": {
                "number": 42,
                "item_id": "PVTI_xxxx"
            }
        }

    Error codes:
        - CONFIG_INVALID: Missing repository field or invalid issue number
        - ISSUE_NOT_FOUND: Issue doesn't exist in the repository
        - API_ERROR: Project not found or other API errors
    """
    # Validate issue number is positive
    if args.number <= 0:
        output_error(
            CONFIG_INVALID,
            f"Invalid issue number: {args.number}",
            "Issue number must be a positive integer.",
        )

    config = load_config(args.config)

    # Repository field is required for this operation
    if not config.repository:
        output_error(
            CONFIG_INVALID,
            "Missing 'repository' field in configuration",
            "The add-to-project operation requires a repository field in config.\n"
            "Add the repository to .compass-rose/config.json:\n\n"
            '{\n  "project": {\n    "owner": "owner-name",\n'
            '    "owner_type": "user",\n    "number": 8,\n'
            '    "repository": "repo-name"\n  }\n}',
        )

    # Parse repository into owner/repo parts
    # The config stores just the repo name, and owner is the project owner
    repo_owner = config.owner
    repo_name = config.repository

    # If repository contains a slash, it's a full owner/repo format
    if "/" in config.repository:
        parts = config.repository.split("/", 1)
        repo_owner = parts[0]
        repo_name = parts[1]

    # Step 1: Get the issue's node ID from the repository
    issue_info = _get_issue_node_id(repo_owner, repo_name, args.number)
    if isinstance(issue_info, GhError):
        output_error(issue_info.code, issue_info.message, issue_info.details)

    # Step 2: Get the project ID
    project_id = _get_project_id(config)
    if isinstance(project_id, GhError):
        output_error(project_id.code, project_id.message, project_id.details)

    # Step 3: Add the issue to the project
    result = _add_issue_to_project(project_id, issue_info.node_id)
    if not result.success:
        assert result.error is not None
        output_error(result.error.code, result.error.message, result.error.details)

    # Extract item ID from response
    assert result.data is not None
    item_data = result.data.get("data", {}).get("addProjectV2ItemById", {}).get("item", {})
    item_id = item_data.get("id", "")

    output_success(
        {
            "number": args.number,
            "item_id": item_id,
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
