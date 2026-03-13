"""
Tests for validate_frontmatter.py.

Uses unittest (stdlib) so tests run without external dependencies beyond PyYAML.
Compatible with pytest when available.

Test structure mirrors the validation pipeline:
  1. Structural checks
  2. Parse checks
  3. Required field checks
  4. Type-specific required fields
  5. Field type checks
  6. Status value checks
  7. Script-level behavior (exit codes, output format, directory scanning)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Allow importing from scripts directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validate_frontmatter import (
    _resolve_doc_type,
    load_custom_status_values,
    merge_status_values,
    scan_directory,
    validate_file,
)
from frontmatter_schema import STATUS_VALUES

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCRIPT = str(Path(__file__).resolve().parent.parent / "validate_frontmatter.py")


def _make_lore_tree(tmpdir, structure):
    """Build a .lore/ directory tree from a dict.

    structure maps relative paths (e.g. 'specs/auth.md') to file content strings.
    Returns the path to the .lore/ directory.
    """
    lore = Path(tmpdir) / ".lore"
    for relpath, content in structure.items():
        fpath = lore / relpath
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
    return str(lore)


VALID_FM = """\
---
title: "Test doc"
date: 2026-03-10
status: draft
tags: [testing]
---

# Body
"""

VALID_BRAINSTORM_FM = """\
---
title: "Test brainstorm"
date: 2026-03-10
status: open
tags: [testing]
---

# Body
"""

VALID_NOTE_FM = """\
---
title: "Test note"
date: 2026-03-10
status: active
tags: [testing]
source: .lore/specs/example.md
---

# Body
"""

VALID_TASK_FM = """\
---
title: "Test task"
date: 2026-03-10
status: pending
tags: [testing]
source: .lore/plans/example.md
sequence: 1
---

