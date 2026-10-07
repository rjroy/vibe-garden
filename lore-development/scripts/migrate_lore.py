#!/usr/bin/env python3
"""Preview or safely move legacy lore documents into current storage zones."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from ensure_local import ensure_local
from legacy_html import convert_html


@dataclass(frozen=True)
class Move:
    source: Path
    destination: Path
    legacy_spec: bool = False
    backup: Path | None = None
    converted_markdown: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Plan:
    root: Path
    moves: tuple[Move, ...]
    edits: tuple[tuple[Path, bytes, bytes], ...]
    unresolved: tuple[str, ...]
    tracked_local: tuple[Path, ...]
    warnings: tuple[str, ...] = ()


FLAT_DIRECTORY_MAP = {
    "specs": ("work/intents", True),
    "intents": ("work/intents", False),
    "brainstorm": ("work/brainstorm", False),
    "design": ("work/design", False),
    "research": ("work/research", False),
    "retros": ("work/retros", False),
    "issues": ("work/issues", False),
    "ideas": ("work/ideas", False),
    "validation": ("work/validation", False),
    "stubs": ("work/stubs", False),
    "diagrams": ("work/diagrams", False),
    "excavations": ("work/excavations", False),
    "plans": ("local/plans", False),
    "tasks": ("local/tasks", False),
    "notes": ("local/notes", False),
}
WORK_DIRECTORY_MAP = {
    "specs": ("work/intents", True),
    "plans": ("local/plans", False),
    "tasks": ("local/tasks", False),
    "notes": ("local/notes", False),
}
PRESERVED_ROOT_DIRS = {"work", "reference", "learned", "local"}
PRESERVED_ROOT_FILES = {
    "heartbeat.md",
    "lore-agents.md",
    "lore-config.md",
    "vision.md",
}


def _requires_local_storage(move: Move) -> bool:
    return ".lore/local/" in move.destination.as_posix() or move.backup is not None


def _preview_command(root: Path) -> str:
    return (
        f"python3 {shlex.quote(str(Path(__file__).resolve()))} "
        f"{shlex.quote(str(root))}"
    )


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def _git_root(root: Path) -> bool:
    return _git(root, "rev-parse", "--show-toplevel").returncode == 0


def _check_no_symlink_chain(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"path {path} escapes supplied project root {root}; inspect the root "
            "and intended migration paths, then rerun preview with the correct root."
        ) from exc
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(
                f"refusing symlink path {current}: migration will not dereference it. "
                "Inspect the link target and decide whether this path is intentional; "
                "do not replace or follow it automatically, then rerun preview."
            )


def _source_files(root: Path, source: Path) -> list[Path]:
    _check_no_symlink_chain(root, source)
    if not source.exists():
        return []
    if not source.is_dir():
        raise ValueError(
            f"expected legacy source directory {source}, but it is not a directory. "
            "Inspect that path and the project root; preserve its contents and rerun "
            "preview after resolving the layout."
        )
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(source, followlinks=False):
        here = Path(current)
        for name in list(dirnames):
            entry = here / name
            if entry.is_symlink():
                raise ValueError(
                    f"refusing symlink directory {entry}: migration will not traverse "
                    "it. Inspect its target and decide whether the linked content "
                    "belongs in this migration; do not dereference it automatically."
                )
        for name in filenames:
            entry = here / name
            if entry.is_symlink():
                raise ValueError(
                    f"refusing symlink file {entry}: migration will not dereference "
                    "it. Inspect its link target and decide whether the linked "
                    "content belongs in this migration; no target was read."
                )
            if not entry.is_file():
                raise ValueError(
                    f"refusing non-regular file {entry}: migration handles only "
                    "regular files. Inspect its type and decide whether this path "
                    "is an intended migration source."
                )
            files.append(entry)
    return sorted(files)


def _scan_lore_text(root: Path) -> list[Path]:
    lore = root / ".lore"
    _check_no_symlink_chain(root, lore)
    if not lore.exists():
        return []
    result: list[Path] = []
    for current, dirnames, filenames in os.walk(lore, followlinks=False):
        here = Path(current)
        relative_here = here.relative_to(lore)
        if relative_here == Path("local"):
            dirnames[:] = [name for name in dirnames if name != "migration-backups"]
        for name in list(dirnames):
            entry = here / name
            if entry.is_symlink():
                raise ValueError(
                    f"refusing symlink directory while scanning lore: {entry}. "
                    "Inspect the link and its intended scope; migration will not "
                    "traverse or dereference it."
                )
        for name in filenames:
            entry = here / name
            if entry.suffix.lower() not in {".md", ".html", ".htm"}:
                continue
            if entry.is_symlink() or not entry.is_file():
                raise ValueError(
                    f"refusing unsafe lore document {entry}: it is not a regular "
                    "file. Inspect the path and decide how to handle it; migration "
                    "will not dereference links."
                )
            result.append(entry)
    return result


def _external_references(root: Path, mapping: dict[str, str]) -> list[str]:
    """Find resolvable or literal references outside .lore without editing them."""
    ignored = {
        ".git",
        ".lore",
        ".beads",
        ".venv",
        "node_modules",
        "vendor",
        "dist",
        "build",
    }
    findings: set[str] = set()
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        here = Path(current)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in ignored and not (here / name).is_symlink()
        ]
        for name in filenames:
            document = here / name
            if document.suffix.lower() not in {".md", ".html", ".htm"}:
                continue
            if document.is_symlink() or not document.is_file():
                continue
            try:
                text = document.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            _rewritten, changed = _rewrite_document(document, text, root, mapping)
            for source in mapping:
                if source in text or source in changed:
                    findings.add(
                        f"{document.relative_to(root)} refers to moved path {source}; "
                        "external documents were not edited"
                    )
    return sorted(findings)


def _source_mapping(root: Path) -> tuple[list[Move], dict[str, str], tuple[str, ...]]:
    lore = root / ".lore"
    moves: list[Move] = []
    mappings: dict[str, str] = {}
    reserved: dict[Path, Path] = {}
    sources: list[tuple[Path, Path, bool]] = []
    for directory, (destination, is_spec) in FLAT_DIRECTORY_MAP.items():
        sources.append((lore / directory, lore / destination, is_spec))
    for directory, (destination, is_spec) in WORK_DIRECTORY_MAP.items():
        sources.append((lore / "work" / directory, lore / destination, is_spec))

    in_git = _git_root(root)
    for source_dir, destination_dir, legacy_spec in sources:
        for source in _source_files(root, source_dir):
            relative = source.relative_to(source_dir)
            destination = destination_dir / relative
            converted_markdown: str | None = None
            backup: Path | None = None
            warnings: tuple[str, ...] = ()
            if source.suffix.lower() in {".html", ".htm"}:
                try:
                    conversion = convert_html(
                        source.read_text(encoding="utf-8"), source.as_posix()
                    )
                except UnicodeDecodeError as exc:
                    raise ValueError(
                        f"cannot safely convert non-UTF-8 HTML source {source}: "
                        "bytes are not valid "
                        "UTF-8, so preserving its content as Markdown is uncertain. "
                        "Keep the original bytes; decide explicitly whether to "
                        "provide a correct encoding/conversion or leave this file "
                        "unmigrated. No lossy conversion was attempted."
                    ) from exc
                converted_markdown = conversion.markdown
                warnings = conversion.warnings
                destination = destination.with_suffix(".md")
                backup = lore / "local/migration-backups" / source.relative_to(lore)
                _check_no_symlink_chain(root, backup.parent)
                if backup.exists() or backup.is_symlink() or backup in reserved:
                    raise ValueError(
                        f"HTML backup collision at {backup}; source is {source}. "
                        "Both paths are preserved. Compare the existing backup and "
                        "source, decide explicitly which path/content should be "
                        "retained, and rerun preview; migration will not overwrite "
                        "or delete either file."
                    )
                if (
                    in_git
                    and _git(
                        root,
                        "ls-files",
                        "--error-unmatch",
                        "--",
                        f":(literal){backup.relative_to(root).as_posix()}",
                    ).returncode
                    == 0
                ):
                    raise ValueError(
                        f"HTML backup path {backup} is already present in the Git "
                        f"index. Inspect it with git ls-files --stage -- "
                        f"{shlex.quote(backup.relative_to(root).as_posix())}, compare "
                        "the indexed and working-tree content with the source, then "
                        "resolve ownership explicitly; neither path was overwritten."
                    )
            _check_no_symlink_chain(root, destination.parent)
            if (
                destination.exists()
                or destination.is_symlink()
                or destination in reserved
            ):
                raise ValueError(
                    f"destination collision: source {source} would move to existing "
                    f"path {destination}. Nothing was overwritten. Compare both "
                    "documents and choose an intentional destination/content; do "
                    "not delete or overwrite either automatically, then rerun preview."
                )
            if in_git:
                indexed = _git(
                    root,
                    "ls-files",
                    "--error-unmatch",
                    "--",
                    f":(literal){destination.relative_to(root).as_posix()}",
                )
                if indexed.returncode == 0:
                    raise ValueError(
                        f"destination collision in Git index at {destination} for "
                        f"source {source}. Inspect its index entry with "
                        "git ls-files --stage -- "
                        f"{shlex.quote(destination.relative_to(root).as_posix())}; "
                        "compare source and destination, then resolve ownership "
                        "explicitly. Migration will not overwrite or remove it."
                    )
            move = Move(
                source, destination, legacy_spec, backup, converted_markdown, warnings
            )
            moves.append(move)
            reserved[destination] = source
            if backup is not None:
                if backup in reserved or backup.exists() or backup.is_symlink():
                    other_source = reserved.get(backup)
                    raise ValueError(
                        f"HTML backup collision at {backup} for source {source}"
                        + (f" (also claimed by {other_source})" if other_source else "")
                        + ". Nothing was overwritten. Compare the sources and backup, "
                        "resolve the intended paths explicitly, and rerun preview."
                    )
                reserved[backup] = source
            old = source.relative_to(root).as_posix()
            new = destination.relative_to(root).as_posix()
            mappings[old] = new
    unknowns: list[str] = []
    if lore.is_dir():
        for entry in sorted(lore.iterdir()):
            if entry.is_dir() and entry.name not in PRESERVED_ROOT_DIRS | set(
                FLAT_DIRECTORY_MAP
            ):
                unknowns.append(
                    f"unmapped legacy directory preserved: {entry.relative_to(root)}"
                )
            elif entry.is_file() and entry.name not in PRESERVED_ROOT_FILES:
                unknowns.append(
                    f"unmapped legacy file preserved: {entry.relative_to(root)}"
                )
    return moves, mappings, tuple(unknowns)


_FM_FIELD = re.compile(r"^([A-Za-z0-9_-]+)\s*:")
_MD_LINK = re.compile(r"(!?\[[^\]]*\]\()([^\s)]*)([^)]*\))")
_HTML_LINK = re.compile(r"(?i)(\b(?:href|src)\s*=\s*)([\"'])([^\"']+)([\"'])")
_CODE_SPAN = re.compile(r"(?s)(```.*?```|~~~.*?~~~|`[^`\n]*`)")
_HTML_META = re.compile(r"(?is)<meta\b[^>]*>")
_HTML_ATTRIBUTE = re.compile(r"(?i)(\b[A-Za-z0-9_-]+\s*=\s*)([\"'])([^\"']*)([\"'])")
_PATH_FIELDS = {"related", "source", "fg-sources", "migrated-from"}

_STATUS_MIGRATION = {
    "draft": "draft", "open": "draft", "pending": "draft",
    "in_progress": "draft", "approved": "approved",
    "completed": "completed", "complete": "completed",
    "implemented": "completed", "executed": "completed",
    "resolved": "completed", "current": "completed", "active": "completed",
    "archived": "archived", "superseded": "archived", "parked": "archived",
    "outdated": "archived", "wontfix": "archived", "skipped": "archived",
}


def _normalize_legacy_status(text: str, source: Path) -> str:
    """Normalize a mapped artifact's lifecycle status without touching its body."""
    if not text.startswith(("---\n", "---\r\n")):
        return text
    newline = "\r\n" if text.startswith("---\r\n") else "\n"
    lines = text.splitlines(keepends=True)
    close = next(
        (i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"), None
    )
    if close is None:
        return text
    status_index = next(
        (i for i in range(1, close) if re.match(r"^status\s*:", lines[i])), None
    )
    if status_index is None:
        return text
    match = re.match(
        r"^status\s*:\s*([\"']?)([A-Za-z_]+)\1\s*(\r?\n)?$",
        lines[status_index],
    )
    if match is None:
        line_number = status_index + 1
        observed = lines[status_index].rstrip("\r\n")
        location = (
            f"{source} (converted Markdown metadata line {line_number})"
            if source.suffix.lower() in {".html", ".htm"}
            else f"{source}:{line_number}"
        )
        raise ValueError(
            f"cannot safely identify lifecycle status in {location}; "
            f"observed {observed!r}. The value must be explicit. Choose draft, "
            "approved, completed, or archived based on the document's meaning; "
            "never infer approval. Preserve the original value in a separate "
            "legacy_status field if useful. Edit this legacy file deliberately, "
            "then rerun the no-write preview."
        )
    original = match.group(2)
    normalized = _STATUS_MIGRATION.get(original.lower())
    if normalized is None:
        location = (
            f"{source} (converted Markdown metadata line {status_index + 1})"
            if source.suffix.lower() in {".html", ".htm"}
            else f"{source}:{status_index + 1}"
        )
        raise ValueError(
            f"unknown legacy status {original!r} in {location}; "
            "preview refused without changing files. Decide what the document "
            "means, then explicitly set status to draft, approved, completed, or "
            "archived; never infer approval from agent work or arbitrary edits. "
            "If useful, retain the source value as legacy_status. After editing, "
            "rerun the no-write preview."
        )
    if original == normalized:
        return text
    if not any(line.startswith("legacy_status:") for line in lines[1:close]):
        lines.insert(close, f"legacy_status: {original}{newline}")
    lines[status_index] = f"status: {normalized}{newline}"
    return "".join(lines)


def _is_legacy_spec_path(path: str) -> bool:
    return path.startswith((".lore/specs/", ".lore/work/specs/"))


def _link_target(document: Path, raw: str, root: Path) -> tuple[Path | None, str]:
    if raw.startswith(("http://", "https://", "mailto:", "#", "//")):
        return None, raw
    without_fragment, fragment_marker, fragment = raw.partition("#")
    path_part, query_marker, query = without_fragment.partition("?")
    suffix = (f"?{query}" if query_marker else "") + (
        f"#{fragment}" if fragment_marker else ""
    )
    if not path_part:
        return None, suffix
    if path_part.startswith(".lore/"):
        resolved = root / path_part
    else:
        resolved = document.parent / path_part
    try:
        relative = resolved.resolve(strict=False).relative_to(root)
    except ValueError:
        return None, raw
    return root / relative, suffix


def _rewrite_document(
    document: Path,
    text: str,
    root: Path,
    mapping: dict[str, str],
    destination_document: Path | None = None,
    unresolved_links: set[str] | None = None,
) -> tuple[str, set[str]]:
    destination_document = destination_document or document
    updated = text
    changed: set[str] = set()
    # Rewrite exact project-root lore paths only in known path-bearing metadata.
    lines = updated.splitlines(keepends=True)
    if lines and lines[0].rstrip("\r\n") == "---":
        closing = next(
            (i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"),
            None,
        )
        if closing is not None:
            field: str | None = None
            for index in range(1, closing):
                match = _FM_FIELD.match(lines[index])
                if match:
                    field = match.group(1)
                elif lines[index].strip() and not lines[index].lstrip().startswith("-"):
                    field = None
                if field in _PATH_FIELDS:
                    for old, new in mapping.items():
                        # Under the reference policy, old plans/notes/tasks are
                        # not durable source authority. Only legacy spec
                        # provenance is remapped; other fg-sources entries are
                        # left for explicit field-guide reassessment.
                        if field == "fg-sources" and not _is_legacy_spec_path(old):
                            continue
                        # Path values are YAML scalars/list entries; replace exact
                        # path tokens, not arbitrary prose or code examples.
                        pattern = re.compile(
                            rf"(?<![A-Za-z0-9_./-]){re.escape(old)}(?=$|[\s,\]}}\"'])"
                        )
                        if pattern.search(lines[index]):
                            lines[index] = pattern.sub(new, lines[index])
                            changed.add(old)
            updated = "".join(lines)

    def rewrite_link(match: re.Match[str], prefix: str, raw: str, suffix: str) -> str:
        target, url_suffix = _link_target(document, raw, root)
        if target is None:
            if (
                document != destination_document
                and not raw.startswith(("http://", "https://", "mailto:", "#", "//"))
                and unresolved_links is not None
            ):
                unresolved_links.add(
                    f"{document}: cannot rebase relative link {raw!r} "
                    "outside project root"
                )
            return match.group(0)
        old = target.relative_to(root).as_posix()
        moved_target = mapping.get(old)
        source_moved = document != destination_document
        if moved_target is None and not source_moved:
            return match.group(0)
        if moved_target is None:
            if not target.exists():
                if unresolved_links is not None:
                    unresolved_links.add(
                        f"{document}: cannot rebase unresolved relative link {raw!r}"
                    )
                return match.group(0)
            new_path = target
        else:
            new_path = root / moved_target
            changed.add(old)
        if raw.startswith(".lore/"):
            rewritten_path = new_path.relative_to(root).as_posix()
        else:
            rewritten_path = os.path.relpath(
                new_path, destination_document.parent
            ).replace(os.sep, "/")
        return f"{prefix}{rewritten_path}{url_suffix}{suffix}"

    def rewrite_meta(match: re.Match[str]) -> str:
        tag = match.group(0)
        attributes = {
            attribute.group(1).strip().split("=", 1)[0].lower(): attribute
            for attribute in _HTML_ATTRIBUTE.finditer(tag)
            if attribute.group(1).strip().split("=", 1)[0].lower()
            in {
                "name",
                "content",
            }
        }
        name_attr = attributes.get("name")
        content_attr = attributes.get("content")
        if name_attr is None or content_attr is None:
            return tag
        field = name_attr.group(3).lower()
        if field not in _PATH_FIELDS:
            return tag
        content = content_attr.group(3)
        for old, new in mapping.items():
            if field == "fg-sources" and not _is_legacy_spec_path(old):
                continue
            pattern = re.compile(
                rf"(?<![A-Za-z0-9_./-]){re.escape(old)}(?=$|[\s,\]}}\"'])"
            )
            if pattern.search(content):
                content = pattern.sub(new, content)
                changed.add(old)
        if content == content_attr.group(3):
            return tag
        start, end = content_attr.span(3)
        return tag[:start] + content + tag[end:]

    # Restrict link rewriting to prose; fenced and inline code may intentionally
    # show historical path strings and are not navigation references.
    chunks = _CODE_SPAN.split(updated)
    for index in range(0, len(chunks), 2):
        prose = _MD_LINK.sub(
            lambda m: rewrite_link(m, m.group(1), m.group(2), m.group(3)),
            chunks[index],
        )
        chunks[index] = _HTML_LINK.sub(
            lambda m: rewrite_link(m, m.group(1) + m.group(2), m.group(3), m.group(4)),
            prose,
        )
        chunks[index] = _HTML_META.sub(rewrite_meta, chunks[index])
    updated = "".join(chunks)
    return updated, changed


def _assert_editable_reference(path: Path) -> None:
    try:
        mode = path.stat().st_mode
    except OSError as exc:
        raise ValueError(
            f"cannot inspect reference path {path} before editing: {exc}. Check "
            "that exact path and its ownership/permissions, preserving current "
            "content; resolve deliberately without sudo or blanket chmod, then "
            "rerun preview."
        ) from exc
    # Check mode bits as well as effective access: privileged processes may be
    # able to write a deliberately read-only file, but migration should not.
    writable = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    if not stat.S_ISREG(mode) or not mode & writable:
        raise ValueError(
            f"reference file is not writable or regular: {path} (mode "
            f"{stat.filemode(mode)}). Review its ownership/permissions and intended "
            "editability; preserve its content and resolve this exact path without "
            "sudo or blanket chmod, then rerun preview."
        )
    if not os.access(path, os.W_OK):
        raise ValueError(
            f"reference file is not writable for this process: {path}. Review its "
            "ownership/permissions and resolve this exact path without sudo or "
            "blanket chmod; preserve content and rerun preview."
        )


def _clean_tracked_paths(root: Path, paths: set[Path]) -> set[Path]:
    if not _git_root(root):
        return set()
    tracked: list[Path] = []
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        literal = f":(literal){relative}"
        listed = _git(root, "ls-files", "--error-unmatch", "--", literal)
        if listed.returncode != 0:
            continue
        # Check both sides of the index separately. `git diff HEAD` alone misses
        # staged-only changes when the worktree has been restored to HEAD.
        index_matches_head = _git(
            root, "diff", "--cached", "--quiet", "HEAD", "--", literal
        )
        worktree_matches_index = _git(root, "diff", "--quiet", "--", literal)
        if index_matches_head.returncode != 0 or worktree_matches_index.returncode != 0:
            quoted = shlex.quote(relative)
            root_arg = shlex.quote(str(root))
            raise ValueError(
                f"tracked source has staged or unstaged changes (including "
                f"reference edits): {relative}. Migration refuses to overwrite "
                "them. Inspect both `git -C "
                f"{root_arg} diff -- {quoted}` and `git -C {root_arg} diff "
                f"--cached -- {quoted}`; preserve or intentionally resolve your "
                "changes, then rerun preview. Do not reset, checkout, or discard "
                "the changes to bypass this check."
            )
        tracked.append(path)
    return set(tracked)


def build_plan(project_root: Path) -> Plan:
    root = project_root.resolve()
    if not root.is_dir():
        raise ValueError(
            f"project root {project_root} is missing or is not a directory. Check "
            "the exact path and that it is the project root containing .lore/; "
            "do not create or modify directories just to bypass this check. Rerun "
            "preview with the intended root."
        )
    moves, mapping, warnings = _source_mapping(root)
    if not moves:
        return Plan(root, (), (), (), (), warnings)
    edits: list[tuple[Path, bytes, bytes]] = []
    unresolved_mentions: set[str] = set()
    unresolved_links: set[str] = set()
    move_destinations = {move.source: move.destination for move in moves}
    moves_by_source = {move.source: move for move in moves}
    for document in _scan_lore_text(root):
        move = moves_by_source.get(document)
        if move is not None and move.converted_markdown is not None:
            original = move.converted_markdown
            original_bytes = original.encode("utf-8")
        else:
            try:
                original_bytes = document.read_bytes()
                original = original_bytes.decode("utf-8")
            except UnicodeDecodeError:
                continue
        if move is not None:
            original = _normalize_legacy_status(original, move.source)
        destination_document = move_destinations.get(document, document)
        replacement, changed = _rewrite_document(
            document, original, root, mapping, destination_document, unresolved_links
        )
        for old in mapping:
            if old in original and old not in changed:
                unresolved_mentions.add(old)
        replacement_bytes = replacement.encode("utf-8")
        if replacement_bytes != original_bytes:
            edits.append((destination_document, original_bytes, replacement_bytes))

    unresolved = tuple(
        f"{source}: literal reference found but not safely rewritten; review manually"
        for source in sorted(unresolved_mentions)
    )
    unresolved += tuple(sorted(unresolved_links))
    external = tuple(_external_references(root, mapping))
    move_sources = {move.source for move in moves}
    destination_to_source = {move.destination: move.source for move in moves}
    moves_by_destination = {move.destination: move for move in moves}
    affected = set(move_sources)
    for path, _original, _replacement in edits:
        source_path = destination_to_source.get(path, path)
        affected.add(source_path)
        move = moves_by_destination.get(path)
        # A normal rename carries the source mode to the edit destination. HTML
        # conversion creates a fresh Markdown output and leaves the source as a
        # read-only byte backup, so only its new output needs checking.
        if move is None or move.converted_markdown is None:
            _assert_editable_reference(source_path)
    tracked_paths = _clean_tracked_paths(root, affected)
    tracked = tuple(
        move.source
        for move in moves
        if move.source in tracked_paths
        and ".lore/local/" in move.destination.relative_to(root).as_posix()
    )
    move_warnings = tuple(
        f"{move.source.relative_to(root)}: {warning}"
        for move in moves
        for warning in move.warnings
    )
    return Plan(
        root,
        tuple(moves),
        tuple(edits),
        unresolved + external,
        tracked,
        warnings + move_warnings,
    )


def _print_plan(plan: Plan, apply: bool) -> None:
    mode = "APPLY" if apply else "PREVIEW (no files changed)"
    print(f"{mode}: {plan.root}")
    if not plan.moves:
        print("No legacy files found; already migrated or nothing to do.")
    for move in plan.moves:
        kind = (
            "legacy spec (history; not newly authored intent)"
            if move.legacy_spec
            else "local context"
        )
        tracked = (
            " [tracked; index removal requires --untrack]"
            if move.source in plan.tracked_local
            else ""
        )
        print(
            "MOVE "
            f"{move.source.relative_to(plan.root)} -> "
            f"{move.destination.relative_to(plan.root)} ({kind}){tracked}"
        )
        if move.backup is not None:
            print(
                f"CONVERT HTML -> Markdown {move.source.relative_to(plan.root)} -> "
                f"{move.destination.relative_to(plan.root)}; original backup: "
                f"{move.backup.relative_to(plan.root)}"
            )
    for document, _old, _new in plan.edits:
        print(f"UPDATE REFERENCES {document.relative_to(plan.root)}")
    for warning in plan.warnings:
        print(f"WARNING: {warning}")
    for warning in plan.unresolved:
        print(f"REVIEW: {warning}")
    if plan.tracked_local:
        print(
            "Tracked local files become ignored. Apply requires --untrack to "
            "stage only their index removals; file bytes remain in .lore/local/."
        )
    if any(_requires_local_storage(move) for move in plan.moves):
        print(
            "Local destinations are Git-ignored and machine-specific; "
            "collaborators may not have these files."
        )
    if not apply and plan.moves:
        print(
            "After reviewing this preview, rerun with --apply. Use --untrack "
            "only to authorize tracked local-source index removals."
        )


def apply_plan(plan: Plan, untrack: bool = False) -> None:
    if plan.tracked_local and not untrack:
        paths = ", ".join(
            path.relative_to(plan.root).as_posix() for path in plan.tracked_local
        )
        raise ValueError(
            f"tracked local sources require explicit --untrack approval: {paths}. "
            "No move or index change was made. Ask the user whether they approve "
            "staging index removals for only these paths; files stay in .lore/local/. "
            "Only after explicit approval, rerun the reviewed command with "
            "--apply --untrack. Otherwise stop or change the plan."
        )
    # Setup/ignore is deliberately after all preflight checks and before moves.
    if any(_requires_local_storage(move) for move in plan.moves):
        try:
            ensure_local(plan.root)
        except (OSError, ValueError) as exc:
            raise ValueError(
                f"local storage/ignore setup failed before lore moves: {exc}. "
                "Inspect .gitignore and verify effective ignore behavior with "
                f"`git -C {shlex.quote(str(plan.root))} check-ignore -v --no-index "
                ".lore/local/.ensure-local-ignore-probe`. If a negation or more "
                "specific rule conflicts, decide whether to edit that exact rule; "
                "do not force past the check. Check git status because setup may "
                "have added the root /.lore/local/ rule before verification failed."
            ) from exc
    started: list[Move] = []
    changed_refs: list[tuple[Path, bytes]] = []
    staged_actions: list[tuple[str, str]] = []
    try:
        for move in plan.moves:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            started.append(move)
            if move.converted_markdown is not None and move.backup is not None:
                move.backup.parent.mkdir(parents=True, exist_ok=True)
                with (
                    move.source.open("rb") as original,
                    move.backup.open("xb") as backup,
                ):
                    shutil.copyfileobj(original, backup)
                shutil.copystat(move.source, move.backup)
                with move.destination.open(
                    "x", encoding="utf-8", newline=""
                ) as converted:
                    converted.write(move.converted_markdown)
                move.source.unlink()
            else:
                os.replace(move.source, move.destination)
        for document, original, replacement in plan.edits:
            changed_refs.append((document, original))
            document.write_bytes(replacement)
        if untrack and plan.tracked_local:
            relative_paths = [
                source.relative_to(plan.root).as_posix()
                for source in plan.tracked_local
            ]
            staged_actions = [
                (
                    relative,
                    next(
                        move.destination.relative_to(plan.root).as_posix()
                        for move in plan.moves
                        if move.source == source
                    ),
                )
                for source, relative in zip(
                    plan.tracked_local, relative_paths, strict=True
                )
            ]
            literal_paths = [f":(literal){path}" for path in relative_paths]
            result = _git(plan.root, "rm", "--cached", "--quiet", "--", *literal_paths)
            if result.returncode != 0:
                raise ValueError(
                    "could not stage the exact tracked local index removals for "
                    f"{', '.join(relative_paths)}: {result.stderr.strip()}"
                )
    except Exception as failure:
        recovery_errors: list[str] = []
        for document, original in reversed(changed_refs):
            try:
                document.write_bytes(original)
            except Exception as rollback_error:
                recovery_errors.append(
                    f"could not restore reference {document}: {rollback_error}"
                )
        for move in reversed(started):
            if move.converted_markdown is not None and move.backup is not None:
                try:
                    if not move.source.exists() and move.backup.exists():
                        move.source.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(move.backup, move.source)
                except Exception as rollback_error:
                    recovery_errors.append(
                        f"could not restore source {move.source}: {rollback_error}"
                    )
                try:
                    if move.backup.exists() and move.source.exists():
                        move.backup.unlink()
                except Exception as rollback_error:
                    recovery_errors.append(
                        "could not remove migration backup "
                        f"{move.backup}: {rollback_error}"
                    )
                try:
                    if move.destination.exists():
                        move.destination.unlink()
                except Exception as rollback_error:
                    recovery_errors.append(
                        "could not remove destination "
                        f"{move.destination}: {rollback_error}"
                    )
            elif move.destination.exists():
                try:
                    move.source.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(move.destination, move.source)
                except Exception as rollback_error:
                    recovery_errors.append(
                        f"could not restore source {move.source}: {rollback_error}"
                    )
        if staged_actions:
            paths = ", ".join(relative for relative, _ in staged_actions)
            recovery_errors.append(
                "Git index state for attempted removal path(s) is unverified and "
                f"was not restored automatically: {paths}"
            )
        if recovery_errors:
            details = "; ".join(recovery_errors)
            raise ValueError(
                f"apply failed ({failure}); rollback incomplete. STOP: do not rerun "
                "apply blindly. Manually inspect the listed unresolved paths, "
                f"source/destination files, references, and `git -C "
                f"{shlex.quote(str(plan.root))} status --short` / staged diff; "
                f"recovery errors: {details}"
            ) from failure
        raise ValueError(
            f"apply failed ({failure}); rollback operations completed, but this was "
            "a best-effort recovery, not proof of an unchanged tree. Inspect source, "
            "destination, reference paths, and Git status before retrying; preserve "
            "any remaining content and run a fresh no-write preview only after "
            "confirming the state."
        ) from failure
    for relative, destination in staged_actions:
        print(f"STAGED INDEX REMOVAL {relative}; file bytes remain at {destination}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_root", type=Path, help="project root containing .lore/"
    )
    parser.add_argument(
        "--apply", action="store_true", help="perform the reviewed migration"
    )
    parser.add_argument(
        "--untrack",
        action="store_true",
        help="explicitly authorize staged Git index removals for tracked local files",
    )
    args = parser.parse_args(argv)
    phase = "preflight"
    try:
        plan = build_plan(args.project_root)
        _print_plan(plan, args.apply)
        if args.apply:
            phase = "apply"
            apply_plan(plan, untrack=args.untrack)
            print(
                "Migration applied; source bodies were preserved. Review Git "
                "status and reported links."
            )
    except (OSError, ValueError) as exc:
        print(f"migrate_lore: {exc}", file=sys.stderr)
        if phase == "preflight":
            print(
                "No migration moves or reference edits have started. Resolve the "
                "condition above, then rerun a no-write preview with: "
                f"{_preview_command(args.project_root)}",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
