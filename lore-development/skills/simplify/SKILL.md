---
name: simplify
description: This skill orchestrates code cleanup by dispatching cleanup agents to simplify code, running tests to validate changes, diagnosing and fixing test failures, and running code review after tests pass. Takes git changes, file patterns, or notes files as input. Use when refactoring, reducing complexity, or cleaning up code without changing behavior. Triggers include "simplify this", "clean up this code", "refactor without changing behavior", "reduce complexity", "clean up after feature work".
---

# Simplify

Orchestrate code cleanup through agent delegation. Preserve behavior while reducing complexity.

## When to Use

- Refactoring code to reduce complexity without changing behavior
- Cleaning up after feature implementation
- Addressing tech debt or code quality issues
- Want enforced test/review cycles for safe refactoring

## When to Skip

- The cleanup is trivial (single obvious change). Skip this skill and edit directly.
- You need to change behavior (use `/implement` instead)
- Still exploring refactoring approaches (use `/brainstorm` or `/design` instead)

## Input

Invoked as `/simplify` with optional arguments:

| Input Type | Pattern | Behavior |
|------------|---------|----------|
| Git changes | No args | Simplify uncommitted changes from git status |
| File patterns | `pattern` | Simplify files matching the pattern |
| Notes | `.lore/build/notes/*.md` | Resume from progress tracker in the notes file |

Read the specified input to identify files requiring simplification. If resuming from notes, load the progress tracker to determine where to continue.

## Output

The primary output is simplified code plus a notes file at `.lore/build/notes/simplify-<identifier>.md`.

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for notes.

Use this template structure for the notes file:

```markdown
---
title: Simplification notes: [identifier]
date: YYYY-MM-DD
status: in_progress | complete
tags: [simplify, cleanup, code-quality]
modules: [from file paths if identifiable]
---

# Simplification Notes: [Identifier]

## Files Processed

- file/path/one.ts
- file/path/two.ts

## Cleanup Agents Run

- agent-name (e.g., code-simplifier:code-simplifier)
- additional-agent (if from registry)

## Results

### Simplification

- Agent: [agent-name]
  Changes: [description of what was simplified]

### Testing

- Command: [test command]
  Result: Pass | Fail
  Failures: [if failed, description]

### Review

- Agent: pr-review-toolkit:code-reviewer
  Result: [no issues | issues found]
  Findings: [if issues, list them]

## Failures

(Empty if no failures occurred)

### [Failure Type]
- Diagnosis: [cleanup bug | brittle test]
- User Decision: [fix cleanup | fix tests | abort]
- Resolution: [how it was resolved]
```

**Field notes:**
- `modules:` in frontmatter should be extracted from file paths when possible (e.g., `src/auth/` → `auth`)
- "Files Processed" is populated during initialization
- "Cleanup Agents Run" is updated after agent selection (step 2)
- "Results > Simplification" is updated after cleanup agents complete (step 2)
- "Results > Testing" is updated after tests run (step 3)
- "Results > Review" is updated after review completes (step 4)
- "Failures" section is populated only if test or review failures occur and require user intervention
- `status:` changes from `active` to `complete` when all steps finish successfully

## Process

### 1. Initialize

**Search for related prior work**: Use the Task tool to invoke the `lore-researcher` agent with the cleanup topic. **Do not run in background.** Wait for the result before continuing. Surface retros from related prior simplifications and relevant research.

**Determine the input source and detect files:**

**Parse invocation arguments:**

1. Check the first argument (if any)
2. Determine input mode:
   - **No arguments**: use git changes mode
   - **First arg ends with `.md` AND contains `.lore/build/notes/`**: use notes file mode
   - **Otherwise**: treat first arg as a file pattern, use file patterns mode

#### Git changes mode

**When invoked with no arguments:**

1. Use the Bash tool to run: `git status --porcelain`
2. For each line in the output:
   a. Extract status codes (first two characters)
   b. If status starts with `D` (deleted file): skip this line
   c. Extract filename (everything after position 3)
   d. If line contains ` -> `, extract text after ` -> ` (rename target filename)
   e. Add filename to candidate list
3. Filter binary files using the procedure below
4. Verify each file exists using `test -f <path>` via Bash tool
   - If file does not exist, skip it

#### File patterns mode