# Body
"""


# -- Unit tests: validate_file ------------------------------------------------

class TestStructuralChecks(unittest.TestCase):
    """REQ-FMVAL-3: structural integrity."""

    def test_missing_opening_delimiter(self):
        fpath = str(FIXTURES / "missing_opening.md")
        findings = validate_file(fpath, str(FIXTURES))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["error_type"], "structural_error")
        self.assertIn("opening", findings[0]["message"])

    def test_missing_closing_delimiter(self):
        fpath = str(FIXTURES / "missing_closing.md")
        findings = validate_file(fpath, str(FIXTURES))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["error_type"], "structural_error")
        self.assertIn("closing", findings[0]["message"])

    def test_tab_in_indentation(self):
        fpath = str(FIXTURES / "tab_indentation.md")
        findings = validate_file(fpath, str(FIXTURES))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["error_type"], "structural_error")
        self.assertIn("Tab", findings[0]["message"])

    def test_structural_error_stops_pipeline(self):
        """Structural errors should prevent parse/field checks."""
        fpath = str(FIXTURES / "missing_closing.md")
        findings = validate_file(fpath, str(FIXTURES))
        error_types = {f["error_type"] for f in findings}
        self.assertEqual(error_types, {"structural_error"})

    def test_empty_file_no_findings(self):
        fpath = str(FIXTURES / "empty_file.md")
        findings = validate_file(fpath, str(FIXTURES))
        self.assertEqual(findings, [])

    def test_no_frontmatter_structural_error(self):
        fpath = str(FIXTURES / "no_frontmatter.md")
        findings = validate_file(fpath, str(FIXTURES))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["error_type"], "structural_error")


class TestParseChecks(unittest.TestCase):
    """REQ-FMVAL-2: parse error detection."""

    def test_unparseable_yaml(self):
        fpath = str(FIXTURES / "bad_yaml.md")
        findings = validate_file(fpath, str(FIXTURES))
        self.assertTrue(len(findings) >= 1)
        self.assertEqual(findings[0]["error_type"], "parse_error")

    def test_parse_error_stops_pipeline(self):
        """Parse errors should prevent field checks."""
        fpath = str(FIXTURES / "bad_yaml.md")
        findings = validate_file(fpath, str(FIXTURES))
        error_types = {f["error_type"] for f in findings}
        self.assertNotIn("missing_field", error_types)


class TestRequiredFields(unittest.TestCase):
    """REQ-FMVAL-4: required fields."""

    def test_missing_title(self):
        fpath = str(FIXTURES / "missing_title.md")
        findings = validate_file(fpath, str(FIXTURES))
        missing = [f for f in findings if f["error_type"] == "missing_field"]
        fields = {f["field"] for f in missing}
        self.assertIn("title", fields)

    def test_missing_date(self):
        fpath = str(FIXTURES / "missing_date.md")
        findings = validate_file(fpath, str(FIXTURES))
        missing = [f for f in findings if f["error_type"] == "missing_field"]
        fields = {f["field"] for f in missing}
        self.assertIn("date", fields)

    def test_missing_status(self):
        fpath = str(FIXTURES / "missing_status.md")
        findings = validate_file(fpath, str(FIXTURES))
        missing = [f for f in findings if f["error_type"] == "missing_field"]
        fields = {f["field"] for f in missing}
        self.assertIn("status", fields)

    def test_missing_tags(self):
        fpath = str(FIXTURES / "missing_tags.md")
        findings = validate_file(fpath, str(FIXTURES))
        missing = [f for f in findings if f["error_type"] == "missing_field"]
        fields = {f["field"] for f in missing}
        self.assertIn("tags", fields)

    def test_valid_file_no_missing_fields(self):
        fpath = str(FIXTURES / "valid_spec.md")
        findings = validate_file(fpath, str(FIXTURES))
        missing = [f for f in findings if f["error_type"] == "missing_field"]
        self.assertEqual(missing, [])


class TestTypeSpecificRequired(unittest.TestCase):
    """Type-specific required fields (notes need source, tasks need source+sequence)."""

    def test_note_missing_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "notes/test.md": (FIXTURES / "note_missing_source.md").read_text()
            })
            findings = scan_directory(lore)
            missing = [f for f in findings if f["error_type"] == "missing_field" and f["field"] == "source"]
            self.assertEqual(len(missing), 1)

    def test_task_missing_sequence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "tasks/test.md": (FIXTURES / "task_missing_sequence.md").read_text()
            })
            findings = scan_directory(lore)
            missing = [f for f in findings if f["error_type"] == "missing_field" and f["field"] == "sequence"]
            self.assertEqual(len(missing), 1)

    def test_valid_note_no_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {"notes/test.md": VALID_NOTE_FM})
            findings = scan_directory(lore)
            self.assertEqual(findings, [])

    def test_valid_task_no_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {"tasks/test.md": VALID_TASK_FM})
            findings = scan_directory(lore)
            self.assertEqual(findings, [])


class TestFieldTypes(unittest.TestCase):
    """REQ-FMVAL-5: field type checking."""

    def test_tags_as_string(self):
        fpath = str(FIXTURES / "tags_as_string.md")
        findings = validate_file(fpath, str(FIXTURES))
        type_errs = [f for f in findings if f["error_type"] == "invalid_type"]
        fields = {f["field"] for f in type_errs}
        self.assertIn("tags", fields)

    def test_bad_date_format(self):
        fpath = str(FIXTURES / "bad_date_format.md")
        findings = validate_file(fpath, str(FIXTURES))
        type_errs = [f for f in findings if f["error_type"] == "invalid_type"]
        fields = {f["field"] for f in type_errs}
        self.assertIn("date", fields)

    def test_valid_date_as_yaml_date(self):
        """PyYAML parses unquoted YYYY-MM-DD as datetime.date; that's valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\ntitle: test\ndate: 2026-03-10\nstatus: draft\ntags: [a]\n---\n"
            lore = _make_lore_tree(tmpdir, {"specs/test.md": content})
            findings = scan_directory(lore)
            self.assertEqual(findings, [])

    def test_valid_date_as_string(self):
        """Quoted YYYY-MM-DD stays a string; that's also valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = '---\ntitle: test\ndate: "2026-03-10"\nstatus: draft\ntags: [a]\n---\n'
            lore = _make_lore_tree(tmpdir, {"specs/test.md": content})
            findings = scan_directory(lore)
            self.assertEqual(findings, [])

    def test_related_must_be_list_of_strings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\ntitle: test\ndate: 2026-03-10\nstatus: draft\ntags: [a]\nrelated:\n  - 123\n---\n"
            lore = _make_lore_tree(tmpdir, {"specs/test.md": content})
            findings = scan_directory(lore)
            type_errs = [f for f in findings if f["error_type"] == "invalid_type" and f["field"] == "related"]
            self.assertEqual(len(type_errs), 1)

    def test_modules_must_be_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = '---\ntitle: test\ndate: 2026-03-10\nstatus: draft\ntags: [a]\nmodules: "not-a-list"\n---\n'
            lore = _make_lore_tree(tmpdir, {"specs/test.md": content})
            findings = scan_directory(lore)
            type_errs = [f for f in findings if f["error_type"] == "invalid_type" and f["field"] == "modules"]
            self.assertEqual(len(type_errs), 1)

    def test_sequence_must_be_integer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = '---\ntitle: test\ndate: 2026-03-10\nstatus: pending\ntags: [a]\nsource: x\nsequence: "one"\n---\n'
            lore = _make_lore_tree(tmpdir, {"tasks/test.md": content})
            findings = scan_directory(lore)
            type_errs = [f for f in findings if f["error_type"] == "invalid_type" and f["field"] == "sequence"]
            self.assertEqual(len(type_errs), 1)


class TestStatusValues(unittest.TestCase):
    """REQ-FMVAL-6: status value validation."""

    def test_invalid_status_for_specs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "specs/test.md": (FIXTURES / "invalid_status.md").read_text()
            })
            findings = scan_directory(lore)
            status_errs = [f for f in findings if f["error_type"] == "invalid_status"]
            self.assertEqual(len(status_errs), 1)
            self.assertIn("wip", status_errs[0]["message"])

    def test_valid_status_for_brainstorm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {"brainstorm/test.md": VALID_BRAINSTORM_FM})
            findings = scan_directory(lore)
            self.assertEqual(findings, [])

    def test_unknown_directory_skips_status_check(self):
        """Files in directories not in schema get no status validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\ntitle: test\ndate: 2026-03-10\nstatus: anything-goes\ntags: [a]\n---\n"
            lore = _make_lore_tree(tmpdir, {"custom-dir/test.md": content})
            findings = scan_directory(lore)
            status_errs = [f for f in findings if f["error_type"] == "invalid_status"]
            self.assertEqual(status_errs, [])

    def test_file_directly_in_lore_skips_status_check(self):
        """Files directly in .lore/ (no subdirectory) skip status validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\ntitle: test\ndate: 2026-03-10\nstatus: whatever\ntags: [a]\n---\n"
            lore = _make_lore_tree(tmpdir, {"test.md": content})
            findings = scan_directory(lore)
            status_errs = [f for f in findings if f["error_type"] == "invalid_status"]
            self.assertEqual(status_errs, [])


# -- Unit tests: helpers -------------------------------------------------------

class TestResolveDocType(unittest.TestCase):
    def test_standard_path(self):
        self.assertEqual(_resolve_doc_type(".lore/specs/auth.md"), "specs")

    def test_nested_path(self):
        self.assertEqual(_resolve_doc_type(".lore/specs/auth/flow.md"), "specs")

    def test_file_directly_in_lore(self):
        self.assertIsNone(_resolve_doc_type(".lore/lore-config.md"))

    def test_no_lore_in_path(self):
        self.assertIsNone(_resolve_doc_type("some/other/path.md"))


# -- Script-level tests --------------------------------------------------------

class TestExitCodes(unittest.TestCase):
    """REQ-FMVAL-10: exit codes."""

    def _run_script(self, *args):
        result = subprocess.run(
            [sys.executable, SCRIPT] + list(args),
            capture_output=True,
            text=True,
        )
        return result

    def test_exit_0_clean_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {"specs/clean.md": VALID_FM})
            result = self._run_script(lore)
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}\nstdout: {result.stdout}")

    def test_exit_1_errors_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\nstatus: draft\ntags: [a]\n---\n"  # missing title, date
            lore = _make_lore_tree(tmpdir, {"specs/bad.md": content})
            result = self._run_script(lore)
            self.assertEqual(result.returncode, 1)

    def test_exit_0_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore_dir = Path(tmpdir) / ".lore"
            lore_dir.mkdir()
            result = self._run_script(str(lore_dir))
            self.assertEqual(result.returncode, 0)

    def test_exit_0_nonexistent_directory(self):
        result = self._run_script("/nonexistent/path/that/does/not/exist")
        self.assertEqual(result.returncode, 0)

    def test_exit_2_pyyaml_missing(self):
        """Mock PyYAML being unavailable via a wrapper script."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a wrapper that makes yaml import fail
            wrapper = Path(tmpdir) / "test_no_yaml.py"
            wrapper.write_text(
                "import sys\n"
                "# Block yaml import\n"
                "import importlib\n"
                "orig_import = __builtins__.__import__\n"
                "def mock_import(name, *args, **kwargs):\n"
                "    if name == 'yaml':\n"
                "        raise ImportError('No module named yaml')\n"
                "    return orig_import(name, *args, **kwargs)\n"
                "__builtins__.__import__ = mock_import\n"
                f"exec(open({SCRIPT!r}).read())\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(wrapper), tmpdir],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("PyYAML", result.stderr)


class TestOutputFormat(unittest.TestCase):
    """REQ-FMVAL-9: JSON lines output."""

    def _run_script(self, *args):
        result = subprocess.run(
            [sys.executable, SCRIPT] + list(args),
            capture_output=True,
            text=True,
        )
        return result

    def test_json_lines_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\nstatus: draft\n---\n"  # missing title, date, tags
            lore = _make_lore_tree(tmpdir, {"specs/bad.md": content})
            result = self._run_script(lore)
            lines = [l for l in result.stdout.strip().split("\n") if l]
            self.assertTrue(len(lines) >= 1, "Expected at least one finding")
            for line in lines:
                obj = json.loads(line)
                self.assertIn("file", obj)
                self.assertIn("error_type", obj)
                self.assertIn("message", obj)

    def test_multiple_errors_produce_multiple_lines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "specs/bad.md": (FIXTURES / "multiple_errors.md").read_text()
            })
            result = self._run_script(lore)
            lines = [l for l in result.stdout.strip().split("\n") if l]
            self.assertTrue(len(lines) >= 3, f"Expected 3+ findings, got {len(lines)}: {lines}")

    def test_clean_directory_no_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {"specs/clean.md": VALID_FM})
            result = self._run_script(lore)
            self.assertEqual(result.stdout.strip(), "")


