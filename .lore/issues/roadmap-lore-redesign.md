---
title: "Roadmap: lore directory redesign and capture-skill rework"
date: 2026-04-23
status: open
tags: [roadmap, directory-structure, capture-skills, retros, extraction]
modules: [lore-development]
related: [.lore/brainstorm/lore-directory-redesign.md, .lore/brainstorm/principles-for-capture-skills.md, .lore/issues/design-extraction-skill.md, .lore/issues/design-learned-structure.md]
---

# Roadmap: lore directory redesign and capture-skill rework

Sequenced path from the current `.lore/` tree to the three-directory model (`build/`, `reference/`, `learned/`) with redesigned capture skills.

## Steps

1. **Brainstorm the distill function.** Names the operation for taking findings from `build/` artifacts and filing their data (not the files) into `reference/`. "Distill" is the working word; candidates include *crystallize* and *inscribe*. Needs a brainstorm session to define: what triggers distillation, what units move (sections? paragraphs? full concepts?), how reference documents grow over time, whether distillation is a skill or an implicit part of other skills.

2. **Brainstorm the learn dialog.** The mistake-extraction skill. Looks at recent `build/` artifacts (or specific ones named by the user) and proposes updates to `learned/`. Must be a dialog, never automatic. Scope: trigger model, relevance ranking, presentation format, write mechanics, dedup. See `.lore/issues/design-extraction-skill.md` for the undesigned pieces.

3. **Strip `/retro` down to event recording.** Remove the graduation flow, the "What Went Well / What Could Improve / Lessons Learned" template, and all analysis vocabulary. Output becomes free-form notes with structured frontmatter. See `.lore/brainstorm/principles-for-capture-skills.md` for the binding principles.

4. **Refactor existing skills to the new hierarchy.** Every skill that writes to `.lore/` needs path updates: `/brainstorm` writes to `build/brainstorm/`, `/specify` to `build/specs/`, etc. Frontmatter schema consolidates (per-directory status values collapse). `/tend` learns the new hierarchy and gains the migration mode. `/lore-researcher` searches the new paths. Vision moves into `reference/`. This step is plugin-wide and probably wants its own spec and plan.

5. **Implement the two new skills.** `/distill` and `/learn`. Both live in the refactored plugin. Both consume the brainstorm outputs from steps 1 and 2.

## Ordering notes

**Steps 2 and 3 are coupled.** Stripping `/retro` before `/learn` exists leaves a window where users produce retro notes with no extraction path — lessons pile up and don't land anywhere. Either build step 2 first, or ship step 3 with a pointer that says "lessons now extract via `/learn` separately."

**Step 4 is larger than it reads.** Path strings live in every SKILL.md that writes artifacts. The frontmatter schema file needs updating. Agent descriptions (including Celeste's, which references `.lore/vision.md`) need updating. This is essentially "refactor the whole plugin," and the blast radius justifies its own spec + plan rather than a single pass.

**Step 1 and step 2 can run in parallel.** Different brainstorm sessions, different skills. No dependency between them beyond sharing the directory model.

## Out of scope (but named)

- **Reference as a skill, not just a directory.** Open question from the brainstorm: is `/lore-development:reference "how does auth work?"` a skill that walks the tree and returns a layered answer? If yes, that's a sixth step eventually.
- **Graduation to higher scopes.** Current `/retro` graduates Critical lessons to project CLAUDE.md and Universal lessons to `~/.claude/rules/lessons-learned.md`. Whether `/learn` replaces, coexists with, or graduates upward to those scopes is undecided. See `.lore/issues/design-learned-structure.md`.
- **Diagram splitting by purpose.** Some diagrams are session-bound (build), some are current-state (reference). The per-diagram decision is fine; no design needed.

## Dependencies on prior artifacts

- `.lore/brainstorm/lore-directory-redesign.md` — the three-directory model, the build → reference and build → learned pipelines.
- `.lore/brainstorm/principles-for-capture-skills.md` — the three principles binding retro, learn, and any future capture skill.
- `.lore/issues/design-extraction-skill.md` — scopes the brainstorm for step 2.
- `.lore/issues/design-learned-structure.md` — informs step 2 and step 5, and needs resolving before `/learn` can be spec'd.
