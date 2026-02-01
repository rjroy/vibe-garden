"""
Unit tests for baseline.py (baseline computation).
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scripts.baseline import (
    compute_baseline,
    compute_baseline_v2,
    compute_bucket_percentiles,
    compute_bucket_stats,
    compute_hourly_counts,
    compute_percentiles,
    compute_session_metrics,
    compute_typical_hours,
    group_by_session,
    parse_history,
    should_recompute_boundaries,
)


@pytest.fixture
def sample_history(tmp_path):
    """Create a sample history file for testing."""
    history_file = tmp_path / "history.jsonl"

    # Create 15 sessions with varied data
    entries = []
    base_time = datetime.now() - timedelta(days=30)

    for session_idx in range(15):
        session_id = f"session-{session_idx}"
        session_start = base_time + timedelta(days=session_idx)

        # Each session has 5-20 prompts
        num_prompts = 5 + (session_idx % 16)

        for prompt_idx in range(num_prompts):
            # Spread prompts over 1-3 hours
            prompt_time = session_start + timedelta(minutes=prompt_idx * 10)

            # Vary the hour (9-20 for most, 2-4 for a few to test unusual hours)
            hour = 9 + (session_idx % 12) if session_idx < 12 else 2 + session_idx % 3

            # Override the hour
            prompt_time = prompt_time.replace(hour=hour)

            entries.append(
                {
                    "sessionId": session_id,
                    "timestamp": int(prompt_time.timestamp() * 1000),
                    "type": "user_prompt",
                    "content": f"Prompt {prompt_idx} of session {session_idx}",
                }
            )

    # Write history file
    with open(history_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    return history_file


class TestParseHistory:
    """Test parse_history function."""

    def test_parse_valid_jsonl(self, tmp_path):
        """Test parsing valid JSONL file."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text(
            '{"sessionId": "s1", "timestamp": 1000}\n'
            '{"sessionId": "s2", "timestamp": 2000}\n'
        )

        entries = parse_history(history_file)
        assert len(entries) == 2
        assert entries[0]["sessionId"] == "s1"
        assert entries[1]["sessionId"] == "s2"

    def test_parse_with_empty_lines(self, tmp_path):
        """Test parsing handles empty lines."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text(
            '{"sessionId": "s1"}\n' "\n" '{"sessionId": "s2"}\n' "\n"
        )

        entries = parse_history(history_file)
        assert len(entries) == 2

    def test_parse_with_invalid_lines(self, tmp_path, capsys):
        """Test parsing skips invalid JSON lines."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text(
            '{"sessionId": "s1"}\n' "not json\n" '{"sessionId": "s2"}\n'
        )

        entries = parse_history(history_file)
        assert len(entries) == 2

        captured = capsys.readouterr()
        assert "invalid json" in captured.err.lower()


class TestGroupBySession:
    """Test group_by_session function."""

    def test_groups_entries(self):
        """Test entries are grouped by session ID."""
        entries = [
            {"sessionId": "s1", "content": "a"},
            {"sessionId": "s2", "content": "b"},
            {"sessionId": "s1", "content": "c"},
        ]

        sessions = group_by_session(entries)

        assert len(sessions) == 2
        assert len(sessions["s1"]) == 2
        assert len(sessions["s2"]) == 1

    def test_skips_entries_without_session_id(self):
        """Test entries without sessionId are skipped."""
        entries = [
            {"sessionId": "s1"},
            {"content": "no session"},
            {"sessionId": "", "content": "empty session"},
        ]

        sessions = group_by_session(entries)
        assert len(sessions) == 1
        assert "s1" in sessions


class TestComputeSessionMetrics:
    """Test compute_session_metrics function."""

    def test_computes_durations_and_counts(self):
        """Test duration and prompt count computation."""
        now = datetime.now()

        sessions = {
            "s1": [
                {"timestamp": int(now.timestamp() * 1000)},
                {"timestamp": int((now + timedelta(minutes=30)).timestamp() * 1000)},
                {"timestamp": int((now + timedelta(minutes=60)).timestamp() * 1000)},
            ],
            "s2": [
                {"timestamp": int(now.timestamp() * 1000)},
                {"timestamp": int((now + timedelta(minutes=15)).timestamp() * 1000)},
            ],
        }

        durations, prompt_counts = compute_session_metrics(sessions)

        assert len(durations) == 2
        assert len(prompt_counts) == 2

        assert 3 in prompt_counts
        assert 2 in prompt_counts

        # Duration should be ~60 minutes for s1
        assert any(55 <= d <= 65 for d in durations)
        # Duration should be ~15 minutes for s2
        assert any(10 <= d <= 20 for d in durations)

    def test_single_prompt_session(self):
        """Test sessions with single prompt."""
        now = datetime.now()

        sessions = {
            "s1": [{"timestamp": int(now.timestamp() * 1000)}],
        }

        durations, prompt_counts = compute_session_metrics(sessions)

        assert prompt_counts == [1]
        assert durations == [0.0]


