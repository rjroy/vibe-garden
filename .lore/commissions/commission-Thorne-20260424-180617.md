---
title: "Commission: Lore-redesign Phase 4: review /distill rewrite"
date: 2026-04-25
status: completed
tags: [commission]
worker: Thorne
workerDisplayTitle: "Guild Warden"
prompt: "Review Phase 4 of the lore-development three-directory redesign — the `/excavate` → `/distill` rename and SKILL.md rewrite. This review combines two perspectives the plan calls for: structural skill-quality (plugin-dev:skill-reviewer style) and brainstorm-fidelity (fresh-lore style). Use both lenses.\n\nPredecessor commission: `commission-Dalton-20260424-180556` (Phase 4 build). Read its result body first.\n\nAuthoritative sources:\n- Plan: `.lore/plans/lore-redesign.md` (Phase 4, ~lines 229–266)\n- Spec: `.lore/specs/lore-redesign.md` — REQ-REDESIGN-26 through 33\n- **Brainstorm (binding)**: `.lore/brainstorm/distill-function.md` — read in full. The SKILL.md must honor this brainstorm's shape rule and null-output-valid stance without reintroducing spec-replacement ambition.\n\nWhat to inspect:\n\n**Structural / skill-quality lens** (plugin-dev:skill-reviewer style):\n- `lore-development/skills/distill/SKILL.md` — frontmatter (`name: distill`, trigger phrases, description). Body is structured for an LLM reader: clear modes, clear steps, no contradictions, no buried instructions. Use the plugin-dev:skill-reviewer subagent if available via Task; otherwise apply its discipline directly.\n- Skill-reviewer-style checks: description is specific enough to trigger reliably; no vague trigger words; modes (`code` vs `build`) are clearly delineated; verification examples are self-contained.\n\n**Brainstorm-fidelity lens** (fresh-lore style):\n- Does the rewritten SKILL.md preserve `.lore/brainstorm/distill-function.md`'s shape rule (reference contains only what code cannot say)?\n- Is null output framed as valid (REQ-REDESIGN-30)? No template pressure?\n- Does build mode actually surface seed-vs-code mismatches explicitly (REQ-REDESIGN-28)?\n- Does it support updating existing reference files when code drifts (REQ-REDESIGN-31), not just append-only writes?\n- Has the rewrite reintroduced any spec-replacement ambition? (Distill's job is reference docs, not specs.)\n\n**Migration completeness**:\n- Directory renamed `excavate/` → `distill/`?\n- `lore-development/agents/surface-surveyor.md` — `/lore-development:excavate` invocation updated to `/lore-development:distill`?\n- `lore-development/skills/tend/SKILL.md` — soft distill-before-archive prompt hook landed in the `directories` archive flow (REQ-REDESIGN-33 with the plan's adopted soft-prompt decision)? Verify it's a soft prompt — user can decline and archival still proceeds.\n- `lore-development/skills/tend/references/status.md` — archive logic note added for `status: implemented` specs?\n- `lore-development/README.md` — skill list shows `distill`, not `excavate`?\n- `.claude-plugin/marketplace.json` — if it references skills, updated; if it doesn't, ignore.\n- Excavation index moved to `.lore/build/excavations/index.md` (REQ-REDESIGN-32)?\n\n**Anti-checks**:\n- Grep `lore-development/` for `excavate` — any remaining hit must be intentional migration documentation.\n- Anti-template: SKILL.md does not demand a count of candidates.\n- Anti-assertion: SKILL.md does not pre-scan or assert candidates without user confirmation.\n\nOut of scope (do not flag):\n- Phase 3 `/tend migrate` (already reviewed).\n- Phase 5/6 work (later).\n\nFindings format: severity (blocker / fix-now / nit), file:line, fix description. Capture in your commission result body. Next commission is a Dalton fix that addresses every finding."
dependencies:
  - commission-Dalton-20260424-180556