class TestDirectoryScanning(unittest.TestCase):
    """REQ-FMVAL-1: directory tree scan."""

    def test_nested_subdirectories_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "---\nstatus: draft\n---\n"  # missing title, date, tags
            lore = _make_lore_tree(tmpdir, {
                "specs/auth/flow.md": content,
                "specs/auth/deep/nested.md": content,
            })
            findings = scan_directory(lore)
            files = {f["file"] for f in findings}
            self.assertTrue(
                any("auth/flow.md" in f for f in files),
                f"Expected auth/flow.md in findings, got {files}",
            )
            self.assertTrue(
                any("nested.md" in f for f in files),
                f"Expected nested.md in findings, got {files}",
            )

    def test_non_md_files_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = Path(tmpdir) / ".lore" / "specs"
            lore.mkdir(parents=True)
            (lore / "readme.txt").write_text("not markdown")
            (lore / "data.json").write_text("{}")
            findings = scan_directory(str(Path(tmpdir) / ".lore"))
            self.assertEqual(findings, [])

    def test_empty_directory_no_findings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore_dir = Path(tmpdir) / ".lore"
            lore_dir.mkdir()
            findings = scan_directory(str(lore_dir))
            self.assertEqual(findings, [])

    def test_nonexistent_directory_no_findings(self):
        findings = scan_directory("/nonexistent/does/not/exist")
        self.assertEqual(findings, [])

    def test_valid_files_no_findings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "specs/a.md": VALID_FM,
                "brainstorm/b.md": VALID_BRAINSTORM_FM,
                "notes/c.md": VALID_NOTE_FM,
                "tasks/d.md": VALID_TASK_FM,
            })
            findings = scan_directory(lore)
            self.assertEqual(findings, [], f"Unexpected findings: {findings}")


