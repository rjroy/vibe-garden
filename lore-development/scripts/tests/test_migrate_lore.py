from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import migrate_lore  # noqa: E402
from legacy_html import convert_html  # noqa: E402


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "migrate_lore.py"), str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def init_git(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")


def test_preview_has_no_filesystem_or_gitignore_mutation(tmp_path: Path) -> None:
    old = tmp_path / ".lore/work/plans/nested/plan.md"
    old.parent.mkdir(parents=True)
    old.write_text("# Preserve\n")
    (tmp_path / ".gitignore").write_text("keep\n")

    result = run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "PREVIEW (no files changed)" in result.stdout
    assert (
        ".lore/work/plans/nested/plan.md -> .lore/local/plans/nested/plan.md"
        in result.stdout
    )
    assert old.read_text() == "# Preserve\n"
    assert not (tmp_path / ".lore/local").exists()
    assert (tmp_path / ".gitignore").read_text() == "keep\n"


def test_apply_preserves_nested_bytes_rewrites_exact_links_and_is_idempotent(
    tmp_path: Path,
) -> None:
    spec = tmp_path / ".lore/work/specs/nested/old.md"
    spec.parent.mkdir(parents=True)
    original = (
        "---\ntitle: Old\ndate: 2024-01-01\nstatus: approved\n"
        "tags: [legacy]\n---\n# Old\n\nREQ-1 remains historical.\n"
    )
    spec.write_text(original)
    plan = tmp_path / ".lore/work/plans/nested/p.md"
    plan.parent.mkdir(parents=True)
    plan.write_bytes(b"\xffbinary preserved\n")
    note = tmp_path / ".lore/work/notes/n.md"
    note.parent.mkdir(parents=True)
    note.write_text(
        "---\nsource: .lore/work/plans/nested/p.md\n"
        "related: [.lore/work/specs/nested/old.md]\n---\n"
        "[old](../specs/nested/old.md#part)\n"
        "<a href='../plans/nested/p.md'>plan</a>\n"
        "`[example](.lore/work/specs/nested/old.md)`\n"
    )
    reference = tmp_path / ".lore/reference/guide.md"
    reference.parent.mkdir(parents=True)
    reference.write_text(
        "---\ntitle: Guide\ndate: 2024-01-01\nstatus: current\ntags: [guide]\n"
        "fg-sources: [.lore/work/specs/nested/old.md, .lore/work/plans/nested/p.md]\n"
        "---\n# Guide\n"
    )
    readme = tmp_path / "README.md"
    readme.write_text("[historic spec](.lore/work/specs/nested/old.md)\n")

    result = run(tmp_path, "--apply")

    assert result.returncode == 0, result.stderr
    moved_spec = tmp_path / ".lore/work/intents/nested/old.md"
    assert moved_spec.read_text() == original
    assert "status: approved" in moved_spec.read_text()
    assert (
        tmp_path / ".lore/local/plans/nested/p.md"
    ).read_bytes() == b"\xffbinary preserved\n"
    migrated_note = (tmp_path / ".lore/local/notes/n.md").read_text()
    assert "source: .lore/local/plans/nested/p.md" in migrated_note
    assert "related: [.lore/work/intents/nested/old.md]" in migrated_note
    assert "[old](../../work/intents/nested/old.md#part)" in migrated_note
    assert "href='../plans/nested/p.md'" in migrated_note
    assert "`[example](.lore/work/specs/nested/old.md)`" in migrated_note
    migrated_reference = reference.read_text()
    assert ".lore/work/intents/nested/old.md" in migrated_reference
    assert ".lore/work/plans/nested/p.md" in migrated_reference
    assert "REVIEW: .lore/work/plans/nested/p.md" in result.stdout
    assert "README.md refers to moved path" in result.stdout
    assert readme.read_text() == "[historic spec](.lore/work/specs/nested/old.md)\n"
    assert (tmp_path / ".gitignore").read_text().endswith("/.lore/local/\n")

    # Migrated documents validate; untouched reference history is not rewritten.
    findings = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "validate_frontmatter.py"),
            str(tmp_path / ".lore"),
        ],
        capture_output=True,
        text=True,
    )
    assert (
        '"file": "work/intents/nested/old.md", "error_type": "invalid_status"'
        not in findings.stdout
    )
    assert (
        '"file": "reference/guide.md", "error_type": "invalid_status"'
        in findings.stdout
    )
    second = run(tmp_path, "--apply")
    assert second.returncode == 0, second.stderr
    assert "No legacy files found" in second.stdout


def test_approved_crlf_spec_stays_marker_free_without_body_normalization(
    tmp_path: Path,
) -> None:
    source = tmp_path / ".lore/work/specs/crlf.md"
    source.parent.mkdir(parents=True)
    original = (
        b"---\r\ntitle: Historical\r\ndate: 2024-01-01\r\n"
        b"status: approved\r\ntags: [legacy]\r\n---\r\n"
        b"# Historical body\r\nExact line endings stay.\r\n"
    )
    source.write_bytes(original)
    body = b"# Historical body\r\nExact line endings stay.\r\n"

    result = run(tmp_path, "--apply")

    destination = tmp_path / ".lore/work/intents/crlf.md"
    assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == original
    assert destination.read_bytes().endswith(body)
    sentinel = tmp_path / ".lore/work/validation/invalid-sentinel.md"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text(
        "---\ntitle: Sentinel\ndate: 2024-01-01\nstatus: legacy\ntags: [test]\n---\n"
    )
    findings = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_frontmatter.py"), str(tmp_path / ".lore")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert findings.returncode == 1, findings.stdout + findings.stderr
    assert '"file": "work/validation/invalid-sentinel.md"' in findings.stdout
    assert '"file": "work/intents/crlf.md", "error_type": "invalid_status"' not in findings.stdout


