---
title: Dates don't belong in filenames
date: 2026-02-04
status: complete
tags: [lore-hygiene, file-organization, naming-conventions]
modules: [lore-development]
---

# Retro: Tend Skill Reorganization

## Summary

Ran `/lore-development:tend` across 50 documents. Major reorganization: removed dates from filenames, organized directories by `modules` field.

## What Went Well

- Module-based directory organization provides clear navigation for this project
- Reference updates via sed worked cleanly across all files
- Git rename tracking preserved history despite extensive moves

## What Could Improve

- Several files had been created without `modules` field, required manual assignment
- Initial file-by-file approach to reference updates was slow; batch sed was better

## Lessons Learned

**Dates in filenames are unnecessary.** Dates belong in frontmatter where they're queryable. Filenames with dates (`2026-01-30-feature.md`) create visual noise and sorting problems. Good directory structure aids discovery better than chronological prefixes.

**Module-based organization works when modules are consistent.** This project's `modules` field was reliable enough to drive directory structure. Not a universal solution, but effective when the field is maintained.

## Artifacts

- Commit: df2c8a2
- Changed: 52 files reorganized by module
