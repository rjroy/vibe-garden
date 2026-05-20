---
name: add-item
description: Use when the user says "file an issue", "log this", "track this", "add a bug", "create a task", "add to backlog", or invokes /compass-rose:add-item. Replaces /lore-development:file-issue. Creates a local issue file in .lore/work/issues/.
allowed-tools: Bash, Read, Write
---

# Add Item

Gather the details, write the issue file, confirm. No GitHub API, no config file, no authentication.

## Step 1: Qualify the observation

If the user's input is too vague to write up clearly, say so and stop. Do not file a placeholder.

## Step 2: Gather details

Ask for the following, in order. Skip any field the user doesn't answer.

**Title** (required): A short, clear label for the issue. Used as the filename.

**Description** (optional): What's happening, why it matters, fix direction if known.

**Priority** (optional): P0 / P1 / P2 / P3. No default. Skip if the user doesn't know.

**Size** (optional): S / M / L / XL. No default. Skip if the user doesn't know.

Do not prompt for status. Status is always `open`.

Do not prompt about XL escalation. That behavior is retired.

## Step 3: Create the issue file

Derive the filename from the title: lowercase, spaces to hyphens, strip punctuation.

Path: `.lore/work/issues/[kebab-case-title].html`

Create the directory if it doesn't exist.

### File format

Standard HTML. Meta tags in `<head>` carry the structured fields. Body carries the human-readable content.

**Required meta tags:**
- `date` — today's date, YYYY-MM-DD
- `status` — always `open`
- `tags` — inferred from content (comma-separated)

**Conditional meta tags (omit if not provided):**
- `priority` — P0 / P1 / P2 / P3
- `size` — S / M / L / XL

**Body must include:**
- A visible status badge (e.g. `<span class="badge">open</span>`)
- A priority indicator if priority was set
- The observation, why it matters, and fix direction if known

Inline CSS is fine. No external dependencies.

**Example meta block:**
```html
<meta name="date" content="2026-05-20">
<meta name="status" content="open">
<meta name="tags" content="bug, auth">
<meta name="priority" content="P1">
<meta name="size" content="S">
```

## Step 4: Confirm and stop

Tell the user the file was created and where it lives. Then stop — do not start working the issue.

## Related skills

- `/compass-rose:next-item` — find the next issue to work
- `/compass-rose:backlog` — review all open issues
- `/lore-development:specify` — write a formal spec for larger items
