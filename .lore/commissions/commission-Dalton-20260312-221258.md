---
title: "Commission: Frontmatter validation Step 1: Schema data module"
date: 2026-03-13
status: dispatched
type: one-shot
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Implement Step 1 from the frontmatter validation plan.\n\n**What to build**: A Python module that encodes the frontmatter schema as importable data structures.\n\n**Files to create**:\n- `lore-development/scripts/frontmatter_schema.py`\n- `lore-development/scripts/tests/test_frontmatter_schema.py`\n\n**Context to read first**:\n- `.lore/plans/frontmatter-validation.md` (Step 1 section for full details)\n- `lore-development/shared/frontmatter-schema.md` (the source of truth)\n\n**The module exports**:\n- `REQUIRED_FIELDS`: list of field names required on all documents (`title`, `date`, `status`, `tags`)\n- `OPTIONAL_FIELDS`: list of common optional fields (`modules`, `related`)\n- `FIELD_TYPES`: dict mapping field name to expected type\n- `STATUS_VALUES`: dict mapping directory name to list of valid status strings\n- `TYPE_SPECIFIC_REQUIRED`: dict mapping directory name to additional required fields\n\nEach constant should have a comment referencing the schema section it encodes.\n\n**Tests must verify**:\n- Every document type in the schema has a STATUS_VALUES entry\n- REQUIRED_FIELDS matches the schema's \"Required vs Optional\" table\n- FIELD_TYPES covers all required and optional fields\n- TYPE_SPECIFIC_REQUIRED covers notes and tasks\n- No empty status value lists\n\nRun tests before declaring complete."
dependencies: []
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-13T05:12:58.310Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-13T05:12:58.312Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
