---
title: "Commission: Review vision document spec and write /vision skill spec"
date: 2026-03-17
status: dispatched
type: one-shot
tags: [commission]
worker: Octavia
workerDisplayTitle: "Guild Chronicler"
prompt: "Two tasks, in order:\n\n## Task 1: Validate the existing spec\n\nReview `.lore/specs/lore-development/vision-document.md` against `.lore/research/lore-development/vision-statements-as-ai-decision-filters.md`. Check whether the spec is still valid and internally consistent with the research findings. Note any gaps, contradictions, or stale assumptions. Update the spec if needed.\n\n## Task 2: Write the `/vision` skill spec\n\nWrite a spec for a new `/vision` command in the lore-development plugin. The skill should:\n\n1. **Guide the user to define a project vision** — interactive, conversational flow that helps the user articulate what the project is, why it matters, and what decisions it should inform.\n2. **Bootstrap from existing code** — if the project already has code, the skill should analyze what exists and draft a vision based on observable patterns, purpose, and structure, then refine it with the user.\n3. **Produce a vision document** — the output is a `.lore/vision.md` (or similar) artifact that other lore-development skills can reference as a decision filter.\n\nLook at the existing lore-development skills in `lore-development/skills/` and `lore-development/.claude-plugin/` for conventions on skill structure, naming, and metadata. The new spec should follow the same patterns.\n\nThe spec lives in `.lore/specs/lore-development/` alongside the vision document spec. Remember: specs for AI-guided skills should be lighter than application specs — leave room for model flexibility."
dependencies: []
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-17T03:58:33.915Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-17T03:58:33.917Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
