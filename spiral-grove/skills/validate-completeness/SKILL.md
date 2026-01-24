---
name: validate-completeness
description: This skill should be used when the user asks to "verify implementation", "audit completeness", "check if done", "validate against spec", or invokes /spiral-grove:validate-completeness. Skeptically verifies that implementation actually fulfills spec requirements rather than trusting progress documents.
allowed-tools: Task, Read, Glob, Grep, Bash, Write
---

# Validate Completeness

Take a skeptic's view of implementation, verifying that code actually fulfills spec requirements rather than trusting progress documents.

## Focus Areas

- **Skeptical audit**: Don't trust "done" status. Verify with actual code evidence.
- **Agent orchestration**: Spawn the `implementation-completeness-auditor` agent
- **Results presentation**: Display findings with two-tier structure
- **User guidance**: Help understand gaps and next steps

## Command Usage

```
/spiral-grove:validate-completeness [feature-name]    # Find spec by feature name
/spiral-grove:validate-completeness [spec-path]       # Direct path to spec file
```

If no argument provided, list available specs and ask which to validate.

## Prerequisites

Before validation, verify:

1. Spec exists in `.sdd/specs/`
2. Implementation is substantially complete (check progress if exists)
3. Codebase has been implemented (not just documents)

Note: Progress document is optional. The audit examines code directly.

## Workflow

### Step 1: Locate Documents

Find spec and any related documents:

```bash
# Find spec by feature name
ls .sdd/specs/*[feature-name]*.md

# Find corresponding progress (optional)
ls .sdd/progress/*[feature-name]*.md
```

If multiple specs match, ask user which to validate.

### Step 2: Pre-Flight Check

If progress document exists:
```markdown
## Pre-Flight Verification

**Spec**: .sdd/specs/[feature-name].md
**Progress**: .sdd/progress/[feature-name]-progress.md

Progress claims:
- Tasks completed: X/Y
- Status: [Complete/In Progress/etc]

Proceeding with skeptical verification of actual implementation...
```

If no progress document:
```markdown
## Pre-Flight Verification

**Spec**: .sdd/specs/[feature-name].md
**Progress**: Not found

Will audit implementation against spec requirements directly.
```

### Step 3: Spawn Auditor Agent

```
Task(
  description: "Audit implementation completeness",
  prompt: "Verify implementation of [feature] against spec at [path]. Check all requirements with code evidence.",
  subagent_type: "spiral-grove:implementation-completeness-auditor"
)
```

Provide:
- Spec file path
- Progress file path (if exists)
- Context about feature scope

### Step 4: Present Findings

Display full agent report. Organize by tier:

```markdown
# Validation Results

[Agent's full report]

## Finding Summary

### Critical Issues (Must Address)
[Issues indicating incomplete or broken implementation]

### Advisory Issues (Should Consider)
[Partial implementations, missing edge cases, untested functionality]
```

### Step 5: Write Report

```bash
mkdir -p .sdd/validation
# Write to .sdd/validation/[feature-name]-validation-report.md
```

### Step 6: Next Steps

```markdown
## Next Steps

Based on validation results:

1. **Address Critical Issues**: Fix blocking problems before declaring complete
2. **Address Advisory Issues**: Improve coverage and edge case handling
3. **Accept Current State**: Acknowledge gaps and proceed (document in progress)
4. **Re-run Validation**: After making fixes, validate again

What would you like to do?
```

## Behavior Guidelines

1. **Trust the agent**: Auditor is thorough. Present findings without second-guessing.

2. **Don't trust documents**: The point is verifying code, not checking document claims.

3. **Evidence required**: Every finding should have file:line references.

4. **Be comprehensive**: Check ALL requirements. Don't stop at first issue.

5. **Two-tier findings**: Clearly separate critical (blocking) from advisory (improve later).

6. **Read-only audit**: This skill doesn't modify code (except writing report).

## "Close Enough" Detection

The auditor specifically looks for implementations that appear complete but have gaps:

| Pattern | Example | Detection |
|---------|---------|-----------|
| Happy path only | Auth works for valid users, no invalid handling | Edge case tests missing |
| Partial feature | Email works, SMS not implemented | Feature subset only |
| Untested | Code exists but no tests | Implementation without verification |
| Unmeasured NFRs | "< 200ms" but no performance tests | Claim without evidence |
| Error swallowing | Catch blocks that log but don't handle | Silent failures |

## Error Handling

### Spec Not Found

```markdown
Could not find specification matching "[argument]"

Available specs:
[List .sdd/specs/*.md files]

Please specify which spec to validate against.
```

### Implementation Not Found

```markdown
Warning: Could not locate implementation for this feature.

The auditor will search for:
- Source files matching feature patterns
- Test files for the feature
- Integration points mentioned in spec

If implementation exists but wasn't found, provide hints about file locations.
```

### Agent Validation Failure

```markdown
Agent Validation Incomplete

The auditor encountered issues:
[Error details]

Options:
1. Provide more context about implementation location
2. Run manual validation (less comprehensive)
3. Fix underlying issues and re-run
```

## Key Reminders

- **Purpose**: Catch "close enough" implementations that would otherwise slip through
- **Trust code, not documents**: Progress document might say "done" when it isn't
- **Comprehensive**: Every single requirement should be verified
- **Actionable**: Findings include specific file locations and recommendations
- **Non-destructive**: Audit only, no automatic fixes
