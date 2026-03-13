---
title: Implementation plan for frontmatter validation
date: 2026-03-10
status: executed
tags: [tend, yaml, validation, frontmatter, scripts, python]
modules: [lore-development, tend-skill]
related:
  - .lore/specs/frontmatter-validation.md
  - .lore/brainstorm/lore-development/yaml-frontmatter-validation.md
---

# Plan: Frontmatter Validation Script for Tend

## Spec Reference

**Spec**: `.lore/specs/frontmatter-validation.md`

Requirements addressed:

| Requirement | Step |
|-------------|------|
| REQ-FMVAL-1: Directory tree scan | Step 2 |
| REQ-FMVAL-2: Parse error detection | Step 2 |
| REQ-FMVAL-3: Structural integrity | Step 2 |
| REQ-FMVAL-4: Required fields | Step 2 |
| REQ-FMVAL-5: Field type checking | Step 2 |
| REQ-FMVAL-6: Status value validation | Step 2 |
| REQ-FMVAL-7: lore-config.md support | Step 3 |
| REQ-FMVAL-8: PyYAML graceful fallback | Step 2 |
| REQ-FMVAL-9: JSON lines output | Step 2 |
| REQ-FMVAL-10-A/B: Exit codes | Step 2 |
| REQ-FMVAL-11: Status mode invocation | Step 4 |
| REQ-FMVAL-12: New report categories | Step 4 |
| REQ-FMVAL-13: Parse failure exclusion | Step 4 |
| REQ-FMVAL-14: Claude-driven repair | Step 4 |
| REQ-FMVAL-15: Confirmation pattern | Step 4 |

## Key Design Decision: Schema Representation

The spec states: "The frontmatter schema source of truth is `shared/frontmatter-schema.md`. The script needs a machine-readable representation of that schema (how it gets one is a plan concern, not a spec concern)."

The plan uses a Python module (`frontmatter_schema.py`) co-located with the script. A Python dict is simpler to consume than JSON (no file-path resolution, no I/O at import time) and can include comments explaining the mapping back to the schema document.

The schema module is a separate step because it's independently testable and its correctness is load-bearing for all subsequent validation.

## Steps

### Step 1: Schema data module

**What gets built**: A Python module that encodes the frontmatter schema as importable data structures.

**Files created**:
- `lore-development/scripts/frontmatter_schema.py`
- `lore-development/scripts/tests/test_frontmatter_schema.py`

**Dependencies**: None.

**Details**:

The module exports:

- `REQUIRED_FIELDS`: list of field names required on all documents (`title`, `date`, `status`, `tags`)
- `OPTIONAL_FIELDS`: list of common optional fields (`modules`, `related`)
- `FIELD_TYPES`: dict mapping field name to expected type (e.g., `{"tags": "list", "date": "date", "status": "string", "modules": "list", "related": "list"}`)
- `STATUS_VALUES`: dict mapping directory name to list of valid status strings (e.g., `{"brainstorm": ["open", "resolved", "parked"], "specs": ["draft", "approved", "implemented", "superseded"], ...}`)
- `TYPE_SPECIFIC_REQUIRED`: dict mapping directory name to additional required fields (e.g., `{"notes": ["source"], "tasks": ["source", "sequence"]}`)

Source of truth: `lore-development/shared/frontmatter-schema.md`. Each constant should have a comment referencing the schema section it encodes.

**What gets tested**:
- Every document type in the schema has a `STATUS_VALUES` entry
- `REQUIRED_FIELDS` matches the schema's "Required vs Optional" table
- `FIELD_TYPES` covers all required and optional fields
- `TYPE_SPECIFIC_REQUIRED` covers notes and tasks
- No empty status value lists

---

### Step 2: Core validation script

**What gets built**: The `validate_frontmatter.py` script covering REQ-FMVAL-1 through REQ-FMVAL-6, REQ-FMVAL-8 through REQ-FMVAL-10.

**Files created**:
- `lore-development/scripts/validate_frontmatter.py`
- `lore-development/scripts/tests/test_validate_frontmatter.py`
- `lore-development/scripts/tests/fixtures/` (directory of test fixture `.md` files)

**Dependencies**: Step 1 (imports `frontmatter_schema`).

**Details**:

The script accepts a single positional argument: the directory path to scan. It walks the directory tree, finds `.md` files, and validates each file's YAML frontmatter.

