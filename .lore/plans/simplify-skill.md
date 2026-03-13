---
title: Implementation plan for simplify skill
date: 2026-02-15
status: executed
tags: [simplify, cleanup, code-quality, orchestration, lore-development]
modules: [lore-development]
related: [.lore/specs/lore-development/simplify-skill.md]
---

# Plan: Simplify Skill

## Spec Reference

**Spec**: `.lore/specs/lore-development/simplify-skill.md`

Requirements addressed:
- REQ-SIMPLIFY-1: Git changes (unstaged + staged) → Step 2
- REQ-SIMPLIFY-2: File patterns → Step 2
- REQ-SIMPLIFY-3: Notes file parsing → Step 2
- REQ-SIMPLIFY-4: No files → inform and exit → Step 2
- REQ-SIMPLIFY-5: Always dispatch code-simplifier → Step 4
- REQ-SIMPLIFY-6: Dispatch cleanup agents from registry → Step 4
- REQ-SIMPLIFY-7: Graceful fallback if registry missing → Step 4
- REQ-SIMPLIFY-8: Dispatch via Task tool → Step 5
- REQ-SIMPLIFY-9: Run tests via Bash → Step 6
- REQ-SIMPLIFY-10: Dispatch code-reviewer after tests pass → Step 8
- REQ-SIMPLIFY-11: Diagnose test failures → Step 7
- REQ-SIMPLIFY-12: Corrections allowed without re-simplification → Steps 6, 7, 8
- REQ-SIMPLIFY-13: One simplification pass → Step 5
- REQ-SIMPLIFY-14: Diagnose using git diff → Step 7
- REQ-SIMPLIFY-15: Present options via AskUserQuestion → Step 7
- REQ-SIMPLIFY-16: Record diagnosis in notes → Step 7
- REQ-SIMPLIFY-17: Create notes at `.lore/notes/simplify-<identifier>.md` → Step 3
- REQ-SIMPLIFY-18: Notes include files, agents, results, failures → Step 3
- REQ-SIMPLIFY-19: Update after each step, status tracking → Step 3
- REQ-SIMPLIFY-20: Follow template structure → Step 3
- REQ-SIMPLIFY-21: Implement suggests simplify on completion → Step 9
- REQ-SIMPLIFY-22: Suggestion is text output only → Step 9

## Codebase Context

