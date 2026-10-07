#!/usr/bin/env python3
"""Create a project's disposable lore directory and ignore it in Git."""

from __future__ import annotations

import argparse
import shlex
import stat
import subprocess
import sys
from pathlib import Path

IGNORE_RULE = b"/.lore/local/"
IGNORE_PROBE = ".lore/local/.ensure-local-ignore-probe"


def _git_repo_state(root: Path) -> bool | None:
    """Return whether root is in a Git worktree, or None if Git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    return result.returncode == 0


def _verify_ignored(root: Path) -> None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "check-ignore",
            "--no-index",
            "--quiet",
            "--",
            IGNORE_PROBE,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 1:
        raise ValueError(
            "Git does not effectively ignore .lore/local; an ignore negation or "
            "more-specific rule may override /.lore/local/. Inspect the matching "
            f"rule with `git -C {shlex.quote(str(root))} check-ignore -v --no-index "
            f"{IGNORE_PROBE}`; decide whether to edit that exact rule, then verify "
            "again. Do not force past this check; existing ignore rules were left "
            "unchanged."
        )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"git check-ignore exited {result.returncode}"
        raise ValueError(
            f"could not verify .lore/local ignore behavior for {root / IGNORE_PROBE}: "
            f"{detail}. Inspect Git availability and the ignore rule, then retry "
            "setup only after resolving the cause."
        )


def _has_local_negation(contents: bytes) -> bool:
    """Avoid overriding an explicit root .gitignore exception for local lore."""
    for line in contents.splitlines():
        pattern = line.strip()
        if pattern.startswith(b"!") and b".lore/local" in pattern:
            return True
    return False


def ensure_local(project_root: Path) -> bool:
    """Ensure .lore/local exists and is ignored; return whether ignore changed."""
    root = project_root.resolve()
    if not root.is_dir():
        raise ValueError(
            f"project root {project_root} is missing or is not a directory. Check "
            "that this is the intended project directory containing .lore/."
        )

    gitignore = root / ".gitignore"
    try:
        mode = gitignore.lstat().st_mode
    except FileNotFoundError:
        mode = None
    if mode is not None and not stat.S_ISREG(mode):
        raise ValueError(
            f"refusing non-regular .gitignore path {gitignore}. Inspect that path "
            "and preserve its contents; do not replace it automatically."
        )

    lore = root / ".lore"
    if lore.is_symlink() or (lore.exists() and not lore.is_dir()):
        raise ValueError(
            f"refusing unsafe .lore target {lore}: it is a symlink or not a "
            "directory. Inspect the path and decide what it should reference; "
            "setup will not dereference or replace it."
        )
    local = lore / "local"
    if local.is_symlink() or (local.exists() and not local.is_dir()):
        raise ValueError(
            f"refusing unsafe local target {local}: it is a symlink or not a "
            "directory. Inspect the path and decide what it should reference; "
            "setup will not dereference or replace it."
        )

    current = gitignore.read_bytes() if mode is not None else b""
    in_git = _git_repo_state(root)
    if in_git and _has_local_negation(current):
        try:
            _verify_ignored(root)
        except ValueError as exc:
            raise ValueError(
                f"{gitignore} contains an explicit .lore/local ignore exception; "
                "refusing to override it. Inspect the exact negation and its "
                f"effect with `git -C {shlex.quote(str(root))} "
                "check-ignore -v --no-index "
                f"{IGNORE_PROBE}`; decide whether to edit that rule, then verify "
                "again. Do not bypass the guard."
            ) from exc
        raise ValueError(
            f"{gitignore} contains an explicit .lore/local ignore exception; "
            "refusing to override it. Inspect the exact negation and its effect "
            f"with `git -C {shlex.quote(str(root))} check-ignore -v --no-index "
            f"{IGNORE_PROBE}`; "
            "decide whether to edit that rule, then verify again. Do not bypass "
            "the guard."
        )

    if any(line.strip() == IGNORE_RULE for line in current.splitlines()):
        changed = False
    else:
        with gitignore.open("ab") as handle:
            if current and not current.endswith((b"\n", b"\r")):
                handle.write(b"\n")
            handle.write(IGNORE_RULE + b"\n")
        changed = True

    if in_git:
        _verify_ignored(root)

    local.mkdir(parents=True, exist_ok=True)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path, help="project directory to set up")
    args = parser.parse_args()
    try:
        changed = ensure_local(args.project_root)
    except (OSError, ValueError) as exc:
        print(f"ensure_local: {exc}", file=sys.stderr)
        return 1
    print(f".lore/local ready; ignore rule {'added' if changed else 'already present'}")
    git_state = _git_repo_state(args.project_root.resolve())
    if git_state is None:
        print(
            "warning: Git is unavailable; ignore effectiveness was not verified.",
            file=sys.stderr,
        )
    elif not git_state:
        print(
            "note: project is not a Git worktree; rule is ready for future "
            "Git initialization."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
