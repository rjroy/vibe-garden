---
title: Excavate Process
date: 2026-01-28
status: complete
tags: [excavate, progressive-discovery, memory-loop, documentation]
modules: [lore-development]
---

# Retro: Excavate Process

## Summary

Documented the Memory Loop codebase using the `/lore-development:excavate` skill. Produced 13 specs (7 features, 6 infrastructure) across 6 commits in a single session.

## What Went Well

- **Progressive discovery worked**: Starting with Ground, then following connections to infrastructure and sub-features naturally mapped the system without overwhelm.

- **User corrections improved output quality**: Early feedback on tab naming (Ground not Home), feature boundaries (ConfigEditorDialog vs SettingsDialog), and missed features (Pair Writing) caught gaps before they compounded.

- **Infrastructure-first ordering helped**: Documenting vault-selection, extraction, configuration before the tabs meant the user-facing specs could reference established infrastructure.

- **Surface surveyor agent was thorough**: The traces produced rich detail on scheduling, cost controls, error handling that would have been tedious to gather manually.

- **Feature vs infrastructure distinction was useful**: Recognizing that WebSocket handlers and /api/sessions were communication infrastructure (not features) led to a better Communication Layer spec rather than fragmented docs.

## What Could Improve

- **Discovery stopped at one layer**: I found what Ground contains (widgets), but when excavating Recall I only documented what it shows (tree, viewers), not what you can do from there (Pair Writing). The "Edit" button was right in the UI. Progressive discovery should trace actions, not just contents.

- **Skill template text leaked into response**: The example session from the excavate README appeared verbatim in my first response ("No existing specs found..."). The skill format needs clearer separation between instructions and example dialogue.

- **REST endpoint paths were wrong initially**: I wrote simplified paths (`/files/*`) instead of actual paths (`/api/vaults/:vaultId/files/*`). Should have verified route structure before documenting.

- **Some specs got verbose**: Card Generator and Communication Layer are detailed but long. Could have been more concise if I'd trimmed implementation details that don't affect understanding.

- **Index maintenance was manual**: Had to remember to update the excavation index after each spec. Would be cleaner if the skill tracked this automatically or prompted for it.

## Lessons Learned

**Ask about naming early**: The Ground/Capture/Think/Recall names vs internal modes (home/note/discussion/browse) caused confusion. Getting naming conventions upfront prevents rework.

**Infrastructure often hides in "entry points"**: WebSocket handlers, /api/sessions, and Card Generator all sounded like features but turned out to be infrastructure supporting other features. The question "is this user-facing or machinery?" separates them.

**Cross-referencing specs builds coherence**: Adding "Connected Features" tables and updating related specs (like Spaced Repetition referencing Card Generator) makes the documentation navigable rather than isolated files.

**Verify before documenting**: The REST endpoint mistake would have been caught by reading `routes/index.ts` first. "Read the code, then document" not "guess and document."

**Trace actions, not just contents**: "What does this feature contain?" finds widgets and sub-views. "What can you do from here?" finds Pair Writing. Each feature should be traced for both what it shows AND what actions it enables.

## Artifacts

- `.lore/work/excavations/index.md` - Master tracking
- `.lore/work/specs/*.md` - 7 feature specs
- `.lore/work/specs/_infrastructure/*.md` - 6 infrastructure specs
- 6 commits on `docs/excavate` branch
