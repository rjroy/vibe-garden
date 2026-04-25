---
title: "Commission: Lore-redesign Phase 4: /excavate → /distill rename and reshape"
date: 2026-04-25
status: dispatched
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 4 of the lore-development three-directory redesign — rename `/excavate` to `/distill` and reshape the skill per the distill brainstorm.\n\nPlan: `.lore/plans/lore-redesign.md` — Phase 4 section (~lines 229–266). Read in full first.\nSpec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-26 through 33.\nBrainstorm (BINDING — do not re-derive shape rule): `.lore/brainstorm/distill-function.md`. Read in full before writing the SKILL.md.\n\nFoundation, path fan-out, agent descriptions, and `/tend migrate` are all landed (Phase 3 fix at commission-Dalton-20260424-180526). Build on those.\n\n**Decision adopted by the plan (Open Question 2)**: distill-before-archive prompt is a SOFT prompt, not hard enforcement. When `directories` mode considers a spec with `status: implemented` for archive, surface \"Distill this spec before archiving?\" — user answers, archive proceeds either way. Rationale: matches the `/tend` dry-run → confirm → apply pattern; preserves user agency.\n\nFiles to touch:\n- `lore-development/skills/excavate/` → rename to `lore-development/skills/distill/` (directory rename, preserve git history if possible).\n- `lore-development/skills/distill/SKILL.md` — full body rewrite per the distill brainstorm. Update `name:` field from `excavate` to `distill`. Update trigger phrases.\n- `lore-development/agents/surface-surveyor.md` — update `/lore-development:excavate` invocation reference to `/lore-development:distill`.\n- `lore-development/skills/tend/SKILL.md` — add the soft distill-before-archive prompt hook in the `directories` mode (or wherever archive logic lives). Do NOT touch the `migrate` mode entry that Phase 3 added.\n- `lore-development/skills/tend/references/status.md` — archive logic for `status: implemented` specs gains the soft-prompt note.\n- `lore-development/README.md` — update skill list: rename `excavate` entry to `distill`.\n- `.claude-plugin/marketplace.json` (root) — confirm whether this plugin's marketplace entry references skill names; update `excavate` → `distill` if present. If not, drop this step.\n\nSKILL.md body shape (REQ-REDESIGN-26 through 32):\n- Two seed modes: `/distill code` (reshape of current excavate behavior, tuned down per REQ-REDESIGN-29 shape rule) and `/distill build` (new — reads from `.lore/build/specs/`, `.lore/build/plans/`, `.lore/build/brainstorm/` as seed material).\n- Shared core: read seed → verify against code → present reconciled candidates → user gates each. Build-seed mismatches surface explicitly (REQ-REDESIGN-28).\n- Shape rule (REQ-REDESIGN-29): reference contains only what the code cannot tell a reader. No function signatures, no endpoint lists. Cite the brainstorm.\n- Null output is valid (REQ-REDESIGN-30). No template pressure to manufacture candidates.\n- Reference is living, not append-only: distill updates existing reference files when code drifts (REQ-REDESIGN-31).\n- Excavation index moves to `.lore/build/excavations/index.md` (REQ-REDESIGN-32). Reference docs themselves stay in `.lore/reference/` (unchanged).\n\nVerification:\n- `grep -rE '\\\\bexcavate\\\\b' lore-development/` — any remaining hit must be intentional migration documentation that references the old name. Skill names, file paths, agent descriptions, README all show `distill`.\n- `grep -rE '\\\\bdistill\\\\b' lore-development/skills/distill/SKILL.md` — confirm `name:` field, trigger phrases, and body all use the new name.\n- Anti-template / anti-assertion spot check on the new SKILL.md: no demand for a count of candidates; \"Null output is valid\" appears in prompt guidance.\n- Manual trigger sanity: `/distill build .lore/build/specs/<a-spec>.md` — skill loads, asks user for seed confirmation, does not pre-scan candidates.\n\nReport in your result body: files renamed/touched, grep audit, SKILL.md body shape summary citing which brainstorm sections drove it, and decisions on edge cases. Two reviewers will follow: plugin-dev:skill-reviewer (structural) and a fresh-context check against the brainstorm (fidelity)."
dependencies:
  - commission-Dalton-20260424-180526
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-25T01:05:56.145Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T01:05:56.147Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
  - timestamp: 2026-04-25T04:34:54.759Z
    event: status_pending
    reason: "Dependencies satisfied"
    from: "blocked"
    to: "pending"
  - timestamp: 2026-04-25T04:34:54.762Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
current_progress: ""
projectName: vibe-garden
---
