"""
Machine-readable encoding of the lore document frontmatter schema.

Source of truth: lore-development/shared/frontmatter-schema.md

Each constant references the schema section it encodes.

Directory keying convention
---------------------------
The schema covers `.lore/local/`, `.lore/work/`, `.lore/reference/`, and
`.lore/learned/`. Status sets are scoped to those trees.

Directory keys in this module follow that layout:

- Disposable local documents are keyed `local/<type>` (plans, notes, tasks).
- Historical work documents are keyed `work/<type>`; `work/specs` and the
  legacy work plans/notes/tasks remain discoverable.
- Reference documents are keyed `reference` (one set covers the whole tree
  including subdirectories like `reference/diagrams/`).
- Learned documents are keyed `learned`.
"""

# Schema section: "Required vs Optional" table
REQUIRED_FIELDS = ["title", "date", "status", "tags"]

# Schema section: "Required vs Optional" table (optional rows)
OPTIONAL_FIELDS = ["modules", "related"]

# Schema section: "Common Fields" code block + notes/task-specific fields
# Maps field name to expected type string.
FIELD_TYPES = {
    "title": "string",
    "date": "date",
    "status": "string",
    "tags": "list",
    "modules": "list",
    "related": "list",
    "source": "string",
    "sequence": "integer",
    "legacy_status": "string",
}

# Schema section: "Status Values". All lore documents share one lifecycle.
# Field-guide freshness remains separate in `fg-status` metadata.
LORE_STATUSES = ["draft", "approved", "completed", "archived"]
STATUS_VALUES = {
    key: LORE_STATUSES
    for key in (
        "work/brainstorm", "work/intents", "work/specs", "work/design",
        "work/plans", "work/tasks", "work/notes", "work/research",
        "work/retros", "work/issues", "work/diagrams", "local/plans",
        "local/notes", "local/tasks", "reference", "learned",
    )
}

# Schema sections: "Notes-Specific Fields" and "Task-Specific Fields"
# Maps directory key to additional required fields beyond REQUIRED_FIELDS.
TYPE_SPECIFIC_REQUIRED = {
    "work/notes": [],
    "work/tasks": ["source", "sequence"],
    "local/notes": [],
    "local/tasks": [],
}
