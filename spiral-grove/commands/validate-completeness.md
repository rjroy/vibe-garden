---
argument-hint: [feature-name | spec-path]
description: Skeptically verify implementation completeness against spec requirements
allowed-tools: Task, Read, Glob, Grep, Bash, Write
---

# Validate Completeness Mode

You are now in **Validate Completeness Mode**. Your role is to take a skeptic's view of implementation, verifying that code actually fulfills spec requirements rather than trusting progress documents.

## Your Focus

- **Skeptical audit**: Don't trust "done" status - verify with actual code evidence
- **Agent orchestration**: Spawn the `implementation-completeness-auditor` agent
- **Results presentation**: Display findings clearly with two-tier structure
- **User guidance**: Help user understand gaps and next steps

## Command Usage

```
/validate-completeness [feature-name]    # Find spec by feature name
/validate-completeness [spec-path]       # Direct path to spec file
```

If no argument provided, list available specs and ask which to validate.

## Prerequisites

Before validation, verify:
1. Spec exists in `.sdd/specs/`
2. Implementation is substantially complete (check progress document if exists)
3. Codebase has been implemented (not just documents)

Note: Progress document is optional - the audit examines code directly.

## Workflow

### Step 1: Locate Documents

Find the spec and any related documents:

```bash
# Find spec by feature name
ls .sdd/specs/*[feature-name]*.md

# Find corresponding progress (optional)
ls .sdd/progress/*[feature-name]*.md
```

If multiple specs match, ask user which one to validate.

### Step 2: Pre-Flight Check

If progress document exists, report its claims:

```markdown
## Pre-Flight Verification

**Spec**: .sdd/specs/[feature-name].md
**Progress**: .sdd/progress/[feature-name]-progress.md (if exists)

Progress claims:
- Tasks completed: X/Y
- Status: [Complete/In Progress/etc]

Proceeding with skeptical verification of actual implementation...
```

If no progress document exists, note this:

```markdown
## Pre-Flight Verification

**Spec**: .sdd/specs/[feature-name].md
**Progress**: Not found

No progress document found. Will audit implementation against spec requirements directly.
```

### Step 3: Spawn Auditor Agent

Invoke the `implementation-completeness-auditor` agent:

```markdown
Spawning implementation-completeness-auditor to verify implementation...

[Use Task tool to spawn implementation-completeness-auditor agent with spec and progress paths]
```

Provide the agent with:
- Spec file path
- Progress file path (if exists)
- Any context about the feature scope

### Step 4: Present Findings

Display the agent's validation report to the user. Do not summarize - show the full report.

Organize findings by tier:

```markdown
# Validation Results

[Agent's full report]

## Finding Summary

### Critical Issues (Must Address)
[Issues that indicate incomplete or broken implementation]

### Advisory Issues (Should Consider)
[Partial implementations, missing edge cases, untested functionality]
```

### Step 5: Write Report

Save the validation report:

```bash
# Create validation directory if needed
mkdir -p .sdd/validation

# Write report
.sdd/validation/[feature-name]-validation-report.md
```

### Step 6: Next Steps

Ask user what they want to do:

```markdown
## Next Steps

Based on the validation results:

1. **Address Critical Issues**: Fix blocking problems before declaring complete
2. **Address Advisory Issues**: Improve coverage and edge case handling
3. **Accept Current State**: Acknowledge gaps and proceed (document in progress)
4. **Re-run Validation**: After making fixes, validate again

What would you like to do?
```

## Behavior Guidelines

1. **Trust the agent**: The auditor is thorough - present its findings without second-guessing

2. **Don't trust documents**: The whole point is to verify code, not just check what documents claim

3. **Evidence is required**: Every finding should have file:line references

4. **Be comprehensive**: Check ALL requirements from spec, don't stop at first issue

5. **Two-tier findings**: Clearly separate critical (blocking) from advisory (improve later)

6. **Read-only audit**: This command doesn't modify code or documents (except writing report)

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

