---
title: Simplify skill for post-implementation cleanup
date: 2026-02-15
status: implemented
tags: [lore-development, simplify, cleanup, code-quality, orchestration]
modules: [lore-development]
related: [.lore/work/brainstorm/implement-cleanup-agents.md, .lore/work/specs/lore-development/implementation-skill.md]
req-prefix: SIMPLIFY
---

# Spec: Simplify Skill

## Overview

A post-implementation cleanup orchestrator that runs code simplification agents, re-runs tests, and performs code review. Operates on completed work to improve clarity and maintainability without changing behavior.

## Entry Points

Users invoke this skill when:
- Implementation is complete and passing, but code feels sprawled or over-engineered
- After `/implement` completes (suggested by implement skill)
- Before creating a PR to polish changes
- Periodically as codebase maintenance

Invocation forms:
- `/simplify` - operates on git changes (unstaged + staged files)
- `/simplify <file-patterns>` - targeted cleanup (e.g., `src/**/*.ts`)
- `/simplify .lore/work/notes/some-impl.md` - cleanup files touched in a completed implementation

## Requirements

### Input Handling

- REQ-SIMPLIFY-1: When invoked without arguments, operate on all files with git changes (unstaged + staged), excluding deleted files and binary files
- REQ-SIMPLIFY-2: When invoked with file patterns, operate on files matching those patterns (glob syntax), excluding binary files
- REQ-SIMPLIFY-3: When invoked with a notes file path, extract files touched during that implementation and operate on those (filter to existing text files only)
- REQ-SIMPLIFY-4: If no files match the input criteria after filtering, inform user and exit (don't error, just inform)

### Agent Selection

- REQ-SIMPLIFY-5: Always dispatch `code-simplifier:code-simplifier` agent on target files with context: "Simplify this code for clarity and maintainability while preserving behavior. Files: [list]"
- REQ-SIMPLIFY-6: If `.lore/lore-agents.md` exists and defines cleanup category agents, dispatch those as well with same context format
- REQ-SIMPLIFY-7: If lore-agents registry is missing or cleanup category is empty, use only code-simplifier (no error)

### Orchestration Cycle

- REQ-SIMPLIFY-8: For each cleanup agent, dispatch via Task tool with context specified in REQ-SIMPLIFY-5
- REQ-SIMPLIFY-9: After all cleanup agents complete, run project test suite via Bash using project-standard test command (detect from context: `bun test`, `pytest`, `npm test`, etc.) and capture pass/fail based on exit code
- REQ-SIMPLIFY-10: After tests pass, dispatch `pr-review-toolkit:code-reviewer` agent with context: "Review code quality for files modified by cleanup. Flag non-conformances only."
- REQ-SIMPLIFY-11: If tests fail after cleanup, diagnose whether cleanup broke tests or revealed brittle tests (see Failure Diagnosis below)
- REQ-SIMPLIFY-12: If test or review failures occur, corrections are allowed to fix the cleanup output without re-running simplification
- REQ-SIMPLIFY-13: Simplification agents run exactly once (no re-simplification loop). Test/review cycle can iterate to correct cleanup output.

### Failure Diagnosis

- REQ-SIMPLIFY-14: When tests fail after cleanup, diagnose using git diff:
  - **Cleanup bug**: Test failure references lines changed by cleanup (check stack trace/assertion against diff)
  - **Brittle test**: Test failure is unrelated to changed lines (e.g., import order, whitespace sensitivity, unrelated assertions)
  - If unclear, present both options to user
- REQ-SIMPLIFY-15: Present diagnosis to user via AskUserQuestion with options: "Fix cleanup changes (revert and re-simplify differently)", "Fix brittle tests (update test expectations)", or "Abort"
- REQ-SIMPLIFY-16: Record diagnosis and user decision in notes file "Failures" section

### Notes Output

- REQ-SIMPLIFY-17: Create notes file at `.lore/work/notes/simplify-<identifier>.md` where identifier is:
  - `git-changes` for no-args invocation
  - sanitized file pattern for pattern invocation (replace `/` with `-`, remove `*`, `.`, `**`; e.g., `src/**/*.ts` → `src-ts`)
  - source notes filename for notes invocation (e.g., `auth-flow` for `.lore/work/notes/auth-flow.md`)
- REQ-SIMPLIFY-18: Notes include: files processed, cleanup agents run, test results, review findings, failures with diagnosis
- REQ-SIMPLIFY-19: Update notes after each step and set status to `active` during execution, `complete` when finished successfully
- REQ-SIMPLIFY-20: Notes file follows template structure (see Notes File Template section below)

### Integration with Implement

- REQ-SIMPLIFY-21: When `/implement` completes successfully, output suggestion: "Implementation complete. Run `/simplify .lore/work/notes/<notes-file>` to clean up the code for clarity."
- REQ-SIMPLIFY-22: Suggestion is informational output only (not AskUserQuestion, just text)

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Complete | All cleanup, tests, and review pass | Notes file marked `status: complete` |
| Abort | User aborts during failure diagnosis | Notes file marked `status: active` with failure recorded |
| No-op | No files match input criteria | Inform user, no notes file created |

## Notes File Template

```markdown
---
title: Simplification notes: [identifier]
date: YYYY-MM-DD
status: active | complete
tags: [simplify, cleanup, code-quality]
modules: [from files processed if determinable]
---

# Simplification Notes: [Identifier]

## Files Processed
- file/path/one.ts
- file/path/two.ts

## Cleanup Agents Run
- code-simplifier:code-simplifier
- [additional cleanup agents if any]

## Results

### Simplification
- Agent: code-simplifier:code-simplifier
- Changes: [brief description of what was simplified]

### Testing
- Command: [test command used]
- Result: Pass/Fail
- [If fail: failure details]

### Review
- Agent: pr-review-toolkit:code-reviewer
- Result: Pass/No issues found
- [If issues: list of findings]

## Failures
(Empty if no failures occurred)

### [Failure Type]
- Diagnosis: [cleanup bug | brittle test]
- User Decision: [fix cleanup | fix tests | abort]
- Resolution: [how it was resolved]
```

## Success Criteria

- [ ] Can invoke with no args and operate on git changes
- [ ] Can invoke with file patterns and operate on matching files
- [ ] Can invoke with notes file and operate on files from that implementation
- [ ] Dispatches code-simplifier via Task tool
- [ ] Dispatches additional cleanup agents from lore-agents registry if defined
- [ ] Re-runs tests after cleanup
- [ ] Performs code review after tests pass
- [ ] Diagnoses test failures (cleanup bug vs brittle test)
- [ ] Records all activity in notes file
- [ ] One cleanup pass (no iteration)
- [ ] `/implement` suggests `/simplify` when it completes

## AI Validation

**Defaults** (apply):
- Unit tests with mocked time/network/filesystem/LLM calls
- 90%+ coverage on new code
- Code review by fresh-context sub-agent

**Custom** (feature-specific):
- Manual smoke test: run `/simplify` on vibe-garden codebase files, verify notes file structure matches template
- Verify test failure diagnosis logic with controlled test case (intentionally break a test after cleanup)

## Constraints

- Orchestrator does not modify code directly (no Write, Edit for code changes)
- Cleanup and review dispatched via Task tool; testing via Bash
- Notes file updated after each step with status tracking
- No multi-pass iteration on simplification (run once, user can invoke again if needed)

## Context

**Related brainstorm**: `.lore/work/brainstorm/implement-cleanup-agents.md` explores integration patterns for cleanup agents in the implement workflow. This spec implements the "standalone skill" pattern with suggestion integration.

**Related spec**: `.lore/work/specs/lore-development/implementation-skill.md` defines the orchestrator pattern this skill follows.

**Stub dependency**: [STUB: lore-agents-cleanup-category] - The lore-agents registry needs a "cleanup" category definition. This is referenced in REQ-SIMPLIFY-6 but not yet defined.

**Stub dependency**: [STUB: update-lore-agents-cleanup] - The `/update-lore-agents` skill needs to scan for and categorize cleanup agents. Currently it doesn't have this category.
