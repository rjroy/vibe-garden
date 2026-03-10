---
title: "Commission: Brainstorm YAML frontmatter validation for tend skill"
date: 2026-03-10
status: completed
type: one-shot
tags: [commission]
worker: Octavia
workerDisplayTitle: "Guild Chronicler"
prompt: "Brainstorm how the lore-development `tend` skill could include a step to validate and fix YAML frontmatter in lore artifacts.\n\nContext: The `tend` skill maintains document health across `.lore/` directories. Currently it doesn't check for malformed YAML frontmatter. Common errors include unquoted string values containing colons (`:`), which break YAML parsing.\n\nExplore these questions:\n1. What common YAML frontmatter errors occur in lore artifacts? (colons in values, unquoted strings, bad indentation, missing closing `---`, etc.)\n2. What would a validation/fix script look like? Should it be a standalone script the tend skill invokes, or inline logic?\n3. Should it auto-fix safe cases (like quoting unquoted strings with colons) vs. reporting errors that need human judgment?\n4. What's the right balance between strictness and permissiveness? We don't want to break valid YAML or over-correct.\n5. How does this fit into the existing tend skill flow?\n\nUse the `/lore-development:brainstorm` skill to capture this exploration as a lore artifact. Look at the existing tend skill implementation and lore artifact formats to ground your ideas in what actually exists."
dependencies: []
linked_artifacts:
  - .lore/brainstorm/lore-development/yaml-frontmatter-validation.md

activity_timeline:
  - timestamp: 2026-03-10T01:24:46.408Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-10T01:24:46.410Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
  - timestamp: 2026-03-10T01:24:46.429Z
    event: status_in_progress
    reason: "Execution started"
    from: "dispatched"
    to: "in_progress"
  - timestamp: 2026-03-10T01:24:53.724Z
    event: progress_report
    reason: "Starting brainstorm on YAML frontmatter validation for the tend skill. Gathering context on the existing tend implementation and lore artifact formats first."
  - timestamp: 2026-03-10T01:25:47.364Z
    event: progress_report
    reason: "Context gathered. Have full picture of tend skill (4 modes: status/tags/filenames/directories), frontmatter schema, config system, and artifact examples. Now reading a few specific files to understand frontmatter parsing patterns before invoking brainstorm skill."
  - timestamp: 2026-03-10T01:26:17.076Z
    event: progress_report
    reason: "Full context gathered. Read tend skill, all mode references, frontmatter schema, config system, and real artifacts. Now invoking the brainstorm skill to capture the exploration."
  - timestamp: 2026-03-10T01:28:53.000Z
    event: result_submitted
    reason: "Created brainstorm artifact exploring YAML frontmatter validation for the tend skill. The document covers five areas:\n\n1. **Error taxonomy** - Four tiers of YAML errors ranked by frequency in real lore artifacts, from common (unquoted colons, missing closing `---`) to rare but catastrophic (anchor characters, hash-as-comment).\n\n2. **Placement recommendation** - Validated three options; recommends extending status mode (Option B) rather than adding a new mode. Status already owns \"is this document's metadata in order?\" and has the report format for it.\n\n3. **Tooling approach** - Recommends heuristic line-by-line checks described in the reference file, with Claude's judgment as fallback for ambiguous cases. Bash YAML linters noted as optional enhancement, not dependency.\n\n4. **Auto-fix spectrum** - Defines what's safe to auto-fix (missing `---`, tabs, quoting unquoted strings with colons) vs. what needs human judgment (duplicate keys, boolean coercion, broken array syntax).\n\n5. **Strictness tiers** - Proposes structural (always), semantic (schema-backed), and stylistic (suggest-only) levels of validation, with lore-config respected for custom fields.\n\nFour open questions flagged for future resolution: confidence levels in reports, performance on large directories, a `--fix` flag for safe auto-fixes, and prevention at creation time vs. repair at tend time."
  - timestamp: 2026-03-10T01:29:00.324Z
    event: status_completed
    reason: "Execution completed"
    from: "in_progress"
    to: "completed"
current_progress: "Full context gathered. Read tend skill, all mode references, frontmatter schema, config system, and real artifacts. Now invoking the brainstorm skill to capture the exploration."
projectName: vibe-garden
---
Created brainstorm artifact exploring YAML frontmatter validation for the tend skill. The document covers five areas:

1. **Error taxonomy** - Four tiers of YAML errors ranked by frequency in real lore artifacts, from common (unquoted colons, missing closing `---`) to rare but catastrophic (anchor characters, hash-as-comment).

2. **Placement recommendation** - Validated three options; recommends extending status mode (Option B) rather than adding a new mode. Status already owns "is this document's metadata in order?" and has the report format for it.

3. **Tooling approach** - Recommends heuristic line-by-line checks described in the reference file, with Claude's judgment as fallback for ambiguous cases. Bash YAML linters noted as optional enhancement, not dependency.

4. **Auto-fix spectrum** - Defines what's safe to auto-fix (missing `---`, tabs, quoting unquoted strings with colons) vs. what needs human judgment (duplicate keys, boolean coercion, broken array syntax).

5. **Strictness tiers** - Proposes structural (always), semantic (schema-backed), and stylistic (suggest-only) levels of validation, with lore-config respected for custom fields.

Four open questions flagged for future resolution: confidence levels in reports, performance on large directories, a `--fix` flag for safe auto-fixes, and prevention at creation time vs. repair at tend time.
