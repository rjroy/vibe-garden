---
title: "Implementation plan: lore-development three-directory redesign"
date: 2026-04-24
status: draft
tags: [plan, lore-development, directory-structure, capture-skills, refactor]
modules: [lore-development]
related:
  - .lore/specs/lore-redesign.md
  - .lore/brainstorm/lore-directory-redesign.md
  - .lore/brainstorm/principles-for-capture-skills.md
  - .lore/brainstorm/distill-function.md
  - .lore/brainstorm/learn-dialog.md
  - .lore/issues/roadmap-lore-redesign.md
---

# Plan: Lore-development three-directory redesign

## Spec Reference

**Spec**: `.lore/specs/lore-redesign.md`

Requirements map to phases:

| Requirement | Subject | Phase |
|-------------|---------|-------|
| REQ-REDESIGN-1 – 5 | Directory structure canon, vision move, diagram split rule | 0, 1 |
| REQ-REDESIGN-6 – 7 | Path migration table, idea-queue exception | 1 |
| REQ-REDESIGN-8 – 13 | Frontmatter schema + status collapse | 0 |
| REQ-REDESIGN-14 – 17 | `/retro` reshape + pointer-note fallback | 5 |
| REQ-REDESIGN-18 – 25 | `/tend migrate` + non-migrate mode updates | 3 |
| REQ-REDESIGN-26 – 33 | `/excavate` → `/distill` refactor + tend archive gating | 4 |
| REQ-REDESIGN-34 – 41 | `/learn` new skill | 5 |
| REQ-REDESIGN-42 – 45 | Agent description updates (incl. Celeste cross-plugin) | 2, 6 |
| REQ-REDESIGN-46 – 48 | SKILL.md hardcoded-path audit, tend references, plugin README | 1, 3, 6 |

## Codebase Context

**Plugin surface** (`lore-development/`):

- **20 skills** under `lore-development/skills/`: `back-propagate`, `brainstorm`, `ddp`, `define-validation`, `design`, `excavate`, `file-issue`, `implement`, `plan-breakdown`, `poke-holes`, `prep-plan`, `research`, `retro`, `review-ideas`, `simplify`, `specify`, `tend`, `update-lore-agents`, `update-stubs`, `vision`.
- **6 agents** under `lore-development/agents/`: `design-reviewer.md`, `fresh-lore.md`, `lore-researcher.md`, `plan-reviewer.md`, `spec-reviewer.md`, `surface-surveyor.md`.
- **Shared schema** at `lore-development/shared/frontmatter-schema.md` — cited by most skills via `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`.
- **Scripts** under `lore-development/scripts/`: `frontmatter_schema.py` (machine-readable schema used by `validate_frontmatter.py`), `validate_frontmatter.py` (consumed by `/tend status`), `idea_hook.py` (writes to `.lore/ideas/`), plus a `tests/` dir.
- **Hooks**: `lore-development/hooks/hooks.json` (wires the idea hook).
- **Tend references**: `lore-development/skills/tend/references/{directories,status,filenames,tags,lore-config}.md` — consumed by the tend orchestrator.

**Cross-plugin touchpoint**: Celeste lives in guild-hall (outside `lore-development/`). Her description references `.lore/vision.md` and needs to move to `.lore/reference/vision.md` (REQ-REDESIGN-45). Spec constraint: this is the only cross-plugin change required.

**Existing validation harness**: `lore-development/scripts/validate_frontmatter.py` is already wired into `/tend status`. It consumes `frontmatter_schema.py` which encodes per-directory statuses. The schema collapse (REQ-REDESIGN-9) and the directory rename (REQ-REDESIGN-6) both alter this script's inputs.

**Already-migrated exemplar**: `lore-development/skills/excavate/SKILL.md` already has `artifact_path: .lore/reference` in frontmatter — reference is the one pre-existing directory that stays put. Everything else moves under `build/`.

**Pre-migration state of this repo's `.lore/`**: old-layout directories present at `.lore/{brainstorm,specs,plans,design,research,retros,issues,commissions,ideas,diagrams,excavations,tasks,notes,stubs,validation}/` plus `.lore/vision.md`. This repo is the canonical end-to-end fixture for `/tend migrate`.

## Phasing strategy

The refactor breaks into **6 phases** grouped into **3 follow-on commissions**. Each phase fits in a single context window. Each commission absorbs 2 phases.

