---
title: "Distill: the named operation for promoting build findings into reference"
date: 2026-04-23
status: resolved
tags: [distill, excavate, reference, capture-skills, directory-structure]
modules: [lore-development]
related: [.lore/brainstorm/lore-directory-redesign.md, .lore/brainstorm/principles-for-capture-skills.md, .lore/issues/roadmap-lore-redesign.md]
---

# Brainstorm: Distill

## Context

The lore directory redesign named an open gap: there's no verb for taking a finding out of a build artifact and promoting it into a reference doc. Working name was "distill." This session resolves the shape of that operation and its relationship to the existing `/excavate` skill.

## The reframe

The original excavate skill was built to extract specs well enough from existing code that the code could be deleted and regenerated cleanly. That never worked, because pure spec-driven development from existing code is a fiction. Specs are always slightly wrong relative to what shipped.

The honest goal is smaller and more useful: reference docs augment code, they don't replace it. The code stays the source of truth. Reference captures what the code cannot say — the invariants, the why, the cross-cutting constraints, the context that isn't expressed syntactically.

Under this reframe, distill isn't a new skill. It's a second seed path for excavate, and excavate gets renamed.

## Shape

- **Single skill, renamed.** `/excavate` becomes `/distill`.
- **Two seed modes.** `/distill code` (what excavate does today, tuned down) and `/distill build` (the new direction — reading specs, plans, and brainstorms as raw material).
- **Same core operation.** Both modes verify against the code before writing anything. The mode only changes what seeds the session.

## The shape rule for reference

Reference contains only what the code cannot tell you. Not function signatures. Not endpoint lists. Not restatements of what a reader could recover by grep. The invariants, the cross-cutting rules, the why-it-is-this-way.

This rule does the "tuning down" of the old excavate automatically. Today's excavate produces layered summaries that partially mirror the code. Under this rule, most of that drops away. Reference reads like marginalia on the codebase.

## Core operation

Whatever the seed, distill's inner loop is the same:

1. Read the seed (build artifact for `/distill build`, feature area of code for `/distill code`).
2. Verify against current code. Identify mismatches between what the seed claims and what the code does.
3. Present promotion candidates, each already reconciled against code. When the seed disagrees with the code, surface the mismatch explicitly.
4. Human gates each candidate: promote the code's truth, correct-and-promote, or skip. Human also decides placement and wording.

This is heavier than "AI reads spec, proposes paragraphs." That weight is the point. The whole motivation is that build artifacts are close but always slightly wrong. A distill that trusted them would propagate the slightly-wrongness into reference, which is supposed to be the version that's right.

## Output characteristics

- **Variable fan-out.** A distill session over one spec file might write a single paragraph into a new reference file, or a sentence each into twelve existing reference files, or nothing at all.
- **Null output is valid.** If the seed's claims are all already discoverable from code, the right answer is zero reference changes. No pressure to invent promotion-worthy material. Matches principle 1 from the capture-skill principles (templates that demand N things hallucinate N things).
- **Reference docs are living.** Distill revises to match current code rather than appending history. Reference under `current` status means "matches the code right now," which gives `outdated` real meaning.

## What feeds distill build, in order of expected yield

- **Specs.** Primary feedstock. Specs describe intent; code describes mechanism; the gap between them is where invariants live.
- **Plans.** Secondary. Useful when the plan recorded something surprising that didn't make it back to the spec.
- **Brainstorms and research.** Tertiary. Ideally these were already captured in the spec. If not, that's a second-order signal worth promoting.

## Placement

Reference has no prescribed topology. Distill navigates it the same way an engineer navigates code when deciding where a new file goes: read the existing tree, follow the convention, place new material alongside similar material. First file in an empty reference tree establishes the convention. Frontmatter (title, tags, modules) aids search the way filenames and directory names do.

This disposes of the "reference as a skill" open question for placement purposes. Reference is a directory with good frontmatter, queried by grep and file reads. A dedicated `/reference` query skill may eventually be useful, but it is not a prerequisite for distill.

## Build artifacts are historical

With distill in place, build artifacts stop being treated as source-of-truth-by-proxy. They are historical documents. They may happen to match reality, but probably not — that's what distill is for.

- Safe to delete at any time.
- Better to distill first.
- `/tend` gains awareness: a spec with status `implemented` is not archivable until distill has been offered on it. Otherwise the reality-capture opportunity gets lost when hygiene runs.

## How the capture-skill principles apply

The three principles bind capture skills (retro, extraction). Distill is not a capture skill in the same sense — it's a promotion operation, not an observation or interpretation of experience. But two principles still matter:

- **Principle 1 (no forced N).** Null output is valid. Variable fan-out is valid. Distill must not manufacture promotion-worthy material to fill a template.
- **Principle 3 (human gate for judgment).** Distill's AI surfaces candidates and proposes code-verified forms. The human decides whether each one is actually reference-worthy and where it belongs. Without the gate, hallucination relocates rather than resolves.

Principle 2 (learn from mistakes only) does not apply. Reference is not a mistake log.

## Open questions

- **First-time distill on an empty reference tree.** Probably the same as writing the first file of a new codebase — nothing special, you just start. Worth confirming once the first real session runs.
- **Dedup across runs.** Running distill twice on the same spec should naturally deduplicate via the code-verification step: if a claim is already in reference and matches the code, no change is proposed. Worth validating once implemented.
- **How aggressively to "tune down" the existing excavate.** The spec-replacement ambition is gone; the reference-doc-writing behavior stays. The exact shape of what disappears is an implementation question for the refactor spec (roadmap step 4).
- **Whether the tend-gating on undistilled specs is enforcement or prompt.** `/tend` could refuse to archive, or could offer distill first with the option to skip.

## Next steps

Feeds roadmap step 5 (implement `/distill`). Also feeds roadmap step 4 (plugin-wide refactor) — the rename from `/excavate` to `/distill` and the `/tend` gating live there.