Validation pipeline per file (in order):
1. **Structural check** (REQ-FMVAL-3): Verify opening `---`, closing `---`, no tab characters in frontmatter indentation. If structural check fails, report and skip to next file.
2. **Parse check** (REQ-FMVAL-2): Attempt `yaml.safe_load()` on the frontmatter block. If parse fails, report `parse_error` and skip to next file.
3. **Required fields** (REQ-FMVAL-4): Check for `title`, `date`, `status`, `tags`. Report `missing_field` for each absent field.
4. **Type-specific required fields**: Check for additional required fields based on directory (e.g., `source` for notes). Report `missing_field`.
5. **Field types** (REQ-FMVAL-5): Validate `tags` is a list, `date` matches `YYYY-MM-DD`, `status` is a string, `modules` is a list (if present), `related` is a list of strings (if present). Report `invalid_type`.
6. **Status values** (REQ-FMVAL-6): Determine document type from the `.lore/` subdirectory path. Look up valid values from schema. Report `invalid_status` if the value isn't in the valid list.

Output format (REQ-FMVAL-9): One JSON object per finding, printed to stdout, one per line. Fields: `file` (relative path), `error_type` (one of `parse_error`, `structural_error`, `missing_field`, `invalid_type`, `invalid_status`), `message` (human-readable description), and `field` (the field name, when applicable).

Example output line:
```json
{"file": ".lore/specs/auth.md", "error_type": "missing_field", "field": "tags", "message": "Required field 'tags' is missing"}
```

Exit codes (REQ-FMVAL-10):
- `0`: No errors found, or target directory is empty/nonexistent
- `1`: One or more validation errors found
- `2`: PyYAML not available

PyYAML handling (REQ-FMVAL-8): The script attempts `import yaml` inside a try/except at the top. If it fails, print a clear message to stderr (`"PyYAML is required but not installed. Install it with: pip install pyyaml"`) and exit with code 2.

Directory type resolution: The script determines document type by finding the first path segment after `.lore/` in the file path. For example, `.lore/specs/auth/flow.md` maps to `specs`. Files directly in `.lore/` (not in a subdirectory) get no type-specific validation (status value check is skipped, only structural/parse/required field checks apply).

**What gets tested**:

Test fixtures (known-good and known-bad `.md` files):
- Clean file with valid frontmatter (each document type)
- Missing opening delimiter
- Missing closing delimiter
- Tab in frontmatter indentation
- Unparseable YAML (e.g., bad indentation after valid delimiters)
- Missing each required field individually
- `tags` as a string instead of list
- `date` in wrong format (e.g., `Jan 5 2026`)
- Invalid status value for a given directory type
- File with no frontmatter at all
- Empty file
- Type-specific: notes missing `source`, tasks missing `sequence`

Script-level tests:
- Exit code 0 on clean directory
- Exit code 1 on directory with errors
- Exit code 0 on empty directory
- Exit code 0 on nonexistent directory
- Exit code 2 when PyYAML is unavailable (mock `import yaml` failure)
- JSON lines output is valid JSON per line
- Multiple errors in one file produce multiple output lines
- Files in nested subdirectories are found

Coverage target: 90%+.

---

### Step 3: lore-config.md support

**What gets built**: Extension to the validation script that reads `.lore/lore-config.md` and merges custom directory types and status values with the schema defaults (REQ-FMVAL-7).

**Files modified**:
- `lore-development/scripts/validate_frontmatter.py`
- `lore-development/scripts/tests/test_validate_frontmatter.py`

**Dependencies**: Step 2.

**Details**:

Before scanning, the script checks for a `lore-config.md` file in the target directory (the scanned directory itself, since it's expected to be `.lore/`). If found, it parses the file's YAML frontmatter and extracts `custom_directories`.

Merge behavior:
- `custom_directories` entries are added to the schema's `STATUS_VALUES` for status validation. Custom entries do not override schema defaults; if a directory appears in both, the schema wins (custom directories are for directories the schema doesn't cover).
- Files in directories that appear in neither the schema nor the config get no status validation (status value check is skipped, other checks still apply).

The script does not need to read `filename_exemptions`, `archive_directory`, or `custom_fields` from the config. Those are concerns for other tend modes.