class TestMultipleErrors(unittest.TestCase):
    """Multiple errors in one file produce multiple findings."""

    def test_multiple_errors_in_one_file(self):
        fpath = str(FIXTURES / "multiple_errors.md")
        findings = validate_file(fpath, str(FIXTURES))
        self.assertTrue(len(findings) >= 3, f"Expected 3+ findings, got {len(findings)}")
        error_types = {f["error_type"] for f in findings}
        self.assertIn("missing_field", error_types)
        self.assertIn("invalid_type", error_types)


# -- Step 3: lore-config.md support (REQ-FMVAL-7) ----------------------------

LORE_CONFIG_WITH_CUSTOM = """\
---
custom_directories:
  commissions: [pending, active, completed, abandoned]
  meetings: [open, closed, deferred]
---

# Project Lore Configuration
"""

LORE_CONFIG_NO_CUSTOM = """\
---
archive_directory: _abandoned
---

# Project Lore Configuration
"""

LORE_CONFIG_UNPARSEABLE = """\
---
custom_directories:
  bad indentation
    - this: won't parse
---
"""

LORE_CONFIG_EMPTY_FM = """\
---
---

# Empty frontmatter
"""


class TestLoadCustomStatusValues(unittest.TestCase):
    """Unit tests for load_custom_status_values."""

    def test_loads_custom_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "lore-config.md").write_text(
                LORE_CONFIG_WITH_CUSTOM, encoding="utf-8"
            )
            result = load_custom_status_values(tmpdir)
            self.assertEqual(result["commissions"], ["pending", "active", "completed", "abandoned"])
            self.assertEqual(result["meetings"], ["open", "closed", "deferred"])

    def test_missing_config_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_custom_status_values(tmpdir)
            self.assertEqual(result, {})

    def test_config_without_custom_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "lore-config.md").write_text(
                LORE_CONFIG_NO_CUSTOM, encoding="utf-8"
            )
            result = load_custom_status_values(tmpdir)
            self.assertEqual(result, {})

    def test_unparseable_config_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "lore-config.md").write_text(
                LORE_CONFIG_UNPARSEABLE, encoding="utf-8"
            )
            result = load_custom_status_values(tmpdir)
            self.assertEqual(result, {})

    def test_empty_frontmatter_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "lore-config.md").write_text(
                LORE_CONFIG_EMPTY_FM, encoding="utf-8"
            )
            result = load_custom_status_values(tmpdir)
            self.assertEqual(result, {})


