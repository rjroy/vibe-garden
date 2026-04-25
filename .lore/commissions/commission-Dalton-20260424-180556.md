---
title: "Commission: Lore-redesign Phase 4: /excavate → /distill rename and reshape"
date: 2026-04-25
status: completed
tags: [commission]
worker: Dalton
workerDisplayTitle: "Guild Artificer"
prompt: "Execute Phase 4 of the lore-development three-directory redesign — rename `/excavate` to `/distill` and reshape the skill per the distill brainstorm.\n\nPlan: `.lore/plans/lore-redesign.md` — Phase 4 section (~lines 229–266). Read in full first.\nSpec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-26 through 33.\nBrainstorm (BINDING — do not re-derive shape rule): `.lore/brainstorm/distill-function.md`. Read in full before writing the SKILL.md.\n\nFoundation, path fan-out, agent descriptions, and `/tend migrate` are all landed (Phase 3 fix at commission-Dalton-20260424-180526). Build on those.\n\n**Decision adopted by the plan (Open Question 2)**: distill-before-archive prompt is a SOFT prompt, not hard enforcement. When `directories` mode considers a spec with `status: implemented` for archive, surface \"Distill this spec before archiving?\" — user answers, archive proceeds either way. Rationale: matches the `/tend` dry-run → confirm → apply pattern; preserves user agency.\n\nFiles to touch:\n- `lore-development/skills/excavate/` → rename to `lore-development/skills/distill/` (directory rename, preserve git history if possible).\n- `lore-development/skills/distill/SKILL.md` — full body rewrite per the distill brainstorm. Update `name:` field from `excavate` to `distill`. Update trigger phrases.\n- `lore-development/agents/surface-surveyor.md` — update `/lore-development:excavate` invocation reference to `/lore-development:distill`.\n- `lore-development/skills/tend/SKILL.md` — add the soft distill-before-archive prompt hook in the `directories` mode (or wherever archive logic lives). Do NOT touch the `migrate` mode entry that Phase 3 added.\n- `lore-development/skills/tend/references/status.md` — archive logic for `status: implemented` specs gains the soft-prompt note.\n- `lore-development/README.md` — update skill list: rename `excavate` entry to `distill`.\n- `.claude-plugin/marketplace.json` (root) — confirm whether this plugin's marketplace entry references skill names; update `excavate` → `distill` if present. If not, drop this step.\n\nSKILL.md body shape (REQ-REDESIGN-26 through 32):\n- Two seed modes: `/distill code` (reshape of current excavate behavior, tuned down per REQ-REDESIGN-29 shape rule) and `/distill build` (new — reads from `.lore/build/specs/`, `.lore/build/plans/`, `.lore/build/brainstorm/` as seed material).\n- Shared core: read seed → verify against code → present reconciled candidates → user gates each. Build-seed mismatches surface explicitly (REQ-REDESIGN-28).\n- Shape rule (REQ-REDESIGN-29): reference contains only what the code cannot tell a reader. No function signatures, no endpoint lists. Cite the brainstorm.\n- Null output is valid (REQ-REDESIGN-30). No template pressure to manufacture candidates.\n- Reference is living, not append-only: distill updates existing reference files when code drifts (REQ-REDESIGN-31).\n- Excavation index moves to `.lore/build/excavations/index.md` (REQ-REDESIGN-32). Reference docs themselves stay in `.lore/reference/` (unchanged).\n\nVerification:\n- `grep -rE '\\\\bexcavate\\\\b' lore-development/` — any remaining hit must be intentional migration documentation that references the old name. Skill names, file paths, agent descriptions, README all show `distill`.\n- `grep -rE '\\\\bdistill\\\\b' lore-development/skills/distill/SKILL.md` — confirm `name:` field, trigger phrases, and body all use the new name.\n- Anti-template / anti-assertion spot check on the new SKILL.md: no demand for a count of candidates; \"Null output is valid\" appears in prompt guidance.\n- Manual trigger sanity: `/distill build .lore/build/specs/<a-spec>.md` — skill loads, asks user for seed confirmation, does not pre-scan candidates.\n\nReport in your result body: files renamed/touched, grep audit, SKILL.md body shape summary citing which brainstorm sections drove it, and decisions on edge cases. Two reviewers will follow: plugin-dev:skill-reviewer (structural) and a fresh-context check against the brainstorm (fidelity)."
dependencies:
  - commission-Dalton-20260424-180526
