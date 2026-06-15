---
name: query
description: Use when asking questions about the project wiki, querying accumulated knowledge, searching project decisions or lessons. Triggers include "query the wiki", "what does the wiki say about", "search project knowledge", and natural language questions directed at the field-guide wiki.
---

# Query

Answer a question using the project wiki and work artifacts. Cite every source. Offer to persist the answer as a synthesis page.

## Gathering sources

Read `.lore/reference/index.md` first. Scan all listed pages to identify which are relevant to the question. Relevance is broad — include any page whose subject could bear on the answer, even indirectly.

Read every candidate page in full. Then scan `.lore/work/` for source documents (specs, designs, retros, plans, research) that may contain context not yet extracted into the wiki. Use judgment: if the question is about a decision, check plans and specs. If it's about what broke, check retros. If it's about how something works, check architecture and research documents.

If no relevant material exists, say so. Don't synthesize an answer from general knowledge when the question is asking what this project specifically decided or learned.

## Answering

Give a direct answer, then the supporting evidence. If sources conflict, name the conflict and both positions — don't arbitrate silently.

After the answer, list every file cited. Use the file path as the identifier. Example:

> Sources: `.lore/reference/auth-flow-decision.md`, `.lore/work/specs/auth-spec.md`

## Saving as synthesis

After delivering the answer, ask whether to save it as a synthesis wiki page. If the user accepts:

Write a Markdown page at `.lore/reference/[descriptive-kebab-name].md` with YAML frontmatter:

```markdown
---
title: Precise noun-first description of what the synthesis answers
date: YYYY-MM-DD
status: current
tags: [kebab-case, terms, subject, domain, question-type]
fg-type: synthesis
fg-sources: [relative/path/to/source1.md, relative/path/to/source2.md]
fg-status: current
---

# Precise noun-first description of what the synthesis answers

<!-- body in Markdown -->
```

`fg-sources` lists every source cited in the answer as a YAML list.

The body must be self-contained in Markdown. A reader with no access to the original question or sources should understand what the page is saying and why it exists. Reach for embedded inline HTML only when a visual carries meaning Markdown cannot — color-coded status, inline `<svg>` diagram, side-by-side comparison. When you do, write it raw and inline; never in a fenced code block.

After writing the page, update `.lore/reference/index.md`. Add the new page to the `synthesis` group. If the group doesn't exist yet, create it. The entry must use the page's `title` as link text, matching the format of other entries in `index.md`. Preserve all other groups and entries.
