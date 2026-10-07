"""Regression checks for simplify scope and behavior-preservation contracts."""

from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def _guidance() -> str:
    return " ".join(
        " ".join(
            (PLUGIN_ROOT / path)
            .read_text(encoding="utf-8")
            .split()
        )
        for path in (
            "skills/simplify/SKILL.md",
            "skills/simplify/scope-resolution.md",
        )
    )


def test_simplify_scope_includes_committed_and_pending_changes() -> None:
    prompt = _guidance()

    assert (
        "integration/target branch only when authoritative repository metadata"
        in prompt
    )
    assert "unique merge-base with `HEAD` as the committed boundary" in prompt
    assert "ask if ambiguous" in prompt
    assert "Include relevant staged, unstaged, and untracked changes too" in prompt
    assert (
        "explicit work artifact identified by the invocation/current conversation"
        in prompt
    )
    assert "Git base/range" in prompt
    assert "ask for an artifact, Git base/range, or paths" in prompt
    assert "do not default to dirty-only or the whole repository" in prompt
    assert "Resolve repo-relative paths against the repository root" in prompt
    assert "`@{upstream}`" in prompt
    assert "Never infer scope solely from" in prompt
    assert "Support explicit user refs" in prompt


def test_simplify_preserves_retained_contracts_and_limits_expansion() -> None:
    prompt = _guidance()

    assert "old artifact, which is context rather than binding authority" in prompt
    assert "The current user's direction governs" in prompt
    assert (
        "Findings are recommendations, not authorization to change behavior" in prompt
    )
    assert (
        "requested retirement or other behavior change must be handled separately"
        in prompt
    )
    assert "do not make automatic behavior changes" in prompt
    assert "test count/apparent lack of use makes behavior obsolete" in prompt
    assert "Keep relevant contracts protected" in prompt
    assert (
        "Include necessary adjacent code/tests without absorbing unrelated work"
        in prompt
    )
    for phase in (
        "**cleanup** (delegated edits)",
        "**test** (read-only verification)",
        "**review** (read-only review)",
    ):
        assert phase in prompt
    assert "user-selected findings" in prompt
    assert (
        "paths/scope, intended structural improvement, preserved behaviors, and checks"
        in prompt
    )
    assert "No plan, spec, or behavior matrix is required" in prompt
    assert "standalone scope" in prompt
    assert "material maintenance cost" in prompt
    assert "read-only verification" in prompt
    assert "read-only review" in prompt
    assert (
        "two failed attempts on an issue, or three total correction rounds" in prompt
    )
    assert "no note is mandatory" in prompt