linked_artifacts:
  - lore-development/skills/distill/SKILL.md

  - lore-development/agents/surface-surveyor.md
  - lore-development/skills/tend/SKILL.md
  - lore-development/skills/tend/references/status.md
  - lore-development/skills/tend/references/directories.md
  - lore-development/README.md
  - lore-development/shared/frontmatter-schema.md
  - lore-development/agents/surface-surveyor.md
  - lore-development/skills/tend/SKILL.md
  - lore-development/skills/tend/references/status.md
  - lore-development/skills/tend/references/directories.md
  - lore-development/README.md
  - lore-development/shared/frontmatter-schema.md
activity_timeline:
  - timestamp: 2026-04-25T01:06:17.547Z
    event: created
    reason: "Commission created"
  - timestamp: 2026-04-25T01:06:17.549Z
    event: status_blocked
    reason: "Dependencies not satisfied"
    from: "pending"
    to: "blocked"
  - timestamp: 2026-04-25T04:42:16.072Z
    event: status_pending
    reason: "Dependencies satisfied"
    from: "blocked"
    to: "pending"
  - timestamp: 2026-04-25T04:42:16.075Z
    event: status_dispatched
    reason: "Dispatched to worker"
    from: "pending"
    to: "dispatched"
  - timestamp: 2026-04-25T04:42:16.092Z
    event: status_in_progress
    reason: "Execution started"
    from: "dispatched"
    to: "in_progress"
  - timestamp: 2026-04-25T04:42:37.130Z
    event: progress_report
    reason: "Read commission, plan Phase 4, distill brainstorm, and spec REQ-REDESIGN-26..33. Now reviewing actual SKILL.md and migration touchpoints."
  - timestamp: 2026-04-25T04:45:38.598Z
    event: progress_report
    reason: "Reviewed all touchpoints. SKILL.md is brainstorm-faithful and structurally sound. One fix-now: directories.md missing the archive-flow soft-prompt hook. Submitting result."
  - timestamp: 2026-04-25T04:46:45.291Z
    event: result_submitted
    reason: "Phase 4 review complete. The rewritten `distill/SKILL.md` is brainstorm-faithful, structurally sound, and free of spec-replacement ambition. Migration is mostly complete. One fix-now finding around the soft-prompt integration; two nits in user-facing prose; one note on audit method.\n\n## Verdict\n\n**Pass with one fix-now.** The SKILL.md body itself needs no changes. The fix sits in `tend/references/directories.md`.\n\n## Findings\n\n### Fix-now\n\n**1. `lore-development/skills/tend/references/directories.md` — soft distill-before-archive prompt missing from the directories archive flow.**\n\nREQ-REDESIGN-33 (verbatim): \"/tend's archive logic is updated: a spec with `status: implemented` is surfaced as a distill candidate (prompt 'Distill this spec before archiving?') before it can be archived.\"\n\nThe plan adopted this as a soft prompt and the new section landed in `tend/SKILL.md` (lines 33–43) and as a one-line note in `tend/references/status.md` (line 53). It did **not** land in `tend/references/directories.md` — which is the reference file the LLM loads when `/tend directories` actually runs (`tend/SKILL.md:67–73` maps each mode to its own reference, and the archive flow physically lives in directories.md, not status.md).\n\nConcretely:\n- `directories.md:124–138` \"Archive Candidates\" lists \"Status: implemented + related retro exists\" with no mention of the prompt.\n- `directories.md:191–208` \"Applying Changes\" describes the apply pipeline (create → move → update related → update links → remove) with no prompt step for implemented specs.\n- `status.md:49–53` flags the coupling but its archive-coupling note correctly describes a behavior triggered \"by `directories` mode\" — directories.md is the file responsible for that behavior.\n\nMitigation: the prompt section in `tend/SKILL.md` will be in context whenever any tend mode runs, so the prompt is not invisible. But operational guidance lives in the per-mode reference, and directories.md's archive table and apply flow are silent on the coupling. Whether the prompt fires reliably depends on the LLM bridging two reference files at runtime.\n\n**Fix**: in `directories.md`, add a row to the \"Archive Candidates\" table (around line 132) calling out implemented specs as the distill-prompt case, and add a step in \"Applying Changes\" (around line 197) that runs the soft prompt before archiving any `status: implemented` spec. Cross-reference `lore-development/skills/distill/SKILL.md` and the SKILL.md prompt section by name.\n\nDalton's edge-case decision #4 explicitly punted directories.md (\"commission did not list it\"). The literal commission file list did not name it, but the spec named the mode and the plan named the archive flow. The miss is a scope-call gap, not an oversight in the rewrite itself.\n\n### Nits\n\n**2. `lore-development/README.md:50` — stale \"Excavated feature documentation\" descriptor.**\n\nIn the legacy `.lore/` storage tree (lines 42–56), line 50 reads:\n```\n├── reference/      # Excavated feature documentation\n```\n\nThe skill is renamed to `/distill`. The descriptor \"Excavated feature documentation\" describes the renamed skill's old name. Acknowledged scope: Dalton's edge-case decision #2 left this whole tree untouched on the grounds that the tree itself uses the old single-level layout (research/, brainstorm/, specs/, plans/, retros/, stubs/, reference/, excavations/, diagrams/, issues/, ideas.md) and is owed a Phase-6 rewrite. That's a reasonable scope call, but the inline descriptor is rename-debt that the next phase needs to clean up. Track it.\n\n**3. `lore-development/agents/surface-surveyor.md:348, 352, 362` — \"Layer 2 (Feature Extraction)\" residue.**\n\nThe agent description and Invocation Context (lines 1–17) were correctly updated to point to `/lore-development:distill`. The output-format example still ends with:\n\n- line 348: \"### Questions for Layer 2\"\n- line 352: \"## Suggested Focus Areas for Layer 2\"\n- line 362: \"*Ready for human review. Proceed to Layer 2 (Feature Extraction) after confirmation.*\"\n\n\"Layer 2 (Feature Extraction)\" is residual vocabulary from the old layered excavate model. The renamed skill does not advertise itself as Layer 2 of anything. The output template instructs callers (or a downstream prompt) to \"proceed to Layer 2,\" which now points at nothing under that name. Either rename to \"next pass / distill\" framing, or remove the layered framing entirely. Not blocking; the agent still functions and surface-survey output is consumed by `/distill code` regardless of the label.\n\n**4. `lore-development/shared/frontmatter-schema.md:10, 257` — surviving \"Excavated\" descriptors.**\n\n- line 10: \"**`.lore/reference/`** — solidified, system-oriented documentation. What the code cannot say. Excavated feature docs, vision, current-state diagrams.\"\n- line 257: \"### Reference (Excavated Feature)\"\n\nOut of Phase 4's literal scope (frontmatter-schema.md is REQ-REDESIGN-8, owned by an earlier phase). Flagged because the rename should sweep these up wherever they live. If schema rewrite is complete in an earlier landed phase, this is genuine drift caused by Phase 4's rename and should be folded into a follow-up.\n\n### Note (not a finding, audit-quality observation)\n\nDalton's grep audit was `\\bexcavate\\b` — verb-only. That regex matches `excavate` but not `excavated`, `excavating`, or `Excavation` (the next character `d` / `i` / etc. is a word character, so `\\b` does not fire after `excavate`). The broader `\\bexcavat` audit Dalton ran did surface the survivors but the report classified all of them as \"intentional.\" On re-inspection, items 2 and 4 above are not intentional — they are user-facing prose that still names the renamed skill. For the next rename audit, the regex should be `excavat[a-z]*` (or similar) and survivors should be triaged individually rather than as a class.\n\n## Brainstorm-fidelity check (passes)\n\nVerified `lore-development/skills/distill/SKILL.md` against `.lore/brainstorm/distill-function.md`:\n\n- **Shape rule** (`.md:35–55`) preserves the brainstorm's \"Reference contains only what the code cannot tell you. Not function signatures. Not endpoint lists.\" Cites the brainstorm by path at line 55.\n- **Null output is valid** (`.md:57–61`) matches the brainstorm's \"Null output is valid\" + capture-skills principle 1. Cites principles brainstorm at line 61.\n- **Core operation** (`.md:63–83`) follows the brainstorm's six-step loop (read seed → verify → apply shape rule → present reconciled candidates → user gates → update index).\n- **Build-seed mismatch handling** (`.md:85–95`) honors the brainstorm's \"When the seed disagrees with the code, surface the mismatch explicitly. Do not silently rewrite.\" The four mismatch interpretations match the brainstorm's framing.\n- **Reference is living** (`.md:97–107`) preserves \"Reference docs are living. Distill revises to match current code rather than appending history.\" `current → outdated → current` flow is captured.\n- **Excavation index path** (`.md:83, 140–165`) at `.lore/build/excavations/index.md` per REQ-REDESIGN-32. The three sub-tables (Distilled Areas / Identified, Not Yet Distilled / Unexplored Entry Points) match the spec's three categories.\n\nNo spec-replacement ambition reintroduced. Nothing in the SKILL.md frames distill as producing spec-equivalents.\n\n## Structural / skill-quality check (passes)\n\n- Frontmatter `name: distill` ✓\n- Trigger phrases include `/distill`, `/distill code`, `/distill build`, plus natural-language triggers for both seeds (\"promote to reference\", \"what should be in reference for X\", \"refresh the reference docs\", \"this spec has invariants worth keeping\") — specific enough to fire reliably without colliding with adjacent skills.\n- Modes table at lines 13–19 cleanly separates `code` and `build` seeds with crisp \"Use when\" guidance.\n- Invocation block (lines 22–33) is self-documenting; both modes have concrete examples.\n- No buried instructions; the body reads top-to-bottom.\n- Anti-template: \"There is no template that asks for N items\" appears at line 61. No \"list N candidates\", \"at least N\", \"exactly N\" pressure anywhere.\n- Anti-assertion: line 183 explicitly says \"Confirm the seed file with the user before scanning. Do not pre-scan or volunteer candidates.\"\n- Verification Pass section (lines 198–206) closes with concrete user-gate-and-grep discipline.\n\n## Migration completeness check (passes except nit #1 territory)\n\n- Directory renamed `excavate/` → `distill/` ✓ (verified by Read on the new path; Dalton's report cites `git mv`).\n- `agents/surface-surveyor.md:17` invocation reference updated to `/lore-development:distill (code mode)` ✓ (modulo the Layer 2 residue, finding #3).\n- `tend/SKILL.md:33–43` soft prompt section landed ✓. Three-option flow (yes / no / skip) preserves user agency. The \"skip\" option is slightly broader than the plan's binary \"user answers, archive proceeds either way\" but is consistent with the soft-prompt principle (skip leaves the file in place for this run only — user can still decline distill via \"no\" and archive proceeds).\n- `tend/references/status.md:53` archive-coupling note added ✓.\n- `README.md:25` skill table shows `/distill` ✓. `README.md:117–119` \"Distilling existing code\" workflow paragraph rewritten ✓. `README.md:165` \"Human checkpoints\" principle line updated ✓.\n- `back-propagate/SKILL.md` and `update-lore-agents/SKILL.md` updated ✓ (caught by Dalton beyond the literal commission file list).\n- `marketplace.json` confirmed not skill-aware; no change needed ✓.\n- Excavation index path: `.lore/build/excavations/index.md` per REQ-REDESIGN-32 ✓.\n\n## What the next Dalton commission should fix\n\n1. **directories.md** — add the soft prompt to the archive flow (table row + apply step). This is the only fix-now.\n2. **README.md:50** — descriptor cleanup (\"Excavated feature documentation\" → \"Distilled reference documentation\" or similar). Track for the Phase-6 tree rewrite if scope-bundled.\n3. **surface-surveyor.md:348, 352, 362** — \"Layer 2 (Feature Extraction)\" residue. Either drop the layered framing or rename to current vocabulary.\n4. **frontmatter-schema.md:10, 257** — fold into whichever phase owns schema rewrite.\n5. (Audit) — for any future rename, broaden the grep to `excavat[a-z]*` (or the equivalent for the next rename) and triage survivors individually."
  - timestamp: 2026-04-25T04:46:50.176Z
    event: status_completed
    reason: "Execution completed"
    from: "in_progress"
    to: "completed"
