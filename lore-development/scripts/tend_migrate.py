#!/usr/bin/env python3
"""
Migration tool for the lore-development three-directory redesign.

Moves files from the legacy `.lore/` layout (one of 14 top-level directories
plus `.lore/vision.md`) into the three-directory model
(`.lore/build/`, `.lore/reference/`, `.lore/learned/`) and rewrites internal
path references in `related:` / `source:` frontmatter fields and in-body
markdown links.

Defaults to dry-run. Pass `--apply` to actually move files. When `--apply` is
set without `--yes`, the script prompts for confirmation before mutating.

Source of truth: `.lore/specs/lore-redesign.md` (REQ-REDESIGN-18 through 25).
Reference docs: `lore-development/skills/tend/references/migrate.md`.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Migration table (REQ-REDESIGN-6, REQ-REDESIGN-21)
# ---------------------------------------------------------------------------

# Legacy top-level directory name -> new path under .lore/.
# Diagrams default to build/diagrams/ per REQ-REDESIGN-21; users promote
# individual files to reference/diagrams/ manually after migration.
LEGACY_DIRS: dict[str, str] = {
    "brainstorm": "build/brainstorm",
    "specs": "build/specs",
    "design": "build/design",
    "plans": "build/plans",
    "tasks": "build/tasks",
    "notes": "build/notes",
    "research": "build/research",
    "retros": "build/retros",
    "issues": "build/issues",
    "ideas": "build/ideas",
    "validation": "build/validation",
    "stubs": "build/stubs",
    "excavations": "build/excavations",
    "diagrams": "build/diagrams",
}

# Legacy .lore/-rooted file name -> new path under .lore/.
LEGACY_FILES: dict[str, str] = {
    "vision.md": "reference/vision.md",
}

# Hard-protected paths (REQ-REDESIGN-24). Names relative to .lore/.
PROTECTED_DIRS: frozenset[str] = frozenset({"commissions", "meetings"})
PROTECTED_FILES: frozenset[str] = frozenset(
    {"heartbeat.md", "lore-agents.md", "lore-config.md"}
)

# Frontmatter tag that opts a document out of body link rewriting.
# The whole point of a migration-doc is to show old paths in prose; rewriting
# them defeats the purpose.
MIGRATION_DOC_TAG = "migration-doc"

# ---------------------------------------------------------------------------
# Plan model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Move:
    src: Path
    dst: Path


@dataclass(frozen=True)
class Rewrite:
    """One file's rewrite plan: a list of (line_no, original, replacement)."""

    path: Path  # destination path (post-move)
    edits: tuple[tuple[int, str, str], ...]


@dataclass
class MigrationPlan:
    lore_root: Path
    moves: list[Move] = field(default_factory=list)
    rewrites: list[Rewrite] = field(default_factory=list)
    skipped_custom: list[str] = field(default_factory=list)
    conflicts: list[Move] = field(default_factory=list)

    @property
    def is_noop(self) -> bool:
        return not self.moves and not self.rewrites

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def render(self) -> str:
        lines: list[str] = []
        lines.append(f"Migration plan for {self.lore_root}")
        lines.append("=" * 60)
        if self.is_noop:
            lines.append("No legacy structure detected. Nothing to do.")
            return "\n".join(lines)

        if self.conflicts:
            lines.append("")
            lines.append(
                f"BLOCKED: {len(self.conflicts)} destination collision(s) detected."
            )
            lines.append(
                "Each move below would overwrite an existing file. "
                "Resolve manually before applying."
            )
            for mv in self.conflicts:
                rel_src = mv.src.relative_to(self.lore_root.parent)
                rel_dst = mv.dst.relative_to(self.lore_root.parent)
                lines.append(f"  {rel_src}  ->  {rel_dst}  (destination exists)")

        if self.skipped_custom:
            lines.append("")
            lines.append("Custom directories preserved (skipped):")
            for name in sorted(self.skipped_custom):
                lines.append(f"  - {name}/")

        lines.append("")
        lines.append(f"Moves ({len(self.moves)}):")
        if self.moves:
            for mv in self.moves:
                rel_src = mv.src.relative_to(self.lore_root.parent)
                rel_dst = mv.dst.relative_to(self.lore_root.parent)
                lines.append(f"  {rel_src}  ->  {rel_dst}")
        else:
            lines.append("  (none)")

        lines.append("")
        lines.append(f"Link rewrites ({len(self.rewrites)} files):")
        if self.rewrites:
            for rw in self.rewrites:
                rel = rw.path.relative_to(self.lore_root.parent)
                lines.append(f"  {rel}  ({len(rw.edits)} change(s))")
                for line_no, before, after in rw.edits:
                    lines.append(f"    L{line_no}: {before.rstrip()}")
                    lines.append(f"         -> {after.rstrip()}")
        else:
            lines.append("  (none)")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def detect_legacy(lore_root: Path) -> tuple[list[str], list[str]]:
    """Return (legacy_dirs_present, legacy_files_present), both sorted."""
    dirs = sorted(
        name
        for name in LEGACY_DIRS
        if (lore_root / name).is_dir()
    )
    files = sorted(
        name
        for name in LEGACY_FILES
        if (lore_root / name).is_file()
    )
    return dirs, files


