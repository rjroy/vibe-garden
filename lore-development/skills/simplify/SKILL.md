---
name: simplify
description: Clean up code without changing behavior. Dispatches cleanup agents, runs tests to verify behavior is preserved, then runs code review. Triggers: "simplify this", "clean up this code", "refactor without changing behavior", "reduce complexity".
---

# Simplify

Orchestrate code cleanup through agent delegation. Preserve behavior. Don't change what the code does.

You are the orchestrator. Dispatch work to sub-agents via the Task tool. You do not edit code directly.

## Input

Invoked as `/simplify` with optional arguments:

- **No args**: simplify files with uncommitted changes (`git status`)
- **File pattern**: simplify files matching the pattern
- **Notes path** (`.lore/work/notes/*.md`): resume a previous session

## Process

**Cleanup.** Dispatch `code-simplifier:code-simplifier` via Task tool with the file list. If `.lore/lore-agents.md` exists, check for additional simplification agents in the Code Quality section and dispatch them too.

**Test.** Dispatch a testing agent via Task tool. Include which files changed and how to run the test suite. Expect pass/fail and notable findings. If tests fail, diagnose and route back to the cleanup agent for correction. After two failed attempts on the same issue, escalate to the user.

**Review.** Dispatch a review agent via Task tool. Include which files to review and the requirement that behavior must be preserved. Route findings back to the cleanup agent for correction. After two failed attempts, escalate to the user.

## Output

Record what happened in a notes file at `.lore/work/notes/simplify-<identifier>.md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields. The body is freeform — capture which files were processed, what was simplified, any failures and how they were resolved.

## Escalation

Two conditions require human intervention. Everything else is autonomous.

1. **Stuck loop**: Two consecutive failed attempts on the same test or review failure.
2. **Behavior change detected**: Tests fail in a way that suggests behavior changed rather than a cleanup regression.