current_progress: "Reviewed all touchpoints. SKILL.md is brainstorm-faithful and structurally sound. One fix-now: directories.md missing the archive-flow soft-prompt hook. Submitting result."
projectName: vibe-garden
---
Phase 4 review complete. The rewritten `distill/SKILL.md` is brainstorm-faithful, structurally sound, and free of spec-replacement ambition. Migration is mostly complete. One fix-now finding around the soft-prompt integration; two nits in user-facing prose; one note on audit method.

## Verdict

**Pass with one fix-now.** The SKILL.md body itself needs no changes. The fix sits in `tend/references/directories.md`.

## Findings

### Fix-now

**1. `lore-development/skills/tend/references/directories.md` — soft distill-before-archive prompt missing from the directories archive flow.**

REQ-REDESIGN-33 (verbatim): "/tend's archive logic is updated: a spec with `status: implemented` is surfaced as a distill candidate (prompt 'Distill this spec before archiving?') before it can be archived."

The plan adopted this as a soft prompt and the new section landed in `tend/SKILL.md` (lines 33–43) and as a one-line note in `tend/references/status.md` (line 53). It did **not** land in `tend/references/directories.md` — which is the reference file the LLM loads when `/tend directories` actually runs (`tend/SKILL.md:67–73` maps each mode to its own reference, and the archive flow physically lives in directories.md, not status.md).

