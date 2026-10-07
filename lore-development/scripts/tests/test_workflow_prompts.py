"""Regression tests for workflow safeguards encoded in plugin prompts."""

import re
from pathlib import Path

import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
def _read(relative_path: str) -> str:
    return (PLUGIN_ROOT / relative_path).read_text(encoding="utf-8")


def _normalized(relative_path: str) -> str:
    return " ".join(_read(relative_path).split())


def _frontmatter(relative_path: str) -> dict[str, object]:
    prompt = _read(relative_path)
    opening, frontmatter, _body = prompt.split("---", maxsplit=2)
    assert opening == ""
    parsed = yaml.safe_load(frontmatter)
    assert isinstance(parsed, dict)
    return parsed


def test_implementation_roles_are_serialized_and_read_only() -> None:
    prompt = _read("skills/implement/SKILL.md")

    assert "Only one agent may operate on a phase's files at a time" in prompt
    assert "Testing and review agents are read-only" in prompt
    assert "Await each result before" in prompt
    assert "dispatching the next role" in prompt


def test_implementation_uses_proportionate_behavioral_evidence() -> None:
    prompt = _normalized("skills/implement/SKILL.md")

    assert "The full suite passing is not enough" in prompt
    assert "focused checks for distinct plausible defects" in prompt
    assert "Do not create requirement IDs, exhaustive mappings" in prompt
    assert "suite passing does not substitute" in prompt
    assert "Current user direction may authorize behavior or contract changes" in prompt
    assert "do not treat an old artifact's silence" in prompt
    assert "new evidence" in prompt


def test_review_workflows_distinguish_initial_and_verification_modes() -> None:
    prompts = [
        _read("skills/implement/SKILL.md"),
        _read("agents/design-reviewer.md"),
        _read("agents/plan-reviewer.md"),
    ]

    for prompt in prompts:
        assert "initial-review" in prompt
        assert "verification" in prompt
        assert "stable ID" in prompt

    for path in [
        "agents/design-reviewer.md",
        "agents/plan-reviewer.md",
    ]:
        prompt = _normalized(path)
        assert "complete unresolved finding records" in prompt
        assert "newly encountered material issue" in prompt
        assert "do not populate a fixed template" in prompt


def test_document_reviewers_do_not_force_ceremonial_output() -> None:
    for path in [
        "agents/design-reviewer.md",
        "agents/plan-reviewer.md",
    ]:
        prompt = _normalized(path)
        assert "guessing which file is newest" in prompt
        assert "force one finding per lens" in prompt
        assert "Reviewed: [timestamp]" not in prompt
        assert "## Strengths" not in prompt


def test_lore_researcher_surfaces_context_without_binding_history() -> None:
    prompt = _normalized("agents/lore-researcher.md")

    assert "shared/frontmatter-schema.md" in prompt
    assert "schema owns document types and lifecycle statuses" in prompt
    assert (
        "their location, status, dates, and links do not make them instructions"
        in prompt
    )
    assert "the user's current direction as the guide" in prompt
    assert "Legacy documents under `work/specs/` are historical input only" in prompt
    assert "Do not silently resolve conflicts" in prompt
    assert "Search all relevant zones even after finding a strong match" in prompt
    assert "Frontmatter improves ranking but is not a prerequisite" in prompt


def test_local_lore_paths_setup_and_legacy_discovery_are_documented() -> None:
    for path in [
        "skills/prep-plan/SKILL.md",
        "skills/implement/SKILL.md",
        "skills/simplify/SKILL.md",
    ]:
        prompt = _normalized(path)
        assert ".lore/local/" in prompt
        assert "scripts/ensure_local.py" in prompt
        assert "from this skill's installed directory" in prompt
        assert "python3 <resolved-helper-path>" in prompt
        assert "Write only after setup succeeds" in prompt
        assert ".lore/work/" in prompt
        assert any(term in prompt for term in ("fall back", "falling back", "fallback"))
    schema = _read("shared/frontmatter-schema.md")
    assert "Legacy plans, tasks, and notes remain readable" in schema