- **Commission A** — Phases 0, 1, 2 (foundation + path fan-out + agent updates). Phase 0 gates Phases 1 and 2. Review gate between foundation and fan-out is load-bearing.
- **Commission B** — Phases 3, 4 (`/tend migrate` new mode + `/distill` rename/reshape). Both introduce substantive new behavior; each needs its own context.
- **Commission C** — Phases 5, 6 (`/learn` + `/retro` coupled pair, then cross-plugin touch + full audit).

**Foundation → fan-out principle.** Phase 0 rewrites the schema every other phase cites. If Phase 1 runs against an unreviewed schema, mistakes propagate 18 files deep before anyone notices. Thorne reviews Phase 0 output before Phase 1 begins — gate is explicit, not informal.

**Coupling constraint (roadmap step 2/3).** `/learn` must ship at-or-before `/retro`'s strip. Phase 5 ships them together. If implementation splits them mid-phase, the fallback is REQ-REDESIGN-17's pointer note in the reshaped `/retro`.

**Release atomicity.** `/tend migrate` (Phase 3) must be present in the released plugin version alongside the path migrations (Phases 1, 4, 5). Development order within the plan can land Phase 1 before Phase 3 — acceptable because no user sees partial state until the full set merges.

## Implementation Steps

### Phase 0 — Foundation: schema + directory canon

**Files**:
- `lore-development/shared/frontmatter-schema.md` (rewrite)
- `lore-development/scripts/frontmatter_schema.py` (regenerate per-directory status sets)
- `lore-development/scripts/tests/test_frontmatter_schema.py` (update fixtures)
- `lore-development/skills/tend/references/directories.md` (rewrite standard-directory list)
- `lore-development/skills/tend/references/status.md` (align with new status sets)
- `lore-development/skills/tend/references/lore-config.md` (read for old-layout assumptions; update if custom-directory registration convention changed)
- `lore-development/scripts/tests/fixtures/` (reorganize into `fixtures/build/`, `fixtures/reference/`, `fixtures/learned/` subtrees)

**Addresses**: REQ-REDESIGN-1, 2, 3 (canon), REQ-REDESIGN-8, 9, 10, 11, 12, 13 (schema), REQ-REDESIGN-47 (tend references).

**Expertise**: none specialized — schema editing + Python fixture updates.

**What to do**:

1. Rewrite `shared/frontmatter-schema.md` per REQ-REDESIGN-9. Three status sets keyed to directory:
   - Build: per-type lifecycle retained (brainstorm `open/parked/resolved/archived`, spec `draft/approved/implemented/superseded/archived`, design same, plan `draft/approved/executed/archived`, task `pending/complete/skipped`, notes `in_progress/complete/archived`, research `active/archived`, retro `open/archived` — note `complete` is collapsed out, REQ-REDESIGN-9, REQ-REDESIGN-14), issue `open/resolved/wontfix/archived`.
   - Reference: `current`, `outdated`, `archived`.
   - Learned: `active`, `superseded`.
2. Update the "Additional Status Values by Document Type" table to map to `build/`, `reference/`, `learned/` subdirectories.
3. Update the vision section: vision lives at `.lore/reference/vision.md`, statuses `current` / `outdated` / `archived` (it becomes a reference document).
4. Retain `req-prefix` (REQ-REDESIGN-10), notes-`source` and task-`source`+`sequence` (REQ-REDESIGN-11). Paths inside these values use the new tree. Update the in-file examples.
5. Regenerate `frontmatter_schema.py` to match: per-directory status sets, path constants pointing at `.lore/build/*`, `.lore/reference/*`, `.lore/learned/*`. Keep the comment trail back to the schema document.
6. Update `lore-development/scripts/tests/test_frontmatter_schema.py`. The existing `SCHEMA_DOCUMENT_TYPES` list hardcodes old-layout keys (`brainstorm`, `specs`, `design`, `retros`, `research`, `diagrams`, `plans`, `notes`, `tasks`, `reference`, `issues`) and will fail `test_every_document_type_has_entry` as soon as `frontmatter_schema.py` is rewritten. Update this list to the new keyset (`build/brainstorm`, `build/specs`, ..., `reference`, `learned`) or whatever keying convention the rewritten schema adopts. Also reorganize `lore-development/scripts/tests/fixtures/` into `fixtures/build/`, `fixtures/reference/`, `fixtures/learned/` subtrees so the fixture-tree validation step below can run.
7. Update `validate_frontmatter.py` path expectations if it hardcodes directory names beyond `frontmatter_schema.py`.
8. Rewrite `tend/references/directories.md` to enumerate the new standard directories (`.lore/build/*`, `.lore/reference/*`, `.lore/learned/*`). Flag legacy top-levels (old 13) as orphans with a pointer to `/tend migrate`. Update the "note on `.lore/ideas/`" to `.lore/build/ideas/`.
9. Update `tend/references/status.md` to reflect the new per-directory status sets.
10. Read `tend/references/lore-config.md`. If it describes custom-directory registration relative to the old layout, update accordingly. REQ-REDESIGN-24 relies on this file for the `/tend migrate` skip list.

