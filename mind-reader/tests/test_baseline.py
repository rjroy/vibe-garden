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
    compute_percentiles,
    compute_session_metrics,
    compute_typical_days,
    compute_typical_hours,
    group_by_session,
    parse_history,
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


class TestComputeTypicalDays:
    """Test compute_typical_days function."""

    def test_finds_typical_days(self):
        """Test identifies days with most activity."""
        entries = []
        base = datetime(2026, 1, 26)  # A Monday

        # Heavy activity on weekdays (Mon-Fri)
        for day_offset in range(5):
            dt = base + timedelta(days=day_offset)
            for _ in range(20):
                entries.append({"timestamp": int(dt.timestamp() * 1000)})

        # Light activity on weekend (Sat-Sun)
        for day_offset in [5, 6]:
            dt = base + timedelta(days=day_offset)
            for _ in range(2):
                entries.append({"timestamp": int(dt.timestamp() * 1000)})

        typical = compute_typical_days(entries)

        # Weekdays should be typical (above median of 20)
        assert "Monday" in typical
        assert "Friday" in typical
        # Weekend should not be typical (below median)
        assert "Saturday" not in typical
        assert "Sunday" not in typical

    def test_empty_entries(self):
        """Test empty entries returns empty list."""
        assert compute_typical_days([]) == []


class TestComputeBaseline:
    """Test compute_baseline function."""

    def test_computes_full_baseline(self, sample_history):
        """Test full baseline computation."""
        baseline = compute_baseline(sample_history)

        assert "computed_at" in baseline
        assert "session_duration_minutes" in baseline
        assert "prompts_per_session" in baseline
        assert "typical_hours" in baseline
        assert "typical_days" in baseline
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
