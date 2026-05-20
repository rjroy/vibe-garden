---
name: define-validation
description: This skill should be used to add validation criteria to a spec or plan. Triggers: "define validation", "how will we validate", "what should the AI check", "add validation to this".
---

# Define Validation

Validation answers: "How will the AI know this is done?"

It must be behavioral and actionable — something the AI can actually run or observe. "Run the CLI with these args and confirm the output contains X." "Use Playwright to confirm clicking the button triggers Y." "Run the test suite and check it passes." Not "verify the UX feels right."

Add a validation section to an existing spec or plan. If none exists, save standalone to `.lore/work/validation/[topic].md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields before writing.

## What counts

- Unit or integration tests
- CLI invocations with expected output
- Browser automation steps
- Manual steps the AI can follow and report on
- Lint and type checks when behavior depends on them

Structural assertions ("verify this function appears only once") don't count. If a regression must not recur, write a test that fails when the behavior regresses, not when lines move.