def load_custom_directories(lore_root: Path) -> set[str]:
    """Parse `.lore/lore-config.md` for custom_directories names.

    The config is a markdown file with YAML frontmatter; we only need the
    directory names so a tiny line-based parser suffices and we avoid a
    hard dependency on a YAML library.
    """
    config_path = lore_root / "lore-config.md"
    if not config_path.is_file():
        return set()

    text = config_path.read_text(encoding="utf-8")
    fm = _extract_frontmatter(text)
    if fm is None:
        return set()

    names: set[str] = set()
    in_block = False
    block_indent: int | None = None
    for raw in fm.splitlines():
        stripped = raw.strip()
        if stripped.startswith("#"):
            continue
        if not in_block:
            if stripped.startswith("custom_directories:"):
                in_block = True
                block_indent = None
            continue

        # Inside the custom_directories block.
        if not stripped:
            continue
        # Determine list-item indent (first child sets it).
        leading = len(raw) - len(raw.lstrip(" "))
        if block_indent is None:
            block_indent = leading
        # A new top-level key with no leading space ends the block.
        if leading == 0 and ":" in stripped:
            break
        if leading < block_indent:
            break
        # Entries look like `name: [status, ...]` or `name:` then nested list.
        if ":" in stripped:
            key = stripped.split(":", 1)[0].strip()
            if key:
                names.add(key)
    return names