def test_prep_plan_prompts_collaborative_evidence_driven_planning() -> None:
    prompt = _normalized("skills/prep-plan/SKILL.md")

    assert "user's present what and why" in prompt
    assert "Discuss the approach and meaningful evidence with the user" in prompt
    assert "revise when repository facts or other evidence change" in prompt
    assert "as suggestions or historical context" in prompt
    assert "Plans and notes are not promoted to reference material" in prompt
    assert "exhaustive obligation maps, coverage matrices" in prompt
    assert "does not add an approval requirement" in prompt
    for forbidden_rule in [
        "Map the goal or requirements to concrete implementation steps",
        "An unmapped obligation is a planning gap",
        "## Coverage Matrix",
    ]:
        assert forbidden_rule not in prompt


def test_plan_reviewer_avoids_exhaustive_mapping_and_historical_authority() -> None:
    reviewer = _normalized("agents/plan-reviewer.md")

    assert "fits the user's current direction" in reviewer
    assert "do not override current user direction" in reviewer
    assert "do not require exhaustive obligation mapping" in reviewer
    assert "acceptance matrices" in reviewer
    assert "meaningful for the project-specific behavior and risks" in reviewer
    assert "Do not report old-artifact noncompliance alone" in reviewer
    assert "one test per requirement" in reviewer


def test_bun_typescript_reviewer_requires_material_traceable_findings() -> None:
    reviewer = _normalized("agents/bun-typescript-reviewer.md")
    implementation = _normalized("skills/implement/SKILL.md")

    assert "A review that finds no material non-conformance is successful" in reviewer
    assert "Architecture concerns are investigative lenses, not a quota" in reviewer
    assert "Judge validation by whether it proves the requested outcome" in reviewer
    assert "Do not request a test merely because production code lacks" in reviewer
    assert "Raise a new finding only for a material defect introduced" in reviewer
    assert "If the implementation is adequate, say `Accept`" in reviewer
    assert "do not populate a fixed template" in reviewer
    assert "## Requirement Evidence" not in reviewer
    assert "## Findings" not in reviewer
    assert "`lore-development:bun-typescript-reviewer`" in implementation
    assert "Accept adequate work" in implementation
    assert "A request for another test must identify" in implementation


def test_intent_prompt_is_conversational_and_nonbinding() -> None:
    prompt = _normalized("skills/intent/SKILL.md")

    assert "what to build and why" in prompt
    assert "conversational" in prompt
    assert "not a binding contract" in prompt
    assert "The plan is where" in prompt
    assert "current direction takes priority" in prompt
    assert "historical context" in prompt
    assert "## Requirements" not in prompt
    assert "## Validation" not in prompt
    assert "REQ-" not in prompt
    assert "acceptance matrix" in prompt


def test_intent_reviewer_has_fresh_context_modes_without_contract_checks() -> None:
    reviewer = _normalized("agents/intent-reviewer.md")

    assert "initial-review" in reviewer
    assert "verification" in reviewer
    assert "faithfully captures intent" in reviewer
    assert "Do not require numbered requirements" in reviewer
    assert "Do not treat an old artifact's noncompliance" in reviewer


def test_intent_reviewer_and_researcher_treat_legacy_specs_as_history() -> None:
    reviewer = _normalized("agents/intent-reviewer.md")
    researcher = _normalized("agents/lore-researcher.md")

    assert "historical context, not a binding contract" in reviewer
    assert "The user's current direction prevails" in reviewer
    assert (
        "Legacy documents under `work/specs/` are historical input only"
        in researcher
    )
    assert "do not override the user's present direction" in researcher
    assert "old-document noncompliance alone is not a blocker" in researcher

    design_reviewer = _normalized("agents/design-reviewer.md")
    assert "Historical specs and other work artifacts" in design_reviewer
    assert "do not constrain current user direction" in design_reviewer
    assert "old-document noncompliance alone" in design_reviewer


def test_intent_schema_keeps_legacy_specs_historical_only() -> None:
    schema = _normalized("shared/frontmatter-schema.md")

    assert "`.lore/work/specs/`" in schema
    assert "legacy_status" in schema
    assert "requirement IDs and validation sections do not make them authoritative for current work" in schema
    assert "does not make a document newly authored or confer authority" in schema


def test_implementation_does_not_block_on_old_artifact_conflict_alone() -> None:
    prompt = _normalized("skills/implement/SKILL.md")

    assert "A conflict with an old artifact alone is not a blocker" in prompt
    assert "follow current user direction" in prompt
    assert "concrete safety or compatibility consequences" in prompt
    assert "old artifact's omission or contradiction alone" in prompt


