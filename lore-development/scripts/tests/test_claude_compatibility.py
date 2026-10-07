"""Keep plugin metadata and delegation guidance native to Claude Code."""

import json
import re
from pathlib import Path

import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def test_plugin_manifest_remains_claude_plugin_metadata() -> None:
    manifest = json.loads(
        (PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["name"] == "lore-development"
    assert manifest["description"]
    assert "specifications" not in manifest["description"]


def test_agents_use_claude_code_frontmatter_and_read_only_tools() -> None:
    for path in sorted((PLUGIN_ROOT / "agents").glob("*.md")):
        _opening, raw_frontmatter, _body = path.read_text(encoding="utf-8").split(
            "---", maxsplit=2
        )
        frontmatter = yaml.safe_load(raw_frontmatter)
        assert frontmatter["name"] == path.stem
        assert frontmatter["description"]
        assert set(frontmatter["tools"].split(", ")) == {"Read", "Grep", "Glob"}
        assert not ({"mode", "permission"} & frontmatter.keys())
        assert "openai/" not in raw_frontmatter


def test_skills_use_qualified_agents_with_claude_tool_fallbacks() -> None:
    prompts = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")
    )
    assert "Claude Code's current `Agent` tool" in prompts
    assert "versions without `Agent`" in prompts
    assert "`Task`" in prompts
    assert "subagent_type" in prompts
    assert "${CLAUDE_PLUGIN_ROOT}" in prompts
    assert not re.search(r"\b(opencode|OpenCode|Task\(\))\b", prompts)
    assert "host's subagent capability" not in prompts
    for agent in (
        "lore-researcher",
        "design-reviewer",
        "plan-reviewer",
        "bun-typescript-reviewer",
    ):
        assert f"lore-development:{agent}" in prompts
        assert not re.search(rf'subagent_type: "{agent}"', prompts)
    assert "No exceptions." not in prompts


def test_retired_specification_workflow_is_not_registered() -> None:
    assert not (PLUGIN_ROOT / "skills/specify").exists()
    assert not (PLUGIN_ROOT / "skills/plan-breakdown").exists()
    assert not (PLUGIN_ROOT / "agents/spec-reviewer.md").exists()
    readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    skill_section = readme.split("## Skills", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    listed = set(re.findall(r"`/lore-development:([^`]+)`", skill_section))
    available = {
        path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")
    }
    assert listed == available


def test_migration_requires_confirmation_and_preserves_unmapped_content() -> None:
    prompt = (PLUGIN_ROOT / "skills/migrate/SKILL.md").read_text(encoding="utf-8")
    assert "no-write preview" in prompt
    assert "Only after the user confirms" in prompt
    assert "Unmapped root directories/files are reported and left untouched" in prompt
    assert "Destination and backup collisions block the entire migration" in prompt


def test_readme_does_not_claim_nonexistent_idea_capture_hook() -> None:
    readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    assert "includes a hook that captures ideas" not in readme
    assert "Start any prompt with `idea:`" not in readme
    assert "via hook" not in readme


def test_current_lore_model_is_historical_and_has_four_zones() -> None:
    readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    schema = (PLUGIN_ROOT / "shared/frontmatter-schema.md").read_text(encoding="utf-8")
    assert "four zones" in readme
    assert "historical context, not binding instructions" in readme
    assert "current direction" in readme
    assert "`.lore/local/`" in schema
    assert "`.lore/work/`" in schema
    assert "`.lore/reference/`" in schema
    assert "`.lore/learned/`" in schema
    assert "do not make them authoritative" in schema
