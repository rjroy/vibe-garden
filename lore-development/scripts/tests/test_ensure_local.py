from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from ensure_local import ensure_local


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def check_ignored(root: Path, path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", path],
        cwd=root,
        text=True,
        capture_output=True,
    )
    assert result.returncode in (0, 1), result.stderr
    return result.returncode == 0


def test_fresh_project_setup_ignores_only_local_lore(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")

    assert ensure_local(tmp_path) is True
    assert (tmp_path / ".lore/local").is_dir()
    (tmp_path / ".lore/local/plan.md").write_text("local")
    (tmp_path / ".lore/work/history.md").parent.mkdir(parents=True)
    (tmp_path / ".lore/work/history.md").write_text("history")
    (tmp_path / ".lore/reference/current.md").parent.mkdir(parents=True)
    (tmp_path / ".lore/reference/current.md").write_text("reference")

    assert check_ignored(tmp_path, ".lore/local/plan.md")
    assert not check_ignored(tmp_path, ".lore/work/history.md")
    assert not check_ignored(tmp_path, ".lore/reference/current.md")


def test_non_git_setup_rule_protects_local_after_git_init(tmp_path: Path) -> None:
    assert ensure_local(tmp_path) is True
    assert (tmp_path / ".lore/local").is_dir()
    git(tmp_path, "init", "-q")

    assert check_ignored(tmp_path, ".lore/local/plan.md")


def test_existing_tracked_historical_work_file_is_preserved(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    historic = tmp_path / ".lore/work/intents/old.md"
    historic.parent.mkdir(parents=True)
    historic.write_text("historical context")
    git(tmp_path, "add", ".lore/work/intents/old.md")
    git(
        tmp_path,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "history",
    )

    ensure_local(tmp_path)

    assert (
        git(tmp_path, "ls-files", ".lore/work/intents/old.md")
        == ".lore/work/intents/old.md"
    )
    assert historic.read_text() == "historical context"


@pytest.mark.parametrize("existing", [b"keep me\n", b"keep me"])
def test_existing_gitignore_is_preserved_and_setup_is_idempotent(
    tmp_path: Path, existing: bytes
) -> None:
    (tmp_path / ".gitignore").write_bytes(existing)

    assert ensure_local(tmp_path) is True
    content = (tmp_path / ".gitignore").read_bytes()
    assert content.startswith(existing)
    assert content.count(b"/.lore/local/\n") == 1
    assert ensure_local(tmp_path) is False
    assert (tmp_path / ".gitignore").read_bytes() == content


def test_explicit_local_negation_fails_without_rewriting_rules(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    original = b"/.lore/local/\n!/.lore/local/\n"
    (tmp_path / ".gitignore").write_bytes(original)
    assert not check_ignored(tmp_path, ".lore/local/plan.md")

    with pytest.raises(ValueError, match="explicit .lore/local ignore exception"):
        ensure_local(tmp_path)

    assert (tmp_path / ".gitignore").read_bytes() == original
    assert not (tmp_path / ".lore/local").exists()


def test_cli_reports_effective_ignore_blocker(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("!/.lore/local/\n")
    script = Path(__file__).resolve().parents[1] / "ensure_local.py"

    result = subprocess.run(
        ["python3", str(script), str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "refusing to override" in result.stderr
    assert (tmp_path / ".gitignore").read_text() == "!/.lore/local/\n"


@pytest.mark.parametrize(
    "target",
    ["gitignore-symlink", "gitignore-directory", "lore-symlink", "local-symlink"],
)
def test_unsafe_targets_fail_without_overwriting_user_data(
    tmp_path: Path, target: str
) -> None:
    outside = tmp_path / "outside"
    outside.write_text("preserve")
    if target == "gitignore-symlink":
        (tmp_path / ".gitignore").symlink_to(outside)
    elif target == "gitignore-directory":
        (tmp_path / ".gitignore").mkdir()
    elif target == "lore-symlink":
        (tmp_path / ".lore").symlink_to(outside)
    else:
        (tmp_path / ".lore").mkdir()
        (tmp_path / ".lore/local").symlink_to(outside)

    with pytest.raises(ValueError):
        ensure_local(tmp_path)
    assert outside.read_text() == "preserve"
