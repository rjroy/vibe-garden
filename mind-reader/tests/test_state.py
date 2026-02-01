"""
Unit tests for state.py (paths, atomic writes, session/baseline management).
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from core.state import (
    Baseline,
    SessionState,
    acquire_baseline_lock,
    cleanup_old_sessions,
    get_baseline_path,
    get_data_dir,
    get_session_path,
    is_baseline_locked,
    read_baseline,
    read_session_state,
    release_baseline_lock,
    write_baseline,
    write_session_state,
)


class TestSessionState:
    """Test SessionState data class."""

    def test_to_dict(self):
        """Test serialization to dict."""
        now = datetime.now()
        state = SessionState(
            session_id="test-123",
            started_at=now,
            prompt_count=5,
            sentiment_scores=[-0.1, 0.2],
            last_nudge_prompt=3,
        )
        d = state.to_dict()
        assert d["session_id"] == "test-123"
        assert d["prompt_count"] == 5
        assert d["sentiment_scores"] == [-0.1, 0.2]
        assert d["last_nudge_prompt"] == 3
        assert "started_at" in d

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {
            "session_id": "test-456",
            "started_at": "2026-01-31T10:00:00",
            "prompt_count": 10,
            "sentiment_scores": [0.5],
            "last_nudge_prompt": None,
        }
        state = SessionState.from_dict(d)
        assert state.session_id == "test-456"
        assert state.prompt_count == 10
        assert state.sentiment_scores == [0.5]
        assert state.last_nudge_prompt is None

    def test_from_dict_with_defaults(self):
        """Test deserialization with missing fields."""
        d = {"session_id": "test-789"}
        state = SessionState.from_dict(d)
        assert state.session_id == "test-789"
        assert state.prompt_count == 0
        assert state.sentiment_scores == []
        assert state.last_nudge_prompt is None


class TestBaseline:
    """Test Baseline data class."""

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {
            "computed_at": "2026-01-31T03:00:00",
            "session_duration_minutes": {"median": 41, "p75": 90, "p95": 180},
            "prompts_per_session": {"median": 5, "p75": 12, "p95": 30},
            "typical_hours": [9, 10, 17, 18, 19],
            "typical_days": ["Monday", "Tuesday"],
            "insufficient_data": False,
        }
        baseline = Baseline.from_dict(d)
        assert baseline.session_duration_minutes["p95"] == 180
        assert baseline.typical_hours == [9, 10, 17, 18, 19]
        assert baseline.insufficient_data is False

    def test_is_stale_when_fresh(self):
        """Test baseline is not stale when recently computed."""
        d = {
            "computed_at": datetime.now().isoformat(),
            "session_duration_minutes": {},
            "prompts_per_session": {},
            "typical_hours": [],
            "typical_days": [],
        }
        baseline = Baseline.from_dict(d)
        assert baseline.is_stale() is False

    def test_is_stale_when_old(self):
        """Test baseline is stale when older than 14 days."""
        old_date = datetime.now() - timedelta(days=15)
        d = {
            "computed_at": old_date.isoformat(),
            "session_duration_minutes": {},
            "prompts_per_session": {},
            "typical_hours": [],
            "typical_days": [],
        }
        baseline = Baseline.from_dict(d)
        assert baseline.is_stale() is True


class TestPathFunctions:
    """Test path utility functions."""

    def test_get_data_dir(self):
        """Test data directory path."""
        with mock.patch("pathlib.Path.home", return_value=Path("/home/test")):
            assert get_data_dir() == Path("/home/test/.claude/mind-reader")

    def test_get_baseline_path(self):
        """Test baseline file path."""
        with mock.patch("pathlib.Path.home", return_value=Path("/home/test")):
            assert get_baseline_path() == Path(
                "/home/test/.claude/mind-reader/baseline.json"
            )

    def test_get_session_path(self):
        """Test session file path."""
        with mock.patch("pathlib.Path.home", return_value=Path("/home/test")):
            assert get_session_path("abc123") == Path(
                "/home/test/.claude/mind-reader/sessions/abc123.json"
            )


class TestLockFunctions:
    """Test lock file functions."""

    def test_acquire_and_release_lock(self, tmp_path):
        """Test acquiring and releasing lock."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            # Initially not locked
            assert is_baseline_locked() is False

            # Acquire lock
            assert acquire_baseline_lock() is True
            assert is_baseline_locked() is True

            # Can't acquire again
            assert acquire_baseline_lock() is False

            # Release lock
            release_baseline_lock()
            assert is_baseline_locked() is False

            # Can acquire again
            assert acquire_baseline_lock() is True
            release_baseline_lock()