**Verification**:
- `pytest lore-development/scripts/tests/test_frontmatter_schema.py` passes.
- `python lore-development/scripts/validate_frontmatter.py` runs against a fixture tree containing samples of each document type in the new layout and reports clean.
- Grep `lore-development/shared/frontmatter-schema.md` for `.lore/` paths — every occurrence uses the new tree or explicitly documents an exception.

**Review gate** (MANDATORY before Phase 1/2 begin):
- **Thorne** reviews the schema rewrite + Python changes for: status-set correctness against REQ-REDESIGN-9, path-constant consistency, test fixture coverage, and unintended omissions.
- Gate closes when Thorne signs off. Fan-out phases do not start until this gate is closed.

### Phase 1 — Path string fan-out across skills

**Files** (SKILL.md for each, plus the idea hook):
- `lore-development/skills/{brainstorm,specify,design,prep-plan,plan-breakdown,implement,simplify,research,file-issue,review-ideas,define-validation,update-stubs,back-propagate,ddp,vision,poke-holes}/SKILL.md`
- `lore-development/skills/retro/SKILL.md` — path strings only, content reshape deferred to Phase 5
- `lore-development/skills/excavate/SKILL.md` — excavation-index path only, full rename/reshape deferred to Phase 4
- `lore-development/scripts/idea_hook.py` — writes to `.lore/build/ideas/`
- `lore-development/skills/update-lore-agents/SKILL.md` — verify for any hardcoded paths

**Addresses**: REQ-REDESIGN-4, 6, 7, REQ-REDESIGN-46 (SKILL.md path audit).

**Expertise**: none specialized. Mechanical but bulk. Bounded scope: path strings only, no behavioral or content restructure in this phase.

**What to do**:

For each SKILL.md, walk the migration table (REQ-REDESIGN-6) and update:
- Output paths in prose (`Save to .lore/X/` → `Save to .lore/build/X/`).
- Example paths in frontmatter snippets.
- Cross-references to sibling skills' output directories.
- Example `related:` and `source:` values.
- Example markdown links in skill-authored document templates.

Idea hook: change the write path from `.lore/ideas/` to `.lore/build/ideas/`. Update hook docstrings.

Explicitly **do not** touch:
- `retro/SKILL.md` body content (reshape is Phase 5).
- `excavate/SKILL.md` command name, directory name, or content (rename is Phase 4).
- Agent descriptions in `lore-development/agents/` (Phase 2 owns these).
- Celeste agent (Phase 6 owns this).

REQ-REDESIGN-7: `/review-ideas` skill's handling of `.lore/build/ideas/` as frontmatter-free queue is unchanged. Its prose paths get updated; its semantics do not.

REQ-REDESIGN-5: `/ddp` gains the split-by-purpose dialog (build vs reference diagrams, default to build when ambiguous). This is a behavior addition, small enough to land here. If the change grows beyond ~30 lines, split into its own step.

**Verification** (path-string audit, REDESIGN AI validation custom check):
- `grep -rE '\.lore/(brainstorm|specs|design|plans|tasks|notes|research|retros|issues|ideas|validation|stubs|excavations|diagrams)/' lore-development/skills/` — any hit must be (a) inside a skill in Phase 4/5 whose reshape hasn't landed yet, (b) migration documentation deliberately showing the old path, or (c) a miss.
- `grep -rE '\.lore/vision\.md' lore-development/` — only hits should be inside migration documentation.
- Trigger smoke test: run each touched skill's trigger phrase (confirming YAML parses and the skill loads). A full invocation cycle for each skill is not required at this phase.

**Review**:
- **fresh-lore** reviews the batch for consistency: same update pattern applied everywhere, no drift. Fresh-lore is appropriate because the work is breadth-first and a fresh context catches skipped files the implementer stopped seeing.

### Phase 2 — Agent descriptions

**Files**:
- `lore-development/agents/lore-researcher.md`
- `lore-development/agents/spec-reviewer.md`
- `lore-development/agents/design-reviewer.md`
- `lore-development/agents/plan-reviewer.md`
- `lore-development/agents/fresh-lore.md`