def test_migration_preserves_existing_legacy_marker_and_other_metadata(
    tmp_path: Path,
) -> None:
    source = tmp_path / ".lore/specs/marked.md"
    source.parent.mkdir(parents=True)
    original = (
        "---\ntitle: Historical\ndate: 2024-01-01\nstatus: active\n"
        "tags: [legacy]\nlegacy_source_type: spec\ncustom-field: retain\n"
        "---\n# Historical body\nExact body.\n"
    )
    source.write_text(original)

    result = run(tmp_path, "--apply")

    destination = tmp_path / ".lore/work/intents/marked.md"
    assert result.returncode == 0, result.stderr
    migrated = destination.read_text()
    assert "legacy_source_type: spec\n" in migrated
    assert "custom-field: retain\n" in migrated
    assert "status: completed\n" in migrated
    assert "legacy_status: active\n" in migrated
    assert migrated.endswith("# Historical body\nExact body.\n")
    sentinel = tmp_path / ".lore/work/validation/invalid-sentinel.md"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text(
        "---\ntitle: Sentinel\ndate: 2024-01-01\nstatus: legacy\ntags: [test]\n---\n"
    )
    findings = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_frontmatter.py"), str(tmp_path / ".lore")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert findings.returncode == 1, findings.stdout + findings.stderr
    assert '"file": "work/validation/invalid-sentinel.md"' in findings.stdout
    assert '"file": "work/intents/marked.md", "error_type": "invalid_status"' not in findings.stdout


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_apply_normalizes_legacy_status_preserving_metadata_and_body(
    tmp_path: Path, newline: str
) -> None:
    source = tmp_path / ".lore/brainstorm/old.md"
    source.parent.mkdir(parents=True)
    original = newline.join([
        "---", "title: Historical", "date: 2024-01-01", "status: current",
        "tags: [legacy]", "custom-field: keep", "---", "# Body", "Exact body.", "",
    ]).encode()
    source.write_bytes(original)

    preview = run(tmp_path)
    assert preview.returncode == 0, preview.stderr
    assert "status: current" in source.read_text()
    result = run(tmp_path, "--apply")
    assert result.returncode == 0, result.stderr
    destination = tmp_path / ".lore/work/brainstorm/old.md"
    migrated = destination.read_bytes()
    assert b"status: completed" + newline.encode() in migrated
    assert b"legacy_status: current" + newline.encode() in migrated
    assert b"custom-field: keep" + newline.encode() in migrated
    assert migrated.endswith(("# Body" + newline + "Exact body." + newline).encode())


def test_apply_normalizes_html_status_and_keeps_original_backup(tmp_path: Path) -> None:
    source = tmp_path / ".lore/research/old.html"
    source.parent.mkdir(parents=True)
    original = (
        b"<html><head><title>Research</title><meta name=\"date\" "
        b"content=\"2024-01-01\"><meta name=\"status\" content=\"active\">"
        b"<meta name=\"tags\" content=\"research\"></head><body><h1>Research</h1>"
        b"<p>Body.</p></body></html>"
    )
    source.write_bytes(original)

    result = run(tmp_path, "--apply")
    assert result.returncode == 0, result.stderr
    destination = tmp_path / ".lore/work/research/old.md"
    converted = destination.read_text()
    assert "status: completed" in converted
    assert "legacy_status: active" in converted
    backup = next((tmp_path / ".lore/local/migration-backups").rglob("*.html"))
    assert backup.read_bytes() == original


def test_unknown_legacy_status_fails_preview_without_mutation(tmp_path: Path) -> None:
    root = tmp_path / "project with spaces"
    source = root / ".lore/issues/unknown.md"
    source.parent.mkdir(parents=True)
    original = b"---\ntitle: Unknown\ndate: 2024-01-01\nstatus: mystery\n---\nBody\n"
    source.write_bytes(original)

    result = run(root)

    assert result.returncode == 1
    assert "unknown legacy status 'mystery'" in result.stderr
    assert f"{source}:4" in result.stderr
    assert (
        "explicitly set status to draft, approved, completed, or archived"
        in result.stderr
    )
    assert "never infer approval" in result.stderr
    assert "rerun the no-write preview" in result.stderr
    assert "No migration moves or reference edits have started" in result.stderr
    assert f"'{root}'" in result.stderr
    assert source.read_bytes() == original
    assert not (root / ".lore/work/issues/unknown.md").exists()
    assert not (root / ".gitignore").exists()


def test_migrate_skill_translates_blockers_into_safe_recovery() -> None:
    skill = (SCRIPTS.parent / "skills/migrate/SKILL.md").read_text()

    for guidance in (
        "Unknown or malformed status",
        "Never infer `approved`",
        "Compare both contents",
        "Inspect both `git -C '<root>' diff",
        "Ask for explicit user approval",
        "will not dereference it",
        "check-ignore -v --no-index",
        "do not use `sudo` or blanket `chmod`",
        "Keep the original bytes",
        "STOP; do not rerun apply blindly",
        "Offer to help inspect or normalize",
    ):
        assert guidance in skill


