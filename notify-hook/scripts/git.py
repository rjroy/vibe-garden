#!/usr/bin/env python3
"""
Git repository detection for notify-hook plugin.
Extracts repository owner and name from git remote URL.
Stdlib only - no external dependencies.
"""

import re
import subprocess
import sys
from typing import Tuple


def get_repo_info() -> Tuple[str, str]:
    """
    Extract repository owner and name from git remote URL.

    Returns:
        Tuple of (owner, repo) strings.
        Returns ("unknown", "unknown") if not in a git repo or remote not configured.
    """
    try:
        # Execute git command to get remote URL
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        remote_url = result.stdout.strip()

        # Parse owner and repo from URL
        owner, repo = parse_git_url(remote_url)

        return owner, repo

    except subprocess.CalledProcessError:
        # Not in a git repo or no remote configured
        print("Warning: Not in a git repository or no remote configured, using fallback topic", file=sys.stderr)
        return "unknown", "unknown"
    except subprocess.TimeoutExpired:
        print("Warning: Git command timed out, using fallback topic", file=sys.stderr)
        return "unknown", "unknown"
    except Exception as e:
        print(f"Warning: Failed to get git info: {e}, using fallback topic", file=sys.stderr)
        return "unknown", "unknown"


def parse_git_url(url: str) -> Tuple[str, str]:
    """
    Parse owner and repository name from git remote URL.

    Supports:
    - HTTPS: https://github.com/owner/repo.git
    - SSH: git@github.com:owner/repo.git
    - Other formats (GitLab, etc.)

    Args:
        url: Git remote URL

    Returns:
        Tuple of (owner, repo) strings.
        Returns ("unknown", "unknown") if URL format is not recognized.
    """
    # HTTPS format: https://github.com/owner/repo.git
    https_match = re.match(r'https?://[^/]+/([^/]+)/([^/]+?)(?:\.git)?$', url)
    if https_match:
        owner, repo = https_match.groups()
        return owner, repo.replace('.git', '')

    # SSH format: git@github.com:owner/repo.git
    ssh_match = re.match(r'git@[^:]+:([^/]+)/([^/]+?)(?:\.git)?$', url)
    if ssh_match:
        owner, repo = ssh_match.groups()
        return owner, repo.replace('.git', '')

    # Fallback for unknown formats
    print(f"Warning: Unrecognized git remote URL format: {url}", file=sys.stderr)
    return "unknown", "unknown"


def generate_topic(owner: str = None, repo: str = None) -> str:
    """
    Generate ntfy.sh topic from repository info.

    Args:
        owner: Repository owner (optional, will auto-detect if None)
        repo: Repository name (optional, will auto-detect if None)

    Returns:
        Topic string in format: claude-{owner}-{repo}
    """
    if owner is None or repo is None:
        owner, repo = get_repo_info()

    return f"claude-{owner}-{repo}"
