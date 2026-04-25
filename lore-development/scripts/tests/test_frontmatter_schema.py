"""
Tests for frontmatter_schema.py against the source of truth:
lore-development/shared/frontmatter-schema.md

Uses unittest (stdlib) so tests run without external dependencies.
Compatible with pytest when available.
"""

import sys
import unittest
from pathlib import Path

# Allow importing from scripts directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontmatter_schema import (
    FIELD_TYPES,
    OPTIONAL_FIELDS,
    REQUIRED_FIELDS,
    STATUS_VALUES,
    TYPE_SPECIFIC_REQUIRED,
)

# Directory keys listed in the schema's "Status Values" tables.
# Keying convention: work/<type> for work documents, single-name keys for
# reference and learned (each covers its whole subtree).
SCHEMA_DOCUMENT_TYPES = [
    "work/brainstorm",
    "work/specs",
    "work/design",
    "work/plans",
    "work/tasks",
    "work/notes",
    "work/research",
    "work/retros",
    "work/issues",
    "work/diagrams",
    "reference",
    "learned",
]


class TestRequiredFields(unittest.TestCase):
    def test_matches_schema_required_table(self):
        """Required fields match the schema's 'Required vs Optional' table."""
        expected = ["title", "date", "status", "tags"]
        self.assertEqual(REQUIRED_FIELDS, expected)

    def test_all_required_fields_have_types(self):
        for field in REQUIRED_FIELDS:
            self.assertIn(field, FIELD_TYPES, f"Required field '{field}' missing from FIELD_TYPES")

    def test_all_optional_fields_have_types(self):
        for field in OPTIONAL_FIELDS:
            self.assertIn(field, FIELD_TYPES, f"Optional field '{field}' missing from FIELD_TYPES")


class TestOptionalFields(unittest.TestCase):
    def test_matches_schema_optional_rows(self):
        """Optional fields match the 'No' rows in the Required vs Optional table."""
        expected = ["modules", "related"]
        self.assertEqual(OPTIONAL_FIELDS, expected)


class TestFieldTypes(unittest.TestCase):
    def test_covers_all_required_and_optional_fields(self):
        """FIELD_TYPES has entries for every required and optional field."""
        all_common = set(REQUIRED_FIELDS + OPTIONAL_FIELDS)
        for field in all_common:
            self.assertIn(field, FIELD_TYPES, f"'{field}' missing from FIELD_TYPES")

    def test_covers_type_specific_fields(self):
        """FIELD_TYPES has entries for fields introduced in type-specific sections."""
        type_specific_fields = set()
        for fields in TYPE_SPECIFIC_REQUIRED.values():
            type_specific_fields.update(fields)
        for field in type_specific_fields:
            self.assertIn(field, FIELD_TYPES, f"Type-specific field '{field}' missing from FIELD_TYPES")

    def test_no_unknown_types(self):
        """Every type value is one of the expected type strings."""
        valid_types = {"string", "date", "list", "integer"}
        for field, ftype in FIELD_TYPES.items():
            self.assertIn(ftype, valid_types, f"Field '{field}' has unexpected type '{ftype}'")


class TestStatusValues(unittest.TestCase):
    def test_every_document_type_has_entry(self):
        """Every document type from the schema has a STATUS_VALUES entry."""
        for doc_type in SCHEMA_DOCUMENT_TYPES:
            self.assertIn(doc_type, STATUS_VALUES, f"Document type '{doc_type}' missing from STATUS_VALUES")

    def test_no_empty_status_lists(self):
        """No document type has an empty list of valid status values."""
        for doc_type, values in STATUS_VALUES.items():
            self.assertGreater(len(values), 0, f"'{doc_type}' has empty status value list")

    def test_no_extra_document_types(self):
        """STATUS_VALUES doesn't contain types not in the schema."""
        for doc_type in STATUS_VALUES:
            self.assertIn(
                doc_type, SCHEMA_DOCUMENT_TYPES,
                f"'{doc_type}' in STATUS_VALUES but not in schema",
            )

    def test_status_values_are_strings(self):
        for doc_type, values in STATUS_VALUES.items():
            for v in values:
                self.assertIsInstance(v, str, f"Non-string status value in '{doc_type}': {v}")


class TestTypeSpecificRequired(unittest.TestCase):
    def test_notes_has_source(self):
        """Notes require 'source' per the Notes-Specific Fields section."""
        self.assertIn("work/notes", TYPE_SPECIFIC_REQUIRED)
        self.assertIn("source", TYPE_SPECIFIC_REQUIRED["work/notes"])

    def test_tasks_has_source_and_sequence(self):
        """Tasks require 'source' and 'sequence' per the Task-Specific Fields section."""
        self.assertIn("work/tasks", TYPE_SPECIFIC_REQUIRED)
        self.assertIn("source", TYPE_SPECIFIC_REQUIRED["work/tasks"])
        self.assertIn("sequence", TYPE_SPECIFIC_REQUIRED["work/tasks"])


if __name__ == "__main__":
    unittest.main()