**Addresses**: REQ-REDESIGN-42, 43, 44.

**Expertise**: prompt engineering — agent descriptions are load-bearing prompts. Search-priority inversion (REQ-REDESIGN-42) is semantic, not mechanical.

**What to do**:

1. `lore-researcher.md`: rewrite search paths to `.lore/build/{brainstorm,specs,design,plans,notes,research,retros,issues,ideas,tasks,validation,stubs,excavations}/`, `.lore/reference/*`, `.lore/learned/*`. Invert search priority per REQ-REDESIGN-42: `learned/` first (operational imperatives), `reference/` second (solidified knowledge), `build/` third (session material). This reverses the current retro-first bias.
2. `spec-reviewer.md`: path update `.lore/specs/` → `.lore/build/specs/`. Fallback-review-save `.lore/reviews/` → `.lore/build/reviews/`.
3. `design-reviewer.md`: path update `.lore/design/` → `.lore/build/design/`. Same fallback rename.
4. `plan-reviewer.md`: path update `.lore/plans/` → `.lore/build/plans/`. Same fallback rename.
5. `fresh-lore.md`: update path examples to the new tree.

**Verification**:
- Grep `lore-development/agents/` for any legacy `.lore/` path — must be zero hits outside intentional migration documentation.
- Launch `lore-researcher` on a fixture tree carrying documents in the new paths. Confirm it returns hits under the new priority order.

**Review**:
- **Thorne** reviews. Search-priority inversion is a behavior change under a prompt; needs critical read.

### Phase 3 — `/tend migrate` mode + non-migrate mode updates

**Files**:
- `lore-development/skills/tend/SKILL.md` (add `migrate` mode to modes table and invocation)
- `lore-development/skills/tend/references/migrate.md` (new reference file)
- `lore-development/scripts/tend_migrate.py` (new — move logic, dry-run, idempotency, link rewriting)
- `lore-development/scripts/tests/test_tend_migrate.py` (new — unit tests + fixture e2e)
- `lore-development/scripts/tests/fixtures/pre-migration/` (new — fixture tree)
- `lore-development/skills/tend/references/directories.md` (pass two: add legacy-orphan → migrate pointer)

**Addresses**: REQ-REDESIGN-18 – 25.

**Expertise**: Python for the migration script. Markdown link rewriting across `related:`, `source:`, and in-body links requires careful parsing — the unit tests are load-bearing (AI Validation default: 90%+ coverage on new migration code).

**What to do**:

1. Write `tend_migrate.py`:
   - Detect legacy structure by scanning for any of the 14 old top-level directories + `.lore/vision.md` (REQ-REDESIGN-19).
   - Build move plan per REQ-REDESIGN-20 (uses the migration table from REQ-REDESIGN-6).
   - Diagrams default to `build/diagrams/` (REQ-REDESIGN-21).
   - Rewrite `related:` frontmatter field values.
   - Rewrite `source:` frontmatter field values.
   - Rewrite in-body markdown links (`[text](.lore/old/path)`).
   - Dry-run by default; emit the full move + link-rewrite plan. Apply only with explicit flag + user confirmation (REQ-REDESIGN-22).
   - Idempotent: re-run on already-migrated tree reports zero changes (REQ-REDESIGN-23).
   - Skip `.lore/commissions/`, `.lore/meetings/`, `.lore/heartbeat.md`, `.lore/lore-agents.md`, and anything registered in `.lore/lore-config.md` under `custom_directories` (REQ-REDESIGN-24).
2. Unit tests:
   - Fixture tree with every legacy directory + one document each + at least one cross-link per document type.
   - Assert dry-run output matches expected moves.
   - Assert apply produces target layout.
   - Assert internal links resolve post-migrate.
   - Assert idempotency: second apply is a no-op.
   - Assert protected paths (commissions, meetings, heartbeat, lore-agents) are untouched.
   - **Fenced-code-block preservation**: add a fixture document whose body contains a fenced code block referencing an old path (e.g., a `bash` block that cat-es `.lore/brainstorm/foo.md`). Assert the script leaves code-block content as-is — these are documentation, not live links.
   - **Migration-documentation exception**: add a fixture document marked as migration documentation (e.g., frontmatter tag `migration-doc` or explicit front-comment). Assert the script leaves its body unmodified. Plan leaves the exact marker convention to implementation; pick a stable one and document it.
