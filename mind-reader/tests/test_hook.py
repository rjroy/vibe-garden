"""
Integration tests for hook.py (main hook entry point).
"""

import io
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestHookIntegration:
    """Integration tests for the main hook."""

    def run_hook(self, input_data: dict, tmp_path: Path) -> tuple[str, str, int]:
        """
        Run the hook with given input and return (stdout, stderr, exit_code).
        """
        # Set up mocked home directory
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            # Create data directory
            data_dir = tmp_path / ".claude" / "mind-reader"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "sessions").mkdir(exist_ok=True)

            # Mock stdin with input data
            stdin_data = json.dumps(input_data)

            # Capture stdout/stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            # Mock sys.stdin and exit
            exit_code = [0]

            def mock_exit(code):
                exit_code[0] = code
                raise SystemExit(code)

            with (
                mock.patch("sys.stdin", io.StringIO(stdin_data)),
                mock.patch("sys.stdout", stdout_capture),
                mock.patch("sys.stderr", stderr_capture),
                mock.patch("sys.exit", mock_exit),
            ):
                try:
                    # Import fresh to avoid cached state
                    import importlib

                    import scripts.hook as hook_module

                    importlib.reload(hook_module)
                    hook_module.main()
                except SystemExit:
                    pass

            return (
                stdout_capture.getvalue(),
                stderr_capture.getvalue(),
                exit_code[0],
            )

    def test_empty_input(self, tmp_path):
        """Test hook handles empty input gracefully."""
        stdout, stderr, exit_code = self.run_hook({}, tmp_path)

        assert exit_code == 0
        output = json.loads(stdout.strip())
        assert output == {}

    def test_no_session_id(self, tmp_path):
        """Test hook handles missing session_id."""
        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test prompt"}, tmp_path
        )

        assert exit_code == 0
        assert "session_id" in stderr.lower()

    def test_creates_session_state(self, tmp_path):
        """Test hook creates session state file."""
        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test prompt", "session_id": "test-123"}, tmp_path
        )

        assert exit_code == 0

        # Check session file was created
        session_file = (
            tmp_path / ".claude" / "mind-reader" / "sessions" / "test-123.json"
        )
        assert session_file.exists()

        state = json.loads(session_file.read_text())
        assert state["session_id"] == "test-123"
        assert state["prompt_count"] == 1

    def test_increments_prompt_count(self, tmp_path):
        """Test hook increments prompt count across calls."""
        # First call
        self.run_hook(
            {"prompt": "prompt 1", "session_id": "test-session"}, tmp_path
        )

        # Second call
        self.run_hook(
            {"prompt": "prompt 2", "session_id": "test-session"}, tmp_path
        )

        session_file = (
            tmp_path / ".claude" / "mind-reader" / "sessions" / "test-session.json"
        )
        state = json.loads(session_file.read_text())
        assert state["prompt_count"] == 2

    def test_disabled_plugin(self, tmp_path):
        """Test hook respects disabled setting."""
        # Create settings with plugin disabled
        data_dir = tmp_path / ".claude" / "mind-reader"
        data_dir.mkdir(parents=True, exist_ok=True)
        settings_file = data_dir / "settings.json"
        settings_file.write_text(json.dumps({"enabled": False}))

        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test", "session_id": "test-123"}, tmp_path
        )

        assert exit_code == 0
        output = json.loads(stdout.strip())
        assert output == {}

    def test_quiet_mode(self, tmp_path):
        """Test hook respects quiet_until setting."""
        # Create settings with quiet mode enabled
        data_dir = tmp_path / ".claude" / "mind-reader"
        data_dir.mkdir(parents=True, exist_ok=True)
        settings_file = data_dir / "settings.json"
        future = datetime.now() + timedelta(hours=1)
        settings_file.write_text(json.dumps({"quiet_until": future.isoformat()}))

        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test", "session_id": "test-123"}, tmp_path
        )

        assert exit_code == 0
        output = json.loads(stdout.strip())
        assert output == {}

    def test_temporal_nudge_with_baseline(self, tmp_path):
        """Test temporal nudge triggers when thresholds exceeded."""
        data_dir = tmp_path / ".claude" / "mind-reader"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "sessions").mkdir(exist_ok=True)

        # Create baseline
        baseline = {
            "computed_at": datetime.now().isoformat(),
            "session_duration_minutes": {"median": 30, "p75": 60, "p95": 120},
            "prompts_per_session": {"median": 5, "p75": 10, "p95": 15},
            "typical_hours": list(range(24)),  # All hours typical
            "insufficient_data": False,
        }
        (data_dir / "baseline.json").write_text(json.dumps(baseline))

        # Create session state with high prompt count
        session_state = {
            "session_id": "test-session",
            "started_at": datetime.now().isoformat(),
            "prompt_count": 20,  # Above p95 of 15
            "sentiment_scores": [],
            "last_nudge_prompt": None,
        }
        (data_dir / "sessions" / "test-session.json").write_text(
            json.dumps(session_state)
        )

        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test", "session_id": "test-session"}, tmp_path
        )

        assert exit_code == 0
        output = json.loads(stdout.strip())
        # Should have a nudge for exceeding prompt threshold
        assert "systemMessage" in output
        assert "prompts" in output["systemMessage"].lower()