class TestBaselineReadWrite:
    """Test baseline read/write functions."""

    def test_read_missing_baseline(self, tmp_path):
        """Test reading non-existent baseline returns None."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            assert read_baseline() is None

    def test_write_and_read_baseline(self, tmp_path):
        """Test writing and reading baseline."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            baseline_data = {
                "computed_at": datetime.now().isoformat(),
                "session_duration_minutes": {"median": 30, "p75": 60, "p95": 120},
                "prompts_per_session": {"median": 5, "p75": 10, "p95": 20},
                "typical_hours": [9, 10, 11],
                "typical_days": ["Monday"],
                "insufficient_data": False,
            }

            assert write_baseline(baseline_data) is True

            baseline = read_baseline()
            assert baseline is not None
            assert baseline.session_duration_minutes["median"] == 30
            assert baseline.typical_hours == [9, 10, 11]

    def test_atomic_write_creates_directory(self, tmp_path):
        """Test write_baseline creates directory if needed."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            # Directory doesn't exist yet
            assert not (tmp_path / ".claude" / "mind-reader").exists()

            write_baseline({"computed_at": datetime.now().isoformat()})

            # Directory should now exist
            assert (tmp_path / ".claude" / "mind-reader").exists()


class TestSessionStateReadWrite:
    """Test session state read/write functions."""

    def test_read_missing_session(self, tmp_path):
        """Test reading non-existent session returns None."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            assert read_session_state("nonexistent") is None

    def test_write_and_read_session(self, tmp_path):
        """Test writing and reading session state."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            state = SessionState(
                session_id="test-session",
                started_at=datetime.now(),
                prompt_count=7,
                sentiment_scores=[-0.3, 0.1],
                last_nudge_prompt=5,
            )

            assert write_session_state(state) is True

            loaded = read_session_state("test-session")
            assert loaded is not None
            assert loaded.session_id == "test-session"
            assert loaded.prompt_count == 7
            assert loaded.sentiment_scores == [-0.3, 0.1]

    def test_session_isolation(self, tmp_path):
        """Test two sessions don't share state."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            state1 = SessionState(
                session_id="session-1",
                started_at=datetime.now(),
                prompt_count=10,
            )
            state2 = SessionState(
                session_id="session-2",
                started_at=datetime.now(),
                prompt_count=20,
            )

            write_session_state(state1)
            write_session_state(state2)

            loaded1 = read_session_state("session-1")
            loaded2 = read_session_state("session-2")

            assert loaded1.prompt_count == 10
            assert loaded2.prompt_count == 20


class TestCleanupOldSessions:
    """Test cleanup_old_sessions function."""

    def test_cleanup_removes_old_files(self, tmp_path):
        """Test old session files are removed."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            sessions_dir = tmp_path / ".claude" / "mind-reader" / "sessions"
            sessions_dir.mkdir(parents=True)

            # Create an old file (manually set mtime)
            old_file = sessions_dir / "old-session.json"
            old_file.write_text("{}")
            old_time = datetime.now() - timedelta(days=10)
            os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))

            # Create a recent file
            new_file = sessions_dir / "new-session.json"
            new_file.write_text("{}")

            removed = cleanup_old_sessions(max_age_days=7)

            assert removed == 1
            assert not old_file.exists()
            assert new_file.exists()

    def test_cleanup_handles_missing_directory(self, tmp_path):
        """Test cleanup handles missing sessions directory."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            removed = cleanup_old_sessions()
            assert removed == 0
