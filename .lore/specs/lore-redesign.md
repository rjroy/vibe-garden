---
title: "Lore-development plugin redesign: three-directory model, capture-skill rework"
date: 2026-04-24
status: draft
tags: [lore-development, directory-structure, capture-skills, retros, distill, learn, refactor]
modules: [lore-development]
related:
  - .lore/brainstorm/lore-directory-redesign.md
  - .lore/brainstorm/principles-for-capture-skills.md
  - .lore/brainstorm/distill-function.md
  - .lore/brainstorm/learn-dialog.md
  - .lore/issues/roadmap-lore-redesign.md
  - .lore/issues/design-learned-structure.md
  - .lore/issues/design-extraction-skill.md
req-prefix: REDESIGN
---

# Spec: Lore-development plugin redesign

## Overview

Restructure the `.lore/` tree into three directories (`build/`, `reference/`, `learned/`), rework the capture skills (`/retro` strips down, `/excavate` becomes `/distill`, `/learn` is new), migrate every existing skill and agent that writes or reads `.lore/` paths, consolidate the frontmatter schema, and give `/tend` a migration mode that moves existing projects onto the new structure.

This spec directs a refactor whose reasoning is already resolved in the four brainstorms listed under Context. It enumerates what has to change, not why. When the "why" matters for edge cases, the spec points back to the brainstorm.

## Entry Points

This spec feeds the plugin-wide implementation plan (roadmap step 4 + direction for steps 3 and 5).

- A plan decomposes these requirements into sequenced phases (path migrations, frontmatter collapse, tend migration mode, retro strip, excavate→distill rename, learn implementation).
- `/distill` and `/learn` land as part of the same plan; `/learn` must ship at-or-before the `/retro` strip per the ordering constraint.

## Scope

**In scope:**
- Three-directory model (`.lore/build/`, `.lore/reference/`, `.lore/learned/`).
- Path migration for every lore-development skill that writes or reads `.lore/` subdirectories.
- Frontmatter schema consolidation (per-directory status values collapse to three short sets).
- `/retro` strip-down to free-form notes with structured frontmatter.
- `/excavate` rename to `/distill` with two seed modes (`code`, `build`) and a tightened shape rule for reference.
- `/learn` as a new user-invoked dialog skill writing to `.lore/learned/`.
- `/tend` migration mode that moves existing projects from the old layout to the new.
- Agent description updates for `lore-researcher`, `spec-reviewer`, `design-reviewer`, `plan-reviewer`, `fresh-lore`, and Celeste's reference to `.lore/vision.md`.
- Frontmatter schema file (`lore-development/shared/frontmatter-schema.md`) rewritten for the new structure.

**Out of scope (named, deferred):**
- Reference-as-a-skill (a `/reference "how does auth work?"` query skill over the reference tree). Open question from the directory-redesign brainstorm; decide later.
- Graduation to higher scopes (whether `learned/` entries graduate upward to project `CLAUDE.md` or `~/.claude/rules/lessons-learned.md`). Deferred per roadmap and `design-learned-structure.md`.
- Per-diagram splitting decisions (which individual diagrams belong in build vs reference). Per-file judgment call; no design needed.
- Internal structure of `.lore/learned/` beyond minimum frontmatter (flat vs categorized, entry granularity, full lifecycle). Owned by `design-learned-structure.md`; spec here defines only what `/learn` needs to write a valid file.
- `.lore/commissions/`, `.lore/meetings/`, `.lore/heartbeat.md`, `.lore/lore-agents.md` — owned by guild-hall or cross-plugin surfaces. Not touched by this redesign.

## The three-directory model

Directly follows `.lore/brainstorm/lore-directory-redesign.md`.

- **`.lore/build/`** — work scaffolding. Session-bound. Dissolves or archives after the work is done.
- **`.lore/reference/`** — anything solidified. Contains only what the code cannot say. Oriented at the system.
- **`.lore/learned/`** — operational imperatives, mistakes-only. Oriented at the worker.

Two one-directional pipelines: build → reference (via `/distill`) and build → learned (via `/learn`). Success does not graduate.

## Requirements

### Directory structure

