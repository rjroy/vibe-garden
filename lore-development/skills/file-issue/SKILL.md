---
name: file-issue
description: This skill files a structured issue to .lore/work/issues/ from an observation made during work. Use when the AI or user spots a bug, gap, or pattern worth tracking and wants to record it directly, bypassing the idea capture flow. Triggers include "file an issue", "log an issue", "record this issue", "create a lore issue", "track this as an issue", "flag this as an issue", "note this problem".
---

# File Issue

Write a structured issue to `.lore/work/issues/` directly from an observation.

## When to Use

- You spotted a bug, gap, or inconsistency during other work
- The user asks you to record something as an issue
- Something is worth tracking but isn't the current task

This bypasses the `idea:` capture and `/review-ideas` refinement flow. Use it when the observation is already clear enough to write up.

## Process

1. Determine the issue from context (working context, user request, or both)
2. Write the issue file to `.lore/work/issues/[kebab-case-title].html`
3. Report what was filed and the path

No conversation loop. No interactive refinement. If the observation is too vague to write up, say so and suggest using `idea:` to capture it for later refinement with `/review-ideas`.

## Output

Save to `.lore/work/issues/[kebab-case-title].html`

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get the HTML shell and frontmatter field definitions for issues.

Copy the HTML base template verbatim. Set `<meta name="lore-status" content="open">`. Replace `<main>` with these sections:

```html
<main>
  <section id="what-happened">
    <h2>What Happened</h2>
    <p>[Description of the observation]</p>
  </section>

  <section id="why-it-matters">
    <h2>Why It Matters</h2>
    <p>[Impact or consequence]</p>
  </section>

  <!-- Omit entirely if no direction is known -->
  <section id="fix-direction">
    <h2>Fix Direction</h2>
    <p>[Suggested approach]</p>
  </section>
</main>
```

Issues are simple artifacts. No collapsibles needed.

### Frontmatter Tips

- **title**: Name the problem, not the symptom (e.g., "Stale cache after config reload" not "Config changes don't apply")
- **tags**: Include problem type (bug, gap, inconsistency, debt), domain, and technology
- **modules**: Match codebase directory structure where possible
- **related**: Link to the lore artifact where you noticed the issue, if applicable. Use `.html` extensions.

## Constraints

- Create the `.lore/work/issues/` directory if it doesn't exist
- Use today's date for the `date` field
- Always set `status: open`
- Omit `modules` and `related` when they don't apply (methodology or process issues)
- Omit "Fix Direction" section entirely if no direction is known, rather than writing a vague placeholder
- Don't work the issue. File it and move on.
