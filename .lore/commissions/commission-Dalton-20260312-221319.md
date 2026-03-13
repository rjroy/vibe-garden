---
title: "Commission: Frontmatter validation Step 3: lore-config.md support"
date: 2026-03-13
status: blocked
type: one-shot
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Implement Step 3 from the frontmatter validation plan.\n\n**What to build**: Extension to `validate_frontmatter.py` that reads `.lore/lore-config.md` and merges custom directory types and status values with the schema defaults (REQ-FMVAL-7).\n\n**Files to modify**:\n- `lore-development/scripts/validate_frontmatter.py`\n- `lore-development/scripts/tests/test_validate_frontmatter.py`\n\n**Context to read first**:\n- `.lore/plans/frontmatter-validation.md` (Step 3 section for full details)\n- `.lore/specs/frontmatter-validation.md` (REQ-FMVAL-7)\n- `lore-development/skills/tend/references/lore-config.md` (config format)\n- `lore-development/scripts/validate_frontmatter.py` (the script from Step 2)\n\n**Key behaviors**:\n- Before scanning, check for `lore-config.md` in the target directory\n- Parse its YAML frontmatter, extract `custom_directories`\n- Custom entries add to STATUS_VALUES; they do NOT override schema defaults\n- Files in directories not in schema or config skip status validation\n- Missing or unparseable config file is silently ignored\n\n**Tests must verify**:\n- Config with custom_directories adds valid status values\n- Files in custom directories validated against custom status values\n- Standard directories still use schema values (no override)\n- Unknown directories skip status validation\n- Missing/unparseable config handled gracefully\n- Config without custom_directories field handled gracefully\n\nRun all tests before declaring complete."
dependencies:
  - commission-Dalton-20260312-221309
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-13T05:13:19.320Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-13T05:15:15.205Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
current_progress: ""
projectName: vibe-garden
---
