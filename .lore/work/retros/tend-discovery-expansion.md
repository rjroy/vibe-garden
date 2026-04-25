---
title: Tend skill should address discovery, not just status hygiene
date: 2026-02-04
status: complete
tags: [lore-development, tend, discovery, organization, methodology]
modules: [tend-skill]
related: []
---

# Retro: Tend Skill Discovery Expansion

## Summary

Ran `/tend` on Memory Loop's `.lore/` directory (41 documents). The skill successfully identified and corrected 3 stale statuses. However, the session surfaced a larger gap: tend addresses *accuracy* but not *discoverability*. A well-tended lore library should be easy to navigate for both humans and AI, not just correct.

## What Went Well

- **Status verification worked**: Cross-referencing specs with plans, plans with retros, and checking for implementation code caught real drift (brainstorm marked open but spec implemented, spec marked approved but code exists).

- **Task tracking forced thoroughness**: Breaking the work into scan → identify stale → verify → present → update prevented rushing through documents.

- **Frontmatter schema was useful**: Having a single source of truth for valid status values per document type made verification unambiguous.

## What Could Improve

- **Flat directories don't scale**: With 13 reference docs, 4 specs, 3 brainstorms, 6 retros, the directories are manageable. At 15+ files per directory, scanning becomes a wall of text. Tend doesn't address this.

- **Related documents are scattered**: The daily-prep feature has documents in `brainstorm/`, `specs/`, `plans/`, `research/`, and `retros/`. You have to know the naming convention to find the full chain. No index or grouping makes this connection visible.

- **`related:` field is underused**: Many documents that should cross-reference don't. Tend doesn't audit this.

- **Completed work clutters active work**: Resolved brainstorms sit next to open ones. Implemented specs sit next to drafts. No archiving strategy.

## Lessons Learned

### Discovery is a separate problem from accuracy

Status hygiene answers "is this document's metadata correct?" Discovery answers "can I find what I need?" Both matter, but tend currently only addresses the first.

### The phone number principle applies to lore

Phone numbers have dashes because `5551234567` is harder to parse than `555-123-4567`. Similarly, 15 files in `specs/` is harder to scan than 3 subdirectories with 5 files each. Chunking aids human cognition and AI context management alike.

### AI discovery depends on declared relationships

The `lore-researcher` agent greps frontmatter fields. If two documents are conceptually related but neither has a `related:` link, the agent can't find the connection. The `related:` field isn't optional metadata; it's the discovery graph.

### Completed cycles could be archived as units

When brainstorm → spec → plan → retro all reach terminal status (resolved → implemented → executed → complete), the chain is done. Moving it to `_archive/feature-name/` would reduce noise in active directories while preserving the full context as a unit.

## Proposed Tend Extensions

| Current Behavior | Proposed Addition |
|------------------|-------------------|
| Check frontmatter exists | Create/update `index.md` per directory |
| Check status exists | Suggest subdirectories when count > 8-10 |
| Verify status accuracy | Audit `related:` field for missing cross-references |
| Update stale statuses | Offer to archive completed feature cycles |
| - | Flag naming inconsistencies |
| - | Detect orphan documents (no references, stale status) |

## Artifacts

- Memory Loop `.lore/` now has accurate statuses
- 3 documents updated: `brainstorm/daily-prep-system.md`, `specs/card-deduplication.md`, `research/daily-planning-science.md`

## Next Steps

Take this retro to lore-development plugin project to inform `/tend` skill improvements.
