---
title: "Commission: Frontmatter validation Step 4: Tend integration and repair"
date: 2026-03-13
status: dispatched
type: one-shot
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Implement Step 4 from the frontmatter validation plan.\n\n**What to build**: Updates to the tend status mode reference file that integrate the validation script as a pre-check and add Claude-driven repair (REQ-FMVAL-11 through REQ-FMVAL-15).\n\n**Files to modify**:\n- `lore-development/skills/tend/references/status.md`\n\n**Context to read first**:\n- `.lore/plans/frontmatter-validation.md` (Step 4 section for full details)\n- `.lore/specs/frontmatter-validation.md` (REQ-FMVAL-11 through 15)\n- `lore-development/skills/tend/references/status.md` (current file, the integration target)\n- `lore-development/skills/tend/SKILL.md` (the orchestrator, for understanding the existing pattern)\n\n**Key changes to status.md**:\n\n1. **Script invocation (REQ-FMVAL-11)**: Add a new section before \"Verification Approach\" that runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_frontmatter.py .lore/` as the first action. Handle exit codes 0, 1, 2.\n\n2. **New report categories (REQ-FMVAL-12)**: Add \"Malformed Frontmatter\" (parse_error, structural_error) and \"Invalid Frontmatter\" (missing_field, invalid_type, invalid_status) between existing \"Missing Frontmatter\" and \"Missing Status\".\n\n3. **Parse failure exclusion (REQ-FMVAL-13)**: Files in \"Malformed Frontmatter\" are excluded from subsequent three-pass verification. Note the count in the report.\n\n4. **Repair flow (REQ-FMVAL-14, REQ-FMVAL-15)**: After presenting the report, offer repair following tend's existing dry-run/confirm/apply pattern. For invalid_status, note when values look like intentional honest-status phrases.\n\n**Verification**: Have a sub-agent review the modified status.md against REQ-FMVAL-11 through 15 for spec compliance."
dependencies:
  - commission-Dalton-20260312-221319
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-13T05:13:32.615Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-13T05:15:15.206Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
  - timestamp: 2026-03-13T05:23:35.486Z
    event: status_pending
    reason: "Dependencies satisfied"
    from: "blocked"
    to: "pending"
  - timestamp: 2026-03-13T05:23:35.489Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