3. Write `tend/references/migrate.md`: describe mode invocation (`/tend migrate`), dry-run behavior, detection logic, protected paths, idempotency guarantee. Not part of default `/tend` sequential run (REQ-REDESIGN-18).
4. Update `tend/SKILL.md`: add `migrate` row to the Modes table. Add invocation line `/tend migrate` to the Invocation section. Note that `migrate` is separate from the sequential `status → tags → filenames → directories` chain.
5. Update `tend/references/directories.md` (second pass): when legacy top-levels are detected by `directories` mode, emit the flag "legacy structure detected; run `/tend migrate`" (REQ-REDESIGN-25).

**Verification**:
- `pytest lore-development/scripts/tests/test_tend_migrate.py` — all cases pass.
- Run `python tend_migrate.py` against a copy of this repo's own `.lore/` as an end-to-end fixture (don't apply to working tree yet). Inspect dry-run output for correctness.
- Coverage report confirms 90%+ on `tend_migrate.py` (AI Validation default).
- Run `/tend status`, `/tend tags`, `/tend filenames`, `/tend directories` modes against a post-migration fixture tree. Confirm they treat `build/`, `reference/`, `learned/` as standard and flag no false orphans.

**Review**:
- **Thorne** reviews. Blast radius is high: the migration script moves user files. Link-rewriting logic across three distinct contexts (frontmatter `related:`, frontmatter `source:`, in-body markdown links) is the most likely bug site. Fixture coverage is the gate.

### Phase 4 — `/excavate` → `/distill` rename and reshape

**Files**:
- `lore-development/skills/excavate/` → `lore-development/skills/distill/` (directory rename)
- `lore-development/skills/distill/SKILL.md` (full rewrite per distill brainstorm)
- `lore-development/agents/surface-surveyor.md` (update the `/lore-development:excavate` invocation reference to `/lore-development:distill`)
- `lore-development/skills/tend/SKILL.md` (add distill-before-archive prompt hook)
- `lore-development/skills/tend/references/status.md` (archive logic for `status: implemented` specs)
- `lore-development/README.md` (update skill list)
- Plugin marketplace entry (`.claude-plugin/marketplace.json` — confirm if this plugin registers its skills here)

**Addresses**: REQ-REDESIGN-26 – 33.

**Expertise**: skill-prompt design. The distill brainstorm is the binding source; do not re-derive the shape rule here.

**What to do**:

1. Rename skill directory `excavate/` → `distill/`. Update the `name:` field in SKILL.md frontmatter from `excavate` to `distill`. Update the description's trigger phrases.
2. Rewrite SKILL.md body per REQ-REDESIGN-26 – 32:
   - Two seed modes: `/distill code` (reshape of current excavate behavior — tuned down per REQ-REDESIGN-29's shape rule) and `/distill build` (new — reads from `.lore/build/specs/`, `.lore/build/plans/`, `.lore/build/brainstorm/` as seed material).
   - Shared core operation: read seed → verify against code → present reconciled candidates → user gates each one. Build-seed mismatches surface explicitly (REQ-REDESIGN-28).
   - Shape rule: reference contains only what the code cannot tell a reader. No function signatures, no endpoint lists (REQ-REDESIGN-29). Cite the distill brainstorm for the full rule.
   - Null output is valid (REQ-REDESIGN-30). No template pressure to manufacture candidates.
   - `/distill` updates existing reference files when code has drifted (REQ-REDESIGN-31). Reference is living, not append-only.
   - Excavation index moves to `.lore/build/excavations/index.md` (REQ-REDESIGN-32). Reference docs themselves stay in `.lore/reference/` (unchanged).
3. Update `tend/SKILL.md` (or the appropriate mode reference): when `directories` mode considers a spec with `status: implemented` for archive, surface a "Distill this spec before archiving?" prompt (REQ-REDESIGN-33). **Implementation decision**: soft prompt, not hard enforcement. Rationale: spec defers the choice; a soft prompt preserves user agency and matches the `/tend` dry-run → confirm → apply pattern. Hard enforcement would block archival if distill is skipped, which is worse UX than an optional prompt. Flag this decision in the Open Questions section.
4. Update `lore-development/README.md` skill list: rename the `excavate` entry to `distill`.

**Verification**:
- **plugin-dev:skill-reviewer** reads the new `distill/SKILL.md` — catches structural and consistency issues.
- Anti-assertion and anti-template spot-check: the post-rewrite SKILL.md doesn't demand a count of candidates. "Null output is valid" appears in prompt guidance.
- Grep for `excavate` across `lore-development/` — any remaining hit must be in migration documentation that intentionally references the old name.
- Manual trigger: `/distill build .lore/build/specs/<test-spec>.md` → skill loads, asks user for seed confirmation, does not pre-scan.

**Review**:
- **plugin-dev:skill-reviewer** on the rewritten SKILL.md.
- **fresh-lore** cross-checks SKILL.md against `.lore/brainstorm/distill-function.md` — did the rewrite preserve the brainstorm's shape rule and null-output-valid stance without reintroducing spec-replacement ambition?

### Phase 5 — `/learn` (new) + `/retro` reshape (coupled)

**Files**:
- `lore-development/skills/learn/` (new directory)
- `lore-development/skills/learn/SKILL.md` (new)
- `lore-development/skills/retro/SKILL.md` (reshape — strip template, strip graduation, strip analysis vocabulary)
- `lore-development/README.md` (add `/learn` entry)

**Addresses**: REQ-REDESIGN-14 – 17 (retro), REQ-REDESIGN-34 – 41 (learn).

**Expertise**: skill-prompt design. Both skills are capture skills under the capture-skill principles (`.lore/brainstorm/principles-for-capture-skills.md`). Prompt design is the deliverable; over-specifying reproduces the exact pathology the rewrite is meant to prevent.

**What to do**:

1. Write `learn/SKILL.md` per REQ-REDESIGN-34 – 41:
   - Frontmatter declares user-invoked only. Description triggers: "learn", "record a lesson", "/learn".
   - Opening two-path question (REQ-REDESIGN-35): specific material or felt pattern.
   - Question-first progression (REQ-REDESIGN-36). AI never asserts; "nothing" is valid at any step and closes without a file.
   - Asymmetric shape gate (REQ-REDESIGN-37): enforced at artifact level, not as a pre-filter. "Don't do X because Y" or "If you find yourself doing X, stop — here's why." "Do X because it worked" is malformed.
   - Active dedup before writing (REQ-REDESIGN-38): grep `.lore/learned/` for related entries on the articulated keywords; surface matches; user decides update vs new.
   - Write discipline (REQ-REDESIGN-39): terse default. No named length budget. Mixed content allowed. No restating. Draft is for trimming, not just approval.
   - On-request fetch (REQ-REDESIGN-40): when user names material ("recent Thorne reviews"), delegate to lore-researcher patterns (file path, tag query, module query). Skill does not pre-scan.
   - Default file layout (REQ-REDESIGN-41): one file per entry, kebab-case filename derived from the articulated mistake, flat under `.lore/learned/`. Revisable when `design-learned-structure.md` resolves.
   - Frontmatter per REQ-REDESIGN-13: common fields only. Status values `active` or `superseded`. No section scaffold in the body.
2. Reshape `retro/SKILL.md` per REQ-REDESIGN-14 – 17:
   - Remove the "What Went Well / What Could Improve / Lessons Learned" template section in full (REQ-REDESIGN-14).
   - Remove the graduation flow (classify Invalid/Valid/Critical/Universal, graduate to project CLAUDE.md or `~/.claude/rules/lessons-learned.md`) — REQ-REDESIGN-15.
   - Rewrite the prompt to direct capture toward describing what happened, not interpreting. Forbid the analysis vocabulary (`lesson`, `insight`, `we learned`, `takeaway`) in output (REQ-REDESIGN-16).
   - Output is free-form notes with structured frontmatter. Frontmatter: common fields only. Status values `open` or `archived` (REQ-REDESIGN-9).
   - **Couple with `/learn`**: both ship together in this phase. No pointer note needed (REQ-REDESIGN-17's fallback is only used if `/retro` ships before `/learn`). If delivery must split: **`/learn` ships first, `/retro` holds**. Shipping `/retro`'s strip without `/learn` leaves users with no extraction path and requires the pointer note; shipping `/learn` without the `/retro` strip leaves the old template in place but adds a working capture skill, which is strictly additive. Order: `/learn` → `/retro`.
3. Update `lore-development/README.md`: add `/learn` to the skill list.

**Verification** (REDESIGN AI Validation custom checks):
- **Anti-template check on `/retro`**: post-rewrite SKILL.md must not contain "What Went Well", "What Could Improve", "Lessons Learned", or prescriptive use of "graduate". Forbidden vocabulary list (`lesson`, `insight`, `we learned`, `takeaway`) appears only as "avoid these" instruction, never as section heading.
- **Anti-assertion check on `/learn`**: post-build SKILL.md prompt must not contain "propose candidate lessons", "identify lessons from", or "extract mistakes from notes". Must contain user-invoked framing and nothing-is-valid framing.
- **plugin-dev:skill-reviewer** reviews both SKILL.md files.
- Manual triggers:
  - `/retro` on a dummy session → produces a file with common frontmatter and free-form body. No "What Went Well" section appears.
  - `/learn` → asks two-path opening. User responds "nothing actually" → session closes without writing a file.
  - `/learn` → user names a mistake → skill runs dedup grep against `.lore/learned/` → writes one file with kebab-case name, terse body.

**Review**:
- **plugin-dev:skill-reviewer** on both SKILL.md files.
- **fresh-lore** cross-checks against `.lore/brainstorm/principles-for-capture-skills.md` and `.lore/brainstorm/learn-dialog.md`. Did the rewrite honor all three principles?

### Phase 6 — Cross-plugin coordination + plugin docs + full audit

**Files**:
- Celeste agent description (located in `~/.guild-hall/` or guild-hall plugin — path to be confirmed at phase start)
- `lore-development/README.md` (three-directory-model section)
- `lore-development/.claude-plugin/` (plugin SKILL.md or manifest, if applicable)

**Addresses**: REQ-REDESIGN-45 (Celeste), REQ-REDESIGN-48 (plugin README/SKILL.md).

**Expertise**: cross-plugin coordination. Celeste lives outside `lore-development/`. The spec's constraint (lines 222–224) flags this as "needs coordination with whoever owns guild-hall workers."

**What to do**:

1. **Cross-plugin coordination (Celeste)**:
   - Locate Celeste's agent description. Per the spec and the vibe-garden project structure, this lives under guild-hall (not `lore-development/`).
   - Update the path reference `.lore/vision.md` → `.lore/reference/vision.md`.
   - This is a one-file change. Before starting, the commission runner should confirm with the user: (a) is it in scope for this commission to touch guild-hall, or (b) is a separate guild-hall-scoped commission required? Default: ask before touching files outside `lore-development/`.
2. Update `lore-development/README.md`:
   - Rewrite the "`.lore/` structure" section (or equivalent) to describe the three-directory model: `build/` (work scaffolding, session-bound), `reference/` (solidified, system-oriented), `learned/` (mistakes-only, worker-oriented).
   - Update the skill list to reflect `/distill` (not `/excavate`) and add `/learn`.
   - Add a short "Migrating from the old layout" pointer to `/tend migrate`.
3. If `lore-development/.claude-plugin/` contains a top-level SKILL.md or manifest that describes the directory structure, update it to match.
4. **Full spec AI Validation** (the custom checks from `.lore/specs/lore-redesign.md`):
   - **Path-string audit**: grep `lore-development/` for every legacy `.lore/` path listed in the spec's AI Validation section. Any hit outside intentional migration documentation is a miss and must be fixed in place.
   - **Anti-template check**: re-run against `/retro` SKILL.md (Phase 5 already verified; re-confirm).
   - **Anti-assertion check**: re-run against `/learn` SKILL.md (Phase 5 already verified; re-confirm).
   - **End-to-end `/tend migrate` fixture test**: run against the fixture tree containing every legacy directory with at least one document and at least one cross-link. Assert target layout, link resolution, and idempotency on re-run.
5. **Real-world validation**: run `/tend migrate` dry-run on this repo's own `.lore/`. Inspect the move plan. If the plan is clean and all link rewrites are correct, consider running apply. (This is both a validation and a dogfooding step — after this runs, this project's `.lore/` is on the new layout.)

**Verification**: spec Success Criteria checklist (spec lines 195–203). Each item confirmed.

**Review**:
- **Thorne** for the Celeste coordination and the full audit.
- **Octavia** reads the plugin README rewrite for clarity and consistency with the spec's three-directory-model description.

### Phase 7 — Validate Against Spec

Launch a sub-agent (fresh context) that reads `.lore/specs/lore-redesign.md` and reviews the full implementation. The agent enumerates every requirement (REQ-REDESIGN-1 through REQ-REDESIGN-48) and flags any that are not met, partially met, or silently dropped. This is the final gate before the refactor is declared complete. Not optional.

## Delegation Guide

| Phase | Implementer | Primary reviewer | Additional reviews |
|-------|-------------|------------------|---------------------|
| 0 — Schema foundation | Dalton | Thorne (gate) | — |
| 1 — Path fan-out | Dalton | fresh-lore | path-string audit grep |
| 2 — Agent descriptions | Dalton | Thorne | — |
| 3 — `/tend migrate` | Dalton | Thorne | unit tests + fixture e2e |
| 4 — `/excavate` → `/distill` | Dalton | plugin-dev:skill-reviewer | fresh-lore (brainstorm fidelity) |
| 5 — `/learn` + `/retro` | Dalton | plugin-dev:skill-reviewer | anti-template + anti-assertion checks; fresh-lore (brainstorm fidelity) |
| 6 — Cross-plugin + audit | Dalton | Thorne | Octavia (README clarity) |
| 7 — Spec validation | Fresh sub-agent | — | — |

**Review gates** (hard):
- Phase 0 → Phase 1/2: **Thorne must sign off on the schema** before fan-out begins. Foundation errors propagate N files deep otherwise.
- Phase 3: **unit tests + fixture e2e must pass** before merging. `/tend migrate` moves user files; coverage is the gate.
- Phase 5: **anti-template and anti-assertion checks must pass** before merging. Both checks are codified in the spec's AI Validation section.
- Phase 7: **full requirement sweep must report clean** before the refactor is declared complete.

## Open Questions

(Questions to resolve at commission start, not during mid-phase execution.)

1. **Celeste cross-plugin touch (decide before Commission C is commissioned, not mid-phase)**: REQ-REDESIGN-45 is not optional — Celeste's description must reference `.lore/reference/vision.md` by the time the full refactor ships, or Phase 7 validation fails. The decision is *when*, not *whether*. Two acceptable paths:
   - **(a)** Commission C's scope is explicitly expanded to touch guild-hall for this one-file change. Commission C then delivers the full refactor including Celeste.
   - **(b)** A separate guild-hall-scoped commission is filed before Commission C completes, and Commission C's success criteria are amended to note REQ-REDESIGN-45 is delegated.
   The "ask the user mid-phase" stance in Phase 6's step 1 is the runtime safety net, not the planning decision. Make the decision upfront.
2. **`/tend` distill-before-archive enforcement (REQ-REDESIGN-33)**: the spec defers hard vs soft choice. Plan adopts **soft prompt** (rationale in Phase 4). Confirm this choice before Phase 4 runs, or flag for revision.
3. **Validation-script fixture migration**: the existing `lore-development/scripts/tests/` probably contains fixture trees in the old layout. Phase 0 updates the schema module and tests; if fixtures under `tests/` use old paths, they migrate in Phase 0 too. Verify at phase start.
4. **`.claude-plugin/marketplace.json` touch points**: confirm whether this plugin's marketplace entry references `.lore/` paths that need updating in Phase 6. If not, drop step 3 of Phase 6.
5. **`/ddp` behavior addition (REQ-REDESIGN-5)**: the split-by-purpose dialog is small enough to land in Phase 1, but if implementation pressure suggests otherwise, promote it to its own step in Phase 4 (alongside the other diagram-adjacent work).
6. **Learned directory seed**: REQ-REDESIGN-4 says `.lore/learned/` is created on first `/learn` invocation. Phase 5 must not pre-create the directory — it is materialized by the first `/learn` write. Confirm the skill's write path creates the parent if missing.

## Notes on spec gaps

These were encountered while planning. None are blocking; each has a reasonable interpretation documented above.

- **REQ-REDESIGN-33 (distill-before-archive enforcement)**: spec explicitly defers; plan adopts soft prompt with rationale.
- **REQ-REDESIGN-41 (`/learn` file layout default)**: spec defers internal layout to `.lore/issues/design-learned-structure.md`; plan adopts the spec's "starting default" (one file per entry, kebab-case, flat).
- **Celeste location**: spec names the cross-plugin touchpoint but doesn't specify the file path. Phase 6 step 1 begins with locating it.
- **`/tend` migration script language**: spec's AI Validation defaults mention "unit tests for the `/tend migrate` move logic." Plan assumes Python (matching the existing `validate_frontmatter.py` and `idea_hook.py` scripts) unless the existing `tend/SKILL.md` pattern suggests prompt-embedded logic. Confirmed Python at Phase 3 start.
- **Pre-existing `.lore/reference/`**: reference is the one pre-existing standard directory that stays put. The excavate SKILL.md already uses `artifact_path: .lore/reference` — confirming reference is not a new creation, it is the survivor around which the new model is built. Phase 0 notes this; Phase 3 migrate should not create `.lore/reference/` if it already exists.
