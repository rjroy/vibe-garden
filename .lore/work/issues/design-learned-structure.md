---
title: Design the internal structure of `.lore/learned/`
date: 2026-04-23
status: resolved
tags: [design-needed, learned, directory-structure, capture-skills]
modules: [lore-development]
related: [.lore/work/brainstorm/lore-directory-redesign.md, .lore/work/brainstorm/principles-for-capture-skills.md]
---

# Design the internal structure of `.lore/learned/`

The lore directory redesign names `.lore/learned/` as the home for operational imperatives ("what must I do, what should I never do"). Entry shape is constrained (asymmetric — mistakes only, never success). How entries are organized, indexed, and retrieved inside the directory is undesigned.

## What's known

- Purpose: operational imperatives for working in this project.
- Entries are asymmetric by shape. "Don't do X because Y happened." "If you find yourself doing X, stop — here's why." Never "do X because it worked."
- Populated by the extraction skill.
- Consumed by: future build work (probably via lore-researcher, or a dedicated query path).

## What's undesigned

- **Flat or categorized.** One directory with one file per lesson? Categorized subdirectories (by module, by pattern type, by severity)? A single `learned.md` that accumulates?
- **Entry granularity.** One file per mistake? Multiple related mistakes in one file? Is a file the atomic unit or is a section?
- **Frontmatter shape.** What fields does a learned entry need beyond common fields? Severity? Source retro? Evidence count (how many times the mistake has occurred)?
- **Retrieval model.** How does the user (or a skill) ask "what do I need to know about working on auth?" Greppable metadata? Query skill? Walk-the-directory and return relevant entries?
- **Lifecycle.** Do learned entries ever get retired? What makes an imperative stop being true? Is there a `superseded` status, or do they live forever?
- **Graduation beyond project.** Current `/retro` has Critical (project CLAUDE.md) and Universal (`~/.claude/rules/lessons-learned.md`) scopes. Does the new learned/ replace these, coexist with them, or graduate upward to them?

## Why this matters

The shape of learned/ directly affects the extraction skill (what it writes) and the lore-researcher's search path (what it queries). Specifying either before learned/ is structured risks baking in arbitrary decisions.

## Resolution path

Brainstorm session focused on this directory specifically. Likely informed by concrete examples — pick two or three existing retro lessons (from `.lore/work/retros/` under the current scheme) and work out what their learned/ form would look like. Shape emerges from examples, not abstractions.
