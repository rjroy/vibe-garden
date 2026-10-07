"""Regression checks for field-guide's authoring and Claude Code contracts."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class FieldGuideContracts(unittest.TestCase):
    def test_all_seven_skills_keep_claude_skill_frontmatter(self):
        expected = {
            "init", "ingest", "update-evidence", "resolve-drift",
            "query", "stratify", "lint",
        }
        found = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        self.assertEqual(expected, found)
        for name in expected:
            content = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(content, rf"(?s)^---\nname: {re.escape(name)}\n.*?\n---\n")
            self.assertNotRegex(content, r"(?i)opencode|open-code")

    def test_ingest_is_selective_nonbinding_and_excludes_execution_artifacts(self):
        ingest = text("skills/ingest/SKILL.md")
        for phrase in (
            "No useful candidate is a valid result",
            "Plans, notes, and tasks",
            "not proof of current behavior",
            "current direction prevails",
            "records provenance only",
            "Merge it into the best-fitting page",
        ):
            self.assertIn(phrase, ingest)

    def test_evidence_is_optional_and_separate_from_provenance(self):
        evidence = text("skills/update-evidence/SKILL.md")
        self.assertIn("Do not require `fg-sources` files to exist", evidence)
        self.assertIn("leave it without a fabricated anchor", evidence)
        self.assertIn('name="fg-evidence-code"', evidence)
        self.assertIn("fg-evidence:", evidence)

    def test_claude_cron_fallback_does_not_replace_tool_names(self):
        init = text("skills/init/SKILL.md")
        for tool in ("CronCreate", "CronList"):
            self.assertIn(tool, init)
        self.assertIn("skip all scheduling operations", init)
        self.assertIn("do not substitute another harness's tools", init)
        call_spec = init.split("If no active job was found, call CronCreate", 1)[1].split("**5.", 1)[0]
        self.assertIn("`cron`:", call_spec)
        self.assertNotIn("`schedule`:", call_spec)
        self.assertIn("only if the exposed schema supports this argument", call_spec)
        self.assertIn("whether the CronCreate response confirms durable persistence", init)
        self.assertIn("Report persistence and expiration separately", init)
        self.assertIn("survives restarts, but recurring CronCreate jobs still expire after 7 days", init)
        self.assertIn("regardless of the persistence result", init)
        self.assertIn("CronCreate", text("README.md"))

    def test_index_and_page_metadata_contracts_cover_both_formats(self):
        readme = text("README.md")
        stratify = text("skills/stratify/SKILL.md")
        ingest = text("skills/ingest/SKILL.md")
        self.assertIn("index.md or index.html", readme)
        self.assertIn("fg-type", readme)
        self.assertIn("fg-sources", readme)
        self.assertIn("fg-evidence", readme)
        self.assertIn("index coverage", stratify.lower())
        self.assertIn("both `.md` and `.html`", ingest)
        self.assertIn("index links", stratify)
        manifest = (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        self.assertIn("searchable wiki", manifest)
        self.assertNotIn("HTML wiki", manifest)


if __name__ == "__main__":
    unittest.main()
