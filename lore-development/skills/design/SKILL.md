---
name: design
description: This skill makes technical decisions for complex problems. Use when the "how" IS the problem - algorithms, data structures, system boundaries, performance, security. Triggers include "design this", "what's the algorithm for", "how should this work technically", "technical approach for", "architecture for".
---

# Design

Make technical decisions when the "how" is the problem.

## When to Use

- **Algorithms**: Non-trivial logic that needs to be thought through
- **Data structures**: How things relate, what to store, how to index
- **System boundaries**: Where does this live? What owns what?
- **Performance-sensitive code**: Choices that affect speed/memory
- **Security-sensitive code**: Choices that affect attack surface

## When to Skip

Design is overhead when the implementation is obvious:
- UI changes where spec describes the outcome
- CRUD operations
- Wiring existing pieces together
- Configuration changes

## The 100 Forks Test

If you ran `/prep-plan` 100 times with current context:
- **Forks diverge**: AI invents different solutions. You need more context. Design provides it.
- **Forks converge**: AI finds the obvious solution. Spec is enough. Skip design.

## Process

1. **Search for related prior work**: Invoke the `lore-researcher` agent with the technical problem description. Include findings in the Context section.
2. Review any relevant `.lore/research/`, `.lore/brainstorm/`, or `.lore/specs/` context
3. Clarify the technical problem - what exactly needs deciding?
4. Explore approaches - at least 2-3 options with trade-offs
5. **Decide**: Pick an approach and document why
6. Define the interface/contract - how will other code interact?
7. Document edge cases
8. Confirm with user before saving
9. Save to `.lore/design/`
10. **Offer fresh-eyes review** (see below)

## Output

Save to `.lore/design/[topic].md`

Use kebab-case for filenames. Match spec naming where a spec exists (e.g., if spec is `history-sync.md`, design is `history-sync.md` or `history-sync-dedup-algorithm.md`).

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for design documents.

```markdown
---
[frontmatter per schema]
---

# Design: [Topic]

## Problem
What technical problem are we solving? Link to spec if one exists.

## Constraints
- Technical constraints
- Performance requirements
- Integration points
- Security considerations

## Approaches Considered

### Option 1: [Name]
Description of the approach.

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

### Option 2: [Name]
Description of the approach.

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

## Decision
Which approach and why. **This section is required.** A design without a decision is just research.

## Interface/Contract
How other code will interact with this:
- Function signatures
- Data structures
- Protocols
- APIs

## Edge Cases
Known edge cases and how they're handled:
- Edge case 1: Handled by...
- Edge case 2: Handled by...

## Open Questions
(Optional) Things still TBD that don't block implementation.
```

## What vs How

Design sits between spec and plan:

| Document | Answers | Example |
|----------|---------|---------|
| **Spec** | What are we building? | "Deduplicate history entries" |
| **Design** | How does it work? | "Use content hashing with LRU eviction" |
| **Plan** | How do we build it? | "Add HashIndex class in src/index.ts" |

**Design is "how it works" in the abstract.** Algorithms, data structures, protocols. Implementation-agnostic where possible.

**Plan is "how to build it" in the concrete.** Files, functions, dependencies. Implementation-specific.

## Research vs Design

Both explore options. The difference is commitment:

| Document | Output | Decision Required? |
|----------|--------|-------------------|
| **Research** | "Here are the options" | No |
| **Design** | "Here's what we're doing and why" | Yes |

If you're documenting options without picking one, that's research. Design requires the Decision section.

## After Saving: Fresh-Eyes Review

After the design is saved, run a fresh-eyes review. Designs written in conversation accumulate assumptions. A reviewer with fresh context reads only what's on the page, catching what the author can't see.

Invoke the `spec-reviewer` agent on the saved design using the Task tool. The agent works for both specs and designs - it checks for clarity, gaps, and ambiguity. Present the findings and offer to address critical issues before moving on.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, performance, or architecture experts can identify trade-offs you might miss. Invoke relevant agents via Task tool and incorporate their insights.

## Linking to Specs

Design documents should reference their parent spec when one exists:
- In frontmatter: `related: [.lore/specs/history-sync.md]`
- In Problem section: "See [Spec: history-sync](.lore/specs/history-sync.md) for requirements."

Design documents can also stand alone for technical problems that don't have user-facing requirements.
