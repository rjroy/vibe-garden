---
title: "Commission: Implement /vision skill from spec"
date: 2026-03-17
status: dispatched
type: one-shot
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Build the `/vision` skill for the lore-development plugin based on the spec Octavia wrote.\n\n## Source artifacts\n\n- Skill spec: `.lore/specs/lore-development/` (look for the vision skill spec Octavia created)\n- Vision document spec: `.lore/specs/lore-development/vision-document.md`\n- Research: `.lore/research/lore-development/vision-statements-as-ai-decision-filters.md`\n\n## Requirements\n\n1. **Implement the skill** following lore-development conventions. Study the existing skills in `lore-development/skills/` and `lore-development/.claude-plugin/` for structure, naming, metadata patterns, and how skills are registered.\n\n2. **Update the frontmatter schema** — the vision document will need a frontmatter definition. Check how other lore artifacts define their frontmatter schemas (look at `lore-development/shared/` and any validation/schema files) and add the vision document's schema following the same pattern.\n\n3. **Run the plugin-dev skill-reviewer** on the completed skill. Use `/plugin-dev:skill-reviewer` to validate the skill against plugin conventions. Fix any issues it surfaces before declaring done.\n\n4. **Run tests** — if there are existing tests for lore-development skills, follow that pattern. If not, ensure the skill at minimum loads without errors.\n\n## Key behavior\n\nThe skill has two modes:\n- **Guided creation**: Walk the user through defining a vision interactively\n- **Bootstrap from code**: If the project has existing code, analyze it and draft a vision based on what exists, then refine with the user\n\nThe output is a vision document artifact that other lore-development skills can reference as a decision filter."
dependencies:
  - commission-Octavia-20260316-205833
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-17T04:09:41.881Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-17T04:09:41.883Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
