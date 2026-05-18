---
name: define-validation
description: This skill defines AI validation criteria for work in progress. Use when validation wasn't defined in spec/plan, or when starting work without formal documentation. Triggers include "how will the AI validate", "define validation criteria", "what should the AI check", "validation for this work".
---

# Define Validation

Define how the AI validates its work before declaring done.

## When to Use

- Spec or plan exists but lacks AI Validation section
- Starting work without formal spec/plan
- Want to make validation criteria explicit for any chunk of work
- Reviewing existing criteria for completeness

## Process

1. **Identify the work**: Read any existing spec, plan, or gather context from conversation
2. **Start with defaults**: Always include the standard validation checklist
3. **Probe for custom needs**: Ask "Does this feature need any specific verification beyond the defaults?"
4. **Output the criteria**: Present for user confirmation
5. **Save or append**: Either update existing spec/plan or save standalone

## Output

If a spec or plan exists, offer to append the AI Validation section to it.

If no formal document exists, save to `.lore/work/validation/[feature-or-work].html`

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get the HTML shell and frontmatter field definitions.

### Validation Criteria Structure

When appending to an existing spec or plan, add a `<section id="ai-validation">` block:

```html
<section id="ai-validation">
  <h2>AI Validation</h2>
  <p><strong>Defaults</strong> (apply unless overridden):</p>
  <ul>
    <li>Unit tests with mocked time/network/filesystem/LLM calls (including Agent SDK <code>query()</code>)</li>
    <li>90%+ coverage on new code</li>
    <li>Code review by fresh-context sub-agent</li>
  </ul>
  <p><strong>Custom</strong>:</p>
  <ul>
    <li>[Feature-specific validation steps]</li>
  </ul>
</section>
```

## Defaults Explained

These apply to virtually all work:

| Default | Why |
|---------|-----|
| Mock time | Tests shouldn't depend on when they run |
| Mock network | Tests shouldn't fail due to connectivity |
| Mock filesystem | Tests should be isolated and reproducible |
| Mock LLM calls | Agent SDK `query()` is an external API, costs money, can fail |
| 90%+ coverage | New code should be exercised by tests |
| Code review | Fresh-context sub-agent catches what the implementer misses |

## Custom Validation Examples

When probing for custom needs, consider:

- **CLI tools**: "Output matches expected format in examples/"
- **Parsers**: "All test fixtures parse without errors"
- **Generators**: "Generated files are syntactically valid"
- **Integrations**: "Integration test passes against staging/mock API"
- **UI components**: "Renders without console errors in test harness"
- **Data migrations**: "Round-trip preserves data integrity"

## Standalone Document Structure

When no spec/plan exists, copy the HTML base template verbatim. Replace `<main>` with:

```html
<main>
  <section id="context">
    <h2>Context</h2>
    <p>Brief description of what's being built. How this validation criteria was derived (conversation, informal description, etc.)</p>
  </section>

  <section id="ai-validation">
    <h2>AI Validation</h2>
    <p><strong>Defaults</strong> (apply unless overridden):</p>
    <ul>
      <li>Unit tests with mocked time/network/filesystem/LLM calls (including Agent SDK <code>query()</code>)</li>
      <li>90%+ coverage on new code</li>
      <li>Code review by fresh-context sub-agent</li>
    </ul>
    <p><strong>Custom</strong>:</p>
    <ul>
      <li>[Feature-specific items]</li>
    </ul>
  </section>
</main>
```

## Keep It Actionable

Validation criteria must be things the AI can actually do:
- "Run the test suite" - actionable
- "Verify the user experience is good" - not actionable
- "Check output matches examples/expected.json" - actionable
- "Ensure performance is acceptable" - not actionable (unless threshold defined)

## Scope: Behavior, Not Code Shape

AI Validation verifies that the spec was followed *after implementation*. It is not CI, and it is not a mechanism to freeze code structure.

Acceptable forms: unit tests, integration tests, manual test steps, lint, type checks, fresh-context code review.

Do **not** invent ad-hoc scripts that assert structural facts about source code, e.g.:
- "verify this string appears exactly once"
- "check that this function is only defined in one place"
- "fail if any file outside X imports Y"

Such scripts add a second surface that can be wrong. Stale code shape validators produce false confidence and break on legitimate refactors. If a regression must not recur, write a test that fails when the *behavior* regresses, not a script that fails when the *lines move*. Structural concerns belong in lint rules or code review, not in AI Validation.
