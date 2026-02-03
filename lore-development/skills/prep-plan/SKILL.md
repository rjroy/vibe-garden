---
name: prep-plan
description: This skill loads project context then enters Claude Code's plan mode. Use when ready to plan implementation with lore context. Triggers include "prep for planning", "plan with context", "load context and plan", "prep-plan".
---

# Prep Plan

Load lore context, then enter plan mode.

## When to Use

- Ready to plan implementation for a chunk of work
- Need to think through technical approach with project context loaded

## Process

1. **Search for related prior work**: Invoke the `lore-researcher` agent with the topic/feature description. Summarize relevant findings.

2. **Gather context** from `.lore/`:
   - Relevant specs from `.lore/specs/`
   - Research from `.lore/research/`
   - Brainstorms from `.lore/brainstorm/`

3. **Present context summary** to the user before entering plan mode. This ensures the planning session starts with shared understanding.

4. **Provide plan structure guidance**: Before entering plan mode, present the mandatory structure that the plan must follow:

   **Spec Reference Section** (required)
   - Include the path to the relevant spec file
   - First implementation task must be "Read the spec file at [path]"

   **Implementation Approach Section** (required)
   - Each major implementation phase should be delegated to a sub-agent with fresh context
   - Sub-agents receive: the relevant spec section + their specific task
   - This prevents context drift during implementation

   **Validation Section** (required)
   - Final task: Launch a fresh-context sub-agent to validate implementation against spec
   - Validation agent reads the spec, reviews the implementation, and flags any gaps
   - This catches drift before declaring work complete

5. **Enter plan mode** using the `EnterPlanMode` tool.

Once plan mode is entered, this skill's work is complete. Plan mode handles the rest: exploration, design, trade-off analysis, and user approval.

## What Happens in Plan Mode

Plan mode is Claude Code's native planning workflow. It has access to exploration tools (Glob, Grep, Read) and works interactively with the user to design an implementation approach.

The plan is written to a scratchpad file during plan mode. When the user approves the plan, implementation begins from that plan.

## Philosophy

This skill is a thin wrapper around plan mode. Its only job is context loading: gathering relevant `.lore/` documents so the planning session starts informed rather than cold.

The planning itself happens in plan mode. This skill does not persist plans to `.lore/plans/` or invoke reviewers. Those would require control after plan mode exits, which this skill doesn't have.
