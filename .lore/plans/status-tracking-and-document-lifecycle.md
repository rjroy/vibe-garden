# Plan: Status Tracking and Document Lifecycle for lore-development

**Status**: approved

## Context

Two brainstorm documents drive this work:

1. **execute-skill-and-status-tracking.md** - Problem: AI skips review step and doesn't mark chunks complete during implementation. Solution: Update breakdown to add status fields, create execute skill with implement → review → test cycle.

2. **document-lifecycle-and-lore-hygiene.md** - Problem: `.lore/` fills up with artifacts of unclear status (active, complete, abandoned). Solution: Add status to all documents, create tend skill for periodic hygiene.

Both brainstorms converged on a shared insight: **status tracking built into artifacts** is the key.

## Scope

Three changes:

1. **Update breakdown skill** - Add status field to chunk template
2. **Create execute skill** - Orchestrate implement → review → test cycle per chunk
3. **Create tend skill** - Periodic hygiene to ensure status accuracy

## Approach

### 1. Update Breakdown Skill

Add status field to chunk structure in `.lore/work/[feature-name].md`:

```markdown
### 1. [Chunk Name]
**Status**: Not Started
**What**: Brief description
**Delivers**: What's usable after this chunk
**Depends on**: Any prerequisites
```

Status values: `Not Started` | `In Progress` | `Done`

This provides the tracking mechanism that execute skill will update.

### 2. Create Execute Skill

New skill at `lore-development/skills/execute/SKILL.md`

**Core behavior:**
- Read breakdown from `.lore/work/`
- Find next incomplete chunk (first with Status != Done)
- Run three-phase cycle per chunk:
  1. **Implement** - Write the code
  2. **Review** - Sub-agent review with fresh context (use lore-docs-reviewer pattern)
  3. **Test** - Run tests, verify they pass
- Update chunk status in breakdown document
- Either continue to next chunk or report completion

**Key design decisions:**
- **Loop through all chunks** until done (user prefers efficiency over checkpoint granularity)
- Review uses **lore-docs-reviewer agent** for fresh context (reuse existing agent)
- Modifies the breakdown document in place (document as source of truth)
- Reports progress after each chunk (visibility even in loop mode)

### 3. Create Tend Skill

New skill at `lore-development/skills/tend/SKILL.md`

**Core behavior:**
- Scan all `.lore/` documents
- Check for missing status fields
- Verify status accuracy (did work actually complete?)
- Update only status field, nothing else
- Follow excavate's progressive discovery philosophy

**Status values by document type:**
- Specs: `draft` | `active` | `complete` | `abandoned`
- Plans: `draft` | `active` | `complete` | `superseded`
- Brainstorms: `open` | `incorporated` | `parked`
- Work breakdowns: Track chunk-level status (via execute)
- Research: `reference` | `stale`

**Key design decision:** Status can be descriptive and honest: `incorporated incorrectly`, `partially complete`, etc. Truth over optimism.

## Files to Modify/Create

### Modify
- `lore-development/skills/breakdown/SKILL.md` - Add status field to template

### Create
- `lore-development/skills/execute/SKILL.md` - New skill
- `lore-development/skills/tend/SKILL.md` - New skill

### Update (dependent)
- `lore-development/README.md` - Add new skills to skill table

## Decisions Made

1. **Execute loop behavior**: Loop until done (efficiency over granular checkpoints)
2. **Review implementation**: Reuse lore-docs-reviewer agent (no new agent needed)

## Verification

1. Create a test breakdown with multiple chunks
2. Run execute skill, verify:
   - Finds next incomplete chunk
   - Runs implement → review → test cycle
   - Updates status in breakdown document
3. Run tend skill, verify:
   - Finds documents without status
   - Reports on status accuracy
   - Updates only status fields