linked_artifacts:
  - lore-development/skills/distill/SKILL.md

  - lore-development/agents/surface-surveyor.md
  - lore-development/skills/tend/SKILL.md
  - lore-development/skills/tend/references/status.md
  - lore-development/README.md
  - lore-development/skills/back-propagate/SKILL.md
  - lore-development/skills/update-lore-agents/SKILL.md
  - lore-development/agents/surface-surveyor.md
  - lore-development/skills/tend/SKILL.md
  - lore-development/skills/tend/references/status.md
  - lore-development/README.md
  - lore-development/skills/back-propagate/SKILL.md
  - lore-development/skills/update-lore-agents/SKILL.md
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
  - timestamp: 2026-04-25T04:34:54.779Z
    event: status_in_progress
    reason: "Execution started"
    from: "dispatched"
    to: "in_progress"
  - timestamp: 2026-04-25T04:35:42.000Z
    event: progress_report
    reason: "Read plan Phase 4, distill brainstorm, spec REQ-26..33, current excavate SKILL.md, surface-surveyor agent, tend SKILL.md, and tend status reference. Starting rename + body rewrite."
  - timestamp: 2026-04-25T04:42:09.265Z
    event: result_submitted
    reason: "Phase 4 complete. /excavate → /distill rename and reshape landed.\n\n## Files touched\n- **Renamed** (git mv, history preserved): `lore-development/skills/excavate/SKILL.md` → `lore-development/skills/distill/SKILL.md`.\n- **Body rewrite**: `lore-development/skills/distill/SKILL.md` — full rewrite per `.lore/brainstorm/distill-function.md`. `name:` field changed from `excavate` to `distill`. Triggers now reference `/distill`, `/distill code`, `/distill build`. `artifact_path: .lore/reference` retained (unchanged per REQ-REDESIGN-32).\n- **Updated**: `lore-development/agents/surface-surveyor.md` — invocation context now points to `/lore-development:distill` (`code` mode).\n- **Updated**: `lore-development/skills/tend/SKILL.md` — added \"Distill-Before-Archive (soft prompt)\" section after the Modes block. Did not touch the `migrate` mode entry from Phase 3.\n- **Updated**: `lore-development/skills/tend/references/status.md` — added archive-coupling note under \"For 'implemented' specs\".\n- **Updated**: `lore-development/README.md` — skill list line `/lore-development:excavate` replaced with `/lore-development:distill`. \"Excavating existing code\" workflow paragraph rewritten to \"Distilling existing code\". The \"Human checkpoints\" principle line updated. (Old layout tree at line 51 left untouched — that's Phase 6's three-directory rewrite.)\n- **Updated**: `lore-development/skills/back-propagate/SKILL.md` — \"Relationship to Other Skills\" line updated from `/excavate` to `/distill`.\n- **Updated**: `lore-development/skills/update-lore-agents/SKILL.md` — two surface-surveyor description lines updated from \"feature excavation\" / \"During excavation\" to distillation framing. Skill-list category line for `excavate` already fixed (renamed to `distill`).\n- **Marketplace.json**: confirmed no skill-name references; no change needed.\n\n## Grep audit results\n- `grep -rE '\\\\bexcavate\\\\b' lore-development/` → **zero hits**.\n- `grep -rE '\\\\bexcavat' lore-development/` (broader) → only nouns survive: `excavations/` directory references (the index path retained per REQ-REDESIGN-32) and \"excavation index\" / \"excavation\" as a generic term in 3 locations within distill SKILL.md — all intentional. lore-researcher.md, spec-reviewer.md, frontmatter-schema.md, tend_migrate.py and tend reference files use the noun for the directory list (Phase 1/3 territory, not Phase 4 scope).\n- `grep -rE '/lore-development:excavate|/excavate' lore-development/` → **zero hits**.\n- \"Null Output Is Valid\" header present (line 57). No \"list of N\", \"at least N candidate\", \"exactly N candidate\" pressure in body. No \"fill out the template\" demand. The single \"N items\" mention is in the negative form: \"There is no template that asks for N items.\"\n\n## SKILL.md body shape (citing brainstorm sections)\nBody sections are organized to surface the brainstorm's binding decisions:\n- **Two Seed Modes** table — drives from \"Shape: Two seed modes\" in the brainstorm.\n- **Shape Rule (binding)** — explicit \"belongs/doesn't belong\" lists, citing `.lore/brainstorm/distill-function.md` \"The shape rule for reference\" and the principles-for-capture-skills brainstorm. Function signatures / endpoint lists / schema descriptions are explicitly disallowed.\n- **Null Output Is Valid** — direct from \"Output characteristics: Null output is valid\" + capture-skills principle 1.\n- **Core Operation** — six-step loop matching the brainstorm's \"Core operation\" (read seed → verify → apply shape rule → present reconciled candidates → user gates → update index).\n- **Build-Seed Mismatches Are Not Silently Corrected** — REQ-REDESIGN-28; the brainstorm's \"When the seed disagrees with the code, surface the mismatch explicitly.\"\n- **Reference Is Living, Not Append-Only** — direct from \"Reference docs are living\" in the brainstorm; REQ-REDESIGN-31. Includes the `current → outdated → current` status flow proposal.\n- **Placement** — paraphrases the brainstorm's \"Placement\" verbatim in spirit; reference has no prescribed topology.\n- **Excavation Index** — at `.lore/build/excavations/index.md` per REQ-REDESIGN-32; null-output sessions still update the index.\n- **When /distill code Walks a Feature** + **When /distill build Reads an Artifact** — separate sections preserve the original excavate walking pattern (tuned down) and add the build-seed feedstock priority order (specs > plans > brainstorms/research) from the brainstorm's \"What feeds distill build, in order of expected yield\".\n- **Tend Coupling** — names the soft-prompt decision adopted by the plan.\n- **Verification Pass** — closes with the user-gate-and-grep discipline.\n\n## Edge-case decisions\n1. **Frontmatter `name:` vs `skill:`**: original used `skill: excavate`; new SKILL.md uses `name: distill` to match every other lore-development SKILL.md (verified via head-5 across all skills). The commission instructed to \"update `name:` field\" so this matches both the convention and the literal instruction.\n2. **README workflow paragraph beyond skill list**: the commission scope listed only the skill-list line, but the workflow section \"Excavating existing code\" (line 119) and the \"Human checkpoints\" principle still referenced `/excavate`. I updated both because the audit rule says \"README all show distill\". The README's `.lore/` storage tree (line 51, old single-level layout) is left untouched — it's Phase 6's three-directory model rewrite territory.\n3. **back-propagate and update-lore-agents references**: both contained skill-name pointers to `/excavate`. Updated, since the audit forbids any non-migration-doc reference to the old skill name. These were not in the commission's named file list but were caught by the grep audit.\n4. **Soft prompt placement**: added a dedicated \"Distill-Before-Archive (soft prompt)\" section in `tend/SKILL.md` after the Modes block (so it's visible in any reading), plus a one-line cross-reference in `status.md` under \"For 'implemented' specs\". The detailed prompt logic lives in SKILL.md; status.md just notes the coupling. Did not touch `directories.md` since the commission did not list it.\n5. **Marketplace.json**: confirmed contents — only top-level plugin metadata, no skill-name references. No change needed; commission-listed conditional dropped.\n\n## Reviewers next\n- `plugin-dev:skill-reviewer` on `lore-development/skills/distill/SKILL.md` (structural).\n- `fresh-lore` (or equivalent fresh-context check) cross-checking SKILL.md against `.lore/brainstorm/distill-function.md` for shape-rule preservation and absence of spec-replacement ambition."
  - timestamp: 2026-04-25T04:42:16.036Z
    event: status_completed
    reason: "Execution completed"
    from: "in_progress"
    to: "completed"
