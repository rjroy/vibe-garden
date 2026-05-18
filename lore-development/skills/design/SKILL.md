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

1. **Search for related prior work**: Use the Task tool to invoke the `lore-researcher` agent with the technical problem description. **Do not run in background.** Wait for the result before continuing. Include findings in the Context section.
2. Review any relevant `.lore/work/research/`, `.lore/work/brainstorm/`, or `.lore/work/specs/` context
3. Clarify the technical problem - what exactly needs deciding?
4. Explore approaches - at least 2-3 options with trade-offs
5. **Decide**: Pick an approach and document why
6. Define the interface/contract - how will other code interact?
7. Document edge cases
8. Confirm with user before saving
9. Save to `.lore/work/design/`
10. **Offer fresh-eyes review** (see below)

## Output

Save to `.lore/work/design/[topic].html`

Use kebab-case for filenames. Match spec naming where a spec exists (e.g., if spec is `history-sync.html`, design is `history-sync.html` or `history-sync-dedup-algorithm.html`).

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get the HTML shell and frontmatter field definitions for design documents.

Copy the HTML base template verbatim. Replace `<main>` with these sections:

```html
<main>
  <section id="problem">
    <h2>Problem</h2>
    <p>What technical problem are we solving? Link to spec if one exists.</p>
  </section>

  <section id="constraints">
    <h2>Constraints</h2>
    <ul>
      <li>Technical constraints</li>
      <li>Performance requirements</li>
      <li>Integration points</li>
      <li>Security considerations</li>
    </ul>
  </section>

  <section id="approaches">
    <h2>Approaches Considered</h2>
    <details>
      <summary>Option 1: [Name]</summary>
      <p>Description of the approach.</p>
      <p><strong>Pros:</strong></p>
      <ul><li>Pro 1</li></ul>
      <p><strong>Cons:</strong></p>
      <ul><li>Con 1</li></ul>
    </details>
    <details>
      <summary>Option 2: [Name]</summary>
      <p>Description of the approach.</p>
      <p><strong>Pros:</strong></p>
      <ul><li>Pro 1</li></ul>
      <p><strong>Cons:</strong></p>
      <ul><li>Con 1</li></ul>
    </details>
  </section>

  <section id="decision">
    <h2>Decision</h2>
    <p>Which approach and why. <strong>This section is required.</strong> A design without a decision is just research.</p>
  </section>

  <section id="interface">
    <h2>Interface / Contract</h2>
    <p>How other code will interact with this: function signatures, data structures, protocols, APIs.</p>
  </section>

  <section id="edge-cases">
    <h2>Edge Cases</h2>
    <ul>
      <li>Edge case 1: Handled by...</li>
      <li>Edge case 2: Handled by...</li>
    </ul>
  </section>

  <!-- Optional -->
  <section id="open-questions">
    <h2>Open Questions</h2>
    <ul>
      <li>Things still TBD that don't block implementation.</li>
    </ul>
  </section>
</main>
```

Use `<details>`/`<summary>` for each approach option. The `open-questions` section receives highlighted amber styling automatically from the base template.

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

Invoke the `design-reviewer` agent on the saved design using the Task tool. The agent evaluates designs through four lenses: decision quality, trade-off clarity, interface implementability, and edge case coverage. Present the findings and offer to address critical issues before moving on.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, performance, or architecture experts can identify trade-offs you might miss. Invoke relevant agents via Task tool and incorporate their insights.

## Linking to Specs

Design documents should reference their parent spec when one exists:
- In `<meta name="lore-related">`: `.lore/work/specs/history-sync.html`
- In Problem section: "See <a href='.lore/work/specs/history-sync.html'>Spec: history-sync</a> for requirements."

Design documents can also stand alone for technical problems that don't have user-facing requirements.
