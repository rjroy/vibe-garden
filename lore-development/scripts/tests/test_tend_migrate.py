"""Unit tests for the tend_migrate.py migration script.

The high-bug-density area is link rewriting across three contexts (`related:`,
`source:`, in-body markdown links). Each test pins one behavior so a failure
points at the right region of the script.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

# Allow importing from the parent scripts/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tend_migrate  # noqa: E402

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "pre-migration" / ".lore"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def lore_root(tmp_path: Path) -> Path:
    """Copy the pre-migration fixture into a temp dir and return its .lore."""
    dst = tmp_path / ".lore"
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def test_detect_legacy_finds_all_old_dirs_and_vision(lore_root: Path) -> None:
    dirs, files = tend_migrate.detect_legacy(lore_root)
    assert set(dirs) == set(tend_migrate.LEGACY_DIRS)
    assert files == ["vision.md"]


def test_detect_legacy_returns_empty_on_clean_tree(tmp_path: Path) -> None:
    clean = tmp_path / ".lore"
    (clean / "build" / "specs").mkdir(parents=True)
    (clean / "reference").mkdir()
    dirs, files = tend_migrate.detect_legacy(clean)
    assert dirs == []
    assert files == []


# ---------------------------------------------------------------------------
# Custom-directory parsing
# ---------------------------------------------------------------------------


def test_load_custom_directories_reads_config(lore_root: Path) -> None:
    custom = tend_migrate.load_custom_directories(lore_root)
    assert custom == {"prototypes"}


def test_load_custom_directories_handles_missing_config(tmp_path: Path) -> None:
    bare = tmp_path / ".lore"
    bare.mkdir()
    assert tend_migrate.load_custom_directories(bare) == set()


def test_load_custom_directories_handles_no_frontmatter(tmp_path: Path) -> None:
    bare = tmp_path / ".lore"
    bare.mkdir()
    (bare / "lore-config.md").write_text("# Just a heading\n", encoding="utf-8")
    assert tend_migrate.load_custom_directories(bare) == set()


# ---------------------------------------------------------------------------
# Path-rewriting unit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "before, after",
    [
        (".lore/brainstorm/foo.md", ".lore/build/brainstorm/foo.md"),
        (".lore/specs/auth.md", ".lore/build/specs/auth.md"),
        (".lore/diagrams/x.md", ".lore/build/diagrams/x.md"),
        (".lore/vision.md", ".lore/reference/vision.md"),
        # No false-positives on already-migrated paths.
        (".lore/build/specs/auth.md", ".lore/build/specs/auth.md"),
        (".lore/reference/vision.md", ".lore/reference/vision.md"),
    ],
)
def test_rewrite_path_string(before: str, after: str) -> None:
    assert tend_migrate.rewrite_path_string(before) == after


def test_rewrite_path_string_does_not_match_vision_md_prefix() -> None:
    # Should not greedily munch `vision.md.bak` into vision.md.
    assert (
        tend_migrate.rewrite_path_string(".lore/vision.md.bak")
        == ".lore/vision.md.bak"
    )


# ---------------------------------------------------------------------------
# Plan building
# ---------------------------------------------------------------------------


def test_build_plan_moves_match_migration_table(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    moves = {
        m.src.relative_to(lore_root): m.dst.relative_to(lore_root)
        for m in plan.moves
    }
    assert moves[Path("brainstorm/exploration.md")] == Path(
        "build/brainstorm/exploration.md"
    )
    assert moves[Path("specs/auth.md")] == Path("build/specs/auth.md")
    assert moves[Path("diagrams/auth-flow.md")] == Path(
        "build/diagrams/auth-flow.md"
    )
    assert moves[Path("vision.md")] == Path("reference/vision.md")
    assert moves[Path("ideas/2026-04-10.md")] == Path(
        "build/ideas/2026-04-10.md"
    )


def test_build_plan_skips_protected_paths(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    move_srcs = {m.src for m in plan.moves}
    assert lore_root / "commissions" / "c1.md" not in move_srcs
    assert lore_root / "meetings" / "m1.md" not in move_srcs
    assert lore_root / "heartbeat.md" not in move_srcs
    assert lore_root / "lore-agents.md" not in move_srcs
    assert lore_root / "prototypes" / "p1.md" not in move_srcs


def test_build_plan_records_skipped_custom_dirs(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    assert plan.skipped_custom == ["prototypes"]


def test_build_plan_render_lists_moves(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    out = plan.render()
    assert "Moves" in out
    assert "vision.md" in out
    assert "build/specs/auth.md" in out


# ---------------------------------------------------------------------------
# Apply: target layout, link resolution, protected paths, idempotency
# ---------------------------------------------------------------------------


def test_apply_produces_target_layout(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)

    # New tree present.
    assert (lore_root / "build" / "specs" / "auth.md").is_file()
    assert (lore_root / "build" / "brainstorm" / "exploration.md").is_file()
    assert (lore_root / "build" / "diagrams" / "auth-flow.md").is_file()
    assert (lore_root / "build" / "ideas" / "2026-04-10.md").is_file()
    assert (lore_root / "reference" / "vision.md").is_file()

    # Old tree gone.
    for legacy in tend_migrate.LEGACY_DIRS:
        assert not (lore_root / legacy).exists(), legacy
    assert not (lore_root / "vision.md").exists()


def test_apply_rewrites_related_frontmatter(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)
    text = _read(lore_root / "build" / "specs" / "auth.md")
    assert "- .lore/build/brainstorm/exploration.md" in text
    assert "- .lore/build/design/oauth.md" in text
    assert ".lore/brainstorm/" not in text
    assert ".lore/design/" not in text


def test_apply_rewrites_source_frontmatter(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)
    notes = _read(lore_root / "build" / "notes" / "install.md")
    task = _read(lore_root / "build" / "tasks" / "setup-oauth.md")
    assert "source: .lore/build/plans/migration.md" in notes
    assert "source: .lore/build/plans/migration.md" in task


def test_apply_rewrites_in_body_markdown_links(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)
    plans = _read(lore_root / "build" / "plans" / "migration.md")
    assert "[.lore/build/brainstorm/exploration.md]" in plans
    assert "(.lore/build/brainstorm/exploration.md)" in plans
    assert ".lore/brainstorm/" not in plans


def test_apply_preserves_fenced_code_block(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)
    notes = _read(lore_root / "build" / "notes" / "install.md")
    # Path inside the bash fence stays as-is.
    assert "cat .lore/brainstorm/exploration.md" in notes
    assert "ls .lore/specs/" in notes
    # Path outside the fence is rewritten.
    assert "`.lore/build/issues/bug-1.md`" in notes


def test_apply_preserves_migration_doc_body(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)
    body = _read(lore_root / "build" / "issues" / "migration-walkthrough.md")
    assert "`.lore/specs/auth.md`" in body
    assert "`.lore/brainstorm/exploration.md`" in body
    assert "`.lore/vision.md`" in body


def test_apply_does_not_touch_protected_files(lore_root: Path) -> None:
    before = {
        path: _read(lore_root / path)
        for path in [
            "commissions/c1.md",
            "meetings/m1.md",
            "heartbeat.md",
            "lore-agents.md",
            "prototypes/p1.md",
        ]
    }
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)
    for rel, original in before.items():
        assert _read(lore_root / rel) == original, rel


def test_apply_then_apply_is_noop(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)

    snapshot = _capture_tree(lore_root)
    second = tend_migrate.build_plan(lore_root)
    assert second.is_noop, second.render()
    tend_migrate.apply_plan(second)
    assert _capture_tree(lore_root) == snapshot


def test_build_plan_flags_destination_collision(lore_root: Path) -> None:
    # Pre-existing post-migration file that would be clobbered by the move.
    target = lore_root / "build" / "specs" / "auth.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("PRE-EXISTING\n", encoding="utf-8")

    plan = tend_migrate.build_plan(lore_root)
    assert plan.has_conflicts
    conflict_dsts = {c.dst for c in plan.conflicts}
    assert target in conflict_dsts


def test_apply_refuses_when_conflicts_exist(lore_root: Path) -> None:
    target = lore_root / "build" / "specs" / "auth.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("PRE-EXISTING\n", encoding="utf-8")

    plan = tend_migrate.build_plan(lore_root)
    with pytest.raises(tend_migrate.MigrationConflictError):
        tend_migrate.apply_plan(plan)
    # Pre-existing file still intact; legacy source still in place.
    assert _read(target) == "PRE-EXISTING\n"
    assert (lore_root / "specs" / "auth.md").is_file()


def test_plan_render_shows_conflicts(lore_root: Path) -> None:
    target = lore_root / "build" / "specs" / "auth.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("PRE-EXISTING\n", encoding="utf-8")

    plan = tend_migrate.build_plan(lore_root)
    out = plan.render()
    assert "BLOCKED" in out
    assert "destination collision" in out
    assert "build/specs/auth.md" in out


def test_main_exits_nonzero_when_conflicts_present(
    lore_root: Path, capsys: pytest.CaptureFixture
) -> None:
    target = lore_root / "build" / "specs" / "auth.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("PRE-EXISTING\n", encoding="utf-8")

    rc = tend_migrate.main(
        ["--lore-dir", str(lore_root), "--apply", "--yes"]
    )
    assert rc == 3
    captured = capsys.readouterr()
    assert "destination collisions detected" in captured.err
    # Tree unchanged.
    assert _read(target) == "PRE-EXISTING\n"
    assert (lore_root / "specs" / "auth.md").is_file()


def test_apply_does_not_create_learned_directory(lore_root: Path) -> None:
    plan = tend_migrate.build_plan(lore_root)
    tend_migrate.apply_plan(plan)
    # REQ-REDESIGN-4: learned/ is created by the first /learn invocation.
    assert not (lore_root / "learned").exists()


# ---------------------------------------------------------------------------
# CLI / entry-point
# ---------------------------------------------------------------------------


def test_main_dry_run_default(lore_root: Path, capsys: pytest.CaptureFixture) -> None:
    rc = tend_migrate.main(["--lore-dir", str(lore_root)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Dry-run only" in out
    # Tree unchanged.
    assert (lore_root / "specs" / "auth.md").is_file()


def test_main_apply_with_yes(lore_root: Path, capsys: pytest.CaptureFixture) -> None:
    rc = tend_migrate.main(["--lore-dir", str(lore_root), "--apply", "--yes"])
    assert rc == 0
    assert "Migration applied" in capsys.readouterr().out
    assert (lore_root / "build" / "specs" / "auth.md").is_file()
    assert not (lore_root / "specs").exists()


def test_main_reports_no_legacy_when_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    clean = tmp_path / ".lore"
    (clean / "build").mkdir(parents=True)
    rc = tend_migrate.main(["--lore-dir", str(clean)])
    assert rc == 0
    assert "No legacy structure detected" in capsys.readouterr().out


def test_main_errors_on_missing_lore_dir(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    rc = tend_migrate.main(["--lore-dir", str(tmp_path / "does-not-exist")])
    assert rc == 2


def test_main_apply_aborts_without_confirmation(
    lore_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
    rc = tend_migrate.main(["--lore-dir", str(lore_root), "--apply"])
    assert rc == 1
    assert "Aborted" in capsys.readouterr().out
    assert (lore_root / "specs" / "auth.md").is_file()


def test_main_apply_proceeds_on_yes_input(
    lore_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    rc = tend_migrate.main(["--lore-dir", str(lore_root), "--apply"])
    assert rc == 0
    assert (lore_root / "build" / "specs" / "auth.md").is_file()


# ---------------------------------------------------------------------------
# Migration-doc detection
# ---------------------------------------------------------------------------


def test_has_migration_doc_tag_inline_list() -> None:
    text = "---\ntags: [migration-doc, docs]\n---\nbody\n"
    assert tend_migrate.has_migration_doc_tag(text)


def test_has_migration_doc_tag_block_list() -> None:
    text = "---\ntags:\n  - docs\n  - migration-doc\n---\nbody\n"
    assert tend_migrate.has_migration_doc_tag(text)


def test_has_migration_doc_tag_absent() -> None:
    text = "---\ntags: [docs]\n---\nbody\n"
    assert not tend_migrate.has_migration_doc_tag(text)


def test_has_migration_doc_tag_no_frontmatter() -> None:
    assert not tend_migrate.has_migration_doc_tag("# heading only\n")


# ---------------------------------------------------------------------------
# Document rewriter unit
# ---------------------------------------------------------------------------


def test_rewrite_document_skips_fenced_block() -> None:
    text = (
        "# header\n"
        "see .lore/specs/x.md\n"
        "```\n"
        "cat .lore/specs/x.md\n"
        "```\n"
        "and .lore/specs/y.md\n"
    )
    new, edits = tend_migrate.rewrite_document(text)
    assert "cat .lore/specs/x.md" in new  # inside fence preserved
    assert "see .lore/build/specs/x.md" in new
    assert "and .lore/build/specs/y.md" in new
    # Two edits: line 2 and line 6.
    assert {e[0] for e in edits} == {2, 6}


def test_rewrite_document_skip_body_keeps_body_unchanged() -> None:
    text = (
        "---\n"
        "title: t\n"
        "related:\n"
        "  - .lore/specs/auth.md\n"
        "---\n"
        "Body refers to .lore/specs/auth.md verbatim.\n"
    )
    new, _ = tend_migrate.rewrite_document(text, skip_body=True)
    assert "- .lore/build/specs/auth.md" in new  # frontmatter rewritten
    assert "Body refers to .lore/specs/auth.md verbatim." in new


def test_rewrite_document_handles_no_frontmatter() -> None:
    text = "Free body that mentions .lore/specs/auth.md once.\n"
    new, edits = tend_migrate.rewrite_document(text)
    assert ".lore/build/specs/auth.md" in new
    assert len(edits) == 1


# ---------------------------------------------------------------------------
# Helpers used in the test module only
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Edge cases bumping coverage past the 90% gate
# ---------------------------------------------------------------------------


def test_plan_render_noop(tmp_path: Path) -> None:
    plan = tend_migrate.MigrationPlan(lore_root=tmp_path / ".lore")
    out = plan.render()
    assert "No legacy structure detected" in out


def test_plan_render_handles_only_rewrites(tmp_path: Path) -> None:
    """`/tend migrate` rerun-after-edit case: rewrites without moves."""
    lore = tmp_path / ".lore"
    (lore / "build" / "specs").mkdir(parents=True)
    target = lore / "build" / "specs" / "doc.md"
    target.write_text(
        "---\ntitle: t\nrelated:\n  - .lore/specs/auth.md\n---\nbody\n",
        encoding="utf-8",
    )
    # Force the path through the pipeline by hand-building a plan:
    plan = tend_migrate.MigrationPlan(
        lore_root=lore,
        rewrites=[
            tend_migrate.Rewrite(path=target, edits=((4, "old\n", "new\n"),))
        ],
    )
    out = plan.render()
    assert "Moves (0)" in out
    assert "(none)" in out
    assert "Link rewrites (1 files)" in out


def test_apply_rewrites_in_place_for_pre_existing_files(tmp_path: Path) -> None:
    lore = tmp_path / ".lore"
    (lore / "specs").mkdir(parents=True)
    (lore / "specs" / "moved.md").write_text(
        "---\ntitle: t\nstatus: draft\ntags: [s]\n---\nbody\n",
        encoding="utf-8",
    )
    # Pre-existing in-tree file with stale link.
    (lore / "build" / "design").mkdir(parents=True)
    pre = lore / "build" / "design" / "settled.md"
    pre.write_text(
        "---\ntitle: settled\nrelated:\n  - .lore/specs/moved.md\n---\n"
        "Link to [old](.lore/specs/moved.md).\n",
        encoding="utf-8",
    )
    plan = tend_migrate.build_plan(lore)
    assert any(rw.path == pre for rw in plan.rewrites)
    tend_migrate.apply_plan(plan)
    text = pre.read_text(encoding="utf-8")
    assert ".lore/build/specs/moved.md" in text
    assert "/specs/moved.md" not in text.replace("/build/specs/moved.md", "")


def test_has_migration_doc_tag_inline_single_value() -> None:
    text = "---\ntags: migration-doc\n---\nbody\n"
    assert tend_migrate.has_migration_doc_tag(text)


def test_has_migration_doc_tag_other_inline_value_is_false() -> None:
    text = "---\ntags: docs\n---\nbody\n"
    assert not tend_migrate.has_migration_doc_tag(text)


def test_remove_if_empty_leaves_nonempty(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    (parent / "child").mkdir(parents=True)
    (parent / "child" / "f.md").write_text("x", encoding="utf-8")
    tend_migrate._remove_if_empty(parent)
    assert (parent / "child" / "f.md").is_file()


def test_remove_if_empty_removes_empty_recursively(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    (parent / "a" / "b").mkdir(parents=True)
    tend_migrate._remove_if_empty(parent)
    assert not parent.exists()


def test_apply_handles_binary_file_in_legacy_dir(tmp_path: Path) -> None:
    lore = tmp_path / ".lore"
    (lore / "diagrams").mkdir(parents=True)
    (lore / "diagrams" / "blob.bin").write_bytes(b"\x00\x01\x02 not utf8 \xff")
    plan = tend_migrate.build_plan(lore)
    tend_migrate.apply_plan(plan)
    moved = lore / "build" / "diagrams" / "blob.bin"
    assert moved.read_bytes() == b"\x00\x01\x02 not utf8 \xff"


def _capture_tree(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = str(path.relative_to(root))
            try:
                out[rel] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                out[rel] = "<binary>"
    return out