Concretely:
- `directories.md:124–138` "Archive Candidates" lists "Status: implemented + related retro exists" with no mention of the prompt.
- `directories.md:191–208` "Applying Changes" describes the apply pipeline (create → move → update related → update links → remove) with no prompt step for implemented specs.
- `status.md:49–53` flags the coupling but its archive-coupling note correctly describes a behavior triggered "by `directories` mode" — directories.md is the file responsible for that behavior.

Mitigation: the prompt section in `tend/SKILL.md` will be in context whenever any tend mode runs, so the prompt is not invisible. But operational guidance lives in the per-mode reference, and directories.md's archive table and apply flow are silent on the coupling. Whether the prompt fires reliably depends on the LLM bridging two reference files at runtime.

**Fix**: in `directories.md`, add a row to the "Archive Candidates" table (around line 132) calling out implemented specs as the distill-prompt case, and add a step in "Applying Changes" (around line 197) that runs the soft prompt before archiving any `status: implemented` spec. Cross-reference `lore-development/skills/distill/SKILL.md` and the SKILL.md prompt section by name.

Dalton's edge-case decision #4 explicitly punted directories.md ("commission did not list it"). The literal commission file list did not name it, but the spec named the mode and the plan named the archive flow. The miss is a scope-call gap, not an oversight in the rewrite itself.

