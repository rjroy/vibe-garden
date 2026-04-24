---
title: "Audience with Guild Visionary"
date: 2026-04-24
status: closed
tags: [meeting]
worker: Celeste
workerDisplayTitle: "Guild Visionary"
agenda: "Are lore files work files or persistent data?\nAre retro files really lessons learned or are we missing a beat?\nIs the real power reducing these data files into two sets of progressive discovery files: \n- architecture insights (the design details you cannot get just by looking at the code)\n- institutional knowledge (the lessons learned only by using the system)"
deferred_until: ""
linked_artifacts: []
meeting_log:
  - timestamp: 2026-04-24T01:37:11.585Z
    event: opened
    reason: "User started audience"
  - timestamp: 2026-04-24T03:12:16.724Z
    event: closed
    reason: "User closed audience"
---
Meeting Notes: Guild Hall `.lore` Directory Redesign

The session explored a structural redesign of the `.lore` directory to better map function rather than artifact type. The proposed three-directory model organizes `.lore/build/` (transient work: brainstorms, specs, plans, retros, research), `.lore/reference/` (solidified knowledge: approved vision, excavated features, current-state diagrams), and `.lore/learned/` (behavioral guidelines: what to do, what never to do in this project). This reframing shifts the organizing question from "what is this?" to "what is this for?"

A critical finding emerged about retro design: current retros hallucinate profoundness due to template-driven sections that demand five learnings. The redesign separates concerns by removing lessons extraction from retro entirely. Retro becomes pure observation—recording what happened without interpretation. Lessons extraction moves to a dedicated skill that surfaces candidates from build artifacts at design time, with explicit human gating to prevent hallucination and survivorship bias. This enforces an asymmetric principle: learn only from mistakes, never from success.

The roadmap identifies five sequential steps: brainstorm the "distill" function (moving data from build to reference), brainstorm the "learn" function (extracting lessons via dialog), strip retro to event recording only, refactor existing skills to the new hierarchy, then implement the two new skills. Step ordering couples retro simplification with learn implementation to avoid a migration gap. Step 4 (refactor) is larger than its description suggests and will require separate specification.

Artifacts produced: two brainstorms (directory-redesign, principles-for-capture-skills), three issues (design-extraction-skill, design-learned-structure, roadmap-lore-redesign), and three worker memories documenting anti-hallucination principles for capture skills. All linked for continuity in the next design phase.

Human approval required on learned-structure and extraction-skill designs before implementation. No blocking dependencies; work can proceed in parallel once those brainstorms complete.
