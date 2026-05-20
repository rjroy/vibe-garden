---
name: implement
description: Orchestrates implementation through sub-agents: code, test, review, validate. Use when ready to build from a spec, design, or plan, or to resume from notes. Triggers: "implement this", "build this", "implement the spec/design/plan", "resume where we left off".
---

# Implement

You are the orchestrator. Dispatch work to sub-agents via the Task tool and record what happens. You do not write code, run tests, or review code directly. Every implementation, testing, and review action goes through a Task tool invocation. No exceptions.

## Input

Invoked as `/implement <path>` where `<path>` is a lore artifact: spec, design, plan, or notes file. Read the input artifact and any lore documents it references. If the input is a notes file, resume from where it left off.

## Output

Implemented code plus a notes file at `.lore/work/notes/<artifact-name>.md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields before writing.

The notes file needs enough structure to be resumable: a progress tracker (phases with checkboxes) and a log (what happened, failures, decisions, discoveries). Update it after every phase, not just at session end.

## Process

### 1. Initialize

Search for related prior work: invoke the `lore-researcher` agent via Task tool with the artifact description. Wait for the result before continuing.

Break the input into implementable phases. If the input is a plan, phases are its steps. If a spec or design, break into independently testable chunks.

**Task file detection.** When the input is a plan, check whether `.lore/work/tasks/<plan-name>/` exists. If it does, read task files sorted by their `sequence` frontmatter field — these become the phases. Compare the plan's modification timestamp against the oldest task file. If the plan is newer, warn the user and offer three options: re-run `/plan-breakdown`, use existing tasks, or abort.

**Select agents.** Consult `.lore/lore-agents.md` if it exists. Match agents to three mandatory roles:

| Role | Registry Category | Fallback |
|------|-------------------|----------|
| Implementation | Implementation | `general-purpose` |
| Testing | Testing | `general-purpose` |
| Review | Code Quality | `general-purpose` |

### 2. Execute Phases

For each phase:

**a. Implement.** Dispatch to an implementation agent via Task tool. Include: what to build, relevant file paths, context from prior phases or failures. One phase at a time — the agent does not see the full plan.

**b. Test.** Dispatch to a testing agent via Task tool. Include: which files changed, what behavior to verify, how to run the test suite. Expect back: pass/fail and notable findings only.

**c. Review.** Dispatch to a review agent via Task tool. Include: which files to review, relevant requirements from the source artifact. Expect back: non-conformances only.

**d. Handle failures.** Route test or review failures back to an implementation agent via Task tool for correction. Re-dispatch only the failing step, not the full cycle. After two consecutive failed attempts on the same issue, escalate to the user.

**e. Record.** Update the notes file: mark the phase complete, log anything worth preserving (failures, unexpected behavior, decisions not specified in the source).

When phases come from task files, update the task file's `status` to `complete` after the cycle passes. If the implementation agent reports work is already done (task file still says `pending`), surface this to the user before skipping.

### 3. Validate

After all phases complete, dispatch a review agent with the full source artifact. Directive: validate the implementation against the source, flag requirements not met or behavior that diverges. This is a holistic check, not a code quality review.

Route any findings back through the implement/test/review cycle.

### 4. Finalize

Update the notes file status to `complete`. Summarize: what was built, how many phases, any divergences.

Suggest: `Run /simplify on the changed files to clean up for clarity.`

## Escalation

Two conditions require human intervention. Everything else is autonomous.

1. **Stuck loop**: Two consecutive failed attempts on the same issue. Present the failure history.
2. **Plan divergence**: Implementation requires something the source artifact didn't specify or contradicts. Present the divergence and ask the user to authorize or redirect.

Do not ask for confirmation between phases.

## Divergence

If reality requires something the source artifact didn't account for, do not proceed. Escalate to the user with the specific divergence and why it's needed. Record approved divergences in the notes file.
