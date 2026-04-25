---
name: prep-plan
description: This skill builds implementation plans as persistent, reviewable lore artifacts. Use when ready to plan how to build something, break work into ordered steps, or decide what to delegate to sub-agents. Triggers include "prep plan", "prep-plan", "prepare a plan", "plan this", "make a plan", "break this into steps", "plan the implementation", "what order should we build this". Not for exploring technical approaches (use /design) or defining requirements (use /specify).
---

# Plan

Build an implementation plan and save it as a lore artifact.

## When to Use

- Ready to plan how to build something -- with or without a spec
- Need to think through implementation approach, ordering, and delegation
- Want a reviewable plan that persists across sessions

## Critical: Do Not Enter Plan Mode

**Do NOT use the `EnterPlanMode` tool.** This skill produces a plan document as its final deliverable, not a precursor to code changes. Claude Code's built-in plan mode assumes "plan then implement," but here the plan is the output. Implementation is a separate step invoked via `/implement`.

This skill is a document-authoring workflow, like `/specify`. It gathers context, drafts a document collaboratively, saves it, and runs a review. No code is written.

## Process

1. **Context check**: Before starting, scan the recent conversation history. If `/specify`, `/design`, or `/brainstorm` was invoked in the last 10-20 messages, warn the user:

   > "I notice we just finished [spec/design/brainstorm] work in this session. Plans written in hot context inherit unstated assumptions - what feels obvious now won't be obvious reading the plan cold. The curse of knowledge means I'll skip details because 'we just talked about this.'
   >
   > Recommendation: Start a fresh session, then run `/prep-plan` and reference the spec/design file. The plan will be stronger.
   >
   > Continue anyway?"

   If the user chooses to continue, proceed. If they decline, stop here.

2. **Search for related prior work**: Use the Task tool to invoke the `lore-researcher` agent with the topic/feature description. **Do not run in background.** Wait for the result before continuing. Include findings in the Codebase Context section.

3. **Gather context** from `.lore/`:
   - Relevant specs from `.lore/work/specs/` (if they exist)
   - Design documents from `.lore/work/design/` (if they exist)
   - Related research or brainstorms

4. **Explore the codebase**: Use the Task tool with an Explore subagent to understand the current state of code relevant to this plan. What exists? What patterns are in use? Where will changes land?

5. **Surface gaps**: Before presenting anything, review the collected context for clarity problems. Look for:
   - Ambiguous requirements (could mean more than one thing)
   - Contradictions between spec, design, and current code
   - Unstated assumptions you'd need to fill to write concrete steps
   - Missing information (error handling, edge cases, integration points not addressed)

   If gaps exist, list them and ask the user to resolve them before continuing. Do not fill gaps with plausible defaults. A plan built on assumptions the user didn't approve will fail during implementation or review.

   If the context is clear enough to plan against, say so and proceed.

6. **Present context summary** to the user. Confirm scope is understood before drafting.

7. **Draft the plan** collaboratively with the user:
   - Map requirements to concrete implementation steps (from spec if one exists, from conversation if not)
   - Order steps by dependency (what must exist before what)
   - Identify which steps need specialized expertise (security, frontend, performance, etc.)
   - Include the validation approach

8. **Confirm with user** before saving.

9. **Save to `.lore/work/plans/`**

10. **Offer fresh-eyes review** (see below)

## Output

Save to `.lore/work/plans/[feature-name].md`

Use kebab-case for filenames. Match spec naming where a spec exists (e.g., if spec is `auth-flow.md`, plan is `auth-flow.md`). When no spec exists, derive the filename from the feature or goal description.

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for plans.

The plan structure adapts based on whether a spec exists:

#### With Spec

```markdown
---
[frontmatter per schema]
---

# Plan: [Feature Name]

## Spec Reference

**Spec**: [path to spec]
**Design**: [path to design, if one exists]

Requirements addressed:
- REQ-XX-1: [brief description] → Steps [N, M]
- REQ-XX-2: [brief description] → Step [P]
- ...

## Codebase Context

What the exploration found:
- [Relevant existing code, patterns, conventions]
- [Where changes will land]
- [Dependencies and integration points]

## Implementation Steps

### Step 1: [Description]

**Files**: [files affected]
**Addresses**: REQ-XX-N
**Expertise**: [none needed / specific domain -- e.g., "security review", "frontend accessibility"]

[What to do, concretely. Not pseudocode -- describe the change.]

### Step 2: [Description]

...

### Step N: Validate Against Spec

Launch a sub-agent that reads the spec at [path], reviews the implementation, and flags any requirements not met. This step is not optional.

## Delegation Guide

Steps requiring specialized expertise:
- [Step X]: [what expertise -- e.g., "security review of auth flow"]
- [Step Y]: [what expertise -- e.g., "performance audit of hot path"]

Consult `.lore/lore-agents.md` (if it exists) for available domain-specific agents.

## Open Questions

(Optional) Things to resolve during implementation that don't block starting.
```

#### Without Spec

```markdown
---
[frontmatter per schema]
---

# Plan: [Feature Name]

## Goal

What we're building and why. This section replaces the spec reference -- state the objective clearly enough that the validation step can check against it.

## Codebase Context

What the exploration found:
- [Relevant existing code, patterns, conventions]
- [Where changes will land]
- [Dependencies and integration points]

## Implementation Steps

### Step 1: [Description]

**Files**: [files affected]
**Expertise**: [none needed / specific domain -- e.g., "security review", "frontend accessibility"]

[What to do, concretely. Not pseudocode -- describe the change.]

### Step 2: [Description]

...

### Step N: Validate Against Goal

Launch a sub-agent that reads the Goal section above, reviews the implementation, and flags anything that doesn't match. This step is not optional.

## Delegation Guide

Steps requiring specialized expertise:
- [Step X]: [what expertise -- e.g., "security review of auth flow"]
- [Step Y]: [what expertise -- e.g., "performance audit of hot path"]

Consult `.lore/lore-agents.md` (if it exists) for available domain-specific agents.

## Open Questions

(Optional) Things to resolve during implementation that don't block starting.
```

## What vs How

Plan sits at the concrete end of the lore chain:

| Document | Answers | Example |
|----------|---------|---------|
| **Spec** | What are we building? | "Deduplicate history entries" |
| **Design** | How does it work? | "Use content hashing with LRU eviction" |
| **Plan** | How do we build it? | "Add HashIndex class in src/index.ts, step 1 of 4" |

A plan names files, functions, and steps. That's what makes it a plan and not a design.

## With or Without a Spec

A plan with a spec gets requirement traceability -- every REQ maps to steps, and the plan-reviewer can verify coverage. This is the stronger path for complex work.

A plan without a spec is fine for straightforward work where you know what you're building. The Goal section stands in for the spec. The plan-reviewer checks against the Goal instead of requirement IDs.

When in doubt, a spec helps. But don't make it a gate.

## After Saving: Fresh-Eyes Review

After the plan is saved, run a fresh-eyes review. Plans drafted in conversation inherit assumptions from the discussion. A reviewer with fresh context reads only the plan and spec (if one exists), catching gaps the author can't see.

Invoke the `plan-reviewer` agent on the saved plan using the Task tool. The agent evaluates plans through four lenses: spec coverage (or goal alignment), step feasibility, scope discipline, and implementability. Present the findings and offer to address critical issues before implementation begins.

## Linking to Specs

When a spec exists, plan documents should reference it:
- In frontmatter: `related: [.lore/work/specs/auth-flow.md]`
- In Spec Reference section: full requirement mapping

Plans can also reference design documents when the technical approach is non-trivial.
