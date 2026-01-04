---
description: Process audit checklist with quality agents
argument-hint: [agent-filter]
allowed-tools: Read, Glob, Grep, Bash, Write, Task
---

# Run Audit

Process the audit checklist by running quality agents against each file.

## Arguments

Optional agent filter: $ARGUMENTS

If provided, only run specified agents:
- `structural` - Only structural-auditor
- `semantic` - Only semantic-auditor
- `api` - Only api-contract-auditor
- `spec` - Only spec-tracer
- (empty) - Run all applicable agents per file

## Prerequisites

Verify `.audit/checklist.md` exists. If not:
- Inform user that audit has not been initialized
- Instruct to run `/waystone:audit-init` first
- Do not proceed

## Process

### 1. Load Checklist

Read `.audit/checklist.md` and parse:
- File list with pending status
- Applicable agents per file
- Filter to only pending files

### 2. Load Quality Rules

Use the quality-project skill to load project-specific rules.
Fall back to quality-universal skill for defaults.

If no rules found:
- Warn that quality rules are not defined
- Recommend creating `docs/rules/` with quality standards
- Proceed with universal defaults

### 3. Process Files in Parallel

For each pending file, invoke applicable agents concurrently using the Task tool.

**Important:** Launch multiple Task invocations in parallel for efficiency. Group files into batches if there are many (e.g., 10 files per batch).

For each file:
1. Determine which agents apply (respecting any filter)
2. Launch agent(s) via Task tool
3. Collect findings

### 4. Agent Invocations

Use the Task tool with explicit `subagent_type` for each agent. **Do not analyze files yourself - spawn agents.**

**structural-auditor:**
```
Task(
  subagent_type="waystone:structural-auditor",
  prompt="Audit [absolute-file-path] for structural quality metrics. Apply thresholds: [from quality rules]. Write report to .audit/reports/[relative-path].md"
)
```

**semantic-auditor:**
```
Task(
  subagent_type="waystone:semantic-auditor",
  prompt="Audit [absolute-file-path] for semantic correctness. Write report to .audit/reports/[relative-path].md"
)
```

**api-contract-auditor:**
```
Task(
  subagent_type="waystone:api-contract-auditor",
  prompt="Quick pass on [absolute-file-path] for API documentation evidence. Write report to .audit/reports/[relative-path].md"
)
```

**spec-tracer:**
```
Task(
  subagent_type="waystone:spec-tracer",
  prompt="Trace [absolute-file-path] to specifications in .sdd/specs/. Write report to .audit/reports/[relative-path].md"
)
```

**CRITICAL:** You MUST use the Task tool with the exact `subagent_type` values shown above. Do NOT attempt to analyze files yourself.

### 5. Track Results

Agents write their own reports directly to `.audit/reports/` (mirroring source path structure):
- `src/api/client.ts` → `.audit/reports/src/api/client.md`
- `lib/utils/helpers.ts` → `.audit/reports/lib/utils/helpers.md`

After agents complete for each file:
1. Update `.audit/checklist.md` status to `audited`
2. Track summary statistics (count issues by severity)

**Note:** You do NOT need to write individual file reports - agents handle this. Your job is to orchestrate and track progress.

### 6. Generate Summary

After all files processed, create `.audit/summary.md`:

```markdown
# Audit Summary

Run: [timestamp]
Files Audited: [count]
Total Issues: [count]

## Status Breakdown
- PASS: [count] files
- WARN: [count] files
- FAIL: [count] files

## Critical Issues
[list with file:line references]

## Files Needing Recheck
[files flagged by api-contract-auditor]

## Recommendations
[prioritized next steps]
```

## Output

After completion:
1. Report summary statistics
2. Highlight critical issues
3. List files needing `/waystone:audit-recheck`
4. Show path to summary: `.audit/summary.md`

## Error Handling

**Agent timeout:**
- Mark file as `error` in checklist
- Note which agent failed
- Continue with remaining files

**File read error:**
- Mark file as `skipped`
- Note reason
- Continue with remaining files

**Too many files:**
- If > 100 files, warn about duration
- Process in batches
- Show progress periodically
