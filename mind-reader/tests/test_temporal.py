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
from core.state import Baseline, BucketStats, DayBaseline, SessionState
from core.temporal import (
    check_bucket_duration,
    check_bucket_rarity,
    check_duration_threshold,
    check_prompt_threshold,
    check_unusual_hour,
    get_current_bucket,
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


# ============================================================================
# V2 Bucket-Based Detection Tests
# ============================================================================


@pytest.fixture
def baseline_v2():
    """Create a v2 baseline with bucket data for testing."""
    # Create bucket stats for different scenarios
    active_bucket = BucketStats(
        session_count=10,
        session_rate=0.24,  # ~24% of days have sessions in this bucket
        duration={"p50": 30, "p75": 60, "p90": 120},
    )

    rare_bucket = BucketStats(
        session_count=2,
        session_rate=0.05,  # ~5% - below default threshold of 0.1
        duration={"p50": 45, "p75": 90, "p90": 180},
    )

    zero_bucket = BucketStats(
        session_count=0,
        session_rate=0.0,
        duration={"p50": 0, "p75": 0, "p90": 0},
    )

    # Create day baselines
    monday = DayBaseline(
        boundaries=[6, 12, 18, 22],
        buckets={
            "late_night": zero_bucket,
            "early_morning": active_bucket,
            "morning": active_bucket,
            "afternoon": rare_bucket,
            "evening": rare_bucket,
        },
    )

    saturday = DayBaseline(
        boundaries=[6, 12, 18, 22],
        buckets={
            "late_night": zero_bucket,
            "early_morning": rare_bucket,
            "morning": rare_bucket,
            "afternoon": rare_bucket,
            "evening": zero_bucket,
        },
    )

    return Baseline(
        computed_at=datetime.now(),
        session_duration_minutes={"median": 30, "p75": 60, "p95": 120},
        prompts_per_session={"median": 5, "p75": 12, "p95": 30},
        typical_hours=[9, 10, 11, 14, 15, 16, 17],
        typical_days=["Monday", "Tuesday", "Wednesday"],
        insufficient_data=False,
        boundaries_computed_at=datetime.now(),
        window_days=42,
        days={
            "monday": monday,
            "tuesday": monday,  # Reuse monday for simplicity
            "wednesday": monday,
            "thursday": monday,
            "friday": monday,
            "saturday": saturday,
            "sunday": saturday,
        },
    )


class TestGetCurrentBucket:
    """Test get_current_bucket function."""

    def test_returns_bucket_for_v2_baseline(self, baseline_v2):
        """Test returns bucket info for v2 baseline."""
        # Monday at 10am (early_morning bucket)
        monday_10am = datetime(2026, 1, 26, 10, 0)

        day, bucket, stats = get_current_bucket(baseline_v2, monday_10am)

        assert day == "monday"
        assert bucket == "early_morning"
        assert stats is not None
        assert stats.session_count == 10

    def test_returns_unknown_for_v1_baseline(self, baseline):
        """Test returns unknown for baseline without v2 data."""
        day, bucket, stats = get_current_bucket(baseline, datetime.now())

        assert stats is None
        assert bucket == "unknown"

    def test_uses_current_time_when_none(self, baseline_v2):
        """Test uses current time when now is None."""
        day, bucket, stats = get_current_bucket(baseline_v2, None)

        # Should return something valid
        assert day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        assert bucket in [
            "late_night",
            "early_morning",
            "morning",
            "afternoon",
            "evening",
        ]


class TestCheckBucketRarity:
    """Test check_bucket_rarity function."""

    def test_no_nudge_common_bucket(self, baseline_v2, settings):
        """Test no nudge for common (high session_rate) bucket."""
        # Monday 10am is early_morning with 0.24 rate (above 0.1 threshold)
        monday_10am = datetime(2026, 1, 26, 10, 0)

        result = check_bucket_rarity(baseline_v2, settings, monday_10am)
        assert result is None

    def test_nudge_rare_bucket(self, baseline_v2, settings):
        """Test nudge for rare bucket (low session_rate)."""
        # Monday 7pm is afternoon bucket with 0.05 rate (below 0.1)
        monday_7pm = datetime(2026, 1, 26, 19, 0)

        result = check_bucket_rarity(baseline_v2, settings, monday_7pm)

        assert result is not None
        assert result.check_type == "bucket_rarity"
        assert "Monday" in result.message
        assert "5%" in result.message or "rare" in result.message.lower()

    def test_nudge_zero_session_bucket(self, baseline_v2, settings):
        """Test nudge for zero-session bucket (maximally rare)."""
        # Monday 3am is late_night with 0 sessions
        monday_3am = datetime(2026, 1, 26, 3, 0)

        result = check_bucket_rarity(baseline_v2, settings, monday_3am)

        assert result is not None
        assert result.check_type == "bucket_rarity"
        assert "no sessions" in result.message.lower()

    def test_respects_disabled_temporal(self, baseline_v2):
        """Test no nudge when temporal is disabled."""
        settings = Settings.from_dict({"temporal": {"enabled": False}})
        monday_3am = datetime(2026, 1, 26, 3, 0)

        result = check_bucket_rarity(baseline_v2, settings, monday_3am)
        assert result is None

    def test_no_nudge_v1_baseline(self, baseline, settings):
        """Test no nudge for v1 baseline (no bucket data)."""
        result = check_bucket_rarity(baseline, settings, datetime.now())
        assert result is None

    def test_respects_custom_threshold(self, baseline_v2):
        """Test respects custom bucket_rarity_threshold."""
        # Set threshold very low so 0.05 rate passes
        settings = Settings.from_dict(
            {"temporal": {"bucket_rarity_threshold": 0.01}}
        )
        monday_7pm = datetime(2026, 1, 26, 19, 0)

        result = check_bucket_rarity(baseline_v2, settings, monday_7pm)
        assert result is None  # 0.05 > 0.01, so no nudge


class TestCheckBucketDuration:
    """Test check_bucket_duration function."""

    def test_no_nudge_below_threshold(self, baseline_v2, settings):
        """Test no nudge when duration below threshold."""
        monday_10am = datetime(2026, 1, 26, 10, 0)

        state = SessionState(
            session_id="test",
            started_at=monday_10am - timedelta(minutes=60),  # 60 min session
            prompt_count=5,
        )

        # p90 for early_morning is 120, session is 60 min
        result = check_bucket_duration(state, baseline_v2, settings, monday_10am)
        assert result is None

    def test_nudge_above_threshold(self, baseline_v2, settings):
        """Test nudge when duration exceeds threshold."""
        monday_10am = datetime(2026, 1, 26, 10, 0)

        state = SessionState(
            session_id="test",
            started_at=monday_10am - timedelta(minutes=150),  # 150 min session
            prompt_count=5,
        )

        # p90 for early_morning is 120, session is 150 min
        result = check_bucket_duration(state, baseline_v2, settings, monday_10am)

        assert result is not None
        assert result.check_type == "bucket_duration"
        assert "150" in result.message
        assert "120" in result.message  # threshold value
        assert "p90" in result.message

    def test_respects_disabled_temporal(self, baseline_v2):
        """Test no nudge when temporal is disabled."""
        settings = Settings.from_dict({"temporal": {"enabled": False}})
        now = datetime(2026, 1, 26, 10, 0)

        state = SessionState(
            session_id="test",
            started_at=now - timedelta(minutes=150),
            prompt_count=5,
        )

        result = check_bucket_duration(state, baseline_v2, settings, now)
        assert result is None

    def test_no_nudge_v1_baseline(self, baseline, settings):
        """Test no nudge for v1 baseline (no bucket data)."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now() - timedelta(minutes=150),
            prompt_count=5,
        )

        result = check_bucket_duration(state, baseline, settings)
        assert result is None

    def test_no_nudge_zero_duration_bucket(self, baseline_v2, settings):
        """Test no nudge when bucket has zero duration threshold."""
        # Saturday evening has zero sessions, so zero duration stats
        saturday_11pm = datetime(2026, 1, 31, 23, 0)

        state = SessionState(
            session_id="test",
            started_at=saturday_11pm - timedelta(minutes=60),
            prompt_count=5,
        )

        result = check_bucket_duration(state, baseline_v2, settings, saturday_11pm)
        assert result is None

    def test_respects_custom_threshold_key(self, baseline_v2):
        """Test respects custom bucket_duration_threshold."""
        settings = Settings.from_dict(
            {"temporal": {"bucket_duration_threshold": "p75"}}
        )

        monday_10am = datetime(2026, 1, 26, 10, 0)

        state = SessionState(
            session_id="test",
            started_at=monday_10am - timedelta(minutes=90),  # 90 min session
            prompt_count=5,
        )

        # p75 for early_morning is 60, session is 90 min
        result = check_bucket_duration(state, baseline_v2, settings, monday_10am)

        assert result is not None
        assert "p75" in result.message


class TestBothChecksFireIndependently:
    """Test that rarity and duration checks fire independently."""

    def test_rarity_nudge_without_duration(self, baseline_v2, settings):
        """Test rarity nudge fires even with short session."""
        # Saturday 3am: rare bucket, short session
        saturday_3am = datetime(2026, 1, 31, 3, 0)

        state = SessionState(
            session_id="test",
            started_at=saturday_3am - timedelta(minutes=5),  # 5 min session
            prompt_count=1,
        )

        rarity = check_bucket_rarity(baseline_v2, settings, saturday_3am)
        duration = check_bucket_duration(state, baseline_v2, settings, saturday_3am)

        assert rarity is not None  # Rare bucket
        assert duration is None  # Short session

    def test_duration_nudge_without_rarity(self, baseline_v2, settings):
        """Test duration nudge fires even in common bucket."""
        # Monday 10am: common bucket, long session
        monday_10am = datetime(2026, 1, 26, 10, 0)

        state = SessionState(
            session_id="test",
            started_at=monday_10am - timedelta(minutes=150),  # Long session
            prompt_count=20,
        )

        rarity = check_bucket_rarity(baseline_v2, settings, monday_10am)
        duration = check_bucket_duration(state, baseline_v2, settings, monday_10am)

        assert rarity is None  # Common bucket
        assert duration is not None  # Long session