class TestComputePercentiles:
    """Test compute_percentiles function."""

    def test_empty_list(self):
        """Test empty list returns zeros."""
        result = compute_percentiles([])
        assert result == {"median": 0, "p75": 0, "p95": 0}

    def test_single_value(self):
        """Test single value."""
        result = compute_percentiles([50.0])
        assert result["median"] == 50.0
        assert result["p75"] == 50.0
        assert result["p95"] == 50.0

    def test_multiple_values(self):
        """Test percentile computation."""
        # 100 values from 1 to 100
        values = [float(i) for i in range(1, 101)]
        result = compute_percentiles(values)

        assert 49 <= result["median"] <= 51
        assert 74 <= result["p75"] <= 76
        assert 94 <= result["p95"] <= 96


class TestComputeTypicalHours:
    """Test compute_typical_hours function."""

    def test_finds_top_hours(self):
        """Test identifies hours with most activity."""
        now = datetime.now()
        entries = []

        # Create entries with activity concentrated in hours 9-17
        for hour in range(9, 18):
            for _ in range(10):  # 10 prompts per hour
                dt = now.replace(hour=hour, minute=0)
                entries.append({"timestamp": int(dt.timestamp() * 1000)})

        # Add a few entries at unusual hours
        for hour in [2, 3, 23]:
            dt = now.replace(hour=hour, minute=0)
            entries.append({"timestamp": int(dt.timestamp() * 1000)})

        typical = compute_typical_hours(entries)

        # Should include the busy hours
        assert 9 in typical
        assert 10 in typical
        # Should not include the sparse hours
        assert 2 not in typical
        assert 23 not in typical

    def test_empty_entries(self):
        """Test empty entries returns empty list."""
        assert compute_typical_hours([]) == []


