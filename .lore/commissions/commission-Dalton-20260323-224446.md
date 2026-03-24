---
title: "Commission: Fix Prep Plan"
date: 2026-03-24
status: dispatched
type: one-shot
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Add a plan example to the frontmatter schema in shared/frontmatter-schema.md.\nThe Examples section (starting around line 109) has concrete examples for every document type except plans. This gap causes workers to infer plan status when running /prep-plan, and they're choosing active (a research-only status) instead of draft.\nAdd a plan example between the existing design and research examples, following the same pattern:\n### Plan\n\n```yaml\n---\ntitle: \"Implementation plan: auth-flow\"\ndate: 2026-02-05\nstatus: draft\ntags: [plan, auth]\nmodules: [auth-service]\nrelated: [.lore/specs/auth-flow.md]\n---\nNew plans should always start as draft. They move to approved when the user accepts them, and executed after implementation completes."
dependencies: []
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-03-24T05:44:46.600Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-03-24T05:44:54.285Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
