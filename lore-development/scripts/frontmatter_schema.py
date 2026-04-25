"""
Machine-readable encoding of the lore document frontmatter schema.

Source of truth: lore-development/shared/frontmatter-schema.md

Each constant references the schema section it encodes.

Directory keying convention
---------------------------
The schema is organized around three top-level directories under `.lore/`:
`work/`, `reference/`, and `learned/`. Status sets are scoped to that tree.

Directory keys in this module follow that layout:

- Work documents are keyed `work/<type>` (e.g. `work/specs`, `work/notes`).
- Reference documents are keyed `reference` (one set covers the whole tree
  including subdirectories like `reference/diagrams/`).
- Learned documents are keyed `learned`.
"""

# Schema section: "Required vs Optional" table
REQUIRED_FIELDS = ["title", "date", "status", "tags"]

# Schema section: "Required vs Optional" table (optional rows)
OPTIONAL_FIELDS = ["modules", "related"]

# Schema section: "Common Fields" code block + spec/notes/task-specific fields
# Maps field name to expected type string.
FIELD_TYPES = {
    "title": "string",
    "date": "date",
    "status": "string",
    "tags": "list",
    "modules": "list",
    "related": "list",
    "req-prefix": "string",
    "source": "string",
    "sequence": "integer",
}

# Schema section: "Status Values" tables (Build / Reference / Learned)
# Maps directory key (see module docstring) to valid status strings.
STATUS_VALUES = {
    # Work documents — per-type lifecycles
    "work/brainstorm": ["open", "parked", "resolved", "archived"],
    "work/specs": ["draft", "approved", "implemented", "superseded", "archived"],
    "work/design": ["draft", "approved", "implemented", "superseded", "archived"],
    "work/plans": ["draft", "approved", "executed", "archived"],
    "work/tasks": ["pending", "complete", "skipped"],
    "work/notes": ["in_progress", "complete", "archived"],
    "work/research": ["active", "archived"],
    "work/retros": ["open", "archived"],
    "work/issues": ["open", "resolved", "wontfix", "archived"],
    "work/diagrams": ["current", "outdated", "archived"],
    # Reference documents — one shared status set, including reference/diagrams/
    "reference": ["current", "outdated", "archived"],
    # Learned documents — minimal set; lifecycle deferred per design-learned-structure.md
    "learned": ["active", "superseded"],
}

# Schema sections: "Notes-Specific Fields" and "Task-Specific Fields"
# Maps directory key to additional required fields beyond REQUIRED_FIELDS.
TYPE_SPECIFIC_REQUIRED = {
    "work/notes": ["source"],
    "work/tasks": ["source", "sequence"],
}