class TestMergeStatusValues(unittest.TestCase):
    """Unit tests for merge_status_values."""

    def test_custom_adds_new_directories(self):
        custom = {"commissions": ["pending", "active"]}
        merged = merge_status_values(custom)
        self.assertIn("commissions", merged)
        self.assertEqual(merged["commissions"], ["pending", "active"])

    def test_schema_wins_on_conflict(self):
        """If a directory exists in both schema and config, schema values are used."""
        schema_specs = STATUS_VALUES["specs"]
        custom = {"specs": ["totally", "different"]}
        merged = merge_status_values(custom)
        self.assertEqual(merged["specs"], schema_specs)

    def test_schema_values_preserved(self):
        custom = {"commissions": ["pending"]}
        merged = merge_status_values(custom)
        for key, values in STATUS_VALUES.items():
            self.assertEqual(merged[key], values)

    def test_empty_custom_returns_schema(self):
        merged = merge_status_values({})
        self.assertEqual(merged, STATUS_VALUES)


class TestConfigIntegration(unittest.TestCase):
    """Integration tests: config + validation pipeline."""

    def test_custom_directory_valid_status(self):
        """Files in custom directories are validated against custom status values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "lore-config.md": LORE_CONFIG_WITH_CUSTOM,
                "commissions/task.md": (
                    "---\n"
                    "title: Test commission\n"
                    "date: 2026-03-10\n"
                    "status: active\n"
                    "tags: [test]\n"
                    "---\n"
                ),
            })
            findings = scan_directory(lore)
            self.assertEqual(findings, [], f"Unexpected findings: {findings}")

    def test_custom_directory_invalid_status(self):
        """Invalid status for a custom directory is flagged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "lore-config.md": LORE_CONFIG_WITH_CUSTOM,
                "commissions/task.md": (
                    "---\n"
                    "title: Test commission\n"
                    "date: 2026-03-10\n"
                    "status: bogus\n"
                    "tags: [test]\n"
                    "---\n"
                ),
            })
            findings = scan_directory(lore)
            status_errs = [f for f in findings if f["error_type"] == "invalid_status"]
            self.assertEqual(len(status_errs), 1)
            self.assertIn("bogus", status_errs[0]["message"])

    def test_standard_directories_use_schema(self):
        """Standard directories use schema values even when config exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "lore-config.md": LORE_CONFIG_WITH_CUSTOM,
                "specs/doc.md": (
                    "---\n"
                    "title: Test spec\n"
                    "date: 2026-03-10\n"
                    "status: draft\n"
                    "tags: [test]\n"
                    "---\n"
                ),
            })
            findings = scan_directory(lore)
            self.assertEqual(findings, [], f"Unexpected findings: {findings}")

    def test_unknown_directory_skips_status_validation(self):
        """Files in dirs not in schema or config skip status validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "lore-config.md": LORE_CONFIG_WITH_CUSTOM,
                "random-dir/doc.md": (
                    "---\n"
                    "title: Unknown dir doc\n"
                    "date: 2026-03-10\n"
                    "status: literally-anything\n"
                    "tags: [test]\n"
                    "---\n"
                ),
            })
            findings = scan_directory(lore)
            status_errs = [f for f in findings if f["error_type"] == "invalid_status"]
            self.assertEqual(status_errs, [])

    def test_missing_config_falls_back_to_schema(self):
        """Without config, schema-only validation still works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "specs/doc.md": (
                    "---\n"
                    "title: Test spec\n"
                    "date: 2026-03-10\n"
                    "status: draft\n"
                    "tags: [test]\n"
                    "---\n"
                ),
            })
            findings = scan_directory(lore)
            self.assertEqual(findings, [])

    def test_config_without_custom_directories_field(self):
        """Config that lacks custom_directories is handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lore = _make_lore_tree(tmpdir, {
                "lore-config.md": LORE_CONFIG_NO_CUSTOM,
                "specs/doc.md": (
                    "---\n"
                    "title: Test spec\n"
                    "date: 2026-03-10\n"
                    "status: draft\n"
                    "tags: [test]\n"
                    "---\n"
                ),
            })
            findings = scan_directory(lore)
            self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
