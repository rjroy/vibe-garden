---
name: implement
description: This skill orchestrates implementation by delegating code, testing, and review to sub-agents while recording what happened. Use when ready to build from a spec, design, plan, or to resume from notes. Triggers include "implement this", "build this", "implement the spec", "implement the design", "implement the plan", "continue implementation", "resume where we left off".
---

# Implement

Orchestrate implementation through agent delegation. Record what happens for future retros.

**You are the orchestrator.** Your two jobs are dispatching work to sub-agents via the Task tool and recording what happens. You do not write code, run tests, or review code directly (no Bash, Write, or Edit tool usage for these actions). Every implementation, testing, and review action goes through a Task tool invocation. No exceptions. There is no case where the orchestrator does the work directly.

## When to Use

- Ready to build from a spec, design, or plan
- Resuming interrupted implementation from a notes file
- Want enforced test/review cycles with a record of decisions

## When to Skip

- The work is trivial (one file, obvious change). Skip this skill and implement directly.
- Still exploring options (use `/design` or `/brainstorm` instead)
- Need a plan first (use `/prep-plan` instead)

## Input

Invoked as `/implement <path>` where `<path>` is a lore artifact:

| Input Type | Path Pattern | Behavior |
|------------|-------------|----------|
| Spec | `.lore/work/specs/*.html` or `.md` | Determine phases from requirements, implement directly |
| Design | `.lore/work/design/*.html` or `.md` | Determine phases from the design, implement directly |
| Plan | `.lore/work/plans/*.html` or `.md` | Follow the plan's steps as phases (but see Task File Detection below) |
| Notes | `.lore/work/notes/*.html` or `.md` | Resume from progress tracker in the notes file |

Read the input artifact. Identify its type from the path. If the artifact references other lore documents (a plan referencing a spec, notes referencing a plan), load those too.

## Output

The primary output is the implemented code plus a notes file at `.lore/work/notes/<artifact-name>.html`.

Use kebab-case. Match the source artifact's filename (e.g., if the plan is `auth-flow.html`, the notes file is `auth-flow.html`).

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get the HTML shell and field definitions for notes.

Copy the HTML base shell from `html-base-template.md` verbatim. The notes file uses this structure for the `<main>` content:

```html
<!-- meta tags: lore-title, lore-date, lore-status (in_progress|complete),
     lore-tags (implementation, notes), lore-source, lore-modules -->

<section id="progress">
  <h2>Progress</h2>
  <ul>
    <li>&#x2611; Phase 1: [description]</li>
    <li>&#x2610; Phase 2: [description]</li>
  </ul>
</section>

<section id="log">
  <h2>Log</h2>

  <h3>Phase 1: [description]</h3>
  <ul>
    <li><strong>Dispatched:</strong> [what was sent to implementation agent]</li>
    <li><strong>Result:</strong> [what came back]</li>
    <li><strong>Tests:</strong> [notable findings only]</li>
    <li><strong>Review:</strong> [concerns only]</li>
    <li><strong>Resolution:</strong> [if failures occurred, how resolved]</li>
  </ul>
</section>

<section id="divergence">
  <h2>Divergence</h2>
  <p>(Empty if implementation matched the source artifact)</p>
</section>
```

## Process

### 1. Initialize

**Search for related prior work**: Use the Task tool to invoke the `lore-researcher` agent with the artifact description. **Do not run in background.** Wait for the result before continuing. Surface retros from related prior implementations, relevant research, and brainstorms. Include findings as context for phase execution.

Read the input artifact. If it is a plan, the phases are its implementation steps. If it is a spec or design, break it into implementable phases (aim for independently testable chunks).