- REQ-REDESIGN-1: `.lore/build/`, `.lore/reference/`, and `.lore/learned/` are the three canonical top-level directories under `.lore/` owned by the lore-development plugin.
- REQ-REDESIGN-2: Every lore-development skill that produces an artifact writes to a subdirectory of exactly one of the three top-level directories. No skill writes directly to `.lore/` root (the sole pre-existing exception, `vision.md`, moves — see REQ-REDESIGN-3).
- REQ-REDESIGN-3: `vision.md` moves from `.lore/vision.md` to `.lore/reference/vision.md`. The `/vision` skill and Celeste's agent description are updated to the new path.
- REQ-REDESIGN-4: `.lore/learned/` is created on first `/learn` invocation in a project. It does not need to pre-exist.
- REQ-REDESIGN-5: Diagrams are split by purpose (session-bound → `build/diagrams/`, current-state → `reference/diagrams/`). `/ddp` asks which on write; per-diagram judgment. Default to `build/diagrams/` when ambiguous.

### Path migration table

- REQ-REDESIGN-6: Every skill listed below writes or reads from the new path in place of the old path. The current-state path cleanups to the old paths are removed (not aliased — see REQ-REDESIGN-18 for the migration bridge).

| Skill | Old path | New path |
|-------|----------|----------|
| `/brainstorm` | `.lore/brainstorm/` | `.lore/build/brainstorm/` |
| `/specify` | `.lore/specs/` | `.lore/build/specs/` |
| `/design` | `.lore/design/` | `.lore/build/design/` |
| `/prep-plan` | `.lore/plans/` | `.lore/build/plans/` |
| `/plan-breakdown` | `.lore/tasks/` | `.lore/build/tasks/` |
| `/implement` | `.lore/notes/` | `.lore/build/notes/` |
| `/simplify` | `.lore/notes/` | `.lore/build/notes/` |
| `/research` | `.lore/research/` | `.lore/build/research/` |
| `/retro` (reshaped) | `.lore/retros/` | `.lore/build/retros/` |
| `/excavate` → `/distill` | `.lore/reference/` (writes), `.lore/excavations/` (index) | `.lore/reference/` (unchanged for feature docs), `.lore/build/excavations/` (index) |
| `/file-issue` | `.lore/issues/` | `.lore/build/issues/` |
| `/review-ideas` | reads `.lore/ideas/`, writes `.lore/issues/` | reads `.lore/build/ideas/`, writes `.lore/build/issues/` |
| `/define-validation` | `.lore/validation/` | `.lore/build/validation/` |
| `/update-stubs` | reads `.lore/specs/`, writes `.lore/stubs/index.md` | reads `.lore/build/specs/`, writes `.lore/build/stubs/index.md` |
| `/back-propagate` | reads `.lore/plans/`, `.lore/notes/`, `.lore/retros/`, writes `.lore/specs/` | all under `.lore/build/` |
| `/ddp` | `.lore/diagrams/` | split: `.lore/build/diagrams/` or `.lore/reference/diagrams/` (see REQ-REDESIGN-5) |
| `/vision` | `.lore/vision.md` | `.lore/reference/vision.md` |
| `/poke-holes` | reads only; no write path | update any path references in prompts |
| `/learn` (new) | — | `.lore/learned/` |
| idea-capture hook | `.lore/ideas/` | `.lore/build/ideas/` |

- REQ-REDESIGN-7: The raw idea queue (`.lore/ideas/` under the old scheme; `.lore/build/ideas/` under the new) continues to hold non-frontmatter markdown per the existing `/review-ideas` convention. `/tend` does not flag missing frontmatter for files under this path.

### Frontmatter schema consolidation

- REQ-REDESIGN-8: The frontmatter schema file at `lore-development/shared/frontmatter-schema.md` is rewritten to reflect the three-directory model. Common fields (`title`, `date`, `status`, `tags`, `modules`, `related`) are unchanged.
- REQ-REDESIGN-9: Status values collapse into three sets, one per top-level directory:
  - **Build documents** retain the meaningful per-type statuses from the current schema, since each build artifact type still has a lifecycle:
    - Brainstorm: `open`, `parked`, `resolved`, `archived`.
    - Spec: `draft`, `approved`, `implemented`, `superseded`, `archived`.
    - Design: `draft`, `approved`, `implemented`, `superseded`, `archived`.
    - Plan: `draft`, `approved`, `executed`, `archived`.
    - Task: `pending`, `complete`, `skipped`.
    - Notes: `in_progress`, `complete`, `archived`.
    - Research: `active`, `archived`.
    - Retro: `open`, `archived`. (The reshape collapses `complete` — notes are not analyzed, so "complete" has no distinct meaning.)
    - Issue: `open`, `resolved`, `wontfix`, `archived`.
  - **Reference documents**: `current`, `outdated`, `archived`.
  - **Learned documents**: `active`, `superseded`. (Minimum set. Lifecycle beyond this deferred to `design-learned-structure.md`.)
