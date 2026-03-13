"""
Machine-readable encoding of the lore document frontmatter schema.

Source of truth: lore-development/shared/frontmatter-schema.md

Each constant references the schema section it encodes.
"""

# Schema section: "Required vs Optional" table
REQUIRED_FIELDS = ["title", "date", "status", "tags"]

# Schema section: "Required vs Optional" table (optional rows)
OPTIONAL_FIELDS = ["modules", "related"]

# Schema section: "Common Fields" code block + "Spec-Specific Fields"
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

# Schema section: "Status Values by Document Type" table
# Maps directory name (the segment after .lore/) to valid status strings.
STATUS_VALUES = {
    "brainstorm": ["open", "resolved", "parked"],
    "specs": ["draft", "approved", "implemented", "superseded"],
    "design": ["draft", "approved", "implemented", "superseded"],
    "retros": ["complete"],
    "research": ["active", "archived"],
    "diagrams": ["current", "outdated"],
    "plans": ["draft", "approved", "executed"],
    "notes": ["active", "complete"],
    "tasks": ["pending", "complete", "skipped"],
    "reference": ["current", "outdated"],
    "issues": ["open", "resolved", "wontfix"],
}

# Schema sections: "Notes-Specific Fields" and "Task-Specific Fields"
# Maps directory name to additional required fields beyond REQUIRED_FIELDS.
TYPE_SPECIFIC_REQUIRED = {
    "notes": ["source"],
    "tasks": ["source", "sequence"],
}
