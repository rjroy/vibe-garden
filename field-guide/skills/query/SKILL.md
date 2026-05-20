---
name: query
description: Use when asking questions about the project wiki, querying accumulated knowledge, searching project decisions or lessons. Triggers include "query the wiki", "what does the wiki say about", "search project knowledge", and natural language questions directed at the field-guide wiki.
---

# Query

Answer a question using the project wiki and work artifacts. Cite every source. Offer to persist the answer as a synthesis page.

## Gathering sources

Read `.lore/reference/index.html` first. Scan all listed pages to identify which are relevant to the question. Relevance is broad — include any page whose subject could bear on the answer, even indirectly.

Read every candidate page in full. Then scan `.lore/work/` for source documents (specs, designs, retros, plans, research) that may contain context not yet extracted into the wiki. Use judgment: if the question is about a decision, check plans and specs. If it's about what broke, check retros. If it's about how something works, check architecture and research documents.

If no relevant material exists, say so. Don't synthesize an answer from general knowledge when the question is asking what this project specifically decided or learned.

## Answering

Give a direct answer, then the supporting evidence. If sources conflict, name the conflict and both positions — don't arbitrate silently.

After the answer, list every file cited. Use the file path as the identifier. Example:

> Sources: `.lore/reference/auth-flow-decision.html`, `.lore/work/specs/auth-spec.html`

## Saving as synthesis

After delivering the answer, ask whether to save it as a synthesis wiki page. If the user accepts:

Write an HTML page at `.lore/reference/[descriptive-kebab-name].html`. The page must be self-contained — no external stylesheets, no external scripts, no external image URLs. Inline styles and scripts are fine.

Required HTML structure:

- `<title>`: a precise noun-first description of what the synthesis answers
- `<h1>`: matches the `<title>` text

Required meta tags:

**Standard lore meta:**
- `<meta name="date">`: today's date
- `<meta name="status" content="current">`
- `<meta name="tags">`: kebab-case terms covering the subject, domain, and question type

**Field-guide meta:**
- `<meta name="fg-type" content="synthesis">`
- `<meta name="fg-sources" content="...">`: comma-separated paths of every source cited in the answer
- `<meta name="fg-status" content="current">`

The body should read as a standalone document. A reader with no access to the original question or sources should understand what the page is saying and why it exists.

After writing the page, update `.lore/reference/index.html`. Add the new page to the `synthesis` group. If the group doesn't exist yet, create it. The entry must use the page's `<title>` as link text and description, matching the format of other entries in `index.html`. Preserve all other groups and entries.