def _make_bucket_stats(count: int, rate: float, p50: int, p75: int, p90: int) -> dict:
    """Helper to create bucket stats dict."""
    return {
        "session_count": count,
        "session_rate": rate,
        "duration": {"p50": p50, "p75": p75, "p90": p90},
    }


def _make_all_buckets(count: int, rate: float, p50: int, p75: int, p90: int) -> dict:
    """Helper to create all bucket stats with same values."""
    stats = _make_bucket_stats(count, rate, p50, p75, p90)
    return {
        "late_night": stats,
        "early_morning": stats.copy(),
        "morning": stats.copy(),
        "afternoon": stats.copy(),
        "evening": stats.copy(),
    }


def _make_days(bucket_data: dict) -> dict:
    """Helper to create days dict from bucket data."""
    days = {}
    day_names = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    ]
    for day in day_names:
        days[day] = {
            "boundaries": [6, 12, 18, 22],
            "buckets": bucket_data,
        }
    return days


class TestHookV2BucketIntegration:
    """Integration tests for v2 bucket-based detection."""

    def run_hook(self, input_data: dict, tmp_path: Path) -> tuple[str, str, int]:
        """Run the hook with given input and return (stdout, stderr, exit_code)."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            data_dir = tmp_path / ".claude" / "mind-reader"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "sessions").mkdir(exist_ok=True)

            stdin_data = json.dumps(input_data)
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            exit_code = [0]

            def mock_exit(code):
                exit_code[0] = code
                raise SystemExit(code)

            with (
                mock.patch("sys.stdin", io.StringIO(stdin_data)),
                mock.patch("sys.stdout", stdout_capture),
                mock.patch("sys.stderr", stderr_capture),
                mock.patch("sys.exit", mock_exit),
            ):
                try:
                    import importlib

                    import scripts.hook as hook_module

                    importlib.reload(hook_module)
                    hook_module.main()
                except SystemExit:
                    pass

            return (
                stdout_capture.getvalue(),
                stderr_capture.getvalue(),
                exit_code[0],
            )

    def test_v2_bucket_rarity_nudge(self, tmp_path):
        """Test v2 bucket rarity nudge triggers on first prompt."""
        data_dir = tmp_path / ".claude" / "mind-reader"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "sessions").mkdir(exist_ok=True)

        now = datetime.now()

        # Create bucket stats - all buckets have 0 sessions (rare)
        bucket_data = _make_all_buckets(0, 0.0, 0, 0, 0)
        days = _make_days(bucket_data)

        baseline = {
            "computed_at": now.isoformat(),
            "session_duration_minutes": {"median": 30, "p75": 60, "p95": 120},
            "prompts_per_session": {"median": 5, "p75": 10, "p95": 15},
            "typical_hours": list(range(24)),
            "insufficient_data": False,
            "boundaries_computed_at": now.isoformat(),
            "window_days": 42,
            "days": days,
            "global_stats": _make_bucket_stats(0, 0.0, 0, 0, 0),
        }

        (data_dir / "baseline.json").write_text(json.dumps(baseline))

        # First prompt should trigger rarity nudge
        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test", "session_id": "test-session"}, tmp_path
        )

        assert exit_code == 0
        output = json.loads(stdout.strip())
        assert "systemMessage" in output
        # Should mention "no sessions" since all buckets have 0 sessions
        assert "no sessions" in output["systemMessage"].lower()

    def test_v2_bucket_duration_nudge(self, tmp_path):
        """Test v2 bucket duration nudge triggers on long session."""
        data_dir = tmp_path / ".claude" / "mind-reader"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "sessions").mkdir(exist_ok=True)

        now = datetime.now()

        # Create bucket stats with low duration threshold (p90=30)
        bucket_data = _make_all_buckets(5, 0.5, 10, 20, 30)
        days = _make_days(bucket_data)

        baseline = {
            "computed_at": now.isoformat(),
            "session_duration_minutes": {"median": 30, "p75": 60, "p95": 120},
            "prompts_per_session": {"median": 5, "p75": 10, "p95": 15},
            "typical_hours": list(range(24)),
            "insufficient_data": False,
            "boundaries_computed_at": now.isoformat(),
            "window_days": 42,
            "days": days,
            "global_stats": _make_bucket_stats(100, 0.5, 10, 20, 30),
        }

        (data_dir / "baseline.json").write_text(json.dumps(baseline))

        # Create session that started 60 minutes ago (above p90 of 30)
        session_state = {
            "session_id": "test-session",
            "started_at": (now - timedelta(minutes=60)).isoformat(),
            "prompt_count": 5,  # Not first prompt, so rarity check won't run
            "sentiment_scores": [],
            "last_nudge_prompt": None,
        }
        session_file = data_dir / "sessions" / "test-session.json"
        session_file.write_text(json.dumps(session_state))

        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test", "session_id": "test-session"}, tmp_path
        )

        assert exit_code == 0
        output = json.loads(stdout.strip())
        assert "systemMessage" in output
        assert "p90" in output["systemMessage"]

    def test_legacy_fallback_without_v2_data(self, tmp_path):
        """Test falls back to legacy checks when v2 data missing."""
        data_dir = tmp_path / ".claude" / "mind-reader"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "sessions").mkdir(exist_ok=True)

        # Create v1-only baseline (no days field)
        baseline = {
            "computed_at": datetime.now().isoformat(),
            "session_duration_minutes": {"median": 30, "p75": 60, "p95": 120},
            "prompts_per_session": {"median": 5, "p75": 10, "p95": 15},
            "typical_hours": list(range(24)),
            "insufficient_data": False,
        }
        (data_dir / "baseline.json").write_text(json.dumps(baseline))

        # Create session with high prompt count
        session_state = {
            "session_id": "test-session",
            "started_at": datetime.now().isoformat(),
            "prompt_count": 20,  # Above p95 of 15
            "sentiment_scores": [],
            "last_nudge_prompt": None,
        }
        session_file = data_dir / "sessions" / "test-session.json"
        session_file.write_text(json.dumps(session_state))

        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "test", "session_id": "test-session"}, tmp_path
        )

        assert exit_code == 0
        output = json.loads(stdout.strip())
        # Should use legacy prompt check
        assert "systemMessage" in output
        assert "prompts" in output["systemMessage"].lower()


class TestHookErrorHandling:
    """Test hook error handling."""

    def test_invalid_json_input(self, tmp_path):
        """Test hook handles invalid JSON gracefully."""
        with mock.patch("pathlib.Path.home", return_value=tmp_path):
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            exit_code = [0]

            def mock_exit(code):
                exit_code[0] = code
                raise SystemExit(code)

            # Invalid JSON input
            with (
                mock.patch("sys.stdin", io.StringIO("not valid json {")),
                mock.patch("sys.stdout", stdout_capture),
                mock.patch("sys.stderr", stderr_capture),
                mock.patch("sys.exit", mock_exit),
            ):
                try:
                    import importlib

                    import scripts.hook as hook_module

                    importlib.reload(hook_module)
                    hook_module.main()
                except SystemExit:
                    pass

            assert exit_code[0] == 0  # Should always exit 0
            stdout = stdout_capture.getvalue()
            assert json.loads(stdout.strip()) == {}
            assert "invalid json" in stderr_capture.getvalue().lower()

    def test_always_exits_zero(self, tmp_path):
        """Test hook always exits 0 even on errors."""
        with (
            mock.patch("pathlib.Path.home", return_value=tmp_path),
            mock.patch(
                "core.settings.load_settings",
                side_effect=Exception("Forced error"),
            ),
        ):
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            exit_code = [0]

            def mock_exit(code):
                exit_code[0] = code
                raise SystemExit(code)

            with (
                mock.patch(
                    "sys.stdin",
                    io.StringIO(
                        json.dumps({"prompt": "test", "session_id": "test"})
                    ),
                ),
                mock.patch("sys.stdout", stdout_capture),
                mock.patch("sys.stderr", stderr_capture),
                mock.patch("sys.exit", mock_exit),
            ):
                try:
                    import importlib

                    import scripts.hook as hook_module

                    importlib.reload(hook_module)
                    hook_module.main()
                except SystemExit:
                    pass

            assert exit_code[0] == 0  # Must always exit 0