current_progress: "Read plan Phase 4, distill brainstorm, spec REQ-26..33, current excavate SKILL.md, surface-surveyor agent, tend SKILL.md, and tend status reference. Starting rename + body rewrite."
projectName: vibe-garden
---
Phase 4 complete. /excavate → /distill rename and reshape landed.

## Files touched
- **Renamed** (git mv, history preserved): `lore-development/skills/excavate/SKILL.md` → `lore-development/skills/distill/SKILL.md`.
- **Body rewrite**: `lore-development/skills/distill/SKILL.md` — full rewrite per `.lore/brainstorm/distill-function.md`. `name:` field changed from `excavate` to `distill`. Triggers now reference `/distill`, `/distill code`, `/distill build`. `artifact_path: .lore/reference` retained (unchanged per REQ-REDESIGN-32).
- **Updated**: `lore-development/agents/surface-surveyor.md` — invocation context now points to `/lore-development:distill` (`code` mode).
- **Updated**: `lore-development/skills/tend/SKILL.md` — added "Distill-Before-Archive (soft prompt)" section after the Modes block. Did not touch the `migrate` mode entry from Phase 3.
- **Updated**: `lore-development/skills/tend/references/status.md` — added archive-coupling note under "For 'implemented' specs".
- **Updated**: `lore-development/README.md` — skill list line `/lore-development:excavate` replaced with `/lore-development:distill`. "Excavating existing code" workflow paragraph rewritten to "Distilling existing code". The "Human checkpoints" principle line updated. (Old layout tree at line 51 left untouched — that's Phase 6's three-directory rewrite.)
- **Updated**: `lore-development/skills/back-propagate/SKILL.md` — "Relationship to Other Skills" line updated from `/excavate` to `/distill`.
- **Updated**: `lore-development/skills/update-lore-agents/SKILL.md` — two surface-surveyor description lines updated from "feature excavation" / "During excavation" to distillation framing. Skill-list category line for `excavate` already fixed (renamed to `distill`).
- **Marketplace.json**: confirmed no skill-name references; no change needed.