**Task file detection.** When the input is a plan, check whether `.lore/work/tasks/<plan-name>/` exists (where `<plan-name>` matches the plan's filename without extension). If the directory exists and contains task files:

- **Staleness check**: Compare the plan's modification timestamp against the oldest task file's timestamp. The oldest task is the right comparison point because all tasks are generated in one `/plan-breakdown` run, so the oldest represents when the decomposition happened. If the plan is newer than the oldest task, warn the user via AskUserQuestion with three options: re-run `/plan-breakdown`, use existing tasks, or abort.
- **Phase list**: Read task files sorted by their `lore-sequence` meta tag value. These become the phases. Each phase corresponds to one task file.

If no task directory exists, derive phases from the plan's steps as usual.

If resuming from notes, read the progress tracker. Skip completed phases. When the source is a plan with task files, also read task file statuses. Tasks marked `complete` or `skipped` are not re-run, regardless of what the notes progress tracker shows. Task file status is authoritative for task-based phases. Load the source artifact referenced in the notes `lore-source` meta tag. If the source reference is missing, ask the user for the path.

**Select agents.** Consult `.lore/lore-agents.md` if it exists. Match agents to roles:

| Role | Registry Category | Fallback `subagent_type` |
|------|-------------------|--------------------------|
| **Implementation** | Implementation | `general-purpose` |
| **Testing** | Testing | `general-purpose` (instruct it to run tests and report pass/fail) |
| **Review** | Code Quality | `pr-review-toolkit:code-reviewer` (if available, else `general-purpose`) |

Use the registry when available. When the registry is missing or doesn't cover a role, use the fallback type. `general-purpose` is always a valid fallback. Domain experts (security, performance, architecture) in the registry can be dispatched when a phase touches their area, but the three core roles are mandatory for every phase.

Create or open the notes file at `.lore/work/notes/<artifact-name>.html`.

### 2. Execute Phases

For each phase:

**When phases come from task files:** The implementation agent prompt includes the task's What, Validation, Why, and Files sections. It does not receive the full plan, other task files, or the task's sequence number. After a task passes the implement/test/review cycle, update the task file's `lore-status` meta tag to `complete`. If the implementation agent reports the work is already done, surface this to the user via AskUserQuestion (the task file says `pending`, so "already done" is unexpected and needs confirmation). If the user confirms skipping, or explicitly requests it for any other reason, mark the task `skipped`. The orchestrator does not skip tasks without user confirmation.

**a. Dispatch implementation.** Use the Task tool to spawn an implementation agent (using the `subagent_type` selected in Initialize). Include in the prompt: what to build, relevant file paths, and context from prior phases or failures if applicable. Feed one phase at a time. The implementation agent does not see the full plan.

**b. Dispatch testing.** Use the Task tool to spawn a testing agent. Include in the prompt: which files were created or changed, what behavior to verify, and how to run the project's test suite. Expect back: pass/fail and notable findings (not raw logs).

**c. Dispatch review.** Use the Task tool to spawn a review agent. Include in the prompt: which files to review and the relevant requirements from the source artifact. Expect back: non-conformances only.

**d. Handle failures.** If testing or review reports issues, use the Task tool to send the findings back to an implementation agent for correction. Re-dispatch only the failing step (test or review) via Task tool, not the entire cycle.

**e. Record.** After the phase completes (all three pass), update the notes file: mark the phase complete in the progress tracker, add a log entry for anything worth preserving. For skipped tasks, mark the progress tracker entry as `- [x] Phase N: [description] (skipped)` and log the reason (user-requested or already complete). Skipped tasks still get a log entry so the notes are a complete record.

### 3. Validate

After all phases complete, use the Task tool to spawn a review agent with the full source artifact (spec, design, or plan). The directive: validate the implementation against the source, flag any requirements not met or behavior that diverges from what was specified. This is a holistic check, not a code quality review.

Record validation findings in the notes log. If validation surfaces issues, route them back through the implementation/test/review cycle for the affected phase.

### 4. Finalize

When all phases and validation pass, update the notes file status to `complete`. Summarize the implementation at the top of the log: what was built, how many phases, any divergences.

Suggest running the simplify skill on the notes file:

```
Implementation complete. Run `/simplify .lore/work/notes/<artifact-name>.html` to clean up the code for clarity.
```

Replace `<artifact-name>` with the actual notes filename (matching the source artifact's filename).

## Notes Guidance

The notes file is the orchestrator's primary output alongside the code itself. Update it after every completed phase (not just at session end) so it is always resumable.

**What to record:**
- Dispatches and results for each phase
- Failures, what caused them, and how they were resolved
- Unexpected discoveries (API behaves differently than documented, framework handles something automatically)
- Decisions the implementation agent made that weren't specified in the source artifact

**What not to record:**
- Routine "tests passed" with no findings
- Review passes with no concerns
- Internal agent process details

## Divergence

If reality requires something the source artifact didn't account for, do not proceed autonomously. Escalate to the user via AskUserQuestion with the specific divergence and why it's needed. Record approved divergences in the Divergence section of the notes file.

## Escalation Rules

Two conditions require human intervention. Everything else is autonomous.

1. **Stuck loop**: The implementation agent cannot resolve a test or review failure after 2 consecutive attempts on the same issue. Present the failure history and ask the user how to proceed.

2. **Plan divergence**: Implementation requires something the source artifact didn't specify or contradicts what it specified. Present the divergence and ask the user to authorize or redirect.

Do not ask for confirmation between phases. The orchestrator runs until complete, stuck, or diverged.

## Context

The lore-researcher invocation in Initialize surfaces relevant prior work automatically.