- REQ-REDESIGN-10: Spec-specific `req-prefix` field persists unchanged.
- REQ-REDESIGN-11: Notes-specific `source` field and task-specific `source` + `sequence` fields persist unchanged; path values inside them migrate to the new tree (e.g., `source: .lore/build/plans/auth-flow.md`).
- REQ-REDESIGN-12: Retro frontmatter gains no new fields. Structured metadata (common fields) plus free-form body is the whole shape. No section-level structure is prescribed.
- REQ-REDESIGN-13: Learned frontmatter requires common fields. The body is free-form and may mix prose and code. No length constraint, no section scaffold. Additional fields (severity, source, evidence count) are deliberately not defined here; owned by `design-learned-structure.md`.

### `/retro` reshape (roadmap step 3)

- REQ-REDESIGN-14: `/retro` output is free-form notes with structured frontmatter. The current "What Went Well / What Could Improve / Lessons Learned" template is removed in full.
- REQ-REDESIGN-15: The current graduation flow (classify each lesson as Invalid / Valid / Critical / Universal, graduate to project `CLAUDE.md` or `~/.claude/rules/lessons-learned.md`) is removed from `/retro`. Whether and how graduation returns in any form is deferred (out of scope, named above).
- REQ-REDESIGN-16: The `/retro` prompt directs the skill to describe what happened rather than interpret it. The vocabulary of analysis (`lesson`, `insight`, `we learned`, `takeaway`) is forbidden in capture output. See `.lore/brainstorm/principles-for-capture-skills.md` for the binding rules.
- REQ-REDESIGN-17: If `/learn` has not yet shipped when `/retro` is reshaped, `/retro`'s closing summary includes a pointer note: "Lessons now live in `.lore/learned/`. Use `/learn` when you're ready to record one." See ordering constraint below.

### `/tend` migration mode

- REQ-REDESIGN-18: `/tend migrate` is a new mode that moves a project from the old `.lore/` layout to the new three-directory layout. It is separate from the existing `status`, `tags`, `filenames`, `directories` modes and is not part of the default sequential run.
- REQ-REDESIGN-19: `/tend migrate` detects legacy structure by presence of any of the old top-level directories (`.lore/brainstorm/`, `.lore/specs/`, `.lore/design/`, `.lore/plans/`, `.lore/tasks/`, `.lore/notes/`, `.lore/research/`, `.lore/retros/`, `.lore/issues/`, `.lore/ideas/`, `.lore/validation/`, `.lore/stubs/`, `.lore/excavations/`, `.lore/diagrams/`) or `.lore/vision.md`.
- REQ-REDESIGN-20: `/tend migrate` moves files to their new locations per REQ-REDESIGN-6, creates the `build/`, `reference/`, `learned/` directories as needed, and updates every internal path reference (`related:`, `source:`, in-body markdown links) to the new paths.
- REQ-REDESIGN-21: For diagrams, `/tend migrate` defaults all existing `.lore/diagrams/*` files to `.lore/build/diagrams/`. The user can manually promote individual diagrams to `.lore/reference/diagrams/` afterward; `/tend` does not decide per-diagram during migration.
- REQ-REDESIGN-22: `/tend migrate` is dry-run by default. It presents the full move plan, including internal-link rewrites, and applies only after user confirmation.
- REQ-REDESIGN-23: `/tend migrate` is idempotent. Running it on an already-migrated tree reports no changes.
- REQ-REDESIGN-24: `/tend migrate` does not touch `.lore/commissions/`, `.lore/meetings/`, `.lore/heartbeat.md`, `.lore/lore-agents.md`, or any custom directory registered in `.lore/lore-config.md`.
- REQ-REDESIGN-25: `/tend`'s non-migrate modes (`status`, `tags`, `filenames`, `directories`) are updated to treat `build/`, `reference/`, `learned/` as the standard directories. Legacy top-level directories (if present) are flagged as orphans with a pointer to `/tend migrate`.

### `/excavate` → `/distill` rewrite (roadmap step 5)

Directs the refactor. Reasoning is in `.lore/brainstorm/distill-function.md`; do not re-derive here.