def test_malformed_legacy_status_reports_exact_line_and_safe_choices(
    tmp_path: Path,
) -> None:
    source = tmp_path / ".lore/issues/malformed.md"
    source.parent.mkdir(parents=True)
    original = (
        b"---\ntitle: Malformed\ndate: 2024-01-01\nstatus: [unknown, shape]\n"
        b"---\nBody\n"
    )
    source.write_bytes(original)

    result = run(tmp_path)

    assert result.returncode == 1
    assert f"{source}:4" in result.stderr
    assert "observed 'status: [unknown, shape]'" in result.stderr
    assert "Choose draft, approved, completed, or archived" in result.stderr
    assert "never infer approval" in result.stderr
    assert "rerun the no-write preview" in result.stderr
    assert source.read_bytes() == original
    assert not (tmp_path / ".lore/work/issues/malformed.md").exists()


def test_unknown_html_meta_status_reports_source_and_no_conversion(
    tmp_path: Path,
) -> None:
    source = tmp_path / ".lore/research/unknown.html"
    source.parent.mkdir(parents=True)
    original = (
        b'<html><head><meta name="status" content="maybe">'
        b"</head><body>History</body></html>"
    )
    source.write_bytes(original)

    result = run(tmp_path)

    assert result.returncode == 1
    assert f"unknown legacy status 'maybe' in {source}" in result.stderr
    assert "converted Markdown metadata line" in result.stderr
    assert "Choose" not in result.stderr
    assert "draft, approved, completed, or archived" in result.stderr
    assert source.read_bytes() == original
    assert not (tmp_path / ".lore/work/research/unknown.md").exists()


def test_legacy_status_mapping_is_complete_and_conservative() -> None:
    expected = {
        "draft": "draft", "open": "draft", "pending": "draft",
        "in_progress": "draft", "approved": "approved",
        "completed": "completed", "complete": "completed",
        "implemented": "completed", "executed": "completed",
        "resolved": "completed", "current": "completed", "active": "completed",
        "archived": "archived", "superseded": "archived", "parked": "archived",
        "outdated": "archived", "wontfix": "archived", "skipped": "archived",
    }
    assert expected == migrate_lore._STATUS_MIGRATION
    for old_status, new_status in expected.items():
        text = (
            "---\ntitle: Legacy\ndate: 2024-01-01\n"
            f"status: {old_status}\ntags: [legacy]\n---\nBody\n"
        )
        migrated = migrate_lore._normalize_legacy_status(text, Path("legacy.md"))
        assert f"status: {new_status}\n" in migrated
        if old_status != new_status:
            assert f"legacy_status: {old_status}\n" in migrated


