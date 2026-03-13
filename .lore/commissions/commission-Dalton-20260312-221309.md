---
title: "Commission: Frontmatter validation Step 2: Core validation script"
date: 2026-03-13
status: blocked
type: one-shot
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Implement Step 2 from the frontmatter validation plan.\n\n**What to build**: The `validate_frontmatter.py` script covering REQ-FMVAL-1 through REQ-FMVAL-6, REQ-FMVAL-8 through REQ-FMVAL-10.\n\n**Files to create**:\n- `lore-development/scripts/validate_frontmatter.py`\n- `lore-development/scripts/tests/test_validate_frontmatter.py`\n- `lore-development/scripts/tests/fixtures/` (directory of test fixture `.md` files)\n\n**Context to read first**:\n- `.lore/plans/frontmatter-validation.md` (Step 2 section for full details)\n- `.lore/specs/frontmatter-validation.md` (requirements REQ-FMVAL-1 through 10)\n- `lore-development/scripts/frontmatter_schema.py` (the schema module from Step 1)\n- `lore-development/scripts/idea_hook.py` (existing script pattern in this codebase)\n\n**Key behaviors**:\n- Accepts a single positional argument: directory path to scan\n- Walks directory tree, finds `.md` files, validates YAML frontmatter\n- Validation pipeline per file: structural check → parse check → required fields → type-specific required fields → field types → status values\n- Output: JSON lines to stdout (one JSON object per finding)\n- Exit codes: 0 (clean), 1 (errors found), 2 (PyYAML missing)\n- Exit 0 on empty or nonexistent directory\n- Graceful PyYAML fallback with clear error message\n\n**Test fixtures needed** (known-good and known-bad `.md` files for each error type). Coverage target: 90%+.\n\nSee the plan's Step 2 section for complete test list. Run all tests before declaring complete."
dependencies:
  - commission-Dalton-20260312-221258
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-13T05:13:09.459Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-13T05:15:15.204Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
current_progress: ""
projectName: vibe-garden
---
