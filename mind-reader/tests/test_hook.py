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
            {"user_prompt": "test prompt"}, tmp_path
        )

        assert exit_code == 0
        assert "session_id" in stderr.lower()

    def test_creates_session_state(self, tmp_path):
        """Test hook creates session state file."""
        stdout, stderr, exit_code = self.run_hook(
            {"user_prompt": "test prompt", "session_id": "test-123"}, tmp_path
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
            {"user_prompt": "prompt 1", "session_id": "test-session"}, tmp_path
        )

        # Second call
        self.run_hook(
            {"user_prompt": "prompt 2", "session_id": "test-session"}, tmp_path
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
            {"user_prompt": "test", "session_id": "test-123"}, tmp_path
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
            {"user_prompt": "test", "session_id": "test-123"}, tmp_path
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
            "typical_days": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
            ],
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
            {"user_prompt": "test", "session_id": "test-session"}, tmp_path
        )

        assert exit_code == 0
        output = json.loads(stdout.strip())
        # Should have a nudge for exceeding prompt threshold
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
                "lib.settings.load_settings",
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
                        json.dumps({"user_prompt": "test", "session_id": "test"})
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