## Grep audit results
- `grep -rE '\\bexcavate\\b' lore-development/` → **zero hits**.
- `grep -rE '\\bexcavat' lore-development/` (broader) → only nouns survive: `excavations/` directory references (the index path retained per REQ-REDESIGN-32) and "excavation index" / "excavation" as a generic term in 3 locations within distill SKILL.md — all intentional. lore-researcher.md, spec-reviewer.md, frontmatter-schema.md, tend_migrate.py and tend reference files use the noun for the directory list (Phase 1/3 territory, not Phase 4 scope).
- `grep -rE '/lore-development:excavate|/excavate' lore-development/` → **zero hits**.
- "Null Output Is Valid" header present (line 57). No "list of N", "at least N candidate", "exactly N candidate" pressure in body. No "fill out the template" demand. The single "N items" mention is in the negative form: "There is no template that asks for N items."

## SKILL.md body shape (citing brainstorm sections)
Body sections are organized to surface the brainstorm's binding decisions:
- **Two Seed Modes** table — drives from "Shape: Two seed modes" in the brainstorm.
- **Shape Rule (binding)** — explicit "belongs/doesn't belong" lists, citing `.lore/brainstorm/distill-function.md` "The shape rule for reference" and the principles-for-capture-skills brainstorm. Function signatures / endpoint lists / schema descriptions are explicitly disallowed.
- **Null Output Is Valid** — direct from "Output characteristics: Null output is valid" + capture-skills principle 1.
- **Core Operation** — six-step loop matching the brainstorm's "Core operation" (read seed → verify → apply shape rule → present reconciled candidates → user gates → update index).
- **Build-Seed Mismatches Are Not Silently Corrected** — REQ-REDESIGN-28; the brainstorm's "When the seed disagrees with the code, surface the mismatch explicitly."
- **Reference Is Living, Not Append-Only** — direct from "Reference docs are living" in the brainstorm; REQ-REDESIGN-31. Includes the `current → outdated → current` status flow proposal.
- **Placement** — paraphrases the brainstorm's "Placement" verbatim in spirit; reference has no prescribed topology.
- **Excavation Index** — at `.lore/build/excavations/index.md` per REQ-REDESIGN-32; null-output sessions still update the index.
- **When /distill code Walks a Feature** + **When /distill build Reads an Artifact** — separate sections preserve the original excavate walking pattern (tuned down) and add the build-seed feedstock priority order (specs > plans > brainstorms/research) from the brainstorm's "What feeds distill build, in order of expected yield".
- **Tend Coupling** — names the soft-prompt decision adopted by the plan.
- **Verification Pass** — closes with the user-gate-and-grep discipline.

## Edge-case decisions
1. **Frontmatter `name:` vs `skill:`**: original used `skill: excavate`; new SKILL.md uses `name: distill` to match every other lore-development SKILL.md (verified via head-5 across all skills). The commission instructed to "update `name:` field" so this matches both the convention and the literal instruction.
2. **README workflow paragraph beyond skill list**: the commission scope listed only the skill-list line, but the workflow section "Excavating existing code" (line 119) and the "Human checkpoints" principle still referenced `/excavate`. I updated both because the audit rule says "README all show distill". The README's `.lore/` storage tree (line 51, old single-level layout) is left untouched — it's Phase 6's three-directory model rewrite territory.
3. **back-propagate and update-lore-agents references**: both contained skill-name pointers to `/excavate`. Updated, since the audit forbids any non-migration-doc reference to the old skill name. These were not in the commission's named file list but were caught by the grep audit.
4. **Soft prompt placement**: added a dedicated "Distill-Before-Archive (soft prompt)" section in `tend/SKILL.md` after the Modes block (so it's visible in any reading), plus a one-line cross-reference in `status.md` under "For 'implemented' specs". The detailed prompt logic lives in SKILL.md; status.md just notes the coupling. Did not touch `directories.md` since the commission did not list it.
5. **Marketplace.json**: confirmed contents — only top-level plugin metadata, no skill-name references. No change needed; commission-listed conditional dropped.

## Reviewers next
- `plugin-dev:skill-reviewer` on `lore-development/skills/distill/SKILL.md` (structural).
- `fresh-lore` (or equivalent fresh-context check) cross-checking SKILL.md against `.lore/brainstorm/distill-function.md` for shape-rule preservation and absence of spec-replacement ambition.
