---
title: "Frontmatter validation script for tend status mode"
date: 2026-03-09
status: implemented
tags: [tend, yaml, validation, frontmatter, scripts]
modules: [lore-development, tend-skill]
req-prefix: FMVAL
related:
  - .lore/work/brainstorm/lore-development/yaml-frontmatter-validation.md
  - .lore/work/brainstorm/tend-discovery-modes.md
---

# Spec: Frontmatter Validation Script for Tend

## Overview

A bundled Python script that validates YAML frontmatter across `.lore/` documents, checking both parseability and schema conformance. Tend's status mode invokes this script before its existing checks. Claude proposes fixes for what the script identifies as broken; Claude does not perform detection.

The core principle: detection is deterministic work. A field is either a valid status value or it isn't. A date either matches YYYY-MM-DD or it doesn't. YAML either parses or it doesn't. Deterministic work belongs in a script, not an LLM.

## Entry Points

- `/tend` or `/tend status` (existing) triggers the script as a pre-check before status verification
- Direct invocation via Bash for debugging or CI use: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_frontmatter.py .lore/`

## Requirements

### Detection (Python script)

- REQ-FMVAL-1: The script scans a directory tree and validates every `.md` file's YAML frontmatter in a single invocation
- REQ-FMVAL-2: The script checks parseability: does the frontmatter block parse as valid YAML? Reports parse errors with file path and error description
- REQ-FMVAL-3: The script checks structural integrity: opening `---`, closing `---`, no tab characters in indentation
- REQ-FMVAL-4: The script checks required fields: every document must have `title`, `date`, `status`, `tags` per the frontmatter schema
- REQ-FMVAL-5: The script checks field types: `tags` and `modules` are arrays, `date` matches YYYY-MM-DD, `status` is a string, `related` is an array of strings
- REQ-FMVAL-6: The script checks status values against valid values for each document type, determined by which `.lore/` subdirectory the file lives in (e.g., `brainstorm/` allows `open`, `resolved`, `parked`). Status mode also supports "honest status" phrases (e.g., `partially complete`, `blocked`). The script flags values not in the schema's valid list; Claude may override during repair if the value is an intentional honest-status phrase.
- REQ-FMVAL-7: The script respects `lore-config.md` custom directories and their status values when the config file exists
- REQ-FMVAL-8: The script handles missing PyYAML gracefully: if `import yaml` fails, it prints a clear message telling the user to install it (`pip install pyyaml`) and exits with a distinct error code
- REQ-FMVAL-9: The script outputs JSON lines (one JSON object per finding) so tend can consume the output programmatically. Each finding includes file path, error type (`parse_error`, `missing_field`, `invalid_type`, `invalid_status`), and error message. JSON avoids ambiguity when error messages contain colons or special characters.
- REQ-FMVAL-10-A: The script exits 0 when no errors are found, 1 when errors are found, and 2 when PyYAML is unavailable
- REQ-FMVAL-10-B: The script scans cleanly (exit 0) when the target directory is empty or does not exist

### Integration (tend status mode)

- REQ-FMVAL-11: Status mode invokes the script via Bash before its existing three-pass verification (missing fields, stale status, verification)
- REQ-FMVAL-12: Script findings appear in the status report under two new categories: "Malformed Frontmatter" (parse failures) and "Invalid Frontmatter" (schema violations), slotting between existing "Missing Frontmatter" and "Missing Status"
- REQ-FMVAL-13: Documents with parse failures are excluded from subsequent status mode passes (can't verify field values if the YAML doesn't parse)

### Repair (Claude, post-detection)

- REQ-FMVAL-14: For files the script flags, Claude reads only those specific files and proposes fixes. For parse failures, Claude examines the raw frontmatter text and proposes corrected YAML. For schema violations, Claude proposes the correct field value from the schema.
- REQ-FMVAL-15: Fixes follow tend's existing confirmation pattern: present proposed changes, wait for user approval, then apply

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Clean scan | No validation errors found | Continue to existing status mode passes |
| Errors found | Script reports failures | Include findings in status report, run three-pass verification on passing files only, present full report, then offer repairs |
| PyYAML missing | `import yaml` fails | Inform user, skip validation, continue without it |

## Success Criteria

- [ ] Script catches all Tier 1 and Tier 2 errors that cause PyYAML to reject the frontmatter (missing delimiters, tabs in indentation, broken array syntax, bad indentation). Fragile-but-parseable patterns (unquoted colons that happen to work, boolean coercion) are out of scope per Constraints.
- [ ] Script validates required fields and field types per frontmatter schema
- [ ] Script validates status values per document type
- [ ] Single Bash invocation processes entire `.lore/` directory
- [ ] Script is independently runnable outside of tend (for CI or manual use)
- [ ] Error messages include file path and specific error description
- [ ] Tend status report integrates script findings without duplicating existing categories

## AI Validation

**Defaults** (apply unless overridden):
- Unit tests with mocked filesystem (no real `.lore/` directory needed)
- 90%+ coverage on the script
- Code review by fresh-context sub-agent

**Custom:**
- Test fixtures with known-good and known-bad frontmatter covering each error type in the taxonomy
- Script exit codes are tested (0 = clean, 1 = errors found, 2 = PyYAML missing)
- Integration test: when the script reports a parse failure, the status report includes the file under "Malformed Frontmatter" and that file is absent from subsequent pass results. Minimum scenarios: clean scan, errors found, PyYAML missing

## Constraints

- The script is bundled at `lore-development/scripts/validate_frontmatter.py` and invoked via `${CLAUDE_PLUGIN_ROOT}/scripts/validate_frontmatter.py`
- The script depends on PyYAML (third-party, not standard library) and handles its absence per REQ-FMVAL-8
- The frontmatter schema source of truth is `shared/frontmatter-schema.md`. The script needs a machine-readable representation of that schema (how it gets one is a plan concern, not a spec concern)
- If the frontmatter parses and conforms to schema, it is valid. No "fragile pattern" warnings for parseable-but-unusual YAML. The parser is the authority.

## Context

This spec was preceded by a brainstorm (`.lore/work/brainstorm/lore-development/yaml-frontmatter-validation.md`) that explored error taxonomy, placement options, tooling approaches, auto-fix safety, and strictness tiers.

Key decisions from the brainstorm and subsequent audience review:
- **Placement**: Extend status mode (Option B), not a new mode
- **Tooling**: Python script for detection, Claude for fixes only. Counter-arguments against Claude-as-reviewer: token cost, circular review (Claude grading its own output), and right-tool-for-each-job
- **Schema validation in script**: Same arguments that apply to parse checking apply to schema checking. Both are deterministic.
- **Fragile patterns out of scope**: If PyYAML accepts it, it's valid. No heuristic warnings.