class TestComputeBaseline:
    """Test compute_baseline function."""

    def test_computes_full_baseline(self, sample_history):
        """Test full baseline computation."""
        baseline = compute_baseline(sample_history)

        assert "computed_at" in baseline
        assert "session_duration_minutes" in baseline
        assert "prompts_per_session" in baseline
        assert "typical_hours" in baseline
        assert baseline["insufficient_data"] is False

        # Check percentiles exist
        assert "median" in baseline["session_duration_minutes"]
        assert "p75" in baseline["session_duration_minutes"]
        assert "p95" in baseline["session_duration_minutes"]

    def test_insufficient_data_flag(self, tmp_path):
        """Test insufficient_data flag with few sessions."""
        history_file = tmp_path / "history.jsonl"

        # Only 5 sessions (below minimum of 10)
        entries = []
        for i in range(5):
            entries.append(
                {
                    "sessionId": f"s{i}",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                }
            )

        with open(history_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        baseline = compute_baseline(history_file)
        assert baseline["insufficient_data"] is True

    def test_includes_v2_data(self, sample_history):
        """Test baseline includes v2 bucket data."""
        baseline = compute_baseline(sample_history)

        # V2 fields should be present
        assert "window_days" in baseline
        assert "days" in baseline
        assert "global_stats" in baseline

        # Days should have all 7 days
        assert len(baseline["days"]) == 7
        assert "monday" in baseline["days"]
        assert "sunday" in baseline["days"]

        # Each day should have boundaries and buckets
        for _day_name, day_data in baseline["days"].items():
            assert "boundaries" in day_data
            assert "buckets" in day_data
            assert len(day_data["boundaries"]) == 4


# ============================================================================
# V2 Baseline Tests
# ============================================================================


class TestComputeHourlyCounts:
    """Test compute_hourly_counts function."""

    def test_counts_by_day(self):
        """Test counts prompts per hour for specific day."""
        # Create entries on Monday at different hours
        monday = datetime(2026, 1, 26, 10, 0)  # A Monday
        entries = [
            {"timestamp": int(monday.replace(hour=9).timestamp() * 1000)},
            {"timestamp": int(monday.replace(hour=9).timestamp() * 1000)},
            {"timestamp": int(monday.replace(hour=10).timestamp() * 1000)},
            {"timestamp": int(monday.replace(hour=14).timestamp() * 1000)},
        ]

        counts = compute_hourly_counts(entries, "Monday")

        assert counts[9] == 2
        assert counts[10] == 1
        assert counts[14] == 1
        assert sum(counts) == 4

    def test_filters_to_day(self):
        """Test only counts entries for specified day."""
        monday = datetime(2026, 1, 26, 10, 0)  # Monday
        tuesday = datetime(2026, 1, 27, 10, 0)  # Tuesday

        entries = [
            {"timestamp": int(monday.timestamp() * 1000)},
            {"timestamp": int(tuesday.timestamp() * 1000)},
        ]

        monday_counts = compute_hourly_counts(entries, "Monday")
        tuesday_counts = compute_hourly_counts(entries, "Tuesday")

        assert sum(monday_counts) == 1
        assert sum(tuesday_counts) == 1

    def test_case_insensitive_day(self):
        """Test day name is case insensitive."""
        monday = datetime(2026, 1, 26, 10, 0)
        entries = [{"timestamp": int(monday.timestamp() * 1000)}]

        assert compute_hourly_counts(entries, "monday") == compute_hourly_counts(
            entries, "MONDAY"
        )


class TestComputeBucketPercentiles:
    """Test compute_bucket_percentiles function."""

    def test_empty_returns_zeros(self):
        """Test empty list returns zeros."""
        result = compute_bucket_percentiles([])
        assert result == {"p50": 0, "p75": 0, "p90": 0}

    def test_single_value(self):
        """Test single value."""
        result = compute_bucket_percentiles([30.0])
        assert result["p50"] == 30.0
        assert result["p75"] == 30.0
        assert result["p90"] == 30.0

    def test_percentiles(self):
        """Test percentile computation."""
        values = [float(i) for i in range(1, 101)]  # 1-100
        result = compute_bucket_percentiles(values)

        assert 49 <= result["p50"] <= 51
        assert 74 <= result["p75"] <= 76
        assert 89 <= result["p90"] <= 91


class TestComputeBucketStats:
    """Test compute_bucket_stats function."""

    def test_computes_session_rate(self):
        """Test session rate calculation."""
        monday = datetime(2026, 1, 26, 10, 0)  # Monday, morning
        sessions = {
            "s1": [
                {"timestamp": int(monday.timestamp() * 1000)},
                {"timestamp": int((monday + timedelta(minutes=30)).timestamp() * 1000)},
            ],
            "s2": [
                {"timestamp": int(monday.replace(hour=11).timestamp() * 1000)},
            ],
        }

        boundaries = [6, 12, 18, 22]
        window_days = 42  # 6 weeks = ~6 Mondays

        stats = compute_bucket_stats(sessions, "Monday", boundaries, window_days)

        # Both sessions in early_morning bucket (6-12)
        early_morning = stats["early_morning"]
        assert early_morning["session_count"] == 2
        # 2 sessions / 6 day instances = 0.333
        assert 0.3 <= early_morning["session_rate"] <= 0.4

    def test_zero_sessions_bucket(self):
        """Test bucket with zero sessions."""
        sessions = {}  # No sessions
        boundaries = [6, 12, 18, 22]

        stats = compute_bucket_stats(sessions, "Monday", boundaries, 42)

        for _bucket_name, bucket_stats in stats.items():
            assert bucket_stats["session_count"] == 0
            assert bucket_stats["session_rate"] == 0.0


class TestShouldRecomputeBoundaries:
    """Test should_recompute_boundaries function."""

    def test_none_baseline_returns_true(self):
        """Test None baseline triggers recompute."""
        assert should_recompute_boundaries(None) is True

    def test_missing_field_returns_true(self):
        """Test missing boundaries_computed_at triggers recompute."""
        baseline = {"computed_at": datetime.now().isoformat()}
        assert should_recompute_boundaries(baseline) is True

    def test_recent_boundaries_returns_false(self):
        """Test recent boundaries don't trigger recompute."""
        baseline = {
            "boundaries_computed_at": datetime.now().isoformat(),
        }
        assert should_recompute_boundaries(baseline) is False

    def test_stale_boundaries_returns_true(self):
        """Test stale boundaries (>7 days) trigger recompute."""
        old = datetime.now() - timedelta(days=10)
        baseline = {
            "boundaries_computed_at": old.isoformat(),
        }
        assert should_recompute_boundaries(baseline) is True


class TestComputeBaselineV2:
    """Test compute_baseline_v2 function."""

    def test_computes_all_days(self, sample_history):
        """Test computes stats for all 7 days."""
        result = compute_baseline_v2(sample_history)

        assert "days" in result
        assert len(result["days"]) == 7

        day_names = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in day_names:
            assert day in result["days"]

    def test_includes_global_stats(self, sample_history):
        """Test includes global statistics."""
        result = compute_baseline_v2(sample_history)

        assert "global_stats" in result
        assert "session_count" in result["global_stats"]
        assert "duration" in result["global_stats"]

    def test_respects_window_days(self, tmp_path):
        """Test only includes entries within window."""
        history_file = tmp_path / "history.jsonl"

        now = datetime.now()
        old = now - timedelta(days=100)  # Outside default 42-day window

        entries = [
            {"sessionId": "recent", "timestamp": int(now.timestamp() * 1000)},
            {"sessionId": "old", "timestamp": int(old.timestamp() * 1000)},
        ]

        with open(history_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = compute_baseline_v2(history_file, window_days=42)

        # Should only count 1 session (the recent one)
        assert result["global_stats"]["session_count"] == 1
