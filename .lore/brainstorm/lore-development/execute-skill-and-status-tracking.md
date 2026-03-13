---
title: Execute Skill and Status Tracking
date: 2026-01-29
status: declined
tags: [execution, status-tracking, workflow, breakdown]
modules: [lore-development]
related: [.lore/retros/lore-development/remove-breakdown-execute.md]
---

# Brainstorm: Execute Skill and Status Tracking

## Problem

When working through a breakdown, the AI:
1. Doesn't mark chunks as complete (no tracking mechanism exists)
2. Skips the review step (testing happens, review doesn't)

The user's CLAUDE.md defines `research → plan → implement → review → test` but review gets ignored in practice.

## Root Causes

**No tracking mechanism**: The breakdown document structure has no status fields. There's nothing to mark, so nothing gets marked.

**"Implementation" feels complete after code is written**: The AI treats "implement" as the whole task rather than 1/3 of execution. Review and test are mentally separate, and review especially gets dropped.

## Solution

Two changes working together:

### 1. Update Breakdown Skill

Add status tracking to the document structure. Each chunk gets a status field:

```markdown
### 1. [Chunk Name]
**Status**: Not Started
**What**: Brief description
**Delivers**: What's usable after this chunk
**Depends on**: Any prerequisites
```

Status values: `Not Started` | `In Progress` | `Done`

The breakdown skill now provides the framework for tracking. The document becomes the source of truth for progress.

### 2. Create Execute Skill

A new skill that orchestrates working through chunks. Key insight: execution is a three-phase cycle, not just "write code."

**Execute cycle per chunk:**
1. **Implement** - Write the code
2. **Review** - Fresh-context review of the work (use sub-agent)
3. **Test** - Verify tests exist and pass

A chunk isn't "Done" until all three phases complete.

**Execute skill responsibilities:**
- Read the breakdown, find next incomplete chunk
- Run the implement → review → test cycle
- Update chunk status in the breakdown document
- Move to next chunk or report completion

## Why This Works

- **Status tracking is built into the artifact** (breakdown document), not session-local
- **Execute skill enforces the full cycle** - review can't be skipped because it's part of the skill's definition
- **Document-centric approach** matches lore-development's philosophy
- **Visible progress** - anyone can look at the breakdown and see what's done

## Open Questions

- Should execute handle one chunk at a time, or loop through all?
- How prescriptive should the review step be? (Sub-agent? Checklist? Both?)
- Should execute create Claude Code tasks (TaskCreate) as a secondary tracking mechanism, or keep it purely document-based?

## Next Steps

1. Update breakdown skill to include status fields in template
2. Create execute skill with implement → review → test cycle
3. Test the workflow end-to-end
