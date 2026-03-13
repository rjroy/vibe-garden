#!/usr/bin/env python3
"""
Validate YAML frontmatter across .lore/ documents.

Scans a directory tree, finds .md files, and validates each file's YAML
frontmatter against the lore schema. Outputs JSON lines to stdout (one
finding per line). Designed for consumption by tend's status mode and
for standalone CLI use.

Exit codes:
  0 - No errors found (or target directory is empty/nonexistent)
  1 - One or more validation errors found
  2 - PyYAML not available
"""

import datetime
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    print(
        "PyYAML is required but not installed. Install it with: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

from pathlib import Path

# Allow importing schema module from same directory as this script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from frontmatter_schema import (
    FIELD_TYPES,
    REQUIRED_FIELDS,
    STATUS_VALUES,
    TYPE_SPECIFIC_REQUIRED,
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# -- config loading (REQ-FMVAL-7) --------------------------------------------

def _parse_frontmatter_data(filepath):
    """Parse YAML frontmatter from a file and return the data dict.

    Returns None if the file is missing, unreadable, has no valid frontmatter,
    or the YAML is unparseable. Failures are silently ignored per spec.
    """
    try:
        content = Path(filepath).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    lines = content.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return None

    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r") == "---":
            close_idx = i
            break
    if close_idx is None:
        return None

    fm_text = "\n".join(lines[1:close_idx])
    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None

    if not isinstance(data, dict):
        return None
    return data


def load_custom_status_values(directory):
    """Read lore-config.md from directory and return custom status values.

    Returns a dict mapping directory name to list of valid status strings
    extracted from the config's custom_directories field. Returns an empty
    dict if the config is missing, unparseable, or lacks custom_directories.
    """
    config_path = Path(directory) / "lore-config.md"
    data = _parse_frontmatter_data(str(config_path))
    if data is None:
        return {}

    custom_dirs = data.get("custom_directories")
    if not isinstance(custom_dirs, dict):
        return {}

    result = {}
    for dirname, statuses in custom_dirs.items():
        if isinstance(statuses, list) and all(isinstance(s, str) for s in statuses):
            result[str(dirname)] = statuses
    return result


def merge_status_values(custom_values):
    """Merge custom status values with schema defaults.

    Schema defaults take precedence: if a directory appears in both the schema
    and the config, the schema values are used. Custom entries only add
    directories the schema doesn't cover.
    """
    merged = dict(STATUS_VALUES)
    for dirname, statuses in custom_values.items():
        if dirname not in merged:
            merged[dirname] = statuses
    return merged


# -- helpers ------------------------------------------------------------------

def _relative_path(filepath, root):
    """Return filepath relative to root, or as-is if it can't be made relative."""
    try:
        return str(Path(filepath).relative_to(root))
    except ValueError:
        return str(filepath)


def _finding(filepath, error_type, message, field=None):
    """Build a single finding dict."""
    obj = {
        "file": filepath,
        "error_type": error_type,
        "message": message,
    }
    if field is not None:
        obj["field"] = field
    return obj


def _resolve_doc_type(filepath, root=None):
    """Determine document type from the .lore/ subdirectory path.

    Returns the first path segment after '.lore/' (e.g. 'specs' for
    '.lore/specs/auth.md'), or None if the file is directly inside .lore/.

    When root is provided and its basename is a known .lore directory pattern
    (e.g. the scan root IS .lore/), the first segment of the relative path
    is used as the doc type.
    """
    parts = Path(filepath).parts

    # Try finding .lore in the path directly
    try:
        lore_idx = parts.index(".lore")
        remaining = parts[lore_idx + 1 :]
        if len(remaining) >= 2:
            return remaining[0]
        return None
    except ValueError:
        pass

    # If root is provided and ends with .lore (or similar), the relative path's
    # first segment is the doc type.
    if root is not None:
        root_path = Path(root).resolve()
        file_path = Path(filepath).resolve()
        try:
            rel = file_path.relative_to(root_path)
        except ValueError:
            return None
        # Check if any ancestor of root is .lore, or root itself ends with .lore
        root_parts = root_path.parts
        if ".lore" in root_parts:
            # root is inside .lore; all of rel's segments are below .lore
            rel_parts = rel.parts
            if len(rel_parts) >= 2:
                return rel_parts[0]
            return None
    return None


# -- validation pipeline ------------------------------------------------------

def validate_file(filepath, root, status_values=None):
    """Run the full validation pipeline on a single file.

    status_values overrides the schema's STATUS_VALUES when provided (used
    after merging lore-config.md custom directories with schema defaults).

    Returns a list of finding dicts.
    """
    if status_values is None:
        status_values = STATUS_VALUES
    rel = _relative_path(filepath, root)
    findings = []

    try:
        content = Path(filepath).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        findings.append(_finding(rel, "structural_error", f"Cannot read file: {exc}"))
        return findings

    # Empty files and files without frontmatter: no findings.
    if not content.strip():
        return findings

    # Step 1: Structural check
    lines = content.split("\n")

    if not lines or lines[0].rstrip("\r") != "---":
        findings.append(
            _finding(rel, "structural_error", "Missing opening '---' delimiter")
        )
        return findings

    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r") == "---":
            close_idx = i
            break

    if close_idx is None:
        findings.append(
            _finding(rel, "structural_error", "Missing closing '---' delimiter")
        )
        return findings

    fm_lines = lines[1:close_idx]
    fm_text = "\n".join(fm_lines)

    # Tab check
    for line_num, line in enumerate(fm_lines, start=2):
        if "\t" in line:
            findings.append(
                _finding(
                    rel,
                    "structural_error",
                    f"Tab character in frontmatter indentation (line {line_num})",
                )
            )
            return findings

    # Step 2: Parse check
    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        findings.append(
            _finding(rel, "parse_error", f"YAML parse error: {exc}")
        )
        return findings

    # safe_load can return None for empty frontmatter or a non-dict for scalar
    if data is None:
        data = {}
    if not isinstance(data, dict):
        findings.append(
            _finding(rel, "parse_error", "Frontmatter is not a YAML mapping")
        )
        return findings

    # Step 3: Required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            findings.append(
                _finding(rel, "missing_field", f"Required field '{field}' is missing", field=field)
            )

    # Step 4: Type-specific required fields
    doc_type = _resolve_doc_type(filepath, root=root)
    if doc_type and doc_type in TYPE_SPECIFIC_REQUIRED:
        for field in TYPE_SPECIFIC_REQUIRED[doc_type]:
            if field not in data:
                findings.append(
                    _finding(
                        rel,
                        "missing_field",
                        f"Required field '{field}' is missing for {doc_type} documents",
                        field=field,
                    )
                )

    # Step 5: Field types
    for field_name, expected_type in FIELD_TYPES.items():
        if field_name not in data:
            continue
        value = data[field_name]

        if expected_type == "list":
            if not isinstance(value, list):
                findings.append(
                    _finding(
                        rel,
                        "invalid_type",
                        f"Field '{field_name}' should be a list, got {type(value).__name__}",
                        field=field_name,
                    )
                )
            elif field_name == "related":
                # related must be a list of strings
                for item in value:
                    if not isinstance(item, str):
                        findings.append(
                            _finding(
                                rel,
                                "invalid_type",
                                f"Field 'related' should be a list of strings, got {type(item).__name__} element",
                                field="related",
                            )
                        )
                        break

        elif expected_type == "string":
            if not isinstance(value, str):
                findings.append(
                    _finding(
                        rel,
                        "invalid_type",
                        f"Field '{field_name}' should be a string, got {type(value).__name__}",
                        field=field_name,
                    )
                )

        elif expected_type == "date":
            # PyYAML may parse dates as datetime.date objects. Accept those,
            # and also accept strings matching YYYY-MM-DD.
            if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
                pass  # valid
            elif isinstance(value, str):
                if not DATE_RE.match(value):
                    findings.append(
                        _finding(
                            rel,
                            "invalid_type",
                            f"Field '{field_name}' should match YYYY-MM-DD, got '{value}'",
                            field=field_name,
                        )
                    )
            else:
                findings.append(
                    _finding(
                        rel,
                        "invalid_type",
                        f"Field '{field_name}' should be a date (YYYY-MM-DD), got {type(value).__name__}",
                        field=field_name,
                    )
                )

        elif expected_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                findings.append(
                    _finding(
                        rel,
                        "invalid_type",
                        f"Field '{field_name}' should be an integer, got {type(value).__name__}",
                        field=field_name,
                    )
                )

    # Step 6: Status values
    if "status" in data and isinstance(data["status"], str):
        if doc_type and doc_type in status_values:
            valid = status_values[doc_type]
            if data["status"] not in valid:
                valid_str = ", ".join(valid)
                findings.append(
                    _finding(
                        rel,
                        "invalid_status",
                        f"Invalid status '{data['status']}' (valid for {doc_type}: {valid_str})",
                        field="status",
                    )
                )

    return findings


# -- main ---------------------------------------------------------------------

def scan_directory(directory):
    """Scan a directory tree for .md files and validate each one.

    Loads lore-config.md from the target directory (if present) and merges
    any custom_directories with schema defaults before validating.

    Returns a list of all finding dicts.
    """
    root = Path(directory)
    if not root.exists() or not root.is_dir():
        return []

    # REQ-FMVAL-7: merge custom status values from config
    custom_values = load_custom_status_values(str(root))
    merged_status = merge_status_values(custom_values)

    all_findings = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in sorted(filenames):
            if not fname.endswith(".md"):
                continue
            # Skip the config file itself; it's not a lore document.
            if fname == "lore-config.md" and Path(dirpath) == root:
                continue
            fpath = Path(dirpath) / fname
            file_findings = validate_file(str(fpath), str(root), status_values=merged_status)
            all_findings.extend(file_findings)

    return all_findings


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>", file=sys.stderr)
        sys.exit(1)

    directory = sys.argv[1]
    findings = scan_directory(directory)

    for f in findings:
        print(json.dumps(f))

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