- REQ-REDESIGN-26: `/excavate` is renamed to `/distill`. The plugin command path changes; skill files move accordingly.
- REQ-REDESIGN-27: `/distill` supports two seed modes: `/distill code` (reshape of existing excavate behavior) and `/distill build` (new mode that reads specs, plans, and brainstorms as seed material). Both modes run the same code-verifying core.
- REQ-REDESIGN-28: The core operation for both modes is: read seed → verify against current code → present reconciled candidates → user gates each one. Build-seed claims that disagree with code are surfaced explicitly as mismatches, not silently corrected.
- REQ-REDESIGN-29: Reference documents written by `/distill` contain only what the code cannot tell a reader. Function signatures, endpoint lists, and other code-recoverable material do not belong in reference. See the distill brainstorm for the full shape rule.
- REQ-REDESIGN-30: Null output is valid. A `/distill` session that finds no reference-worthy material writes zero files. No template pressure to manufacture candidates.
- REQ-REDESIGN-31: `/distill` updates existing reference files when code has drifted since the reference was written. Reference is living documentation, not append-only history.
- REQ-REDESIGN-32: The excavation index (currently `.lore/excavations/index.md`) moves to `.lore/build/excavations/index.md` and continues to track documented features, discovered-but-undocumented features, and unexplored entry points.
- REQ-REDESIGN-33: `/tend`'s archive logic is updated: a spec with `status: implemented` is surfaced as a distill candidate (prompt "Distill this spec before archiving?") before it can be archived. The spec does not mandate whether this is hard enforcement or a soft prompt; resolve during implementation.

### `/learn` skill (roadmap step 5)

Directs the build. Reasoning is in `.lore/brainstorm/learn-dialog.md`; do not re-derive here.

