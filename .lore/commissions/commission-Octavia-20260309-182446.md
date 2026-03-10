---
title: "Commission: Brainstorm YAML frontmatter validation for tend skill"
date: 2026-03-10
status: dispatched
type: one-shot
tags: [commission]
worker: Octavia
workerDisplayTitle: "Guild Chronicler"
prompt: "Brainstorm how the lore-development `tend` skill could include a step to validate and fix YAML frontmatter in lore artifacts.\n\nContext: The `tend` skill maintains document health across `.lore/` directories. Currently it doesn't check for malformed YAML frontmatter. Common errors include unquoted string values containing colons (`:`), which break YAML parsing.\n\nExplore these questions:\n1. What common YAML frontmatter errors occur in lore artifacts? (colons in values, unquoted strings, bad indentation, missing closing `---`, etc.)\n2. What would a validation/fix script look like? Should it be a standalone script the tend skill invokes, or inline logic?\n3. Should it auto-fix safe cases (like quoting unquoted strings with colons) vs. reporting errors that need human judgment?\n4. What's the right balance between strictness and permissiveness? We don't want to break valid YAML or over-correct.\n5. How does this fit into the existing tend skill flow?\n\nUse the `/lore-development:brainstorm` skill to capture this exploration as a lore artifact. Look at the existing tend skill implementation and lore artifact formats to ground your ideas in what actually exists."
dependencies: []
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-10T01:24:46.408Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-10T01:24:46.410Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
