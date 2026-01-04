---
description: Test a single audit agent on one file
argument-hint: <agent> <file-path>
allowed-tools: Read, Bash, Task
---

# Audit Test

Test a single agent on one file to verify it works correctly.

## Arguments

Required: `$ARGUMENTS` should be `<agent> <file-path>`

Agents:
- `structural` → waystone:structural-auditor
- `semantic` → waystone:semantic-auditor
- `api` → waystone:api-contract-auditor
- `spec` → waystone:spec-tracer

## Process

1. Parse arguments to get agent name and file path
2. Verify file exists
3. Invoke the agent via Task tool
4. Report what happened

## Invocation

Use Task with the exact subagent_type:

```
Task(
  subagent_type="waystone:<agent-name>-auditor",
  prompt="Audit [absolute-file-path]. Write report to .audit/reports/[relative-path].md"
)
```

For spec-tracer use `waystone:spec-tracer`.

## Output

After agent completes:
1. Check if report file was created
2. If created, show its contents
3. If not created, report failure

This command exists to debug agent behavior before running full audits.
