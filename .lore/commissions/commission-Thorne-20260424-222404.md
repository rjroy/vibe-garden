---
title: "Commission: Lore-redesign Phase 5: review /learn + /retro"
date: 2026-04-25
status: blocked
tags: [commission]
worker: Thorne
workerDisplayTitle: "Guild Warden"
prompt: "Review Phase 5 of the lore-development three-directory redesign — `/learn` (new skill) and `/retro` (reshape). Combine two perspectives the plan calls for: structural skill-quality (plugin-dev:skill-reviewer style) and brainstorm-fidelity against the capture-skill principles.\n\nPredecessor commission: `commission-Dalton-20260424-222341` (Phase 5 build). Read its result body first.\n\nAuthoritative sources:\n- Plan: `.lore/plans/lore-redesign.md` (Phase 5, ~lines 268–310)\n- Spec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-14 through 17 (retro), REQ-REDESIGN-34 through 41 (learn)\n- **Brainstorms (binding)**:\n  - `.lore/brainstorm/principles-for-capture-skills.md` — three principles binding both skills.\n  - `.lore/brainstorm/learn-dialog.md` — `/learn` design source.\n\nRead both brainstorms in full before reviewing.\n\nWhat to inspect:\n\n**Structural / skill-quality lens** for both `/learn/SKILL.md` and `/retro/SKILL.md`:\n- Frontmatter trigger phrases specific enough to fire reliably; description states purpose clearly.\n- Body is structured for an LLM reader: clear flow, no contradictions, no buried instructions.\n- Manual-invocation framing on `/learn` (REQ-REDESIGN-34).\n- `/retro` does not direct interpretation, only description.\n\n**Brainstorm-fidelity lens**:\n\nFor `/learn`, against `.lore/brainstorm/learn-dialog.md`:\n- Two-path opening (specific material vs felt pattern) — REQ-REDESIGN-35.\n- Question-first progression, AI never asserts, \"nothing\" is valid at any step — REQ-REDESIGN-36.\n- Asymmetric shape gate at artifact level — REQ-REDESIGN-37. \"Do X because it worked\" should be flagged as malformed.\n- Active dedup against `.lore/learned/` before writing — REQ-REDESIGN-38.\n- Terse write discipline, no length budget — REQ-REDESIGN-39.\n- On-request fetch only — skill never pre-scans — REQ-REDESIGN-40.\n- One file per entry, kebab-case, flat under `.lore/learned/` — REQ-REDESIGN-41.\n- Does NOT pre-create `.lore/learned/` (materialized by first write).\n\nFor `/retro`, against `.lore/brainstorm/principles-for-capture-skills.md`:\n- \"What Went Well / What Could Improve / Lessons Learned\" template fully removed — REQ-REDESIGN-14.\n- Graduation flow removed (no Invalid/Valid/Critical/Universal classification, no project CLAUDE.md / ~/.claude/rules graduation) — REQ-REDESIGN-15.\n- Analysis vocabulary forbidden in OUTPUT (`lesson`, `insight`, `we learned`, `takeaway`) — but allowed in instruction prose to TELL the model to avoid them — REQ-REDESIGN-16.\n- Status values are `open` or `archived` only.\n\n**Anti-checks (run independently)**:\n- Grep `lore-development/skills/retro/SKILL.md` for \"What Went Well\", \"What Could Improve\", \"Lessons Learned\" — only acceptable hit is in an \"avoid these forbidden phrases\" instruction. Section headings using these phrases are blockers.\n- Grep `lore-development/skills/learn/SKILL.md` for \"propose candidate lessons\", \"identify lessons from\", \"extract mistakes\" — must be absent.\n- Confirm `lore-development/README.md` lists `/learn`.\n\n**Capture-skill principle audit**: re-read `.lore/brainstorm/principles-for-capture-skills.md`. Both skills must honor every principle. If either skill violates one, that's a fix-now (this is the exact pathology the rewrite is meant to prevent).\n\nOut of scope (do not flag):\n- Phase 6 (cross-plugin + audit, next commission).\n- Celeste vision-path update — explicitly delegated to a separate guild-hall commission. Do NOT flag this.\n\nFindings format: severity (blocker / fix-now / nit), file:line, fix description. Capture in commission result body."
dependencies:
  - commission-Dalton-20260424-222341
linked_artifacts: []

activity_timeline:
  - timestamp: 2026-04-25T05:24:04.091Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T05:24:04.092Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
current_progress: ""
projectName: vibe-garden
---