**What gets tested**:
- Config file with `custom_directories` adds valid status values for those directories
- Files in custom directories are validated against custom status values
- Files in standard directories still use schema status values (config doesn't override)
- Files in directories not in schema or config skip status validation
- Missing or unparseable config file is silently ignored (fall back to schema only)
- Config file without `custom_directories` field is handled gracefully

---

### Step 4: Tend status mode integration and repair

**What gets built**: Updates to the status mode reference file that integrate the validation script as a pre-check and add Claude-driven repair for script-identified issues (REQ-FMVAL-11 through REQ-FMVAL-15).

**Files modified**:
- `lore-development/skills/tend/references/status.md`

**Dependencies**: Steps 2 and 3 (the script must exist and be tested before the skill references it).

**Details**:

**Script invocation (REQ-FMVAL-11)**:

Add a new section near the top of status.md, before the existing "Verification Approach" section. The script runs as the first action in status mode:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_frontmatter.py .lore/
```

Capture stdout (JSON lines) and the exit code. Parse each JSON line into a structured finding.

Exit code handling:
- `0`: No validation errors. Proceed to existing three-pass verification.
- `1`: Errors found. Parse findings, include in report, proceed with three-pass verification on passing files only.
- `2`: PyYAML missing. Log a note in the status report ("Frontmatter validation skipped: PyYAML not installed"). Proceed to existing three-pass verification without the pre-check.

**New report categories (REQ-FMVAL-12)**:

Add two categories to the status report output format, positioned between existing "Missing Frontmatter" and "Missing Status":

```markdown
### Malformed Frontmatter
- `.lore/specs/broken.md` - YAML parse error: mapping values are not allowed here (line 3)
- `.lore/retros/old.md` - structural: missing closing delimiter

### Invalid Frontmatter
- `.lore/specs/auth.md` - missing required field: tags
- `.lore/plans/migration.md` - invalid status "wip" (valid: draft, approved, executed)
- `.lore/brainstorm/ideas.md` - field type: tags should be a list, got string
```

Mapping from script error types to categories:
- `parse_error`, `structural_error` go to "Malformed Frontmatter"
- `missing_field`, `invalid_type`, `invalid_status` go to "Invalid Frontmatter"

**Parse failure exclusion (REQ-FMVAL-13)**:

Files that appear in "Malformed Frontmatter" (parse errors and structural errors) are excluded from the subsequent three-pass verification. They can't be meaningfully checked for missing fields or stale status if the YAML doesn't parse. Mention this exclusion in the report: "N files excluded from status verification due to malformed frontmatter."

**Repair flow (REQ-FMVAL-14, REQ-FMVAL-15)**:

After presenting the full status report (including the two new categories), offer repair for files flagged by the script. The repair section follows tend's existing dry-run, confirm, apply pattern:

1. For each file in "Malformed Frontmatter": Read the raw frontmatter text, propose corrected YAML.
2. For each file in "Invalid Frontmatter": Propose the correct field value from the schema. For `invalid_status`, note that the value might be an intentional honest-status phrase (per REQ-FMVAL-6). Present the finding but let the user decide whether to change it.
3. Present all proposed fixes together.
4. Wait for user confirmation (accept all, accept some, reject).
5. Apply confirmed fixes.

Honest-status handling: The script flags any status value not in the schema's valid list. Claude should note when a flagged value looks like an honest-status phrase (e.g., "partially complete", "blocked") and present it as "flagged by script, may be intentional" rather than a definitive error. The user decides.

**What gets tested**:

This step modifies a skill reference file (markdown instructions for Claude), not executable code. Testing is covered by:

- **Integration test scenarios** (documented in the test file from Step 2): Run the script against a fixture directory, verify the JSON lines output, then manually verify the report categories are correctly populated. Minimum scenarios per the spec's AI Validation section:
  1. Clean scan: script exits 0, no new categories appear in report
  2. Errors found: script exits 1, findings populate Malformed/Invalid categories, parse-failed files are excluded from subsequent passes
  3. PyYAML missing: script exits 2, report notes validation was skipped, existing passes run normally

- **Spec compliance check**: The modified status.md should be reviewed against REQ-FMVAL-11 through REQ-FMVAL-15 by a fresh-context sub-agent.

## File Summary

| File | Action | Steps |
|------|--------|-------|
| `lore-development/scripts/frontmatter_schema.py` | Create | 1 |
| `lore-development/scripts/tests/test_frontmatter_schema.py` | Create | 1 |
| `lore-development/scripts/validate_frontmatter.py` | Create | 2, 3 |
| `lore-development/scripts/tests/test_validate_frontmatter.py` | Create | 2, 3 |
| `lore-development/scripts/tests/fixtures/` | Create | 2 |
| `lore-development/skills/tend/references/status.md` | Modify | 4 |

## Dependency Graph

```
Step 1 (schema module)
  └─→ Step 2 (core script)
        └─→ Step 3 (lore-config support)
              └─→ Step 4 (tend integration + repair)
```

All steps are sequential. Each depends on the prior step being complete and tested.

## Notes for Commission Decomposition

Each step is a single commission for Dalton. Context each commission needs:

- **Step 1**: Read `lore-development/shared/frontmatter-schema.md`. That's the only input.
- **Step 2**: Read the spec (`.lore/specs/frontmatter-validation.md`) for requirements and the schema module from Step 1. Also read `lore-development/scripts/idea_hook.py` for the existing script pattern in this codebase.
- **Step 3**: Read the spec for REQ-FMVAL-7 and `lore-development/skills/tend/references/lore-config.md` for the config format. Extend the script from Step 2.
- **Step 4**: Read the spec for REQ-FMVAL-11 through REQ-FMVAL-15, the current `status.md`, and the SKILL.md orchestrator. The existing report format and confirmation pattern in `status.md` are the integration targets.
