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

1. **Search for related prior work**: Invoke the `lore-researcher` agent with the topic/feature description. Include any findings in the spec's Context section.
2. Review any relevant `.lore/research/` or `.lore/brainstorm/` context
3. Ask clarifying questions about scope and success
4. Draft the specification
5. **Probe for stubs**: For each major action identified, ask "Are we stubbing [action], or defining it now?" User can choose to define inline or mark as stub.
6. **Probe for validation**: Ask "Are defaults sufficient for AI validation, or does this feature need custom checks?" Most features use defaults; some need specific verification.
7. Confirm with user before saving
8. Save to `.lore/specs/`
9. **Offer fresh-eyes review** (see below)

## Output

Save to `.lore/specs/[feature-name].md`

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for specs.

**Requirement prefix**: Each spec has a unique prefix for its requirement IDs. See "Requirement ID Prefix" section below.

```markdown
---
[frontmatter per schema]
---

# Spec: [Feature Name]

## Overview
One paragraph describing what this is.

## Entry Points
How users arrive at this feature:
- [Entry description] (from [source])

## Requirements
- REQ-{PREFIX}-1: [requirement]
- REQ-{PREFIX}-2: [requirement]

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
Include findings from lore-researcher here.
```

## Requirement ID Prefix

Requirements use namespaced IDs to avoid collisions across specs: `REQ-{PREFIX}-N`

**Auto-generation (default):**
- Derived from spec filename
- Take first 2 segments of kebab-case name, uppercase
- Max 12 characters
- Examples:
  - `auth-flow.md` → `REQ-AUTH-FLOW-1`
  - `user-authentication-oauth2.md` → `REQ-USER-AUTH-1`
  - `checkout.md` → `REQ-CHECKOUT-1`

**Manual override:**
Add `req-prefix` to frontmatter when you want explicit control:
```yaml
---
req-prefix: AUTH
---
```
Then: `REQ-AUTH-1`, `REQ-AUTH-2`, etc.

Use manual override when:
- Auto-generated prefix is awkward or unclear
- You want shorter IDs for frequently-referenced specs
- Coordinating prefixes across a large project

**Collision detection:** The `/tend` skill warns if two specs would generate the same prefix.

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

## What vs How

A spec answers two questions:
1. **What** are we building?
2. **How** will we verify it's done?

It does NOT answer "How do we build it?" That belongs in the plan.

**Two types of "how":**
- "How to verify" (belongs in spec): "User can authenticate and access protected resources"
- "How to build" (belongs in plan): "Use JWT tokens with RS256 algorithm, store refresh tokens in httpOnly cookies"

**Anti-patterns** (you've crossed into plan territory):
- Specifying algorithms or data structures
- Naming files, directories, or modules
- Describing implementation steps or code patterns
- Defining internal APIs or interfaces

If you're writing something that would appear in code, stop. That's plan territory.

## After Saving: Fresh-Eyes Review

After the spec is saved, run a fresh-eyes review. Specs written in conversation accumulate assumptions. A reviewer with fresh context reads only what's on the page, catching what the author can't see.

Invoke the `spec-reviewer` agent on the saved spec using the Task tool. Present the findings and offer to address critical issues before moving on.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, compliance, or architecture experts can identify requirements you might miss. Invoke relevant agents via Task tool and incorporate their insights.