def _extract_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block content, or None if absent."""
    if not text.startswith("---"):
        return None
    # Find the closing --- on its own line.
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "\n".join(lines[1:idx])
    return None


# ---------------------------------------------------------------------------
# Move planning
# ---------------------------------------------------------------------------


def plan_moves(lore_root: Path) -> list[Move]:
    moves: list[Move] = []
    for legacy_name, new_subpath in LEGACY_DIRS.items():
        legacy_dir = lore_root / legacy_name
        if not legacy_dir.is_dir():
            continue
        new_root = lore_root / new_subpath
        for src in sorted(legacy_dir.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(legacy_dir)
            dst = new_root / rel
            moves.append(Move(src=src, dst=dst))

    for legacy_name, new_subpath in LEGACY_FILES.items():
        legacy_file = lore_root / legacy_name
        if legacy_file.is_file():
            moves.append(Move(src=legacy_file, dst=lore_root / new_subpath))
    return moves


# ---------------------------------------------------------------------------
# Path-rewriting engine
# ---------------------------------------------------------------------------


def _build_path_pattern() -> re.Pattern[str]:
    """One regex that finds any old `.lore/<legacy>/...` or `.lore/vision.md`.

    Group `dir` matches a legacy directory name; group `file` matches a
    legacy single-file name (currently just `vision.md`). Exactly one of the
    two groups participates in any given match.
    """
    dir_alt = "|".join(re.escape(name) for name in LEGACY_DIRS)
    file_alt = "|".join(re.escape(name) for name in LEGACY_FILES)
    # Trailing context: dirs require `/`; files require not-word/not-dot/end
    # so we don't match `vision.md.bak`.
    return re.compile(
        r"\.lore/(?:(?P<dir>" + dir_alt + r")/"
        r"|(?P<file>" + file_alt + r")(?![\w.]))"
    )


_PATH_RE = _build_path_pattern()


def rewrite_path_string(s: str) -> str:
    """Rewrite every legacy `.lore/...` reference in `s`."""

    def repl(m: re.Match[str]) -> str:
        if m.group("dir") is not None:
            return ".lore/" + LEGACY_DIRS[m.group("dir")] + "/"
        return ".lore/" + LEGACY_FILES[m.group("file")]

    return _PATH_RE.sub(repl, s)


# Detect a fenced code block opener: ``` or ~~~ (3+) optionally followed by
# an info string. We don't try to be perfect about indented code blocks; the
# common case in lore docs is fenced.
_FENCE_RE = re.compile(r"^(?P<indent>\s*)(?P<fence>`{3,}|~{3,})")


def rewrite_document(
    text: str,
    *,
    skip_body: bool = False,
) -> tuple[str, list[tuple[int, str, str]]]:
    """Rewrite legacy path strings in `text`.

    Returns the rewritten document plus an `edits` list of
    `(line_no, before, after)` tuples (1-indexed) for reporting.

    Frontmatter is always rewritten. Body lines are rewritten only when
    `skip_body` is False; lines inside fenced code blocks are never rewritten.
    """
    lines = text.splitlines(keepends=True)
    edits: list[tuple[int, str, str]] = []

    # Locate frontmatter range, if any. fm_open/fm_close are line indices of
    # the opening and closing `---` delimiters; frontmatter content lies
    # strictly between them.
    fm_open: int | None = None
    fm_close: int | None = None
    if lines and lines[0].rstrip("\r\n") == "---":
        for idx in range(1, len(lines)):
            if lines[idx].rstrip("\r\n") == "---":
                fm_open = 0
                fm_close = idx
                break

    in_code = False
    fence_marker: str | None = None
    out: list[str] = []
    for idx, line in enumerate(lines):
        if fm_open is not None and (idx == fm_open or idx == fm_close):
            # The `---` delimiters themselves; never contain paths.
            new_line = line
        elif fm_open is not None and fm_open < idx < fm_close:
            new_line = _rewrite_line(line)
        else:
            # Body region: track fenced code blocks; never rewrite inside.
            fence_match = _FENCE_RE.match(line)
            if fence_match:
                marker = fence_match.group("fence")[0]  # ` or ~
                if not in_code:
                    in_code = True
                    fence_marker = marker
                elif marker == fence_marker:
                    in_code = False
                    fence_marker = None
                new_line = line
            elif in_code or skip_body:
                new_line = line
            else:
                new_line = _rewrite_line(line)

        if new_line != line:
            edits.append((idx + 1, line, new_line))
        out.append(new_line)

    return "".join(out), edits


def _rewrite_line(line: str) -> str:
    return rewrite_path_string(line)


def has_migration_doc_tag(text: str) -> bool:
    """Check whether the document's frontmatter tags include `migration-doc`.

    Intentionally lenient: matches `tags: [..., migration-doc, ...]` and
    block-style `tags:\n  - migration-doc`.
    """
    fm = _extract_frontmatter(text)
    if fm is None:
        return False
    in_tags = False
    for raw in fm.splitlines():
        stripped = raw.strip()
        if not in_tags:
            if stripped.startswith("tags:"):
                value = stripped[len("tags:") :].strip()
                if value.startswith("["):
                    inner = value.strip("[]")
                    parts = [p.strip().strip("\"'") for p in inner.split(",")]
                    if MIGRATION_DOC_TAG in parts:
                        return True
                elif value:
                    # Single inline value, e.g., `tags: migration-doc`.
                    if value.strip("\"'") == MIGRATION_DOC_TAG:
                        return True
                else:
                    in_tags = True
            continue
        # Inside block-style list under `tags:`.
        if stripped.startswith("- "):
            entry = stripped[2:].strip().strip("\"'")
            if entry == MIGRATION_DOC_TAG:
                return True
            continue
        if not stripped or stripped.startswith("#"):
            continue
        # Any non-list line ends the block.
        break
    return False


# ---------------------------------------------------------------------------
# Plan building
# ---------------------------------------------------------------------------


def is_protected(rel_path: Path, custom_dirs: set[str]) -> bool:
    """True if a path under `.lore/` must not be touched."""
    parts = rel_path.parts
    if not parts:
        return True
    head = parts[0]
    if head in PROTECTED_DIRS or head in custom_dirs:
        return True
    if len(parts) == 1 and head in PROTECTED_FILES:
        return True
    return False


def _candidate_files_for_rewrite(
    lore_root: Path,
    moves: list[Move],
    custom_dirs: set[str],
) -> Iterable[Path]:
    """Yield destination paths whose contents may need rewriting.

    Includes (a) all move destinations and (b) every existing markdown file
    under `.lore/` that is not protected and not the source of a planned move.
    """
    move_srcs = {m.src for m in moves}
    seen: set[Path] = set()

    for m in moves:
        if m.dst.suffix == ".md" and m.dst not in seen:
            seen.add(m.dst)
            yield m.dst

    if not lore_root.exists():
        return

    for path in sorted(lore_root.rglob("*.md")):
        if not path.is_file():
            continue
        if path in move_srcs:
            continue  # will be rewritten at its destination
        try:
            rel = path.relative_to(lore_root)
        except ValueError:
            continue
        if is_protected(rel, custom_dirs):
            continue
        if path in seen:
            continue
        seen.add(path)
        yield path


def build_plan(lore_root: Path) -> MigrationPlan:
    custom_dirs = load_custom_directories(lore_root)
    moves = plan_moves(lore_root)
    conflicts = [m for m in moves if m.dst != m.src and m.dst.exists()]
    plan = MigrationPlan(
        lore_root=lore_root,
        moves=moves,
        skipped_custom=sorted(custom_dirs),
        conflicts=conflicts,
    )

    # We need source content for files being moved; build a map src -> text.
    src_text: dict[Path, str] = {}
    for mv in moves:
        try:
            src_text[mv.src] = mv.src.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            # Non-text file (e.g., binary diagram). Move it as-is, no rewrite.
            src_text[mv.src] = ""

    src_to_dst = {mv.src: mv.dst for mv in moves}

    for path in _candidate_files_for_rewrite(lore_root, moves, custom_dirs):
        if path in src_to_dst.values():
            # Destination of a move: read text from source.
            src = next(s for s, d in src_to_dst.items() if d == path)
            text = src_text.get(src, "")
        else:
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

        if not text:
            continue

        skip_body = has_migration_doc_tag(text)
        new_text, edits = rewrite_document(text, skip_body=skip_body)
        if edits:
            plan.rewrites.append(Rewrite(path=path, edits=tuple(edits)))

    return plan


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


class MigrationConflictError(RuntimeError):
    """Raised when apply_plan is called with a plan that has conflicts."""

    def __init__(self, conflicts: list[Move]) -> None:
        self.conflicts = conflicts
        msg = (
            f"{len(conflicts)} destination collision(s); refusing to apply. "
            "Resolve manually and re-run."
        )
        super().__init__(msg)


def apply_plan(plan: MigrationPlan) -> None:
    """Execute the plan: move files, then write rewritten contents."""
    if plan.conflicts:
        # Refusing to mutate is the right call: rename() would silently
        # overwrite on POSIX and raise on Windows, leaving a half-migrated
        # tree. Surface the list and let the human resolve it.
        raise MigrationConflictError(plan.conflicts)
    # 1. Move files. Create parent directories as needed. Reference dir is
    #    only created if a move targets it (vision.md), preserving the
    #    "learned/ is born from /learn" rule (REQ-REDESIGN-4).
    pending_writes: list[tuple[Path, str]] = []
    rewrite_map = {rw.path: rw for rw in plan.rewrites}

    for mv in plan.moves:
        mv.dst.parent.mkdir(parents=True, exist_ok=True)
        # Read source text for any rewrite, then move.
        try:
            text = mv.src.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            text = None

        mv.src.rename(mv.dst)

        if text is not None and mv.dst in rewrite_map:
            new_text, _ = rewrite_document(
                text, skip_body=has_migration_doc_tag(text)
            )
            pending_writes.append((mv.dst, new_text))

    # 2. Rewrite files that were already in place (not part of a move).
    moved_dsts = {mv.dst for mv in plan.moves}
    for rw in plan.rewrites:
        if rw.path in moved_dsts:
            continue  # handled in the move step above
        try:
            text = rw.path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new_text, _ = rewrite_document(
            text, skip_body=has_migration_doc_tag(text)
        )
        pending_writes.append((rw.path, new_text))

    for path, content in pending_writes:
        path.write_text(content, encoding="utf-8")

    # 3. Remove now-empty legacy directories.
    for legacy_name in LEGACY_DIRS:
        legacy_dir = plan.lore_root / legacy_name
        if legacy_dir.is_dir():
            _remove_if_empty(legacy_dir)


def _remove_if_empty(path: Path) -> None:
    """Remove `path` and its empty parents up the tree."""
    if not path.is_dir():
        return
    # Recurse into subdirs first.
    for child in sorted(path.iterdir()):
        if child.is_dir():
            _remove_if_empty(child)
    if not any(path.iterdir()):
        path.rmdir()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tend_migrate",
        description=(
            "Migrate a project's .lore/ tree from the legacy 14-directory "
            "layout to the build/reference/learned model. Dry-run by default."
        ),
    )
    p.add_argument(
        "--lore-dir",
        type=Path,
        default=Path(".lore"),
        help="Path to the .lore/ directory (default: ./.lore).",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Apply the plan. Without this flag, runs in dry-run mode.",
    )
    p.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt when applying.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    lore_root = args.lore_dir.resolve()

    if not lore_root.is_dir():
        print(f"error: {lore_root} is not a directory", file=sys.stderr)
        return 2

    legacy_dirs, legacy_files = detect_legacy(lore_root)
    if not legacy_dirs and not legacy_files:
        print(f"No legacy structure detected under {lore_root}.")
        print("Nothing to do (already migrated or never used the old layout).")
        return 0

    plan = build_plan(lore_root)
    print(plan.render())

    if plan.has_conflicts:
        print("", file=sys.stderr)
        print(
            "Cannot apply: destination collisions detected. "
            "Resolve the conflicts above and re-run.",
            file=sys.stderr,
        )
        return 3

    if not args.apply:
        print("")
        print("Dry-run only. Re-run with --apply to execute.")
        return 0

    if not args.yes:
        try:
            answer = input("\nApply this plan? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print("Aborted.")
            return 1

    apply_plan(plan)
    print("\nMigration applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
