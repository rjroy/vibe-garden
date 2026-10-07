---
name: define-validation
description: Use to add validation criteria to a spec or plan. Triggers include "define validation", "how will we validate", "what should the AI check", and "add validation to this".
---

# Define Validation

Validation answers: "How will the AI know this is done?"

It must be behavioral and actionable — something the AI can actually run or observe, like "run the CLI with these args and confirm the output contains X." Not "verify the UX feels right." See "What counts" below for the range of forms this can take.

Add a validation section to an existing spec or plan. If none exists, save standalone to `.lore/work/validation/[topic].md`. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields before writing. New documents start `draft`; use `approved` only for explicit user approval (including editing to approve) or a request for the relevant next process step, never infer it from arbitrary edits. Use `completed` when applicable agent work is done, independently of approval; use `archived` when archived. Status tracks lifecycle, not maturity/correctness. Current user direction may revise approved artifacts; approval is not a veto or mandatory gate. Don't ask approval for minor transitions or every document.

When saving standalone, write the body in Markdown per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML only when a visual carries meaning prose can't, such as a diagram separating automated from manual steps.

## What counts

- Unit or integration tests
- CLI invocations with expected output
- Browser automation steps
- Manual steps the AI can follow and report on
- Lint and type checks when behavior depends on them

Structural assertions ("verify this function appears only once") don't count. If a regression must not recur, write a test that fails when the behavior regresses, not when lines move.

Map every source requirement to at least one executable check and name the evidence
the check will produce. Discover affected consumers, state transitions, and system
boundaries from the feature rather than applying a fixed checklist. Use realistic
interfaces and persistence where mocks could hide behavior. A broad suite command
complements these checks but does not replace them.
