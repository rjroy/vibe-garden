"""Tests for idea_hook.py."""

import contextlib
import io
import json
import sys
from datetime import date
from pathlib import Path
from unittest import mock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestIdeaHook:
    """Tests for the /idea capture hook."""

    def run_hook(
        self, input_data: dict | str, tmp_path: Path, mock_date: str = "2026-02-18"
    ) -> tuple[str, str, int]:
        """Run the hook with given input and return (stdout, stderr, exit_code)."""
        if isinstance(input_data, dict):
            stdin_data = json.dumps(input_data)
        else:
            stdin_data = input_data

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        exit_code = [0]

        def mock_exit(code):
            exit_code[0] = code
            raise SystemExit(code)

        mock_today = date.fromisoformat(mock_date)

        # Reload before patching so the mock applies to the fresh module
        import importlib

        import idea_hook

        importlib.reload(idea_hook)

        with (
            mock.patch("sys.stdin", io.StringIO(stdin_data)),
            mock.patch("sys.stdout", stdout_capture),
            mock.patch("sys.stderr", stderr_capture),
            mock.patch("sys.exit", mock_exit),
            mock.patch("idea_hook.date") as patched_date,
        ):
            patched_date.today.return_value = mock_today
            patched_date.fromisoformat = date.fromisoformat
            with contextlib.suppress(SystemExit):
                idea_hook.main()

        return stdout_capture.getvalue(), stderr_capture.getvalue(), exit_code[0]

    # --- Prefix matching ---

    def test_idea_with_text_matches(self, tmp_path):
        """'/idea some text' triggers capture."""
        stdout, _, exit_code = self.run_hook(
            {"prompt": "/idea fix the sidebar", "cwd": str(tmp_path)}, tmp_path
        )
        assert exit_code == 0
        output = json.loads(stdout.strip())
        assert output["decision"] == "block"
        assert "2026-02-18.md" in output["reason"]

    def test_ideas_does_not_match(self, tmp_path):
        """'/ideas' (no space) does not trigger capture."""
        stdout, _, exit_code = self.run_hook(
            {"prompt": "/ideas something", "cwd": str(tmp_path)}, tmp_path
        )
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}

    def test_idea_no_space_does_not_match(self, tmp_path):
        """'/idea' without trailing space does not trigger."""
        stdout, _, exit_code = self.run_hook(
            {"prompt": "/idea", "cwd": str(tmp_path)}, tmp_path
        )
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}

    def test_idea_empty_text_does_not_match(self, tmp_path):
        """'/idea   ' (only whitespace after prefix) does not trigger."""
        stdout, _, exit_code = self.run_hook(
            {"prompt": "/idea   ", "cwd": str(tmp_path)}, tmp_path
        )
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}

    def test_non_idea_prompt_passes_through(self, tmp_path):
        """Regular prompts produce empty output."""
        stdout, _, exit_code = self.run_hook(
            {"prompt": "tell me about ideas", "cwd": str(tmp_path)}, tmp_path
        )
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}

    # --- File creation ---

    def test_creates_new_daily_file_with_header(self, tmp_path):
        """New file gets date header and bullet."""
        self.run_hook(
            {"prompt": "/idea fix the sidebar", "cwd": str(tmp_path)}, tmp_path
        )
        daily_file = tmp_path / ".lore" / "ideas" / "2026-02-18.md"
        assert daily_file.exists()
        content = daily_file.read_text()
        assert content == "# 2026-02-18\n\n- fix the sidebar\n"

    def test_appends_to_existing_file(self, tmp_path):
        """Existing file gets append only, no duplicate header."""
        ideas_dir = tmp_path / ".lore" / "ideas"
        ideas_dir.mkdir(parents=True)
        daily_file = ideas_dir / "2026-02-18.md"
        daily_file.write_text("# 2026-02-18\n\n- first idea\n")

        self.run_hook(
            {"prompt": "/idea second idea", "cwd": str(tmp_path)}, tmp_path
        )
        content = daily_file.read_text()
        assert content == "# 2026-02-18\n\n- first idea\n- second idea\n"
        assert content.count("# 2026-02-18") == 1

    # --- Directory creation ---

    def test_creates_ideas_directory(self, tmp_path):
        """.lore/ideas/ is created when missing."""
        ideas_dir = tmp_path / ".lore" / "ideas"
        assert not ideas_dir.exists()

        self.run_hook(
            {"prompt": "/idea test", "cwd": str(tmp_path)}, tmp_path
        )
        assert ideas_dir.exists()

    # --- No frontmatter ---

    def test_no_frontmatter_in_created_file(self, tmp_path):
        """Created files start with #, not ---."""
        self.run_hook(
            {"prompt": "/idea test", "cwd": str(tmp_path)}, tmp_path
        )
        daily_file = tmp_path / ".lore" / "ideas" / "2026-02-18.md"
        content = daily_file.read_text()
        assert not content.startswith("---")
        assert content.startswith("# ")

    # --- Output format ---

    def test_block_decision_on_match(self, tmp_path):
        """Matching prompt returns block decision JSON."""
        stdout, _, _ = self.run_hook(
            {"prompt": "/idea some text", "cwd": str(tmp_path)}, tmp_path
        )
        output = json.loads(stdout.strip())
        assert output == {
            "decision": "block",
            "reason": "Idea saved to .lore/ideas/2026-02-18.md",
        }

    def test_empty_json_on_no_match(self, tmp_path):
        """Non-matching prompt returns {}."""
        stdout, _, _ = self.run_hook(
            {"prompt": "hello world", "cwd": str(tmp_path)}, tmp_path
        )
        assert json.loads(stdout.strip()) == {}

    # --- Error handling ---

    def test_invalid_json_input(self, tmp_path):
        """Invalid JSON input produces {} and exits 0."""
        stdout, _, exit_code = self.run_hook("not json at all", tmp_path)
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}

    def test_missing_cwd(self, tmp_path):
        """Missing cwd produces {} and exits 0."""
        stdout, stderr, exit_code = self.run_hook(
            {"prompt": "/idea test"}, tmp_path
        )
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}

    def test_empty_cwd(self, tmp_path):
        """Empty cwd produces {} and exits 0."""
        stdout, _, exit_code = self.run_hook(
            {"prompt": "/idea test", "cwd": ""}, tmp_path
        )
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}

    def test_filesystem_error_produces_empty(self, tmp_path):
        """Filesystem errors produce {} and exit 0."""
        with mock.patch("idea_hook.Path.mkdir", side_effect=PermissionError("denied")):
            stdout, stderr, exit_code = self.run_hook(
                {"prompt": "/idea test", "cwd": str(tmp_path)}, tmp_path
            )
        assert exit_code == 0
        assert json.loads(stdout.strip()) == {}
        assert "denied" in stderr

    # --- Edge cases ---

    def test_idea_with_special_characters(self, tmp_path):
        """Ideas with special characters are preserved."""
        prompt = "/idea fix `code` with **bold** and [links](url)"
        self.run_hook(
            {"prompt": prompt, "cwd": str(tmp_path)},
            tmp_path,
        )
        daily_file = tmp_path / ".lore" / "ideas" / "2026-02-18.md"
        content = daily_file.read_text()
        assert "- fix `code` with **bold** and [links](url)\n" in content

    def test_different_dates_create_different_files(self, tmp_path):
        """Different dates create separate files."""
        self.run_hook(
            {"prompt": "/idea day one", "cwd": str(tmp_path)},
            tmp_path,
            mock_date="2026-02-17",
        )
        self.run_hook(
            {"prompt": "/idea day two", "cwd": str(tmp_path)},
            tmp_path,
            mock_date="2026-02-18",
        )
        assert (tmp_path / ".lore" / "ideas" / "2026-02-17.md").exists()
        assert (tmp_path / ".lore" / "ideas" / "2026-02-18.md").exists()
