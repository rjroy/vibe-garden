---
title: Compound loop implementation for lore-development
date: 2026-01-30
status: complete
tags: [methodology, compound-engineering, feedback-loop, plugin-development]
modules: [lore-development]
---

# Retro: Compound Loop Implementation

## Summary

Added the "compound loop" to lore-development: a feedback mechanism where past learnings automatically surface during new work. Created `lore-researcher` agent, shared frontmatter schema, and updated 8 skills to close the loop.

## What Went Well

- **Brainstorm-to-spec-to-implementation flow was smooth**: The compound-engineering article provided clear inspiration, and the brainstorm captured the key insight (compounding happens in retrieval, not capture) that shaped the design.

- **Single source of truth worked**: Creating `shared/frontmatter-schema.md` and having all skills load it (rather than duplicating templates) keeps the system maintainable. One file to update when schema changes.

- **Fresh-eyes review caught real issues**: The lore-docs-reviewer agent identified that skills were duplicating templates instead of loading the schema. Without that review, skills would have diverged over time.

- **Scope stayed tight**: Resisted the urge to add 30+ agents like compound-engineering. One search agent, one schema file, minimal changes to existing skills.

## What Could Improve

- **First pass duplicated templates**: Initially added inline frontmatter examples to each skill rather than instructing them to load the schema. Had to go back and fix this. Should have caught this during spec review.

- **Excavate was forgotten initially**: The spec didn't mention `.lore/reference/` documents from `/excavate`. Had to add it after the fact. When modifying document structure, check all document types.

- **Open questions file was overhead**: Created a questions file to track decisions, but ended up resolving everything in the same session anyway. For single-session work, questions can stay in conversation.

## Lessons Learned

**"Load the schema" not "here's the template"**: When multiple skills need the same structure, they should load a shared file, not have copies. Copies drift. The instruction matters: "Reference X" means "it exists somewhere"; "Load X" means "read it before proceeding."

**The compound loop has three parts**: Capture (retro), Store (frontmatter), Retrieve (lore-researcher). Lore-development already had capture. Adding structured storage and automatic retrieval closed the loop.

**Agent for search preserves context**: Using a subagent for lore-researcher means the search happens in fresh context, and findings return without polluting the main conversation with grep output.

**Schema needs all document types**: When creating a shared schema, enumerate every document type the plugin produces. Missing one (like excavation references) means that type won't participate in the system.

## Artifacts

- Brainstorm: `.lore/brainstorm/lore-development/compound-loop-lore-development.md`
- Spec: `.lore/specs/lore-development/lore-researcher-agent.md`
- Agent: `lore-development/agents/lore-researcher.md`
- Schema: `lore-development/shared/frontmatter-schema.md`
- Updated skills: retro, specify, brainstorm, research, ddp, prep-plan, tend, excavate

## Testing Required

Before merging:
1. Test `../../shared/` path loading works with local plugin
2. Run `/tend` to retrofit existing `.lore/` documents
3. Test `/specify` invokes lore-researcher automatically
