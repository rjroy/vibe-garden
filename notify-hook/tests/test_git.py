"""
Unit tests for git.py (repository detection and topic generation).
"""

import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from git import get_repo_info, parse_git_url, generate_topic


class TestParseGitUrl:
    """Test git URL parsing."""

    def test_parse_https_github(self):
        """Test parsing HTTPS GitHub URL."""
        url = "https://github.com/owner/repo.git"
        owner, repo = parse_git_url(url)
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_https_github_no_git_suffix(self):
        """Test parsing HTTPS GitHub URL without .git suffix."""
        url = "https://github.com/owner/repo"
        owner, repo = parse_git_url(url)
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_ssh_github(self):
        """Test parsing SSH GitHub URL."""
        url = "git@github.com:owner/repo.git"
        owner, repo = parse_git_url(url)
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_ssh_github_no_git_suffix(self):
        """Test parsing SSH GitHub URL without .git suffix."""
        url = "git@github.com:owner/repo"
        owner, repo = parse_git_url(url)
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_https_gitlab(self):
        """Test parsing HTTPS GitLab URL."""
        url = "https://gitlab.com/owner/repo.git"
        owner, repo = parse_git_url(url)
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_ssh_gitlab(self):
        """Test parsing SSH GitLab URL."""
        url = "git@gitlab.com:owner/repo.git"
        owner, repo = parse_git_url(url)
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_https_custom_domain(self):
        """Test parsing HTTPS URL with custom domain."""
        url = "https://git.company.com/team/project.git"
        owner, repo = parse_git_url(url)
        assert owner == "team"
        assert repo == "project"

    def test_parse_ssh_custom_domain(self):
        """Test parsing SSH URL with custom domain."""
        url = "git@git.company.com:team/project.git"
        owner, repo = parse_git_url(url)
        assert owner == "team"
        assert repo == "project"

    def test_parse_unknown_format(self, capsys):
        """Test parsing unknown URL format returns fallback."""
        url = "file:///local/path/to/repo"
        owner, repo = parse_git_url(url)
        assert owner == "unknown"
        assert repo == "unknown"

        # Should log warning
        captured = capsys.readouterr()
        assert "Unrecognized git remote URL format" in captured.err

    def test_parse_empty_url(self):
        """Test parsing empty URL returns fallback."""
        url = ""
        owner, repo = parse_git_url(url)
        assert owner == "unknown"
        assert repo == "unknown"

    def test_parse_with_hyphenated_names(self):
        """Test parsing URLs with hyphenated owner/repo names."""
        url = "https://github.com/my-org/my-repo.git"
        owner, repo = parse_git_url(url)
        assert owner == "my-org"
        assert repo == "my-repo"

    def test_parse_with_underscored_names(self):
        """Test parsing URLs with underscored owner/repo names."""
        url = "git@github.com:my_org/my_repo.git"
        owner, repo = parse_git_url(url)
        assert owner == "my_org"
        assert repo == "my_repo"


class TestGetRepoInfo:
    """Test repository info extraction."""

    def test_get_repo_info_success(self):
        """Test successful extraction of repo info."""
        mock_result = mock.Mock()
        mock_result.stdout = "https://github.com/user/project.git\n"

        with mock.patch('subprocess.run', return_value=mock_result) as mock_run:
            owner, repo = get_repo_info()

            # Verify subprocess was called correctly
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ['git', 'remote', 'get-url', 'origin']

            # Verify result
            assert owner == "user"
            assert repo == "project"

    def test_get_repo_info_not_in_git_repo(self, capsys):
        """Test fallback when not in a git repository."""
        with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(128, 'git')):
            owner, repo = get_repo_info()

            # Should return fallback
            assert owner == "unknown"
            assert repo == "unknown"

            # Should log warning
            captured = capsys.readouterr()
            assert "Not in a git repository" in captured.err

    def test_get_repo_info_timeout(self, capsys):
        """Test fallback when git command times out."""
        with mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('git', 5)):
            owner, repo = get_repo_info()

            # Should return fallback
            assert owner == "unknown"
            assert repo == "unknown"

            # Should log warning
            captured = capsys.readouterr()
            assert "Git command timed out" in captured.err

    def test_get_repo_info_other_exception(self, capsys):
        """Test fallback when unexpected exception occurs."""
        with mock.patch('subprocess.run', side_effect=RuntimeError("Unexpected error")):
            owner, repo = get_repo_info()

            # Should return fallback
            assert owner == "unknown"
            assert repo == "unknown"

            # Should log warning
            captured = capsys.readouterr()
            assert "Failed to get git info" in captured.err


class TestGenerateTopic:
    """Test topic generation."""

    def test_generate_topic_with_explicit_params(self):
        """Test topic generation with explicit owner and repo."""
        topic = generate_topic("myuser", "myrepo")
        assert topic == "claude-myuser-myrepo"

    def test_generate_topic_auto_detect(self):
        """Test topic generation with auto-detection."""
        mock_result = mock.Mock()
        mock_result.stdout = "https://github.com/autouser/autorepo.git\n"

        with mock.patch('subprocess.run', return_value=mock_result):
            topic = generate_topic()
            assert topic == "claude-autouser-autorepo"

    def test_generate_topic_fallback(self):
        """Test topic generation with fallback when git fails."""
        with mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(128, 'git')):
            topic = generate_topic()
            assert topic == "claude-unknown-unknown"

    def test_generate_topic_partial_params(self):
        """Test topic generation when only one param is None."""
        # When one is None, both should be auto-detected
        mock_result = mock.Mock()
        mock_result.stdout = "https://github.com/detected/repo.git\n"

        with mock.patch('subprocess.run', return_value=mock_result):
            topic = generate_topic(owner="explicit", repo=None)
            assert topic == "claude-detected-repo"

            topic = generate_topic(owner=None, repo="explicit")
            assert topic == "claude-detected-repo"

    def test_generate_topic_with_special_chars(self):
        """Test topic generation with hyphens and underscores."""
        topic = generate_topic("my-org", "my_project")
        assert topic == "claude-my-org-my_project"