def test_readonly_reference_is_preflighted_before_any_move(tmp_path: Path) -> None:
    init_git(tmp_path)
    source = tmp_path / ".lore/work/specs/a.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"---\ntitle: A\ndate: 2024-01-01\nstatus: approved\n---\n# A\n")
    reference = tmp_path / ".lore/reference/a.md"
    reference.parent.mkdir(parents=True)
    reference_bytes = b"[a](../work/specs/a.md)\n"
    # Create a test-owned read-only file; don't alter permissions on repository
    # or caller-owned files. The explicit mode remains detectable under root.
    descriptor = os.open(reference, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(reference_bytes)
    source_bytes = source.read_bytes()
    git(tmp_path, "add", ".lore/work/specs/a.md", ".lore/reference/a.md")
    git(tmp_path, "commit", "-qm", "readonly reference baseline")
    status_before = git(tmp_path, "status", "--porcelain=v1")

    result = run(tmp_path, "--apply")

    assert result.returncode == 1
    assert "reference file is not writable" in result.stderr
    assert "ownership/permissions" in result.stderr
    assert "without sudo or blanket chmod" in result.stderr
    assert source.read_bytes() == source_bytes
    assert not (tmp_path / ".lore/work/intents/a.md").exists()
    assert reference.read_bytes() == reference_bytes
    assert git(tmp_path, "status", "--porcelain=v1") == status_before


def test_staged_only_tracked_source_is_refused_without_mutating_git_or_files(
    tmp_path: Path,
) -> None:
    init_git(tmp_path)
    source = tmp_path / ".lore/work/plans/plan.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"HEAD bytes\r\n")
    git(tmp_path, "add", ".lore/work/plans/plan.md")
    git(tmp_path, "commit", "-qm", "baseline")
    source.write_bytes(b"staged-only INDEX bytes\r\n")
    git(tmp_path, "add", ".lore/work/plans/plan.md")
    staged_blob = git(tmp_path, "show", ":.lore/work/plans/plan.md")
    source.write_bytes(b"HEAD bytes\r\n")
    status_before = git(tmp_path, "status", "--porcelain=v1")

    result = run(tmp_path, "--apply", "--untrack")

    assert result.returncode == 1
    assert "tracked source has staged or unstaged changes" in result.stderr
    assert "git -C" in result.stderr and "diff --cached" in result.stderr
    assert "Do not reset, checkout, or discard" in result.stderr
    assert source.read_bytes() == b"HEAD bytes\r\n"
    assert git(tmp_path, "show", ":.lore/work/plans/plan.md") == staged_blob
    assert git(tmp_path, "status", "--porcelain=v1") == status_before
    assert not (tmp_path / ".lore/local").exists()


def test_staged_only_tracked_reference_edit_is_refused_before_moves(
    tmp_path: Path,
) -> None:
    init_git(tmp_path)
    source = tmp_path / ".lore/work/plans/plan.md"
    source.parent.mkdir(parents=True)
    source.write_text("Plan\n")
    reference = tmp_path / ".lore/reference/index.md"
    reference.parent.mkdir(parents=True)
    reference.write_bytes(b"[plan](.lore/work/plans/plan.md)\r\n")
    git(tmp_path, "add", ".lore/work/plans/plan.md", ".lore/reference/index.md")
    git(tmp_path, "commit", "-qm", "baseline")
    reference.write_bytes(b"[staged edit](.lore/work/plans/plan.md)\r\n")
    git(tmp_path, "add", ".lore/reference/index.md")
    staged_blob = git(tmp_path, "show", ":.lore/reference/index.md")
    reference.write_bytes(b"[plan](.lore/work/plans/plan.md)\r\n")
    status_before = git(tmp_path, "status", "--porcelain=v1")

    result = run(tmp_path, "--apply", "--untrack")

    assert result.returncode == 1
    assert "tracked source has staged or unstaged changes" in result.stderr
    assert source.read_text() == "Plan\n"
    assert reference.read_bytes() == b"[plan](.lore/work/plans/plan.md)\r\n"
    assert git(tmp_path, "show", ":.lore/reference/index.md") == staged_blob
    assert git(tmp_path, "status", "--porcelain=v1") == status_before
    assert not (tmp_path / ".lore/local").exists()


def test_collision_refuses_all_work_before_setup_or_any_move(tmp_path: Path) -> None:
    source = tmp_path / ".lore/work/tasks/a.md"
    source.parent.mkdir(parents=True)
    source.write_text("source")
    destination = tmp_path / ".lore/local/tasks/a.md"
    destination.parent.mkdir(parents=True)
    destination.write_text("destination")
    other = tmp_path / ".lore/work/notes/b.md"
    other.parent.mkdir(parents=True)
    other.write_text("other")

    result = run(tmp_path, "--apply")

    assert result.returncode == 1
    assert "destination collision" in result.stderr
    assert str(source) in result.stderr and str(destination) in result.stderr
    assert "Compare both documents" in result.stderr
    assert "do not delete or overwrite either automatically" in result.stderr
    assert source.read_text() == "source"
    assert other.read_text() == "other"
    assert destination.read_text() == "destination"
    assert not (tmp_path / ".gitignore").exists()


def test_git_index_destination_collision_refuses_move(tmp_path: Path) -> None:
    init_git(tmp_path)
    source = tmp_path / ".lore/work/plans/a.md"
    source.parent.mkdir(parents=True)
    source.write_text("source")
    target = tmp_path / ".lore/local/plans/a.md"
    target.parent.mkdir(parents=True)
    target.write_text("tracked target")
    git(tmp_path, "add", "-f", ".lore/local/plans/a.md")
    git(tmp_path, "commit", "-qm", "tracked local target")
    target.unlink()

    result = run(tmp_path, "--apply", "--untrack")

    assert result.returncode == 1
    assert "destination collision in Git index" in result.stderr
    assert "git ls-files --stage" in result.stderr
    assert source.read_text() == "source"
    assert not target.exists()


def test_symlink_source_refuses_without_following_or_mutating(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text("outside")
    source_dir = tmp_path / ".lore/work/plans"
    source_dir.mkdir(parents=True)
    (source_dir / "link.md").symlink_to(outside)

    result = run(tmp_path, "--apply")

    assert result.returncode == 1
    assert "symlink" in result.stderr
    assert "will not dereference it" in result.stderr
    assert "Inspect its link target" in result.stderr
    assert outside.read_text() == "outside"
    assert (source_dir / "link.md").is_symlink()
    assert not (tmp_path / ".lore/local").exists()


def test_tracked_local_file_requires_approval_and_untracks_only_that_path(
    tmp_path: Path,
) -> None:
    init_git(tmp_path)
    plan = tmp_path / ".lore/work/plans/plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("tracked plan\n")
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("one\n")
    git(tmp_path, "add", ".lore/work/plans/plan.md", "unrelated.txt")
    git(tmp_path, "commit", "-qm", "baseline")
    unrelated.write_text("staged unrelated\n")
    git(tmp_path, "add", "unrelated.txt")

    preview = run(tmp_path)
    assert preview.returncode == 0
    assert "requires --untrack" in preview.stdout
    refused = run(tmp_path, "--apply")
    assert refused.returncode == 1
    assert "Ask the user whether they approve" in refused.stderr
    assert "files stay in .lore/local/" in refused.stderr
    assert plan.read_text() == "tracked plan\n"
    assert git(tmp_path, "ls-files", ".lore/work/plans/plan.md")

    applied = run(tmp_path, "--apply", "--untrack")
    assert applied.returncode == 0, applied.stderr
    local = tmp_path / ".lore/local/plans/plan.md"
    assert local.read_text() == "tracked plan\n"
    assert not git(tmp_path, "ls-files", ".lore/work/plans/plan.md")
    assert (
        git(tmp_path, "ls-files", "--error-unmatch", "unrelated.txt") == "unrelated.txt"
    )
    assert "staged unrelated" in git(tmp_path, "show", ":unrelated.txt")
    assert ".lore/local/plans/plan.md" not in git(tmp_path, "status", "--short")
    assert "D  .lore/work/plans/plan.md" in git(tmp_path, "status", "--short")


@pytest.mark.parametrize("staged", [False, True])
def test_dirty_tracked_local_source_fails_before_setup(
    tmp_path: Path, staged: bool
) -> None:
    init_git(tmp_path)
    plan = tmp_path / ".lore/work/plans/plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("original\n")
    git(tmp_path, "add", ".lore/work/plans/plan.md")
    git(tmp_path, "commit", "-qm", "baseline")
    plan.write_text("changed\n")
    if staged:
        git(tmp_path, "add", ".lore/work/plans/plan.md")

    result = run(tmp_path, "--apply", "--untrack")

    assert result.returncode == 1
    assert "tracked source has staged or unstaged changes" in result.stderr
    assert "git -C" in result.stderr and "diff --cached" in result.stderr
    assert "Do not reset, checkout, or discard" in result.stderr
    assert plan.read_text() == "changed\n"
    assert not (tmp_path / ".lore/local").exists()


def test_apply_stops_if_ignore_setup_fails_before_move(tmp_path: Path) -> None:
    init_git(tmp_path)
    plan = tmp_path / ".lore/work/plans/plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("preserve")
    (tmp_path / ".gitignore").write_text("!/.lore/local/\n")

    result = run(tmp_path, "--apply")

    assert result.returncode == 1
    assert "check-ignore -v --no-index" in result.stderr
    assert "decide whether to edit that exact rule" in result.stderr
    assert "Do not bypass the guard" in result.stderr
    assert ".gitignore" in result.stderr
    assert plan.read_text() == "preserve"
    assert not (tmp_path / ".lore/local").exists()
    assert (tmp_path / ".gitignore").read_text() == "!/.lore/local/\n"


def test_link_rewriter_uses_exact_resolvable_destinations(tmp_path: Path) -> None:
    document = tmp_path / ".lore/work/design/d.md"
    document.parent.mkdir(parents=True)
    mapping = {".lore/work/specs/x.md": ".lore/work/intents/x.md"}
    original = (
        "[x](../specs/x.md)\n"
        "[external](https://example.test/.lore/work/specs/x.md)\n"
        "`(.lore/work/specs/x.md)`\n"
    )

    updated, changed = migrate_lore._rewrite_document(
        document, original, tmp_path, mapping
    )

    assert "[x](../intents/x.md)" in updated
    assert "https://example.test/.lore/work/specs/x.md" in updated
    assert "`(.lore/work/specs/x.md)`" in updated
    assert changed == {".lore/work/specs/x.md"}


def test_html_metadata_rewrites_spec_provenance_but_not_local_work_sources(
    tmp_path: Path,
) -> None:
    document = tmp_path / ".lore/reference/legacy.html"
    mapping = {
        ".lore/work/specs/old.html": ".lore/work/intents/old.html",
        ".lore/work/plans/old.html": ".lore/local/plans/old.html",
    }
    original = (
        '<meta name="fg-sources" '
        'content=".lore/work/specs/old.html,.lore/work/plans/old.html">'
    )

    updated, changed = migrate_lore._rewrite_document(
        document, original, tmp_path, mapping
    )

    assert ".lore/work/intents/old.html" in updated
    assert ".lore/work/plans/old.html" in updated
    assert changed == {".lore/work/specs/old.html"}


def test_flat_and_work_spec_provenance_paths_both_rewrite() -> None:
    root = Path("/tmp/project")
    document = root / ".lore/reference/index.md"
    mapping = {
        ".lore/specs/flat.html": ".lore/work/intents/flat.md",
        ".lore/work/specs/work.html": ".lore/work/intents/work.md",
    }
    original = (
        "---\nfg-sources: [.lore/specs/flat.html, .lore/work/specs/work.html]\n---\n"
    )

    updated, changed = migrate_lore._rewrite_document(document, original, root, mapping)

    assert ".lore/work/intents/flat.md" in updated
    assert ".lore/work/intents/work.md" in updated
    assert changed == set(mapping)


def test_flat_pre_work_fixture_migrates_recognized_layout_and_keeps_unknowns(
    tmp_path: Path,
) -> None:
    import shutil

    fixture_lore = Path(__file__).parent / "fixtures/pre-migration/.lore"
    shutil.copytree(fixture_lore, tmp_path / ".lore")
    old_spec = tmp_path / ".lore/specs/auth.md"
    old_wiki = tmp_path / ".lore/issues/migration-walkthrough.md"
    original_wiki = old_wiki.read_text()

    preview = run(tmp_path)

    assert preview.returncode == 0, preview.stderr
    assert ".lore/specs/auth.md -> .lore/work/intents/auth.md" in preview.stdout
    assert (
        ".lore/plans/migration.md -> .lore/local/plans/migration.md" in preview.stdout
    )
    assert "unmapped legacy directory preserved: .lore/commissions" in preview.stdout
    assert not (tmp_path / ".lore/local").exists()
    assert old_spec.exists()

    applied = run(tmp_path, "--apply")

    assert applied.returncode == 0, applied.stderr
    assert (tmp_path / ".lore/work/intents/auth.md").exists()
    assert (tmp_path / ".lore/work/brainstorm/exploration.md").exists()
    assert (tmp_path / ".lore/work/design/oauth.md").exists()
    assert (tmp_path / ".lore/work/research/competitors.md").exists()
    assert (tmp_path / ".lore/work/retros/sprint1.md").exists()
    assert (tmp_path / ".lore/work/issues/bug-1.md").exists()
    assert (tmp_path / ".lore/work/diagrams/auth-flow.md").exists()
    assert (tmp_path / ".lore/work/stubs/index.md").exists()
    assert (tmp_path / ".lore/work/validation/check-spec.md").exists()
    assert (tmp_path / ".lore/work/ideas/2026-04-10.md").exists()
    assert (tmp_path / ".lore/work/excavations/index.md").exists()
    assert (tmp_path / ".lore/local/tasks/setup-oauth.md").exists()
    assert (tmp_path / ".lore/local/notes/install.md").exists()
    assert not old_spec.exists()
    assert (
        "[.lore/specs/auth.md](.lore/work/intents/auth.md)"
        in (tmp_path / ".lore/vision.md").read_text()
    )
    expected_wiki = original_wiki.replace("status: open\n", "status: draft\n")
    expected_wiki = expected_wiki.replace(
        "---\n\n# Migration", "legacy_status: open\n---\n\n# Migration"
    )
    migrated_wiki = (tmp_path / ".lore/work/issues/migration-walkthrough.md")
    assert migrated_wiki.read_text() == expected_wiki
    assert (tmp_path / ".lore/commissions/c1.md").exists()
    assert (tmp_path / ".lore/meetings/m1.md").exists()
    assert (tmp_path / ".lore/prototypes/p1.md").exists()


def test_mixed_flat_and_work_destination_collision_fails_before_mutation(
    tmp_path: Path,
) -> None:
    flat = tmp_path / ".lore/specs/nested/a.md"
    current = tmp_path / ".lore/work/intents/nested/a.md"
    flat.parent.mkdir(parents=True)
    current.parent.mkdir(parents=True)
    flat.write_text("flat")
    current.write_text("current")

    result = run(tmp_path, "--apply")

    assert result.returncode == 1
    assert "destination collision" in result.stderr
    assert flat.read_text() == "flat"
    assert current.read_text() == "current"
    assert not (tmp_path / ".lore/local").exists()


def test_html_conversion_preserves_content_metadata_and_warns_on_complex_markup() -> (
    None
):
    source = """<!doctype html>
    <html><head><title>Archive</title>
    <meta name="date" content="2020-02-03">
    <meta name="status" content="approved">
    <meta name="tags" content="auth, legacy">
    <meta name="modules" content="auth-service">
    <meta name="related" content=".lore/work/design/oauth.html">
    <meta name="source" content=".lore/work/plans/old.html">
    <meta name="sequence" content="7"><meta name="req-prefix" content="AUTH">
    <meta name="fg-type" content="decision">
    <meta name="custom:field" content="retained">
    <style>.diagram { color: red }</style>
    <script>runLegacy()</script></head><body>
    <h1>Archive</h1><p>A <strong>historical</strong>
    <a href="../design/oauth.html">link</a>.</p>
    <ol><li>First</li><li>Second</li></ol>
    <pre><code class="language-python">print(&quot;safe&quot;)</code></pre>
    <svg viewBox="0 0 4 4"><circle cx="2" cy="2" r="1"/></svg>
    <table><tr><td>meaningful</td></tr></table>
    </body></html>"""

    converted = convert_html(source, ".lore/specs/archive.html")

    assert 'title: "Archive"' in converted.markdown
    assert 'date: "2020-02-03"' in converted.markdown
    assert 'status: "approved"' in converted.markdown
    assert 'tags: ["auth", "legacy"]' in converted.markdown
    assert 'related: [".lore/work/design/oauth.html"]' in converted.markdown
    assert "sequence: 7" in converted.markdown
    assert 'req-prefix: "AUTH"' in converted.markdown
    assert 'fg-type: "decision"' in converted.markdown
    assert '"custom:field": "retained"' in converted.markdown
    assert "# Archive" in converted.markdown
    assert "**historical**" in converted.markdown
    assert "[link](../design/oauth.html)" in converted.markdown
    assert "1. First" in converted.markdown and "2. Second" in converted.markdown
    assert 'print("safe")' in converted.markdown
    assert '<svg viewBox="0 0 4 4">' in converted.markdown
    assert "<table>" in converted.markdown and "meaningful" in converted.markdown
    assert "&lt;script&gt;runLegacy()&lt;/script&gt;" in converted.markdown
    assert any("<style>" in warning for warning in converted.warnings)
    assert any("<script>" in warning for warning in converted.warnings)
    assert any("<svg>" in warning for warning in converted.warnings)
    assert any("<table>" in warning for warning in converted.warnings)
    without_date = convert_html("<h1>No date in source</h1>")
    assert "date:" not in without_date.markdown


def test_html_heading_anchor_is_separate_from_markdown_heading() -> None:
    converted = convert_html('<h2 id="migration-safety">Migration safety</h2>')

    assert '<a id="migration-safety"></a>\n\n## Migration safety' in converted.markdown


def test_pretty_ordered_lists_count_only_items_and_render_nested_lists() -> None:
    source = """<ol>
  <li>First
    <ol>
      <li>Nested one</li>
      <li>Nested two</li>
    </ol>
  </li>

  <li>Second</li>
</ol>"""

    converted = convert_html(source)

    assert "1. First" in converted.markdown
    assert "2. Second" in converted.markdown
    assert "3. Second" not in converted.markdown
    assert "1. First\n   1. Nested one\n   2. Nested two\n2. Second" in converted.markdown


def test_nested_mixed_lists_indent_by_parent_marker_width() -> None:
    converted = convert_html(
        "<ul><li>Parent<ol><li>Ordered child<ul><li>Unordered grandchild</li>"
        "</ul></li></ol></li></ul>"
    )

    assert converted.markdown == (
        "- Parent\n"
        "  1. Ordered child\n"
        "     - Unordered grandchild\n"
    )


def test_nested_lists_under_double_digit_ordered_marker_align_correctly() -> None:
    preceding_items = "".join(f"<li>Item {number}</li>" for number in range(1, 10))
    source = (
        f"<ol>{preceding_items}<li>Tenth<ul><li>Unordered child"
        "<ol><li>Ordered grandchild</li></ol></li></ul></li></ol>"
    )

    converted = convert_html(source)

    assert "9. Item 9\n10. Tenth" in converted.markdown
    assert "10. Tenth\n    - Unordered child\n      1. Ordered grandchild" in converted.markdown


def test_html_apply_previews_backup_conversion_and_rewrites_links(
    tmp_path: Path,
) -> None:
    source = tmp_path / ".lore/specs/auth.html"
    source.parent.mkdir(parents=True)
    original = (
        b'<html><head><title>Old Auth</title><meta name="date" '
        b'content="2022-01-02"><meta name="status" content="approved">'
        b'<meta name="tags" content="auth, legacy"></head><body>'
        b'<h1>Old Auth</h1><p>See <a href="../design/oauth.html#flow">design</a>.</p>'
        b"</body></html>"
    )
    source.write_bytes(original)
    design = tmp_path / ".lore/design/oauth.html"
    design.parent.mkdir(parents=True)
    design.write_text("<html><body><h1>OAuth</h1></body></html>")
    index = tmp_path / ".lore/vision.md"
    index.write_text("[auth](specs/auth.html)\n")

    preview = run(tmp_path)

    assert preview.returncode == 0, preview.stderr
    assert "CONVERT HTML -> Markdown .lore/specs/auth.html" in preview.stdout
    assert ".lore/local/migration-backups/specs/auth.html" in preview.stdout
    assert not (tmp_path / ".lore/local").exists()
    assert source.read_bytes() == original

    applied = run(tmp_path, "--apply")

    assert applied.returncode == 0, applied.stderr
    destination = tmp_path / ".lore/work/intents/auth.md"
    backup = tmp_path / ".lore/local/migration-backups/specs/auth.html"
    assert backup.read_bytes() == original
    converted = destination.read_text()
    assert "legacy_source_type:" not in converted
    assert 'status: "approved"' in converted
    assert "[design](../design/oauth.md#flow)" in converted
    assert not (tmp_path / ".lore/work/intents/oauth.md").exists()
    assert (tmp_path / ".lore/work/design/oauth.md").exists()
    assert index.read_text() == "[auth](work/intents/auth.md)\n"


def test_moved_documents_rebase_relative_links_to_unmoved_targets(
    tmp_path: Path,
) -> None:
    assets = tmp_path / ".lore/assets"
    assets.mkdir(parents=True)
    (assets / "chart.svg").write_text("<svg/>")
    specs = tmp_path / ".lore/specs"
    specs.mkdir(parents=True)
    (specs / "chart.md").write_text(
        "[chart](../assets/chart.svg?size=small#view)\n"
        "[missing](../assets/missing.svg#anchor)\n"
        "[web](https://example.test/chart.svg#external)\n"
    )
    (specs / "chart-html.html").write_text(
        '<h1>Chart</h1><a href="../assets/chart.svg?raw=1#view">asset</a>'
    )

    preview = run(tmp_path)
    assert (
        "cannot rebase unresolved relative link '../assets/missing.svg#anchor'"
        in preview.stdout
    )

    applied = run(tmp_path, "--apply")

    assert applied.returncode == 0, applied.stderr
    markdown = (tmp_path / ".lore/work/intents/chart.md").read_text()
    converted = (tmp_path / ".lore/work/intents/chart-html.md").read_text()
    assert "[chart](../../assets/chart.svg?size=small#view)" in markdown
    assert "[missing](../assets/missing.svg#anchor)" in markdown
    assert "https://example.test/chart.svg#external" in markdown
    assert "[asset](../../assets/chart.svg?raw=1#view)" in converted
    assert (assets / "chart.svg").read_text() == "<svg/>"


def test_later_migration_never_rewrites_an_earlier_html_backup(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / ".lore/specs"
    source_dir.mkdir(parents=True)
    first_source = source_dir / "a.html"
    original = b'<a href=".lore/work/specs/b.html#part">B</a>'
    first_source.write_bytes(original)

    first = run(tmp_path, "--apply")

    assert first.returncode == 0, first.stderr
    backup = tmp_path / ".lore/local/migration-backups/specs/a.html"
    assert backup.read_bytes() == original
    later_source = tmp_path / ".lore/work/specs/b.html"
    later_source.parent.mkdir(parents=True)
    later_source.write_text("<h1>B</h1>")

    second = run(tmp_path, "--apply")

    assert second.returncode == 0, second.stderr
    assert backup.read_bytes() == original
    current = (tmp_path / ".lore/work/intents/a.md").read_text()
    assert "[B](.lore/work/intents/b.md#part)" in current
    assert (tmp_path / ".lore/work/intents/b.md").exists()


def test_spec_assets_move_as_bytes_without_frontmatter_decoding(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / ".lore/work/specs"
    spec_dir.mkdir(parents=True)
    spec = spec_dir / "spec.md"
    spec.write_text(
        "---\ntitle: Spec\ndate: 2024-01-01\nstatus: approved\n"
        "tags: [legacy]\n---\n# Historical\n"
    )
    image = spec_dir / "diagram.png"
    image_bytes = b"\x89PNG\r\n\x1a\n\x00\xffbinary asset"
    image.write_bytes(image_bytes)

    result = run(tmp_path, "--apply")

    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".lore/work/intents/diagram.png").read_bytes() == image_bytes
    migrated_spec = (tmp_path / ".lore/work/intents/spec.md").read_text()
    assert "legacy_source_type:" not in migrated_spec
    assert "# Historical" in migrated_spec
    assert not spec.exists() and not image.exists()


def test_apply_failure_rolls_back_original_bytes_references_and_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_git(tmp_path)
    (tmp_path / ".lore/local").mkdir(parents=True)
    (tmp_path / ".gitignore").write_bytes(b"/.lore/local/\n")
    source = tmp_path / ".lore/work/plans/plan.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"plan original\r\n")
    legacy_spec = tmp_path / ".lore/work/specs/spec.md"
    legacy_spec.parent.mkdir(parents=True)
    legacy_spec.write_bytes(
        b"---\r\ntitle: Historical\r\ndate: 2024-01-01\r\n"
        b"status: approved\r\ntags: [legacy]\r\n---\r\n# History\r\n"
    )
    reference = tmp_path / ".lore/reference/index.md"
    reference.parent.mkdir(parents=True)
    reference.write_bytes(b"[plan](.lore/work/plans/plan.md)\r\n")
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("base\n")
    git(
        tmp_path,
        "add",
        ".gitignore",
        ".lore/work/plans/plan.md",
        ".lore/reference/index.md",
        "unrelated.txt",
    )
    git(tmp_path, "commit", "-qm", "baseline")
    unrelated.write_text("staged elsewhere\n")
    git(tmp_path, "add", "unrelated.txt")
    plan = migrate_lore.build_plan(tmp_path)
    source_before = source.read_bytes()
    spec_before = legacy_spec.read_bytes()
    reference_before = reference.read_bytes()
    index_before = git(tmp_path, "diff", "--cached", "--binary")
    tree_before = git(tmp_path, "write-tree")
    status_before = git(tmp_path, "status", "--porcelain=v1")
    real_git = migrate_lore._git

    def fail_index_removal(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        if args[:2] == ("rm", "--cached"):
            return subprocess.CompletedProcess(args, 1, "", "injected failure")
        return real_git(root, *args)

    monkeypatch.setattr(migrate_lore, "_git", fail_index_removal)
    with pytest.raises(ValueError, match="injected failure"):
        migrate_lore.apply_plan(plan, untrack=True)

    assert source.read_bytes() == source_before
    assert legacy_spec.read_bytes() == spec_before
    assert reference.read_bytes() == reference_before
    assert not (tmp_path / ".lore/local/plans/plan.md").exists()
    assert git(tmp_path, "diff", "--cached", "--binary") == index_before
    assert git(tmp_path, "write-tree") == tree_before
    assert git(tmp_path, "status", "--porcelain=v1") == status_before


def test_rollback_restore_failure_does_not_skip_moved_source_restoration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / ".lore/work/specs/spec.md"
    source.parent.mkdir(parents=True)
    source_before = (
        b"---\ntitle: Historical\ndate: 2024-01-01\nstatus: approved\n"
        b"tags: [legacy]\n---\n# Historical\n"
    )
    source.write_bytes(source_before)
    reference = tmp_path / ".lore/reference/index.md"
    reference.parent.mkdir(parents=True)
    reference_before = b"[spec](../work/specs/spec.md)\n"
    reference.write_bytes(reference_before)
    plan = migrate_lore.build_plan(tmp_path)
    replacement = next(new for path, _old, new in plan.edits if path == reference)
    original_write_bytes = Path.write_bytes

    def fail_restoring_reference(self: Path, data: bytes) -> int:
        if self == reference and data == reference_before:
            raise OSError("injected reference restoration failure")
        if self == reference and data == replacement:
            original_write_bytes(self, data)
            raise OSError("injected failure after reference write")
        return original_write_bytes(self, data)

    monkeypatch.setattr(Path, "write_bytes", fail_restoring_reference)

    with pytest.raises(
        ValueError,
        match="rollback incomplete.*injected reference restoration failure",
    ) as failure:
        migrate_lore.apply_plan(plan)

    assert "STOP: do not rerun apply blindly" in str(failure.value)
    assert str(reference) in str(failure.value)

    # Reference recovery failed as injected, but the later rollback actions
    # still restore the historical source bytes and remove the destination.
    assert reference.read_bytes() != reference_before
    assert source.read_bytes() == source_before
    assert not (tmp_path / ".lore/work/intents/spec.md").exists()


def test_html_conversion_collision_or_decode_failure_has_no_mutation(
    tmp_path: Path,
) -> None:
    source = tmp_path / ".lore/plans/a.html"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"<h1>Plan</h1>")
    destination = tmp_path / ".lore/local/plans/a.md"
    destination.parent.mkdir(parents=True)
    destination.write_text("occupied")
    result = run(tmp_path, "--apply")
    assert result.returncode == 1 and "destination collision" in result.stderr
    assert source.read_bytes() == b"<h1>Plan</h1>"
    assert destination.read_text() == "occupied"

    destination.unlink()
    source.write_bytes(b"\xffnot utf-8")
    failed_conversion = run(tmp_path, "--apply")
    assert failed_conversion.returncode == 1
    assert "cannot safely convert non-UTF-8 HTML" in failed_conversion.stderr
    assert "Keep the original bytes" in failed_conversion.stderr
    assert "decide explicitly" in failed_conversion.stderr
    assert source.read_bytes() == b"\xffnot utf-8"
    assert not (tmp_path / ".lore/local/migration-backups").exists()


def test_html_original_backup_collision_refuses_conversion(tmp_path: Path) -> None:
    source = tmp_path / ".lore/work/specs/nested/auth.html"
    source.parent.mkdir(parents=True)
    source.write_text("<h1>Legacy</h1>")
    backup = tmp_path / ".lore/local/migration-backups/work/specs/nested/auth.html"
    backup.parent.mkdir(parents=True)
    backup.write_text("user-owned backup")

    result = run(tmp_path, "--apply")

    assert result.returncode == 1
    assert "HTML backup collision" in result.stderr
    assert "Compare the existing backup and source" in result.stderr
    assert "will not overwrite or delete either file" in result.stderr
    assert source.read_text() == "<h1>Legacy</h1>"
    assert backup.read_text() == "user-owned backup"
    assert not (tmp_path / ".lore/work/intents/nested/auth.md").exists()
