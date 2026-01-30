---
name: plan
description: This skill orchestrates Claude Code's plan mode with project context, then persists the approved plan. Use when ready to plan implementation, thinking through technical approach, or wanting to capture planning decisions. Triggers include "plan the implementation", "how should we build this", "create a plan for", "think through the approach".
---

# Plan

Orchestrate planning with context, persist the result.

## When to Use

- Ready to plan implementation for a chunk of work
- Want to capture a planning session for future reference
- Need to think through technical approach

## Process

1. **Gather context** from `.lore/`:
   - Relevant specs from `.lore/specs/`
   - Work breakdown from `.lore/work/`
   - Research from `.lore/research/`
   - Brainstorms from `.lore/brainstorm/`

2. **Enter plan mode** using the `EnterPlanMode` tool. This transitions to Claude Code's native planning workflow where:
   - The codebase can be explored
   - Architecture can be designed
   - Trade-offs can be analyzed
   - The user approves or refines the plan

3. **After plan approval**, save the approved plan to `.lore/plans/` using the document structure below.

4. **If user declines plan mode**: Offer to save any discussion notes to `.lore/brainstorm/` instead. Planning conversations have value even if formal plan mode isn't used.

## Output

Save to `.lore/plans/[feature-or-chunk-name].md`

### Document Structure

```markdown
# Plan: [Feature/Chunk Name]

**Status**: draft

## Context
Links to relevant `.lore/` documents.

## Approach
High-level approach and key decisions.

## Steps
1. Step one
2. Step two
3. ...

## Considerations
Any technical decisions, trade-offs, or risks noted.
```

## Philosophy

This skill is a wrapper around Claude Code's native plan mode. It adds:

1. **Context loading** - Relevant `.lore/` documents are gathered before planning begins
2. **Persistence** - Approved plans are saved to `.lore/plans/` for future reference
3. **Graceful fallback** - If plan mode is declined, discussion notes can still be captured

The planning itself happens in plan mode, which has access to exploration tools (Glob, Grep, Read) and can design implementation approaches interactively with the user.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, performance, or architecture reviewers can validate technical decisions. Invoke relevant agents via Task tool and incorporate their insights.
