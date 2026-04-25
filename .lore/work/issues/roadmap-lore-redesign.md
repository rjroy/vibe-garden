---
title: "Roadmap: lore directory redesign and capture-skill rework"
date: 2026-04-23
status: approved
tags: [roadmap, directory-structure, capture-skills, retros, extraction]
modules: [lore-development]
related: [.lore/work/brainstorm/lore-directory-redesign.md, .lore/work/brainstorm/principles-for-capture-skills.md, .lore/work/issues/design-extraction-skill.md, .lore/work/issues/design-learned-structure.md]
---

# Roadmap: lore directory redesign and capture-skill rework

Sequenced path from the current `.lore/` tree to the three-directory model (`build/`, `reference/`, `learned/`) with redesigned capture skills.

## Steps

1. **Brainstorm the distill function.** *(Done 2026-04-23 — see `.lore/work/brainstorm/distill-function.md`.)* Key outcome: distill is not a new skill. `/excavate` is renamed to `/distill` with two seed modes (`/distill code`, `/distill build`), a shared code-verifying core, and a tightened shape rule for reference (contains only what the code cannot say). This reshapes step 4 (rename + tune-down) and step 5 (implement only `/learn` as a new skill; `/distill` is a refactor).

2. **Brainstorm the learn dialog.** *(Done 2026-04-24 — see `.lore/work/brainstorm/learn-dialog.md`.)* Key outcome: `/learn` is not an extractor. It's a user-invoked dialog for recording lessons in the moment the user recognizes them. Two-path opening (specific material or felt pattern), question-first progression, nothing-asserted ("nothing" is a valid user answer), terse write discipline with no length budget, and active dedup against existing `learned/` entries. The `design-extraction-skill.md` framing (auto-scan build/ for candidates) was wrong and is superseded.

3. **Strip `/retro` down to event recording.** Remove the graduation flow, the "What Went Well / What Could Improve / Lessons Learned" template, and all analysis vocabulary. Output becomes free-form notes with structured frontmatter. See `.lore/work/brainstorm/principles-for-capture-skills.md` for the binding principles.

4. **Refactor existing skills to the new hierarchy.** Every skill that writes to `.lore/` needs path updates: `/brainstorm` writes to `build/brainstorm/`, `/specify` to `build/specs/`, etc. Frontmatter schema consolidates (per-directory status values collapse). `/tend` learns the new hierarchy and gains the migration mode. `/lore-researcher` searches the new paths. Vision moves into `reference/`. This step is plugin-wide and probably wants its own spec and plan.

5. **Implement `/learn` and land the `/distill` refactor.** `/learn` is a new skill built from the step-2 brainstorm. `/distill` is the renamed-and-reshaped `/excavate`, per the step-1 brainstorm outcome; its refactor details belong in step 4's plugin-wide spec.

## Ordering notes

**Steps 2 and 3 are coupled.** Stripping `/retro` before `/learn` exists leaves a window where users produce retro notes with no extraction path — lessons pile up and don't land anywhere. Either build step 2 first, or ship step 3 with a pointer that says "lessons now extract via `/learn` separately."

**Step 4 is larger than it reads.** Path strings live in every SKILL.md that writes artifacts. The frontmatter schema file needs updating. Agent descriptions (including Celeste's, which references `.lore/reference/vision.md`) need updating. This is essentially "refactor the whole plugin," and the blast radius justifies its own spec + plan rather than a single pass.

**Step 1 and step 2 can run in parallel.** Different brainstorm sessions, different skills. No dependency between them beyond sharing the directory model.

## Out of scope (but named)

- **Reference as a skill, not just a directory.** Open question from the brainstorm: is `/lore-development:reference "how does auth work?"` a skill that walks the tree and returns a layered answer? If yes, that's a sixth step eventually.
- **Graduation to higher scopes.** Current `/retro` graduates Critical lessons to project CLAUDE.md and Universal lessons to `~/.claude/rules/lessons-learned.md`. Whether `/learn` replaces, coexists with, or graduates upward to those scopes is undecided. See `.lore/work/issues/design-learned-structure.md`.
- **Diagram splitting by purpose.** Some diagrams are session-bound (build), some are current-state (reference). The per-diagram decision is fine; no design needed.

## Dependencies on prior artifacts

- `.lore/work/brainstorm/lore-directory-redesign.md` — the three-directory model, the build → reference and build → learned pipelines.
- `.lore/work/brainstorm/principles-for-capture-skills.md` — the three principles binding retro, learn, and any future capture skill.
- `.lore/work/issues/design-extraction-skill.md` — scopes the brainstorm for step 2.
- `.lore/work/issues/design-learned-structure.md` — informs step 2 and step 5, and needs resolving before `/learn` can be spec'd.
