---
name: implement
description: This skill orchestrates implementation by delegating code, testing, and review to sub-agents while recording what happened. Use when ready to build from a spec, design, plan, or to resume from notes. Triggers include "implement this", "build this", "implement the spec", "implement the design", "implement the plan", "continue implementation", "resume where we left off".
---

# Implement

Orchestrate implementation through agent delegation. Record what happens for future retros.

## When to Use

- Ready to build from a spec, design, or plan
- Resuming interrupted implementation from a notes file
- Want enforced test/review cycles with a record of decisions

## When to Skip

- The work is trivial (one file, obvious change, just do it)
- Still exploring options (use `/design` or `/brainstorm` instead)
- Need a plan first (use `/prep-plan` instead)

## Input

Invoked as `/implement <path>` where `<path>` is a lore artifact:

| Input Type | Path Pattern | Behavior |
|------------|-------------|----------|
| Spec | `.lore/specs/*.md` | Determine phases from requirements, implement directly |
| Design | `.lore/design/*.md` | Determine phases from the design, implement directly |
| Plan | `.lore/plans/*.md` | Follow the plan's steps as phases |
| Notes | `.lore/notes/*.md` | Resume from progress tracker in the notes file |

Read the input artifact. Identify its type from the path. If the artifact references other lore documents (a plan referencing a spec, notes referencing a plan), load those too.

## Output

The primary output is the implemented code plus a notes file at `.lore/notes/<artifact-name>.md`.

Use kebab-case. Match the source artifact's filename (e.g., if the plan is `auth-flow.md`, the notes file is `auth-flow.md`).

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for notes.

```markdown
---
title: Implementation notes: [artifact name]
date: YYYY-MM-DD
status: active | complete
tags: [implementation, notes]
source: [path to spec/design/plan]
modules: [from source artifact if available]
---

# Implementation Notes: [Artifact Name]

## Progress
- [x] Phase 1: [description]
- [x] Phase 2: [description]
- [ ] Phase 3: [description]

## Log

### Phase 1: [description]
- Dispatched: [what was sent to implementation agent]
- Result: [what came back]
- Tests: [notable findings only]
- Review: [concerns only]
- Resolution: [if failures occurred, how resolved]

### Phase 2: [description]
...

## Divergence
(Empty if implementation matched the source artifact)

- [description]: [why it was necessary] (approved/pending)
```

## Process

### 1. Initialize

**Search for related prior work**: Invoke the `lore-researcher` agent with the artifact description. Surface retros from related prior implementations, relevant research, and brainstorms. Include findings as context for phase execution.

Read the input artifact. If it is a plan, the phases are its implementation steps. If it is a spec or design, break it into implementable phases (aim for independently testable chunks).

If resuming from notes, read the progress tracker. Skip completed phases. Load the source artifact referenced in the notes frontmatter (`source:` field). If the source reference is missing, ask the user for the path.

**Select agents.** Consult `.lore/lore-agents.md` if it exists. Match agents to roles:

| Role | Registry Category | Fallback `subagent_type` |
|------|-------------------|--------------------------|
| **Implementation** | Implementation | `general-purpose` |
| **Testing** | Testing | `general-purpose` (instruct it to run tests and report pass/fail) |
| **Review** | Code Quality | `pr-review-toolkit:code-reviewer` (if available, else `general-purpose`) |

Use the registry when available. When the registry is missing or doesn't cover a role, use the fallback type.

Create or open the notes file at `.lore/notes/<artifact-name>.md`.

### 2. Execute Phases

For each phase:

**a. Dispatch implementation.** Send the phase description to an implementation agent via the Task tool. Include: what to build, relevant file paths, and context from prior phases or failures if applicable. Feed one phase at a time. The implementation agent does not see the full plan.

**b. Dispatch testing.** Send the implemented code to a testing agent. Expect back: pass/fail and notable findings (not raw logs).

**c. Dispatch review.** Send the implemented code to a review agent. Expect back: non-conformances only.

**d. Handle failures.** If testing or review reports issues, send the findings back to the implementation agent for correction. Re-run only the failing step (test or review), not the entire cycle.

**e. Record.** After the phase completes (all three pass), update the notes file: mark the phase complete in the progress tracker, add a log entry for anything worth preserving.

### 3. Validate

After all phases complete, dispatch a review agent with the full source artifact (spec, design, or plan). The directive: validate the implementation against the source, flag any requirements not met or behavior that diverges from what was specified. This is a holistic check, not a code quality review.

Record validation findings in the notes log. If validation surfaces issues, route them back through the implementation/test/review cycle for the affected phase.

### 4. Finalize

When all phases and validation pass, update the notes file status to `complete`. Summarize the implementation at the top of the log: what was built, how many phases, any divergences.

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

Check `.lore/retros/` for lessons from prior implementations. Check `.lore/research/` and `.lore/brainstorm/` for context that might inform implementation decisions. The lore-researcher invocation in Initialize handles this automatically.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents beyond the core three (implementation, testing, review). Domain experts (security, performance, architecture) can be dispatched when a phase touches their area. Use judgment; not every phase needs every expert.
