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

1. **Search for related prior work**: Use the Task tool to invoke the `lore-researcher` agent with the topic/feature description. **Do not run in background.** Wait for the result before continuing. Include any findings in the spec's Context section.
2. Review any relevant `.lore/work/research/` or `.lore/work/brainstorm/` context
3. Ask clarifying questions about scope and success
4. Draft the specification
5. **Probe for stubs**: For each major action identified, ask "Are we stubbing [action], or defining it now?" User can choose to define inline or mark as stub.
6. **Probe for validation**: Ask "Are defaults sufficient for AI validation, or does this feature need custom checks?" Most features use defaults; some need specific verification.
7. Confirm with user before saving
8. Save to `.lore/work/specs/`
9. **Offer fresh-eyes review** (see below)

## Output

Save to `.lore/work/specs/[feature-name].html`

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get the HTML shell and frontmatter field definitions for specs.

**Requirement prefix**: Each spec has a unique prefix for its requirement IDs. See "Requirement ID Prefix" section below.

Copy the HTML base template verbatim. Add `<meta name="lore-req-prefix" content="...">` in the type-specific field slot. Replace `<main>` with these sections:

```html
<main>
  <section id="overview">
    <h2>Overview</h2>
    <p>One paragraph describing what this is.</p>
  </section>

  <section id="entry-points">
    <h2>Entry Points</h2>
    <ul>
      <li>[Entry description] (from [source])</li>
    </ul>
  </section>

  <section id="requirements">
    <h2>Requirements</h2>
    <ul>
      <li><span class="req-id">REQ-{PREFIX}-1</span> [requirement]</li>
      <li><span class="req-id">REQ-{PREFIX}-2</span> [requirement]</li>
    </ul>
  </section>

  <section id="exit-points">
    <h2>Exit Points</h2>
    <table>
      <thead><tr><th>Exit</th><th>Triggers When</th><th>Target</th></tr></thead>
      <tbody>
        <tr>
          <td>[Exit name]</td>
          <td>[User action or condition]</td>
          <td>[STUB: target-name] or [Spec: existing-spec]</td>
        </tr>
      </tbody>
    </table>
  </section>

  <section id="success-criteria">
    <h2>Success Criteria</h2>
    <ul>
      <li><input type="checkbox"> Criterion 1</li>
      <li><input type="checkbox"> Criterion 2</li>
    </ul>
  </section>

  <details>
    <summary>AI Validation</summary>
    <p><strong>Defaults</strong> (apply unless overridden):</p>
    <ul>
      <li>Unit tests with mocked time/network/filesystem/LLM calls (including Agent SDK <code>query()</code>)</li>
      <li>90%+ coverage on new code</li>
      <li>Code review by fresh-context sub-agent</li>
    </ul>
    <p><strong>Custom</strong> (feature-specific, if needed):</p>
    <ul>
      <li>[e.g., "CLI output matches format in examples/"]</li>
    </ul>
  </details>

  <section id="constraints">
    <h2>Constraints</h2>
    <p>Any boundaries or limitations.</p>
  </section>

  <section id="context">
    <h2>Context</h2>
    <p>Links to related <code>.lore/</code> documents if relevant. Include findings from lore-researcher here.</p>
  </section>

  <section id="open-questions">
    <h2>Open Questions</h2>
    <ul>
      <li>Unresolved question 1</li>
    </ul>
  </section>
</main>
```

Requirement IDs must always render as `<span class="req-id">REQ-{PREFIX}-N</span>`. The `open-questions` section receives highlighted amber styling automatically from the base template.

## Requirement ID Prefix

Requirements use namespaced IDs to avoid collisions across specs: `REQ-{PREFIX}-N`

**Auto-generation (default):**
- Derived from spec filename
- Take first 2 segments of kebab-case name, uppercase
- Max 12 characters
- Examples:
  - `auth-flow.html` → `REQ-AUTH-FLOW-1`
  - `user-authentication-oauth2.html` → `REQ-USER-AUTH-1`
  - `checkout.html` → `REQ-CHECKOUT-1`

**Manual override:**
Add `<meta name="lore-req-prefix" content="AUTH">` to the spec's `<head>` when you want explicit control.
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
- `[Spec: checkout-flow]` - Links to existing `.lore/work/specs/checkout-flow.html`

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
