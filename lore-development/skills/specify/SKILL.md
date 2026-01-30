---
name: specify
description: This skill defines requirements and success criteria for features. Use when capturing requirements, defining what "done" looks like, or documenting constraints. Triggers include "write a spec for", "define the requirements", "what should this do", "capture the requirements".
---

# Specify

Define what to build and how to know it's done.

## When to Use

- Capturing requirements for a feature or change
- Defining success criteria
- Documenting constraints or boundaries

## Process

1. Review any relevant `.lore/research/` or `.lore/brainstorm/` context
2. Ask clarifying questions about scope and success
3. Draft the specification
4. **Probe for stubs**: For each major action identified, ask "Are we stubbing [action], or defining it now?" User can choose to define inline or mark as stub.
5. **Probe for validation**: Ask "Are defaults sufficient for AI validation, or does this feature need custom checks?" Most features use defaults; some need specific verification.
6. Confirm with user before saving
7. Save to `.lore/specs/`
8. **Offer fresh-eyes review** (see below)

## Output

Save to `.lore/specs/[feature-name].md`

### Document Structure

```markdown
# Spec: [Feature Name]

**Status**: draft

## Overview
One paragraph describing what this is.

## Entry Points
How users arrive at this feature:
- [Entry description] (from [source])

## Requirements
- REQ-1: [requirement]
- REQ-2: [requirement]

## Exit Points
| Exit | Triggers When | Target |
|------|---------------|--------|
| [Exit name] | [User action or condition] | [STUB: target-name] or [Spec: existing-spec] |

## Success Criteria
How we know this is done:
- [ ] Criterion 1
- [ ] Criterion 2

## AI Validation
How the AI verifies completion before declaring done.

**Defaults** (apply unless overridden):
- Unit tests with mocked time/network/filesystem/LLM calls (including Agent SDK `query()`)
- 90%+ coverage on new code
- Code review by fresh-context sub-agent

**Custom** (feature-specific, if needed):
- [e.g., "CLI output matches format in examples/"]
- [e.g., "Generated files parse without errors"]

## Constraints
Any boundaries or limitations.

## Context
Links to related `.lore/` documents if relevant.
```

## Stub Notation

When a feature connects to undefined areas, mark them as stubs:

**Format**: `[STUB: stub-name]`

**Naming**: Use kebab-case matching spec filename conventions (e.g., `auth-flow`, `payment-processing`). The stub name should match what the spec file would be named when defined.

**Examples**:
- `[STUB: user-authentication]` - Links to undefined auth feature
- `[Spec: checkout-flow]` - Links to existing `.lore/specs/checkout-flow.md`

**When to stub**: Mark something as a stub when it's needed by this feature but defining it would expand scope beyond the current layer. The stub becomes a documented "known unknown" that can be specified later.

## Keep It Light

Don't over-specify. Capture the essence. Trust that implementation will fill gaps appropriately.

## After Saving: Fresh-Eyes Review

After the spec is saved, offer a review:

> "Spec saved. Would you like a fresh-eyes review? This catches clarity issues and gaps that are easy to miss when you're close to the work."

If yes: Invoke the `lore-docs-reviewer` agent on the saved spec using the Task tool. Present the findings and offer to address critical issues before moving on.

If no: Proceed. The user can always run the review later.

**Why this matters**: Specs written in conversation accumulate assumptions. A reviewer with fresh context reads only what's on the page, catching what the author can't see.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, compliance, or architecture experts can identify requirements you might miss. Invoke relevant agents via Task tool and incorporate their insights.