**Existing Patterns to Follow**:
- Implement skill (`lore-development/skills/implement/SKILL.md`) - canonical orchestrator pattern for dispatching agents via Task tool and maintaining notes files
- Notes files in `.lore/notes/` with Progress/Log/Divergence structure
- Frontmatter schema at `lore-development/shared/frontmatter-schema.md` defines metadata structure
- Agent registry at `.lore/lore-agents.md` (cleanup category doesn't exist yet, noted as STUB dependency in spec)

**Where Changes Will Land**:
- New file: `lore-development/skills/simplify/SKILL.md`
- Modified: `lore-development/skills/implement/SKILL.md` (add suggestion output)
- Generated at runtime: `.lore/notes/simplify-*.md` files

**Dependencies**:
- Task tool for agent dispatch (code-simplifier, cleanup agents, code-reviewer)
- Bash tool for git operations and test execution
- AskUserQuestion for failure diagnosis decisions
- Write tool for notes file creation and updates

**Integration Points**:
- Implement skill will suggest `/simplify` on completion
- Git status parsing for file detection (no prior art in codebase, need to implement)
- Test command detection from project context (check package.json, pyproject.toml)

## Implementation Steps

### Step 1: Create Skill Structure

**Files**: `lore-development/skills/simplify/SKILL.md`
**Addresses**: Foundation for all requirements
**Expertise**: None needed

Create the skill file with frontmatter and section headers:
- Frontmatter: `name: simplify`, description in third-person (what the skill does, not "I do...")
- Sections: When to Use, Input, Process, Output, Context
- Follow the pattern from prep-plan and implement skills

The skill executes from the user's working directory. Use absolute paths or cwd-relative paths, not paths relative to the skill file location.

### Step 2: Implement Input Detection Logic

**Files**: `lore-development/skills/simplify/SKILL.md` (Process section)
**Addresses**: REQ-SIMPLIFY-1, REQ-SIMPLIFY-2, REQ-SIMPLIFY-3, REQ-SIMPLIFY-4
**Expertise**: None needed

Define three input modes in the Process section:

1. **No args** (REQ-SIMPLIFY-1): Run `git status --porcelain` via Bash to get unstaged + staged files. Parse output to extract file paths, filter out deleted files (`D` status prefix) and binary files (check file extension or use `file` command).

2. **File patterns** (REQ-SIMPLIFY-2): Use Glob tool with provided patterns (supports syntax like `src/**/*.ts`). Filter out binary files from results.

3. **Notes file path** (REQ-SIMPLIFY-3): Use Read tool to load the notes file. Parse the Log section entries to extract file paths mentioned in phase descriptions, "Dispatched" fields, or "Files" fields. Use only existing files (check with Bash `test -f`). Filter to text files only.

After detection, if file list is empty (REQ-SIMPLIFY-4): output "No files match the input criteria" and exit gracefully (no error, just inform).

### Step 3: Implement Notes File Creation

**Files**: `lore-development/skills/simplify/SKILL.md` (Process section, Output section)
**Addresses**: REQ-SIMPLIFY-17, REQ-SIMPLIFY-18, REQ-SIMPLIFY-19, REQ-SIMPLIFY-20
**Expertise**: None needed

Define notes file identifier logic (REQ-SIMPLIFY-17):
- No args → `git-changes`
- File patterns → sanitized pattern: replace `/` with `-`, remove `*`, `.`, `**` (e.g., `src/**/*.ts` → `src-ts`)
- Notes file → extract base name without `.md` extension (e.g., `auth-flow.md` → `auth-flow`)

Create notes file at `.lore/notes/simplify-<identifier>.md` immediately after file detection using Write tool.

Include the complete notes file template from spec (lines 88-130) in the Output section. Template structure:
- Frontmatter: title, date, status (`active` | `complete`), tags, modules
- Sections: Files Processed, Cleanup Agents Run, Results (Simplification, Testing, Review), Failures

In Process section, specify:
- Create notes file with `status: active` after Step 2
- Update notes file after each orchestration step (Steps 5, 6, 8)
- Set `status: complete` when all steps finish successfully

Reference `lore-development/shared/frontmatter-schema.md` for status values.

### Step 4: Implement Agent Selection

**Files**: `lore-development/skills/simplify/SKILL.md` (Process section)
**Addresses**: REQ-SIMPLIFY-5, REQ-SIMPLIFY-6, REQ-SIMPLIFY-7
**Expertise**: None needed

Define agent selection logic:

1. Always include `code-simplifier:code-simplifier` in the dispatch list (REQ-SIMPLIFY-5)

2. Check if `.lore/lore-agents.md` exists using Read tool (REQ-SIMPLIFY-6):
   - If exists: read and parse for "cleanup" category agents
   - Extract agent names from that category
   - Add those agents to the dispatch list

3. If registry file missing or cleanup category empty, proceed with only code-simplifier (REQ-SIMPLIFY-7). This is not an error condition - just use the default.

Record the selected agents in notes file "Cleanup Agents Run" section using Edit tool.

### Step 5: Implement Cleanup Orchestration

**Files**: `lore-development/skills/simplify/SKILL.md` (Process section)
**Addresses**: REQ-SIMPLIFY-8, REQ-SIMPLIFY-13
**Expertise**: None needed

For each cleanup agent from Step 4:

1. Dispatch via Task tool (REQ-SIMPLIFY-8) with prompt format:
   ```
   Simplify this code for clarity and maintainability while preserving behavior. Files: [comma-separated file list from Step 2]
   ```

2. Use blocking calls (not `run_in_background: true`) - wait for each agent to complete before continuing

3. After agent completes, update notes file "Results > Simplification" section using Edit tool:
   - Agent: [agent name]
   - Changes: [brief description from agent output]

4. Mark this phase complete in notes

One simplification pass only (REQ-SIMPLIFY-13). No iteration on simplification. If user wants another round, they invoke `/simplify` again manually.

### Step 6: Implement Test Execution

**Files**: `lore-development/skills/simplify/SKILL.md` (Process section)
**Addresses**: REQ-SIMPLIFY-9, REQ-SIMPLIFY-11, REQ-SIMPLIFY-12
**Expertise**: None needed

After all cleanup agents complete:

1. Detect test command (REQ-SIMPLIFY-9):
   - Check for `package.json` using Read tool: if `scripts.test` exists, use that command
   - Check for `pyproject.toml` using Read tool: if `[tool.pytest.ini_options]` section exists, use `pytest`
   - Fallback order: try `bun test`, then `npm test`, then `pytest`
   - If none found, skip testing and note in results

2. Run detected test command via Bash tool, capture exit code

3. If exit code = 0 (pass): update notes "Results > Testing" section with "Command: [command], Result: Pass"

4. If exit code ≠ 0 (fail): proceed to Step 7 for failure diagnosis

Note in Process section: REQ-SIMPLIFY-12 allows corrections to cleanup output without re-running simplification. After fixing issues, re-run tests. Test/review cycle can iterate; simplification runs once.

### Step 7: Implement Failure Diagnosis

**Files**: `lore-development/skills/simplify/SKILL.md` (Process section)
**Addresses**: REQ-SIMPLIFY-14, REQ-SIMPLIFY-15, REQ-SIMPLIFY-16
**Expertise**: None needed

When tests fail after cleanup:

1. Run `git diff` via Bash to see changes made by cleanup agents (REQ-SIMPLIFY-14)

2. Analyze test failure output against the diff:
   - **Cleanup bug**: Test failure stack trace or assertion references lines that were changed by cleanup
   - **Brittle test**: Test failure is in lines not changed by cleanup (e.g., import order sensitivity, whitespace-dependent assertions, unrelated test expectations)
   - If unclear from automated analysis: present both options to user

3. Use AskUserQuestion (REQ-SIMPLIFY-15) with three options:
   - Label: "Fix cleanup changes (revert and re-simplify differently)", Description: "The cleanup introduced a bug. Revert cleanup changes and try a different approach."
   - Label: "Fix brittle tests (update test expectations)", Description: "The tests are overly sensitive. Update test expectations to match new code."
   - Label: "Abort", Description: "Stop simplification and leave code as-is."

4. Record diagnosis and user decision in notes "Failures" section (REQ-SIMPLIFY-16):
   - Failure Type: [Test Failure]
   - Diagnosis: [cleanup bug | brittle test]
   - User Decision: [fix cleanup | fix tests | abort]
   - Resolution: [describe what was done]

5. Based on decision:
   - "Fix cleanup changes": revert via `git checkout` and either manual fix or ask user to handle
   - "Fix brittle tests": allow manual test updates or Edit tool corrections
   - "Abort": set notes status to `active` (not `complete`) and exit

After resolution, re-run tests (return to Step 6). Allow multiple correction attempts per REQ-SIMPLIFY-12.

### Step 8: Implement Code Review

**Files**: `lore-development/skills/simplify/SKILL.md` (Process section)
**Addresses**: REQ-SIMPLIFY-10
**Expertise**: Code quality review

After tests pass:

1. Dispatch `pr-review-toolkit:code-reviewer` via Task tool (REQ-SIMPLIFY-10) with prompt:
   ```
   Review code quality for files modified by cleanup. Flag non-conformances only.
   ```

2. Use blocking call - wait for review completion

3. Update notes "Results > Review" section using Edit tool:
   - Agent: pr-review-toolkit:code-reviewer
   - Result: "No issues found" OR list of findings if issues present

4. If issues found:
   - Allow corrections using Edit tool or manual fixes (REQ-SIMPLIFY-12)
   - Re-run tests after corrections (return to Step 6)
   - Re-run review after tests pass (return to Step 8 start)

5. When review passes with no issues, mark notes file `status: complete` using Edit tool

### Step 9: Integrate with Implement Skill

**Files**: `lore-development/skills/implement/SKILL.md`
**Addresses**: REQ-SIMPLIFY-21, REQ-SIMPLIFY-22
**Expertise**: None needed

Locate the section in implement skill where implementation completes successfully (after all phases finish, tests pass, review passes).

Add suggestion output as plain text (REQ-SIMPLIFY-22 - not AskUserQuestion, just informational output):

```
Implementation complete. Run `/simplify .lore/notes/<notes-file>` to clean up the code for clarity.
```

Replace `<notes-file>` with the actual notes filename variable. This is a suggestion only - user can choose to invoke `/simplify` or ignore it.

### Step 10: Validate Against Spec

**Files**: All implementation artifacts
**Addresses**: All requirements
**Expertise**: Fresh-context review

Launch `lore-development:plan-reviewer` agent via Task tool (blocking call) with prompt:
```
Review the implementation plan at .lore/plans/simplify-skill.md and the implemented skill at lore-development/skills/simplify/SKILL.md against the spec at .lore/specs/lore-development/simplify-skill.md. Check that all 22 requirements are addressed. Flag any gaps or implementation issues.
```

Present findings to user. Address any critical issues before marking implementation complete.

This validation step is not optional.

## Delegation Guide

Steps requiring specialized expertise:
- **Step 8**: Code quality review expertise - handled by dispatching `pr-review-toolkit:code-reviewer` agent
- **Step 10**: Fresh-context validation - handled by dispatching `lore-development:plan-reviewer` agent

All other steps are orchestration logic and don't require domain-specific expertise. The simplify skill itself is an orchestrator and doesn't implement cleanup directly.

## Open Questions

None at this time. The spec is comprehensive and all required patterns exist in the codebase to follow.