### Nits

**2. `lore-development/README.md:50` — stale "Excavated feature documentation" descriptor.**

In the legacy `.lore/` storage tree (lines 42–56), line 50 reads:
```
├── reference/      # Excavated feature documentation
```

The skill is renamed to `/distill`. The descriptor "Excavated feature documentation" describes the renamed skill's old name. Acknowledged scope: Dalton's edge-case decision #2 left this whole tree untouched on the grounds that the tree itself uses the old single-level layout (research/, brainstorm/, specs/, plans/, retros/, stubs/, reference/, excavations/, diagrams/, issues/, ideas.md) and is owed a Phase-6 rewrite. That's a reasonable scope call, but the inline descriptor is rename-debt that the next phase needs to clean up. Track it.

**3. `lore-development/agents/surface-surveyor.md:348, 352, 362` — "Layer 2 (Feature Extraction)" residue.**

The agent description and Invocation Context (lines 1–17) were correctly updated to point to `/lore-development:distill`. The output-format example still ends with:

- line 348: "### Questions for Layer 2"
- line 352: "## Suggested Focus Areas for Layer 2"
- line 362: "*Ready for human review. Proceed to Layer 2 (Feature Extraction) after confirmation.*"

"Layer 2 (Feature Extraction)" is residual vocabulary from the old layered excavate model. The renamed skill does not advertise itself as Layer 2 of anything. The output template instructs callers (or a downstream prompt) to "proceed to Layer 2," which now points at nothing under that name. Either rename to "next pass / distill" framing, or remove the layered framing entirely. Not blocking; the agent still functions and surface-survey output is consumed by `/distill code` regardless of the label.

