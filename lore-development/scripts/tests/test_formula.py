"""Regression tests for the reusable Beads workflow formula."""

import tomllib
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
FORMULA_PATH = PLUGIN_ROOT / "formulas/lore-development.formula.toml"


def _formula() -> dict[str, object]:
    with FORMULA_PATH.open("rb") as formula_file:
        return tomllib.load(formula_file)


def test_formula_has_required_inputs_and_workflow_steps() -> None:
    formula = _formula()

    assert formula["formula"] == "lore-development"
    assert formula["type"] == "workflow"
    variables = formula["vars"]
    assert variables["topic"]["required"] is True
    assert variables["artifact_name"]["required"] is True

    steps = formula["steps"]
    assert [step["id"] for step in steps] == [
        "research",
        "brainstorm",
        "intent",
        "design",
        "approve-design",
        "plan",
        "approve-plan",
        "implement",
        "validate",
        "retro",
    ]


def test_approval_steps_are_human_gates() -> None:
    steps = {step["id"]: step for step in _formula()["steps"]}

    for step_id in ("approve-design", "approve-plan"):
        assert steps[step_id]["gate"]["type"] == "human"
    assert "gate" not in steps["intent"]


def test_approval_steps_block_the_next_phase() -> None:
    steps = {step["id"]: step for step in _formula()["steps"]}

    assert steps["design"]["needs"] == ["intent"]
    assert steps["plan"]["needs"] == ["approve-design"]
    assert steps["implement"]["needs"] == ["approve-plan"]
