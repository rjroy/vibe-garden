---
title: "Commission: Lore-redesign Phase 1: path string fan-out across skills"
date: 2026-04-25
status: dispatched
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 1 of the lore-development three-directory redesign.\n\nPlan: `.lore/plans/lore-redesign.md` — Phase 1 section. Read in full first.\nSpec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-4, 5, 6, 7, 46.\n\nFoundation already landed via Phase 0 (commission-Dalton-20260424-164331). The schema, frontmatter_schema.py, tend reference files, and fixture trees now use the three-directory model. Build on that — do not re-touch Phase 0 files.\n\nScope: mechanical but bulk path-string updates across skill prompts and the idea hook. Bounded — path strings only, no behavioral or content restructure (with one small behavior addition, see REQ-REDESIGN-5 below).\n\nFiles to touch:\n- `lore-development/skills/{brainstorm,specify,design,prep-plan,plan-breakdown,implement,simplify,research,file-issue,review-ideas,define-validation,update-stubs,back-propagate,ddp,vision,poke-holes}/SKILL.md` — update output paths in prose, example paths in frontmatter snippets, cross-references to sibling skill output dirs, example `related:` and `source:` values, and example markdown links in document templates. Use the migration table from REQ-REDESIGN-6.\n- `lore-development/skills/retro/SKILL.md` — path strings only (e.g. `.lore/retros/` → `.lore/build/retros/`). Do NOT touch body content, template, or graduation flow — Phase 5 owns the reshape.\n- `lore-development/skills/excavate/SKILL.md` — excavation-index path only (`.lore/excavations/` → `.lore/build/excavations/`). Do NOT rename the directory or skill, do NOT touch body — Phase 4 owns that.\n- `lore-development/scripts/idea_hook.py` — change write path from `.lore/ideas/` to `.lore/build/ideas/`. Update docstrings.\n- `lore-development/skills/update-lore-agents/SKILL.md` — verify and update any hardcoded paths.\n\nBehavior addition (REQ-REDESIGN-5): `/ddp` gains a small split-by-purpose dialog (build vs reference diagrams; default to build when ambiguous). Keep this small (~30 lines max). If it grows beyond that, leave a TODO marker and flag it in your result; we'll promote to its own step.\n\nDo NOT touch in this phase:\n- Agent descriptions in `lore-development/agents/` — Phase 2 owns these.\n- Celeste agent (lives outside lore-development) — Phase 6 owns this.\n- Anything Phase 0 already settled (schema, frontmatter_schema.py, tend references).\n\nREQ-REDESIGN-7 reminder: `/review-ideas` handles `.lore/build/ideas/` as a frontmatter-free queue. Update prose paths only; semantics unchanged.\n\nVerification (run all and report):\n1. `grep -rE '\\.lore/(brainstorm|specs|design|plans|tasks|notes|research|retros|issues|ideas|validation|stubs|excavations|diagrams)/' lore-development/skills/` — every hit must be (a) inside retro/SKILL.md or excavate/SKILL.md body content the later phases own, (b) deliberate migration documentation, or (c) a miss to fix.\n2. `grep -rE '\\.lore/vision\\.md' lore-development/` — only hits should be in migration documentation.\n3. Smoke test: confirm each touched SKILL.md still parses (YAML frontmatter intact, file readable).\n\nReport in your result body: file list touched, grep audit output, any path strings you intentionally left unchanged with reasons. The next commission is a Thorne review (fresh-context, breadth-first consistency check)."
dependencies:
  - commission-Dalton-20260424-164331
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-25T00:16:45.973Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T00:16:45.974Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