**4. `lore-development/shared/frontmatter-schema.md:10, 257` — surviving "Excavated" descriptors.**

- line 10: "**`.lore/reference/`** — solidified, system-oriented documentation. What the code cannot say. Excavated feature docs, vision, current-state diagrams."
- line 257: "### Reference (Excavated Feature)"

Out of Phase 4's literal scope (frontmatter-schema.md is REQ-REDESIGN-8, owned by an earlier phase). Flagged because the rename should sweep these up wherever they live. If schema rewrite is complete in an earlier landed phase, this is genuine drift caused by Phase 4's rename and should be folded into a follow-up.

### Note (not a finding, audit-quality observation)

Dalton's grep audit was `\bexcavate\b` — verb-only. That regex matches `excavate` but not `excavated`, `excavating`, or `Excavation` (the next character `d` / `i` / etc. is a word character, so `\b` does not fire after `excavate`). The broader `\bexcavat` audit Dalton ran did surface the survivors but the report classified all of them as "intentional." On re-inspection, items 2 and 4 above are not intentional — they are user-facing prose that still names the renamed skill. For the next rename audit, the regex should be `excavat[a-z]*` (or similar) and survivors should be triaged individually rather than as a class.

## Brainstorm-fidelity check (passes)

Verified `lore-development/skills/distill/SKILL.md` against `.lore/brainstorm/distill-function.md`:

- **Shape rule** (`.md:35–55`) preserves the brainstorm's "Reference contains only what the code cannot tell you. Not function signatures. Not endpoint lists." Cites the brainstorm by path at line 55.
- **Null output is valid** (`.md:57–61`) matches the brainstorm's "Null output is valid" + capture-skills principle 1. Cites principles brainstorm at line 61.
- **Core operation** (`.md:63–83`) follows the brainstorm's six-step loop (read seed → verify → apply shape rule → present reconciled candidates → user gates → update index).
- **Build-seed mismatch handling** (`.md:85–95`) honors the brainstorm's "When the seed disagrees with the code, surface the mismatch explicitly. Do not silently rewrite." The four mismatch interpretations match the brainstorm's framing.
- **Reference is living** (`.md:97–107`) preserves "Reference docs are living. Distill revises to match current code rather than appending history." `current → outdated → current` flow is captured.
- **Excavation index path** (`.md:83, 140–165`) at `.lore/build/excavations/index.md` per REQ-REDESIGN-32. The three sub-tables (Distilled Areas / Identified, Not Yet Distilled / Unexplored Entry Points) match the spec's three categories.

No spec-replacement ambition reintroduced. Nothing in the SKILL.md frames distill as producing spec-equivalents.

## Structural / skill-quality check (passes)

- Frontmatter `name: distill` ✓
- Trigger phrases include `/distill`, `/distill code`, `/distill build`, plus natural-language triggers for both seeds ("promote to reference", "what should be in reference for X", "refresh the reference docs", "this spec has invariants worth keeping") — specific enough to fire reliably without colliding with adjacent skills.
- Modes table at lines 13–19 cleanly separates `code` and `build` seeds with crisp "Use when" guidance.
- Invocation block (lines 22–33) is self-documenting; both modes have concrete examples.
- No buried instructions; the body reads top-to-bottom.
- Anti-template: "There is no template that asks for N items" appears at line 61. No "list N candidates", "at least N", "exactly N" pressure anywhere.
- Anti-assertion: line 183 explicitly says "Confirm the seed file with the user before scanning. Do not pre-scan or volunteer candidates."
- Verification Pass section (lines 198–206) closes with concrete user-gate-and-grep discipline.

## Migration completeness check (passes except nit #1 territory)

