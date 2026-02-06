---
name: plan
description: This skill builds implementation plans as persistent, reviewable lore artifacts. Use when ready to plan how to build a specified feature. Triggers include "plan this", "make a plan", "how should we build this", "plan the implementation", "plan".
---

# Plan

Build an implementation plan and save it as a lore artifact.

## When to Use

- A spec exists and you're ready to plan how to build it
- Need to think through implementation approach, ordering, and delegation
- Want a reviewable plan that persists across sessions

## When to Skip

- The spec is simple enough that implementation is obvious (just build it)
- You need to explore options first (use `/design` instead)
- You don't have a spec yet (use `/specify` first)

## Process

1. **Search for related prior work**: Invoke the `lore-researcher` agent with the topic/feature description. Include findings in the Context section.

2. **Gather context** from `.lore/`:
   - The relevant spec from `.lore/specs/` (required -- a plan without a spec is guessing)
   - Design documents from `.lore/design/` if they exist
   - Related research or brainstorms

3. **Explore the codebase**: Use the Task tool with an Explore subagent to understand the current state of code relevant to this plan. What exists? What patterns are in use? Where will changes land?

4. **Present context summary** to the user. Confirm the spec is the right one and the scope is understood before drafting.

5. **Draft the plan** collaboratively with the user:
   - Map each spec requirement to concrete implementation steps
   - Order steps by dependency (what must exist before what)
   - Identify which steps benefit from fresh-context sub-agents
   - Include the validation approach

6. **Confirm with user** before saving.

7. **Save to `.lore/plans/`**

8. **Offer fresh-eyes review** (see below)

## Output

Save to `.lore/plans/[feature-name].md`

Use kebab-case for filenames. Match spec naming where a spec exists (e.g., if spec is `auth-flow.md`, plan is `auth-flow.md`).

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for plans.

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
**Delegation**: [inline / fresh-context sub-agent]

[What to do, concretely. Not pseudocode -- describe the change.]

### Step 2: [Description]

...

### Step N: Validate Against Spec

**Delegation**: fresh-context sub-agent (required)

Launch a sub-agent that reads the spec at [path], reviews the implementation, and flags any requirements not met. This step is not optional.

## Delegation Guide

Steps that benefit from fresh-context sub-agents:
- [Step X]: [why -- e.g., "large scope, context will be noisy by this point"]
- [Step Y]: [why]

Steps safe to run inline:
- [Step A]: [why -- e.g., "small, depends on Step A-1's output"]

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

## Spec Required

A plan without a spec is building without knowing what "done" means. If no spec exists, recommend `/specify` first. If the user insists on planning without a spec, proceed but note this in the plan's Open Questions as a risk.

## After Saving: Fresh-Eyes Review

After the plan is saved, run a fresh-eyes review. Plans drafted in conversation inherit assumptions from the discussion. A reviewer with fresh context reads only the plan and spec, catching gaps the author can't see.

Invoke the `plan-reviewer` agent on the saved plan using the Task tool. The agent evaluates plans through four lenses: spec coverage, step feasibility, scope discipline, and implementability. Present the findings and offer to address critical issues before implementation begins.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, performance, or architecture experts can identify implementation risks you might miss. Invoke relevant agents via Task tool and incorporate their insights.

## Linking to Specs

Plan documents must reference their parent spec:
- In frontmatter: `related: [.lore/specs/auth-flow.md]`
- In Spec Reference section: full requirement mapping

Plans can also reference design documents when the technical approach is non-trivial.