def test_implementation_accepts_direct_requests_and_keeps_notes_optional() -> None:
    prompt = _normalized("skills/implement/SKILL.md")
    schema = _normalized("shared/frontmatter-schema.md")
    readme = _normalized("README.md")

    assert "current request or intent, optionally informed" in prompt
    assert "user's current request" in prompt
    assert "A plan is useful but not required" in prompt
    assert "do not create one by default" in prompt
    assert "Do not ask for confirmation between phases" in prompt
    assert "read-only testing agent" in prompt
    assert "read-only review agent" in prompt
    assert "Route material findings to implementation for correction" in prompt
    assert "repeat only the failed checks" in prompt
    assert "terminal review to catch interactions" in prompt
    assert "reuse, replace, or remove" in prompt
    assert "obsolete parallel path or unused scaffolding" in prompt
    assert "material maintenance or behavior cost, not a cleanup quota" in prompt
    assert "does not determine `/implement` execution order" in schema
    assert "an optional plan can help, but is not required" in readme


def test_implementation_reviewers_follow_current_direction() -> None:
    implementation = _normalized("skills/implement/SKILL.md")

    assert "relevant requirements from the source artifact" not in implementation
    assert "mapped source obligations" not in implementation
    assert "obligation-to-evidence mapping" not in implementation
    for path in [
        "agents/bun-typescript-reviewer.md",
        "agents/rust-daemon-cli-reviewer.md",
    ]:
        reviewer = _normalized(path)
        assert "user's current requested behavior" in reviewer
        assert "do not override current user direction" in reviewer
        assert "Do not report noncompliance with an old artifact alone" in reviewer


def test_design_skill_runs_fresh_context_review() -> None:
    prompt = _normalized("skills/design/SKILL.md")

    assert 'subagent_type: "lore-development:design-reviewer"' in prompt
    assert "`initial-review` mode" in prompt
    assert "complete unresolved finding records" in prompt
    assert "`verification` mode" in prompt
    assert "terminal broad acceptance review" in prompt
    assert "do not run another broad review unless accepted scope changed" in prompt


def test_lore_search_contract_includes_lower_confidence_body_matches() -> None:
    schema = _normalized("shared/frontmatter-schema.md")
    readme = _normalized("README.md")

    for document in (schema, readme):
        assert "body" in document
        assert "lower-confidence legacy material" in document


def test_readme_skill_table_matches_active_inventory_and_shared_lifecycle() -> None:
    readme = _normalized("README.md")
    schema = _normalized("shared/frontmatter-schema.md")

    table = readme.split("## Skills", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    listed_skills = set(re.findall(r"`/lore-development:([^`]+)`", table))
    active_skills = {
        path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")
    }
    assert listed_skills == active_skills

    agent_table = readme.split("## Agents", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    listed_agents = set(re.findall(r"\| `([^`]+)` \|", agent_table))
    active_agents = {path.stem for path in (PLUGIN_ROOT / "agents").glob("*.md")}
    assert listed_agents == active_agents
    assert "learned/" in readme
    assert "no lore-development skill currently writes it" in schema
    assert "Shared four-value lifecycle across all lore zones" in schema
    assert "Document-type-specific" not in schema


def test_retired_plan_breakdown_is_not_an_active_skill_or_implement_path(
) -> None:
    implementation = _read("skills/implement/SKILL.md")
    skill_dir = PLUGIN_ROOT / "skills/plan-breakdown"

    assert not skill_dir.exists()
    assert "plan-breakdown" not in implementation
    assert "Task file detection" not in implementation
    assert "task's exact Validation section" not in implementation

def test_commit_handoff_revalidates_changes_after_review() -> None:
    prompt = _read("skills/implement/SKILL.md")

    assert "check the intended changes and required project safeguards" in prompt
    assert (
        "If code changes after testing/review, validate and review the "
        "changed behavior again"
        in prompt
    )


def test_design_inputs_use_relevant_evidence_without_exhaustive_mapping() -> None:
    prompt = _normalized("skills/implement/SKILL.md")

    assert "affected consumers, actual behavior" in prompt
    assert "Identify the project-specific behavior and risks" in prompt
    assert "Do not create requirement IDs, exhaustive mappings" in prompt