- Directory renamed `excavate/` → `distill/` ✓ (verified by Read on the new path; Dalton's report cites `git mv`).
- `agents/surface-surveyor.md:17` invocation reference updated to `/lore-development:distill (code mode)` ✓ (modulo the Layer 2 residue, finding #3).
- `tend/SKILL.md:33–43` soft prompt section landed ✓. Three-option flow (yes / no / skip) preserves user agency. The "skip" option is slightly broader than the plan's binary "user answers, archive proceeds either way" but is consistent with the soft-prompt principle (skip leaves the file in place for this run only — user can still decline distill via "no" and archive proceeds).
- `tend/references/status.md:53` archive-coupling note added ✓.
- `README.md:25` skill table shows `/distill` ✓. `README.md:117–119` "Distilling existing code" workflow paragraph rewritten ✓. `README.md:165` "Human checkpoints" principle line updated ✓.
- `back-propagate/SKILL.md` and `update-lore-agents/SKILL.md` updated ✓ (caught by Dalton beyond the literal commission file list).
- `marketplace.json` confirmed not skill-aware; no change needed ✓.
- Excavation index path: `.lore/build/excavations/index.md` per REQ-REDESIGN-32 ✓.

## What the next Dalton commission should fix

1. **directories.md** — add the soft prompt to the archive flow (table row + apply step). This is the only fix-now.
2. **README.md:50** — descriptor cleanup ("Excavated feature documentation" → "Distilled reference documentation" or similar). Track for the Phase-6 tree rewrite if scope-bundled.
3. **surface-surveyor.md:348, 352, 362** — "Layer 2 (Feature Extraction)" residue. Either drop the layered framing or rename to current vocabulary.
4. **frontmatter-schema.md:10, 257** — fold into whichever phase owns schema rewrite.
5. (Audit) — for any future rename, broaden the grep to `excavat[a-z]*` (or the equivalent for the next rename) and triage survivors individually.

## Decisions

**Does directories.md integrate the REQ-REDESIGN-33 soft prompt where archive logic actually lives?**
No. The soft prompt is in tend/SKILL.md (lines 33–43) and tend/references/status.md (line 53), but directories.md — the operational reference loaded when `/tend directories` runs — has no mention. Its Archive Candidates table (124–138) and Applying Changes flow (191–208) are unchanged. fix-now.
*Reasoning: REQ-REDESIGN-33 names `directories` mode as the locus. tend/SKILL.md line 67–73 loads `references/<mode>.md` as the operational guide. status.md is loaded only when `status` mode runs — by the time `directories` mode is processing archive candidates, the LLM has SKILL.md + directories.md in context. SKILL.md carries the prompt at the top, so the prompt is not invisible, but the archive flow inside directories.md never points at it. Dalton's edge-case #4 explicitly punted directories.md ("commission did not list it"). The plan and the spec did.*

**Is the SKILL.md body faithful to .lore/brainstorm/distill-function.md without reintroducing spec-replacement ambition?**
Yes. Shape rule (lines 35–55) cites the brainstorm verbatim in spirit; null-output section (57–61) cites principles-for-capture-skills principle 1; build-seed mismatch (85–95), living updates (97–107), and excavation-index (140–165) all match the brainstorm. No spec-replacement language anywhere.
*Reasoning: Cross-checked SKILL.md against brainstorm sections "The shape rule for reference," "Output characteristics," "Core operation," "Reference docs are living," and "What feeds distill build, in order of expected yield." All preserved. The brainstorm's explicit reframe ("excavate's spec-replacement ambition is gone") is honored — the SKILL.md never frames distill as producing spec-equivalents.*

**Did Dalton's grep audit catch all stale rename references?**
No. The audit `\bexcavate\b` is verb-only; it misses "Excavated" / "excavating" / "Excavation" forms. Two stale descriptors remain in user-facing prose: README.md:50 "Excavated feature documentation" and shared/frontmatter-schema.md:10 + 257 ("Excavated feature docs", "Reference (Excavated Feature)").
*Reasoning: README's storage tree at lines 42–56 is the old single-level layout deferred to a later phase per Dalton's edge-case #2. The descriptor on line 50 is therefore in deferred territory. frontmatter-schema.md is owned by Phase 1 (REQ-REDESIGN-8). Both are out of Phase 4's literal scope but are real consistency drift caused by the rename. Nit-level findings — flag for follow-up phase, not Phase 4 blockers.*
