"""
Unit tests for temporal.py (temporal detection logic).
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from core.settings import Settings
from core.state import Baseline, SessionState
from core.temporal import (
    check_duration_threshold,
    check_prompt_threshold,
    check_unusual_hour,
)


@pytest.fixture
def baseline():
    """Create a sample baseline for testing."""
    return Baseline(
        computed_at=datetime.now(),
        session_duration_minutes={"median": 30, "p75": 60, "p95": 120},
        prompts_per_session={"median": 5, "p75": 12, "p95": 30},
        typical_hours=[9, 10, 11, 14, 15, 16, 17],
        typical_days=["Monday", "Tuesday", "Wednesday"],
        insufficient_data=False,
    )


@pytest.fixture
def settings():
    """Create default settings for testing."""
    return Settings.from_dict({})


@pytest.fixture
def session_state():
    """Create a sample session state for testing."""
    return SessionState(
        session_id="test-session",
        started_at=datetime.now(),
        prompt_count=10,
        sentiment_scores=[],
        last_nudge_prompt=None,
    )


class TestCheckDurationThreshold:
    """Test check_duration_threshold function."""

    def test_below_threshold(self, baseline, settings):
        """Test no nudge when duration is below threshold."""
        # Session started 60 minutes ago (below p95 of 120)
        state = SessionState(
            session_id="test",
            started_at=datetime.now() - timedelta(minutes=60),
            prompt_count=5,
        )
        result = check_duration_threshold(state, baseline, settings)
        assert result is None

    def test_above_threshold(self, baseline, settings):
        """Test nudge when duration exceeds threshold."""
        # Session started 150 minutes ago (above p95 of 120)
        state = SessionState(
            session_id="test",
            started_at=datetime.now() - timedelta(minutes=150),
            prompt_count=5,
        )
        result = check_duration_threshold(state, baseline, settings)
        assert result is not None
        assert result.check_type == "duration"
        assert "150" in result.message  # Should mention actual duration
        assert "p95" in result.message  # Should mention threshold key

    def test_disabled_temporal(self, baseline):
        """Test no nudge when temporal is disabled."""
        settings = Settings.from_dict({"temporal": {"enabled": False}})
        state = SessionState(
            session_id="test",
            started_at=datetime.now() - timedelta(minutes=150),
            prompt_count=5,
        )
        result = check_duration_threshold(state, baseline, settings)
        assert result is None

    def test_insufficient_data(self, settings):
        """Test no nudge when baseline has insufficient data."""
        baseline = Baseline(
            computed_at=datetime.now(),
            session_duration_minutes={},
            prompts_per_session={},
            typical_hours=[],
            typical_days=[],
            insufficient_data=True,
        )
        state = SessionState(
            session_id="test",
            started_at=datetime.now() - timedelta(minutes=150),
            prompt_count=5,
        )
        result = check_duration_threshold(state, baseline, settings)
        assert result is None

    def test_custom_threshold_key(self, baseline):
        """Test using p75 instead of p95."""
        settings = Settings.from_dict({"temporal": {"duration_threshold": "p75"}})
        # Session is 90 minutes (above p75 of 60, below p95 of 120)
        state = SessionState(
            session_id="test",
            started_at=datetime.now() - timedelta(minutes=90),
            prompt_count=5,
        )
        result = check_duration_threshold(state, baseline, settings)
        assert result is not None
        assert "p75" in result.message


class TestCheckPromptThreshold:
    """Test check_prompt_threshold function."""

    def test_below_threshold(self, baseline, settings):
        """Test no nudge when prompt count is below threshold."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=20,  # Below p95 of 30
        )
        result = check_prompt_threshold(state, baseline, settings)
        assert result is None

    def test_above_threshold(self, baseline, settings):
        """Test nudge when prompt count exceeds threshold."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=35,  # Above p95 of 30
        )
        result = check_prompt_threshold(state, baseline, settings)
        assert result is not None
        assert result.check_type == "prompts"
        assert "35" in result.message
        assert "p95" in result.message

    def test_disabled_temporal(self, baseline):
        """Test no nudge when temporal is disabled."""
        settings = Settings.from_dict({"temporal": {"enabled": False}})
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=50,
        )
        result = check_prompt_threshold(state, baseline, settings)
        assert result is None


class TestCheckUnusualHour:
    """Test check_unusual_hour function."""

    def test_typical_hour(self, baseline, settings):
        """Test no nudge during typical hours."""
        result = check_unusual_hour(baseline, settings, current_hour=10)
        assert result is None

    def test_unusual_hour(self, baseline, settings):
        """Test nudge during unusual hours."""
        result = check_unusual_hour(baseline, settings, current_hour=3)
        assert result is not None
        assert result.check_type == "hour"
        assert "03:00" in result.message

    def test_check_hours_disabled(self, baseline):
        """Test no nudge when check_hours is disabled."""
        settings = Settings.from_dict({"temporal": {"check_hours": False}})
        result = check_unusual_hour(baseline, settings, current_hour=3)
        assert result is None

    def test_temporal_disabled(self, baseline):
        """Test no nudge when temporal is disabled."""
        settings = Settings.from_dict({"temporal": {"enabled": False}})
        result = check_unusual_hour(baseline, settings, current_hour=3)
        assert result is None

    def test_empty_typical_hours(self, settings):
        """Test no nudge when no typical hours defined."""
        baseline = Baseline(
            computed_at=datetime.now(),
            session_duration_minutes={},
            prompts_per_session={},
            typical_hours=[],
            typical_days=[],
            insufficient_data=False,
        )
        result = check_unusual_hour(baseline, settings, current_hour=3)
        assert result is None

    def test_uses_current_time_when_not_specified(self, baseline, settings):
        """Test uses current time when current_hour is None."""
        current_hour = datetime.now().hour

        # Mock typical_hours to exclude current hour
        baseline.typical_hours = [(current_hour + 12) % 24]

        result = check_unusual_hour(baseline, settings, current_hour=None)
        assert result is not None
        assert result.check_type == "hour"