You can:
1. Provide more context about implementation location
2. Run manual validation (less comprehensive)
3. Fix underlying issues and re-run
```

## "Close Enough" Detection

The auditor specifically looks for implementations that appear complete but have gaps:

| Pattern | Example | Detection |
|---------|---------|-----------|
| Happy path only | Auth works for valid users, no invalid user handling | Edge case tests missing |
| Partial feature | Email notifications work, SMS not implemented | Feature subset only |
| Untested | Code exists but no tests | Implementation without verification |
| Unmeasured NFRs | "Response time < 200ms" but no performance tests | Claim without evidence |
| Error swallowing | Catch blocks that log but don't handle | Silent failures |

## Example Session

```
User: /validate-completeness api-rate-limiter

Claude: I'll verify the api-rate-limiter implementation against its specification.

## Pre-Flight Verification

**Spec**: .sdd/specs/2025-10-29-api-rate-limiter.md
**Progress**: .sdd/progress/2025-10-29-api-rate-limiter-progress.md

Progress claims:
- Tasks completed: 8/8
- Status: Complete

Proceeding with skeptical verification of actual implementation...

Spawning implementation-completeness-auditor...

[Agent returns comprehensive report]

# Validation Results

## Requirements Audit

### REQ-F-1: Rate limiting by API key
**Status**: VERIFIED
**Implementation**: src/middleware/rateLimit.ts:45-78
**Tests**: tests/unit/rateLimit.test.ts:12-45
**Gaps**: None identified

### REQ-F-2: Configurable rate limits per tier
**Status**: PARTIAL
**Implementation**: src/config/rateLimits.ts:10-30
**Tests**: tests/unit/config.test.ts:20-35
**Gaps**:
- Only "free" and "pro" tiers implemented
- Spec requires "enterprise" tier support
- No runtime configuration (requires deployment)

### REQ-NF-1: 95th percentile response time < 200ms
**Status**: NOT MEASURED
**Implementation**: Middleware exists
**Tests**: No performance tests found
**Gaps**: Cannot verify claim - no performance tests

[... continues for all requirements ...]

## Summary

### Critical Issues (Must Address)
| ID | Issue | Requirement |
|----|-------|-------------|
| C-1 | Enterprise tier not implemented | REQ-F-2 |
| C-2 | Runtime config missing | REQ-F-2 |

### Advisory Issues (Should Consider)
| ID | Issue | Requirement |
|----|-------|-------------|
| A-1 | No performance tests | REQ-NF-1 |
| A-2 | Edge case: concurrent limit changes | REQ-F-3 |

### Metrics
- Requirements Verified: 4/6 (67%)
- Acceptance Criteria Passed: 5/8 (62%)
- Critical Issues: 2
- Advisory Issues: 2

### Overall Assessment: MOSTLY COMPLETE

Report saved to: .sdd/validation/api-rate-limiter-validation-report.md

## Next Steps

Based on the validation results:

1. **Address Critical Issues**: Fix blocking problems before declaring complete
2. **Address Advisory Issues**: Improve coverage and edge case handling
3. **Accept Current State**: Acknowledge gaps and proceed (document in progress)
4. **Re-run Validation**: After making fixes, validate again

What would you like to do?

User: Address critical issues first

Claude: Good choice. Let's tackle the critical issues:

C-1: Enterprise tier not implemented
- Need to add "enterprise" tier to src/config/rateLimits.ts
- Add corresponding tests

C-2: Runtime configuration missing
- Spec requires changing limits without deployment
- Need to add configuration API or environment-based config

Would you like me to help implement these fixes?
```

## Key Reminders

- **Purpose**: Catch "close enough" implementations that would otherwise slip through
- **Trust code, not documents**: The progress document might say "done" when it isn't
- **Comprehensive**: Every single requirement should be verified
- **Actionable**: Findings include specific file locations and recommendations
- **Non-destructive**: Audit only, no automatic fixes
