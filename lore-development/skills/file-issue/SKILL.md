---
name: file-issue
description: This skill should be used when something worth tracking surfaces during work — a bug, gap, or inconsistency. Triggers: "file an issue", "log this", "track this as an issue", "flag this problem".
---

# File Issue

Write it up and move on. Don't work the issue — file it.

If the observation is too vague to write up clearly, say so rather than filing a placeholder.

## Saving

Save to `.lore/work/issues/[kebab-case-title].html`. Load `${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md` for the meta tag fields before writing. Set `status: open`. The document body is freeform — describe what happened, why it matters, and a fix direction if one is clear.

The output is HTML — a prominent status badge (open / resolved / wontfix), a clear severity or impact indicator if one is apparent, and the fix direction visually separated from the observation. Inline CSS and JS are fine; no external dependencies.
