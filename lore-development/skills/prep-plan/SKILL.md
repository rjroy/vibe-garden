---
name: prep-plan
description: This skill loads project context then enters Claude Code's plan mode. Use when ready to plan implementation with lore context, or wanting to capture planning decisions. Triggers include "prep for planning", "plan with context", "load context and plan", "prep-plan".
---

# Prep Plan

Load lore context, then enter plan mode.

## When to Use

- Ready to plan implementation for a chunk of work
- Want to capture a planning session for future reference
- Need to think through technical approach

## Process

1. **Search for related prior work**: Invoke the `lore-researcher` agent with the topic/feature description. Include any relevant findings in the plan's Context section.

2. **Gather context** from `.lore/`:
   - Relevant specs from `.lore/specs/`
   - Research from `.lore/research/`
   - Brainstorms from `.lore/brainstorm/`

3. **Enter plan mode** using the `EnterPlanMode` tool. This transitions to Claude Code's native planning workflow where:
   - The codebase can be explored
   - Architecture can be designed
   - Trade-offs can be analyzed
   - The user approves or refines the plan

4. **After plan approval**, save the approved plan to `.lore/plans/` using the document structure below.

5. **Offer fresh-eyes review** (see below).

6. **If user declines plan mode**: Offer to save any discussion notes to `.lore/brainstorm/` instead. Planning conversations have value even if formal plan mode isn't used.

## Output

Save to `.lore/plans/[feature-or-chunk-name].md`

### Document Structure

**Before writing**: Load `../../shared/frontmatter-schema.md` to get frontmatter field definitions and status values for plans.

```markdown
---
[frontmatter per schema]
---

# Plan: [Feature/Chunk Name]

## Context
Links to relevant `.lore/` documents.
Include findings from lore-researcher here.

## Approach
High-level approach and key decisions.

## Steps
1. Step one
2. Step two
3. ...

## Considerations
Any technical decisions, trade-offs, or risks noted.

## AI Validation
How the AI verifies completion (inherit from spec if exists, or define here).

**Defaults** (apply unless overridden):
- Unit tests with mocked time/network/filesystem/LLM calls (including Agent SDK `query()`)
- 90%+ coverage on new code
- Code review by fresh-context sub-agent

**Custom** (if needed):
- [Feature-specific validation steps]
```

## Philosophy

This skill is a wrapper around Claude Code's native plan mode. It adds:

1. **Context loading** - Relevant `.lore/` documents are gathered before planning begins
2. **Persistence** - Approved plans are saved to `.lore/plans/` for future reference
3. **Graceful fallback** - If plan mode is declined, discussion notes can still be captured

The planning itself happens in plan mode, which has access to exploration tools (Glob, Grep, Read) and can design implementation approaches interactively with the user.

## After Saving: Fresh-Eyes Review

After the plan is saved, offer a review:

> "Plan saved. Would you like a fresh-eyes review? This catches gaps and assumptions that are easy to miss when you're close to the work."

If yes: Invoke the `lore-docs-reviewer` agent on the saved plan using the Task tool. Present the findings and offer to address critical issues before moving on.

If no: Proceed. The user can always run the review later.

**Why this matters**: Plans written in conversation accumulate assumptions. A reviewer with fresh context reads only what's on the page, catching what the author can't see.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, performance, or architecture reviewers can validate technical decisions. Invoke relevant agents via Task tool and incorporate their insights.
