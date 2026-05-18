---
name: review-ideas
description: Reviews captured ideas from "idea:" prompts and refines them into structured issues through conversation. Use when you have accumulated ideas and want to process them. Triggers include "review ideas", "process ideas", "check my ideas", "what ideas do I have".
---

# Review Ideas

Refine raw ideas captured by `idea:` into structured issues or discard them.

## When to Use

- After accumulating ideas via `idea:` during sessions
- When ready to process the idea backlog
- Periodically, to keep `.lore/work/ideas/` from growing stale

## Process

1. Read all files in `.lore/work/ideas/*.md`, collecting bullets across all daily files
2. If no ideas exist, report "No ideas to review" and stop
3. Present ideas one at a time, oldest first (earliest date file, top bullet first)
4. For each idea, ask clarifying questions to understand:
   - What was observed or noticed
   - Why it matters
   - What direction a fix or improvement might take
5. After the conversation clarifies the idea, offer three outcomes:
   - **Save as issue**: Write to `.lore/work/issues/` with standard frontmatter
   - **Discard**: Remove without creating an issue
   - **Stop**: End the review session, leaving remaining ideas for later
6. After saving or discarding, remove that bullet from the source ideas file
7. If removing the last bullet leaves only a date header, delete the ideas file
8. Present the next idea and ask if the user wants to continue

## Issue Output

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

  <section id="fix-direction">
    <h2>Fix Direction</h2>
    <p>[Suggested approach, if known]</p>
  </section>
</main>
```

## Removing Processed Bullets

After saving or discarding an idea:

1. Read the source ideas file
2. Remove the specific bullet line (`- idea text`)
3. If only the date header remains (with optional blank lines), delete the file
4. Write the updated file back otherwise

## Constraints

- Process one idea at a time. Don't batch.
- The user controls pace. They can stop at any time.
- Don't work the issue. Refine understanding and save. Acting on issues is separate.
- Ideas files are not lore documents. Issues are.
