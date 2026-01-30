---
name: execute
description: This skill orchestrates working through a breakdown's chunks. Use when ready to implement a breakdown, or continuing interrupted implementation work. Runs implement → review → test cycle per chunk, updating status in the breakdown document. Triggers include "execute the work", "implement the breakdown", "start working on chunks", "continue implementation".
---

# Execute

Orchestrate implementation of breakdown chunks.

## When to Use

- Ready to implement a breakdown created by `/lore-development:breakdown`
- Continuing work after interruption
- Need structured implement → review → test cycle per chunk

## Process

1. Find the breakdown document in `.lore/work/`
2. Identify the next incomplete chunk (first with Status != Done)
3. For each chunk, run the execution cycle:
   - **Implement**: Write the code
   - **Review**: Fresh-context review (via lore-docs-reviewer agent)
   - **Test**: Run tests, verify they pass
4. Update the chunk's Status to `Done` in the breakdown document
5. Loop to the next chunk until all are complete
6. Report completion summary

## The Execution Cycle

Each chunk goes through three phases. A chunk is only "Done" when all three complete.

### Phase 1: Implement

Write the code as described in the chunk's **What** and **Delivers** fields. Follow these principles:

- Check **Depends on** to ensure prerequisites are met
- Keep changes focused on what this chunk delivers
- Don't over-engineer or add scope beyond the chunk

### Phase 2: Review

Get fresh-context review of the implementation. The goal is verification by someone (or something) that didn't write the code.

**Option A: Use a code review agent** (if available)

Check `.lore/lore-agents.md` for code review agents (e.g., `code-reviewer`, `pr-review-toolkit:code-reviewer`). Invoke via Task tool:

```
Review the code just written for [chunk name]. Focus on: correctness, clarity, obvious issues.
```

**Option B: Self-review with fresh perspective**

If no dedicated reviewer is available, do a structured self-review:
- Does the code do what the chunk's **What** and **Delivers** describe?
- Are there obvious bugs or edge cases missed?
- Is the code clear to someone who didn't write it?
- Would the user be surprised by any behavior?

Address critical and important issues before proceeding to Phase 3.

### Phase 3: Test

Verify the work:

1. Run existing tests to ensure nothing broke
2. If new functionality was added, ensure tests exist for it
3. Tests must pass before marking the chunk Done
4. If no test infrastructure exists, verify manually and document what was checked

If tests fail, fix the issues (return to Phase 1 if needed) before proceeding.

## Updating Status

After completing all three phases for a chunk, edit the breakdown document to update the chunk's status:

```markdown
### 1. [Chunk Name]
**Status**: Done  ← Update this
**What**: ...
```

This makes progress visible to anyone reading the breakdown.

## Behavior

**Loop through all chunks**: Continue until all chunks are Done, reporting progress after each. This prioritizes efficiency over checkpoint granularity.

**Respect dependencies**: Before starting a chunk, check its **Depends on** field. If it references chunks that aren't Done:
- Skip the chunk
- Report: "Chunk N skipped due to incomplete dependency: Chunk M"
- If all remaining chunks have unmet dependencies, halt and report: "Execution blocked. Resolve dependency cycle or update breakdown before continuing."

**Handle interruptions**: Before starting a chunk, mark it `In Progress`. If execution is interrupted:
- The interrupted chunk remains `In Progress`
- On resume: Find the `In Progress` chunk and ask: "Chunk N was interrupted. Restart from beginning or continue (assume code is written)?"
- After resolving, continue to next `Not Started` chunk

**Report clearly**: After each chunk, briefly report what was done. After all chunks, summarize the overall completion.

## Output

This skill modifies:
- The breakdown document (`.lore/work/[feature-name].md`) - status updates
- The codebase - implementation work

No separate output document is created. The breakdown document is the source of truth for progress.

## Example Session

```
User: /lore-development:execute

AI: Reading breakdown from .lore/work/auth-flow.md...

Found 3 chunks:
1. Token generation - Not Started
2. Token validation - Not Started
3. Session refresh - Not Started

Starting with chunk 1: Token generation

[Implement phase]
Writing token generation code...

[Review phase]
Running fresh-context review...
Review feedback: Minor issue - consider adding rate limiting comment.
Addressed.

[Test phase]
Running tests... 4 passed.

Updated status to Done.

Moving to chunk 2: Token validation
...

All 3 chunks complete.
Summary: Implemented auth-flow with token generation, validation, and session refresh.
```

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with the review phase (code-reviewer, security review, performance analysis). The agent registry helps match available capabilities to execution needs.
