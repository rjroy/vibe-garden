"""Regression checks for read-only smell diagnosis and user-selected handoff."""

from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def _prompt() -> str:
    return " ".join(
        (PLUGIN_ROOT / "skills/refactor/SKILL.md")
        .read_text(encoding="utf-8")
        .split()
    )


def test_refactor_is_bounded_read_only_diagnosis() -> None:
    prompt = _prompt()

    assert "Begin with read-only diagnosis" in prompt
    assert "If it is unclear, ask one bounded question" in prompt
    assert "Do not infer a large scope from Git state" in prompt
    assert (
        "Inspect the relevant implementation, tests, callers, and consumers"
        in prompt
    )
    assert "current user intent governs" in prompt
    assert "No finding is a valid result" in prompt
    assert "Do not edit files, apply fixes, or begin implementation" in prompt


def test_refactor_smells_are_cues_and_handoff_requires_user_choice() -> None:
    prompt = _prompt()

    for smell in (
        "duplication",
        "shotgun surgery",
        "speculative generality",
        "lazy elements",
        "middle men",
        "data clumps",
        "primitive obsession",
    ):
        assert smell in prompt
    assert "not a required catalog to complete" in prompt
    assert (
        "A loop, switch, data class, comment, or simple name is not inherently a defect"
        in prompt
    )
    assert "Explain the actual maintenance or future-change cost" in prompt
    assert "let them choose whether, and which, to address" in prompt
    assert (
        "If the user asks to proceed, hand `/simplify` only the selected findings"
        in prompt
    )
    assert "never bundle it quietly into a behavior-preserving cleanup" in prompt