**When first argument is a file pattern (doesn't match notes file criteria):**

1. Use the Glob tool with the provided pattern (e.g., `src/**/*.ts`)
2. Filter binary files using the procedure below
3. Verify each file exists using `test -f <path>` via Bash tool
   - If file does not exist, skip it

#### Notes file mode

**When invoked with a path to `.lore/build/notes/*.md`:**

1. Use Read tool to load the notes file
2. Parse the Log section entries to extract file paths mentioned in:
   - Phase descriptions (lines starting with `### File:` or `### [filename]:`)
   - "Dispatched" fields (look for file paths in cleanup instructions)
   - "Files" fields (explicit file lists in log entries)
3. Filter binary files using the procedure below
4. Verify each file exists using `test -f <path>` via Bash tool
   - If file does not exist, skip it

**Binary file filtering procedure (used by all modes):**

For each file in the candidate list:
1. Check extension against binary patterns: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`, `.pdf`, `.zip`, `.tar`, `.gz`, `.exe`, `.bin`, `.so`, `.dll`, `.dylib`, `.a`, `.o`, `.wasm`
   - If extension matches: skip this file
2. For files without recognized extensions:
   - Run `file --brief --mime-type <path>` via Bash tool
   - If exit code is non-zero (command failed): assume text and keep file
   - Parse MIME type from output (text before `;` if present)
   - If MIME type starts with `text/`: keep file
   - Otherwise: skip file

#### Empty file list handling

After detecting files from any input mode, check if the file list is empty. If empty:
- Output "No files match the input criteria" to the user
- Exit gracefully without error (do not create notes file or continue to agent selection)

#### Notes file identifier

Determine the identifier for the notes file based on input mode:

**Git changes mode (no args):**
- Identifier is `git-changes`

**File patterns mode (first arg is a pattern):**
- Sanitize the pattern to create identifier:
  - Replace `/` with `-`
  - Remove `*`, `.`, `**`
  - Example: `src/**/*.ts` → `src-ts`
  - Example: `*.py` → `py`

**Notes file mode (path argument):**
- Extract base name without `.md` extension
- Example: `.lore/build/notes/auth-flow.md` → `auth-flow`
- Example: `feature-impl.md` → `feature-impl`

#### Create notes file

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for notes.

Create the notes file at `.lore/build/notes/simplify-<identifier>.md` using the Write tool immediately after determining the identifier.

Set initial values:
- `status: active` in frontmatter
- `date:` to current date (YYYY-MM-DD format)
- `title:` to "Simplification notes: [identifier]"
- Fill "Files Processed" section with the detected file list
- Leave "Cleanup Agents Run", "Results", and "Failures" sections empty (they will be populated as the process executes)

See the Output section for the complete template structure.

#### Agent selection

**Select cleanup agents based on registry availability:**

1. **Always include code-simplifier** (REQ-SIMPLIFY-5):
   - Start the dispatch list with `code-simplifier:code-simplifier`
   - This agent is mandatory and always runs

2. **Check for agent registry** (REQ-SIMPLIFY-6):
   - Use Read tool to check if `.lore/lore-agents.md` exists
   - If the file exists:
     a. Read the file contents
     b. Look for a heading "## Code Quality" (H2 level, case-sensitive)
        - Note: "cleanup" category doesn't exist in the current registry schema
     c. If section not found or table is malformed: treat as "no registry" and fallback to default agent only
     d. Parse the table to extract agent names from the "Agent" column
     e. Look for agents with "simplif" in the agent name or "Simplifies" in the purpose
     f. Add ALL matching agents to the dispatch list (after code-simplifier)
        - Deduplicate: if an agent already appears in the list, do not add it again
        - Example: if registry contains `code-simplifier:code-simplifier`, it should appear only once (from step 1)
   - Example agents that match: `pr-review-toolkit:code-simplifier`, `code-simplifier:code-simplifier`

3. **Graceful fallback** (REQ-SIMPLIFY-7):
   - If `.lore/lore-agents.md` doesn't exist: use only `code-simplifier:code-simplifier`
   - If the file exists but has no Code Quality section: use only `code-simplifier:code-simplifier`
   - If the file exists but has no simplification agents: use only `code-simplifier:code-simplifier`
   - This is not an error condition - log "Using default cleanup agent only" and proceed

4. **Record selected agents**:
   - After selection, update the notes file's "Cleanup Agents Run" section
   - Use Edit tool to replace the empty section with the actual agent list
   - Format: one agent per line, as bullet items (e.g., `- code-simplifier:code-simplifier`)
   - Use Read tool to verify the section was updated correctly before proceeding

### 2. Execute Files

#### Dispatch cleanup agents

**For each agent in the dispatch list** (from step 1 agent selection):

1. **Dispatch the agent** (REQ-SIMPLIFY-8):
   - Use Task tool to invoke the agent
   - Do NOT set `run_in_background: true` - omit this parameter entirely to ensure blocking behavior
   - Prompt format: "Simplify this code for clarity and maintainability while preserving behavior. Files: [comma-separated file list from step 1 initialization]"
   - **Wait for agent to complete and return results before continuing**
   - Process agents sequentially: do not start dispatching agent N+1 until agent N has returned results

2. **After each agent completes and returns results**:
   - Immediately update notes file "Results > Simplification" section using Edit tool
   - Append new entry below any existing entries (do not replace):
     ```markdown
     - Agent: [agent-name]
       Changes: [extract 1-2 sentence summary from agent output]
     ```
   - Example with multiple agents:
     ```markdown
     ### Simplification

     - Agent: code-simplifier:code-simplifier
       Changes: Extracted magic numbers to named constants
     - Agent: pr-review-toolkit:code-simplifier
       Changes: Simplified nested conditionals to early returns
     ```
   - Verify update succeeded by reading back the section

3. **One pass only** (REQ-SIMPLIFY-13):
   - Run each cleanup agent exactly once for simplification attempts
   - After all agents in dispatch list complete, immediately proceed to testing phase
   - Do not re-run cleanup agents to "simplify more" based on user request or iteration
   - **Exception**: If tests fail or review finds issues introduced by cleanup, routing fixes back to cleanup agents is allowed (this is correction of introduced bugs, not iterative simplification)
   - If user wants another simplification round after session completes, they invoke `/simplify` again manually

4. **After all agents complete**:
   - Verify notes file was updated using Read tool
   - This completes the simplification phase
   - Proceed to testing phase

**Legacy compatibility note:**

The old structure referenced "For each file" iteration with cleanup, testing, and review per file. The current implementation processes all files with all cleanup agents first, then tests, then reviews. The notes file template still uses singular "Simplification" / "Testing" / "Review" sections because there is one simplification phase (potentially multiple agents), one test phase, and one review phase.

#### Dispatch testing

After all cleanup agents have completed, run the test suite to validate that behavior is preserved.

**Dispatch the testing agent:**

1. Use the Task tool to spawn a testing agent
2. Include in the prompt: which files were changed, what behavior to verify, and how to run the project's test suite
3. Expect back: pass/fail and notable findings

**After testing completes:**
- Update the notes file "Results > Testing" section with:
  - Command used to run tests
  - Result (Pass/Fail)
  - If failed: failure details

#### Handle test failures

If testing reports failures, diagnose and fix the issue.

**Diagnosis and correction cycle:**

1. Use the Task tool to spawn a diagnosis agent
2. Include in the prompt: the test failure output and the changes made
3. Expect back: root cause analysis and recommended fix
4. If diagnosis indicates cleanup bug:
   - Route the diagnosis back to the cleanup agent that last modified the failing code
   - If unclear which agent, default to code-simplifier:code-simplifier
   - Use Task tool to prompt: "Fix the following test failure: [diagnosis and error]"
   - Wait for agent to apply fix
5. Re-run testing by repeating the testing dispatch above
6. **If this cycle repeats more than 2 times on the same failure, escalate to user.**

**If test failures require user intervention:**
- Update the notes file "Failures" section with:
  - Failure Type: "Test Failure"
  - Diagnosis from diagnosis agent
  - User Decision (after prompting user)
  - Resolution (what was done to fix)

#### Dispatch review

After tests pass, review the changes to ensure code quality and behavior preservation.

**Dispatch the review agent:**

1. Use the Task tool to spawn a review agent
2. Include in the prompt: which files to review and the requirement that behavior must be preserved
3. Expect back: non-conformances only

**After review completes:**
- Update the notes file "Results > Review" section with:
  - Agent name
  - Result (no issues / issues found)
  - If issues: list of findings

#### Handle review concerns

If review reports issues, route them back to the cleanup agent for correction.

**Review correction cycle:**

1. Route findings back to the cleanup agent that last modified the files with issues
   - If unclear which agent, default to code-simplifier:code-simplifier
2. Use Task tool to prompt: "Address these code review findings: [findings]"
3. Wait for agent to apply fixes
4. Re-run review by repeating the review dispatch above
5. **If this cycle repeats more than 2 times on the same findings, escalate to user.**

**If review failures require user intervention:**
- Update the notes file "Failures" section with:
  - Failure Type: "Review Failure"
  - Diagnosis (what review found)
  - User Decision (after prompting user)
  - Resolution (what was done to fix)

#### Record completion

After all phases complete successfully (cleanup, testing, review):

1. Verify all notes file sections are current with the final state
2. Proceed to Finalize step

### 3. Finalize

When all files complete successfully:

1. Update the notes file frontmatter to set `status: complete`
2. Verify all sections are populated correctly:
   - Files Processed (list of all files)
   - Cleanup Agents Run (all agents dispatched)
   - Results sections (Simplification, Testing, Review)
   - Failures section (populated if any failures occurred, empty otherwise)

The notes file is now a complete record of the simplification session and can be referenced for future work.

## Notes Guidance

The notes file is the orchestrator's primary output alongside the code itself. Update it after every completed file (not just at session end) so it is always resumable.

**What to record:**
- Dispatches and results for each file
- Simplifications made (what was complex, what it became)
- Test failures, diagnoses, and how they were resolved
- Review concerns and how they were addressed
- Unexpected discoveries (behavior not covered by tests, hidden dependencies)

**What not to record:**
- Routine "tests passed" with no findings
- Review passes with no concerns
- Internal agent process details

## Escalation Rules

Two conditions require human intervention. Everything else is autonomous.

1. **Stuck loop**: The cleanup agent cannot resolve a test or review failure after 2 consecutive attempts on the same issue. Present the failure history and ask the user how to proceed.

2. **Behavior change detected**: Tests fail in a way that suggests behavior changed, not just broken by refactoring. Present the failure and ask the user whether to proceed or revert.

Do not ask for confirmation between files. The orchestrator runs until complete, stuck, or behavior-changing.

## Context

The lore-researcher invocation in Initialize surfaces relevant prior work automatically.
