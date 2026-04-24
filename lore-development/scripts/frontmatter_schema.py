"""
Machine-readable encoding of the lore document frontmatter schema.

Source of truth: lore-development/shared/frontmatter-schema.md

Each constant references the schema section it encodes.

Directory keying convention
---------------------------
The schema is organized around three top-level directories under `.lore/`:
`build/`, `reference/`, and `learned/`. Status sets are scoped to that tree.

Directory keys in this module follow that layout:

- Build documents are keyed `build/<type>` (e.g. `build/specs`, `build/notes`).
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
    # Build documents — per-type lifecycles
    "build/brainstorm": ["open", "parked", "resolved", "archived"],
    "build/specs": ["draft", "approved", "implemented", "superseded", "archived"],
    "build/design": ["draft", "approved", "implemented", "superseded", "archived"],
    "build/plans": ["draft", "approved", "executed", "archived"],
    "build/tasks": ["pending", "complete", "skipped"],
    "build/notes": ["in_progress", "complete", "archived"],
    "build/research": ["active", "archived"],
    "build/retros": ["open", "archived"],
    "build/issues": ["open", "resolved", "wontfix", "archived"],
    "build/diagrams": ["current", "outdated", "archived"],
    # Reference documents — one shared status set, including reference/diagrams/
    "reference": ["current", "outdated", "archived"],
    # Learned documents — minimal set; lifecycle deferred per design-learned-structure.md
    "learned": ["active", "superseded"],
}

# Schema sections: "Notes-Specific Fields" and "Task-Specific Fields"
# Maps directory key to additional required fields beyond REQUIRED_FIELDS.
TYPE_SPECIFIC_REQUIRED = {
    "build/notes": ["source"],
    "build/tasks": ["source", "sequence"],
}
