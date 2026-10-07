---
name: query
description: Use when asking questions about the project wiki, querying accumulated knowledge, searching project decisions or lessons. Triggers include "query the wiki", "what does the wiki say about", "search project knowledge", and natural language questions directed at the field-guide wiki.
---

# Query

Answer a question using the project wiki and relevant work artifacts. Cite every source and distinguish current, implementation-backed understanding from historical context. Offer to persist the answer as a synthesis page when it would add useful knowledge.

## Gathering sources

Read the field-guide index first. Prefer `.lore/reference/index.md`; if it does not exist, read `.lore/reference/index.html`. Scan all listed pages to identify which are relevant to the question. Relevance is broad — include any page whose subject could bear on the answer, even indirectly.

Read every candidate page in full. Candidate pages may be Markdown or HTML. For HTML pages, use meta tags as metadata and visible body content as the page body. Scan relevant `.lore/work/` documents for context not in the wiki. Historical brainstorms, designs, intents, research, and retros can suggest context or investigation leads; plans, notes, and tasks are not reference sources. None of these artifacts establishes current behavior or overrides current user direction. Verify current behavior claims against implementation/tests; identify unverified rationale as historical context. Where current direction conflicts with old artifacts, follow current direction and mention concrete safety or compatibility consequences when relevant, not old-document noncompliance.

If no relevant material exists, say so. Don't synthesize an answer from general knowledge when the question is asking what this project specifically decided or learned. Do not create a synthesis page that merely duplicates existing implementation or reference material; no page is a valid outcome.

## Answering

Give a direct answer, then the supporting evidence. Distinguish actual current implementation from historical intentions or rationale. If historical sources conflict, identify their context without treating the conflict as a current requirement or blocking ambiguity. If code/tests and a reference conflict, report the observed behavior and the reference drift.

After the answer, list every file cited. Use the file path as the identifier. Example:

> Sources: `.lore/reference/auth-flow-decision.md`, `.lore/work/specs/auth-spec.md`

## Saving as synthesis

After delivering the answer, offer to save it as a synthesis wiki page only when it would preserve useful understanding that code/tests and existing pages do not adequately communicate. If the user accepts:

Write a Markdown page at `.lore/reference/[descriptive-kebab-name].md`. If the wiki is stratified into category directories (the index will have a "Layout" section), write the page into the best-fitting existing category directory instead of the root. Use YAML frontmatter:

```markdown
---
title: Precise noun-first description of what the synthesis answers
date: YYYY-MM-DD
status: completed
tags: [kebab-case, terms, subject, domain, question-type]
fg-type: synthesis
fg-sources: [relative/path/to/source1.md, relative/path/to/source2.md]
fg-status: current
---

# Precise noun-first description of what the synthesis answers

<!-- body in Markdown -->
```

`fg-sources` lists every source cited in the answer as a YAML list. Sources may be Markdown or HTML files.

The body must be self-contained in Markdown. A reader with no access to the original question or sources should understand what the page is saying and why it exists. Reach for embedded inline HTML only when a visual carries meaning Markdown cannot — color-coded status, inline `<svg>` diagram, side-by-side comparison. When you do, write it raw and inline; never in a fenced code block.

Before writing, merge useful new context into an existing page where appropriate rather than accumulating a duplicate. If a distinct page genuinely adds reference-worthy understanding, update the field-guide index. Prefer `.lore/reference/index.md`; if only `.lore/reference/index.html` exists, update it in place. Add it to the `synthesis` group or existing category. Preserve unrelated entries.