- REQ-REDESIGN-34: `/learn` is a new skill, user-invoked only. It is not triggered by any other skill. `/specify`, `/prep-plan`, `/design`, and others do not auto-invoke `/learn`.
- REQ-REDESIGN-35: `/learn`'s opening asks a two-path question: is the user recording from specific material (a retro, a Thorne review, a spec) or describing a felt pattern across sessions? Both paths are valid.
- REQ-REDESIGN-36: After the opening, progression is question-first. The AI asks; the user articulates. The AI never asserts that something is a lesson. "Nothing" is a valid user answer at any step and closes the session without writing a file.
- REQ-REDESIGN-37: Entries enforce the asymmetric shape at the artifact level: "don't do X because Y happened" or "if you find yourself doing X, stop — here's why." A `/learn` entry that reads like "do X because it worked" is malformed. See `.lore/brainstorm/principles-for-capture-skills.md` principle 2.
- REQ-REDESIGN-38: The skill runs active dedup before writing. It searches `.lore/learned/` for related entries (mechanism unspecified; grep on keywords from the user's articulation is a reasonable default) and surfaces matches. User decides: update existing, or write new.
- REQ-REDESIGN-39: Write discipline:
  - Terse default. One sentence is often enough.
  - No length budget, no "aim for N sentences" instruction in the prompt. Any named count becomes a target and the model fills to it.
  - Mixed content (prose, code blocks) is allowed. No forced structure.
  - No restating. One articulation, not three framings.
  - Draft is presented for the user to trim, not just approve.
- REQ-REDESIGN-40: When the user names specific material ("look at my recent Thorne reviews"), `/learn` fetches it on request — file path, tag query, or module query, delegated to `lore-researcher` patterns. The skill does not pre-scan or volunteer candidates.
- REQ-REDESIGN-41: The file layout inside `.lore/learned/` (flat vs categorized, file-per-entry vs topic-file append, filename convention) is not specified here. `/learn` picks a default that can be revised when `design-learned-structure.md` resolves. Starting default: one file per entry, kebab-case filename derived from the articulated mistake, placed flat in `.lore/learned/`.

### Agent description updates

- REQ-REDESIGN-42: `lore-researcher`'s description and search-path lists update to search the three new directories. Retros, specs, brainstorms, research, and issues all live under `build/`; feature docs under `reference/`; lessons under `learned/`. Search priority order is rewritten to prioritize `learned/` highest (operational imperatives), then `reference/` (solidified knowledge), then `build/` (session material) — an inversion of current priority, which leads with retros.
- REQ-REDESIGN-43: `spec-reviewer`, `design-reviewer`, and `plan-reviewer` agent descriptions update paths: `.lore/specs/` → `.lore/build/specs/`, `.lore/design/` → `.lore/build/design/`, `.lore/plans/` → `.lore/build/plans/`. Fallback-review-save path (`.lore/reviews/`) moves to `.lore/build/reviews/`.
- REQ-REDESIGN-44: `fresh-lore` agent description updates path examples to the new tree.
- REQ-REDESIGN-45: Celeste's agent description (guild-hall worker, external to lore-development plugin) updates to reference `.lore/reference/vision.md` instead of `.lore/vision.md`. This is the only cross-plugin touchpoint the spec requires; all other guild-hall surfaces stay untouched.

### SKILL.md hardcoded paths

- REQ-REDESIGN-46: Every SKILL.md file in `lore-development/skills/` that hardcodes an old `.lore/` path is updated to the new path. The following are known and enumerated in REQ-REDESIGN-6's migration table: `brainstorm`, `specify`, `design`, `prep-plan`, `plan-breakdown`, `implement`, `simplify`, `research`, `retro`, `excavate` (→ `distill`), `file-issue`, `review-ideas`, `define-validation`, `update-stubs`, `back-propagate`, `ddp`, `vision`, `poke-holes`.
- REQ-REDESIGN-47: `tend/references/directories.md` and `tend/references/status.md` (reference files consumed by `/tend`) are rewritten for the new directory set.
- REQ-REDESIGN-48: The plugin's own SKILL.md and README documentation that references the lore directory structure is updated to describe the three-directory model.

## Ordering constraints

From the roadmap:

- **Steps 2 and 3 are coupled.** `/learn` (step 2, reqs REDESIGN-34–41) must ship at-or-before `/retro`'s strip-down (step 3, reqs REDESIGN-14–17). If shipped together, no pointer note is needed. If `/retro` ships first, it must include the pointer from REQ-REDESIGN-17.
- **The `/tend migrate` mode must ship before path migrations land in a given user's project.** Without it, users on the old layout have no supported way to move. In the plugin's release itself, `/tend migrate` can land in the same plan phase as the other skill path updates as long as the phase ships atomically.
- **Step 1 (distill brainstorm) and step 2 (learn brainstorm) are already done.** They're inputs to this spec, not sequencing constraints.

## Success Criteria

- [ ] All three directories (`build/`, `reference/`, `learned/`) are the only `.lore/` subdirectories touched by lore-development skills on new projects.
- [ ] Every skill in REQ-REDESIGN-6's table writes to its new path and reads from new paths. No skill still writes to a legacy path.
- [ ] `/tend migrate` runs cleanly on a representative pre-migration project (e.g., this repo's own `.lore/`) and produces a working post-migration tree. Internal links resolve. `lore-researcher` finds documents under the new paths.
- [ ] `/retro` produces a free-form notes file with common frontmatter only. No "What Went Well" section. No "Lessons Learned" section. No graduation flow runs.
- [ ] `/distill code` and `/distill build` both work. A `/distill build` session on a spec produces either a reference update, a mismatch surfaced for user resolution, or zero files — never a fabricated promotion candidate.
- [ ] `/learn` runs as a user-invoked dialog. It writes a valid file in `.lore/learned/`, or ends without writing if the user says so. It does not auto-trigger from any other skill.
- [ ] The frontmatter schema file describes the three-directory model with the status sets from REQ-REDESIGN-9. Examples are updated.
- [ ] Agent descriptions (`lore-researcher`, `spec-reviewer`, `design-reviewer`, `plan-reviewer`, `fresh-lore`) reference the new paths. Celeste's description references `.lore/reference/vision.md`.
- [ ] Running the post-migration plugin on a fresh project produces the new tree on first use with no legacy directories.

## AI Validation

**Defaults** (apply unless overridden):
- Code review by fresh-context sub-agent on the plan decomposition and on every large SKILL.md rewrite.
- Unit tests for the `/tend migrate` move logic: dry-run output matches expected moves, idempotency holds, internal-link rewriting is correct across `related:`, `source:`, and in-body links.
- 90%+ coverage on new code (primarily the migration logic and `/learn` dialog state handling).

**Custom** (feature-specific):
- **Path-string audit.** After the refactor, grep the `lore-development/` tree for `.lore/brainstorm/`, `.lore/specs/`, `.lore/design/`, `.lore/plans/`, `.lore/tasks/`, `.lore/notes/`, `.lore/research/`, `.lore/retros/`, `.lore/issues/`, `.lore/ideas/`, `.lore/validation/`, `.lore/stubs/`, `.lore/excavations/`, `.lore/diagrams/`, and `.lore/vision.md` (exact strings with leading `.lore/`, not nested under `build/`). Any hit in a SKILL.md, agent description, or shared reference file must be justified (e.g., migration documentation that intentionally shows the old path) or fixed.
- **`/retro` anti-template check.** The post-rewrite `/retro` SKILL.md must not contain the strings "What Went Well", "What Could Improve", "Lessons Learned", or "graduate" in prescriptive form. The forbidden-vocabulary list (`lesson`, `insight`, `we learned`, `takeaway`) appears only as an instruction to avoid, not as section headings.
- **`/learn` anti-assertion check.** The post-build `/learn` SKILL.md prompt must not contain phrases like "propose candidate lessons", "identify lessons from", or "extract mistakes from notes". It must contain the user-invoked framing and the nothing-is-valid framing.
- **`/tend migrate` end-to-end test.** Run `/tend migrate` on a fixture tree containing every legacy directory with at least one document and at least one internal cross-link. Assert: target tree matches expected layout, all internal links resolve, re-running migrate reports no changes.

## Constraints

- Specs for AI-guided skills are light. Prompts for `/retro`, `/distill`, and `/learn` leave room for model judgment. The spec defines *what the prompt forbids* and *what the prompt must elicit*, not the prompt's exact wording.
- `/learn` must not auto-invoke. This is load-bearing: the current `/retro` pathology comes from fixed-trigger capture against a template that demands N items. The fix requires user-initiated invocation.
- The three-directory model is not negotiable within this spec. Debate about the boundary between build and reference, or about whether learned should exist, belongs in a new brainstorm, not a requirement revision.
- Cross-plugin dependencies: Celeste lives in guild-hall, not lore-development. The vision-path update to her agent description is a one-file change that needs coordination with whoever owns guild-hall workers. Flag this in the plan.
- Guild-hall–owned paths (`.lore/commissions/`, `.lore/meetings/`, `.lore/heartbeat.md`, `.lore/lore-agents.md`) are not moved under `build/`. They are separate concerns.

## Resolved inconsistencies between input brainstorms

Two places where the brainstorms disagreed had to be resolved to write this spec.

**1. `/learn` as extractor vs dialog.** `.lore/brainstorm/lore-directory-redesign.md` describes extraction as an AI-scans-build-for-candidates skill fired at the front of new work. `.lore/brainstorm/learn-dialog.md` explicitly supersedes that: `/learn` is user-invoked only, doesn't scan, doesn't propose, doesn't fire at the front of new work. The roadmap names the supersession. The spec follows the learn-dialog framing (REQ-REDESIGN-34 through REQ-REDESIGN-41). `.lore/issues/design-extraction-skill.md`'s automated-scan framing is formally retired by this spec.

**2. The "named promotion verb" open question.** `.lore/brainstorm/lore-directory-redesign.md` flagged that build-to-reference promotion had no named operation. `.lore/brainstorm/distill-function.md` resolves this by renaming `/excavate` to `/distill` and adding `/distill build` as the second seed mode. The spec adopts the resolved form (REQ-REDESIGN-26 through REQ-REDESIGN-33). The lore-directory-redesign brainstorm's open question on this point is closed by the distill brainstorm.

## Context

Binding sources (read these before acting on any requirement):

- `.lore/brainstorm/lore-directory-redesign.md` — three-directory model.
- `.lore/brainstorm/principles-for-capture-skills.md` — binding rules for `/retro` and `/learn` (no N-demanding templates; mistakes only; observation separate from interpretation).
- `.lore/brainstorm/distill-function.md` — shape of `/distill`, the code-verifying core, the reference shape rule.
- `.lore/brainstorm/learn-dialog.md` — shape of `/learn`, two-path opening, write discipline.
- `.lore/issues/roadmap-lore-redesign.md` — step sequencing and ordering constraints.
- `.lore/issues/design-learned-structure.md` — open design work on the internal structure of `learned/`. The spec defers to this issue for anything beyond minimum frontmatter.
- `.lore/issues/design-extraction-skill.md` — superseded by `.lore/brainstorm/learn-dialog.md`; preserved for historical context only.
