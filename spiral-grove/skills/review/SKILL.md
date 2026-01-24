---
name: review
description: This skill should be used when the user asks to "review a spec", "validate a plan", "check tasks", "review progress", or invokes /spiral-grove:review. Validates phase documents (spec/plan/tasks/progress) by delegating to specialized validator agents before progression to next phase.
---

# Review

Validate phase documents by delegating to specialized validator agents and presenting findings for user decision.

## Focus Areas

- **Agent orchestration**: Spawn appropriate validator based on document type
- **Results presentation**: Display validation report clearly
- **User guidance**: Help understand findings and next steps
- **Status updates**: Update document status with user approval

## Command Usage

This skill accepts a phase argument:

```
/spiral-grove:review spec       # Spawn spec-validator agent
/spiral-grove:review plan       # Spawn plan-validator agent
/spiral-grove:review tasks      # Spawn tasks-validator agent
/spiral-grove:review progress   # Spawn progress-validator agent
```

## Prerequisites

Before review, verify:

1. User specified which phase to review (spec, plan, tasks, or progress)
2. Corresponding document exists in `.sdd/` directory
3. **Check for parent/child relationships**: If reviewing child document, consider parent context

If document doesn't exist, inform user and suggest running appropriate skill first.

## Workflow

### Step 1: Identify Document

Based on argument (spec/plan/tasks/progress), locate document to validate:

```bash
# Find most recent spec
ls -t .sdd/specs/*.md | head -1

# Or ask user if multiple exist
```

### Step 2: Spawn Validator Agent

Spawn appropriate validator in **verbose mode**:

| Argument | Agent |
|----------|-------|
| `spec` | `spiral-grove:spec-validator` |
| `plan` | `spiral-grove:plan-validator` |
| `tasks` | `spiral-grove:tasks-validator` |
| `progress` | `spiral-grove:progress-validator` |

```
Task(
  description: "Validate [type] document",
  prompt: "Validate document at [path] in verbose mode",
  subagent_type: "spiral-grove:[type]-validator"
)
```

### Step 3: Present Findings

Display agent's validation report to user:

```markdown
# Validation Results

[Agent's structured report with pass/fail/warning indicators]

## Summary
- Passed: X checks
- Warnings: Y checks
- Failed: Z checks

Overall: [Agent's assessment]
```

### Step 4: Get User Decision

Ask what user wants to do:

```markdown
## Next Steps

Based on validation results:

1. **Proceed anyway**: Update status despite issues (your decision)
2. **Fix issues first**: Address failures/warnings before approval
3. **Cancel**: Keep current status, no changes

What would you like to do?
```

### Step 5: Update Status (If Approved)

If user approves, modify document's frontmatter `status` field:

| Review Type | Status Change |
|-------------|---------------|
| Spec | Draft → Under Review |
| Plan | Draft → Ready for Implementation |
| Tasks | Draft → Ready for Implementation |
| Progress | No status change (validation only) |

Use Edit tool to update YAML frontmatter.

## Validator Agents

### Spec Validator

**Purpose**: Validate specs for phase boundary compliance, requirements numbering, measurable criteria

**Checks**:
- Phase boundary (no HOW details)
- Measurable success criteria
- Requirements numbering (REQ-F-N, REQ-NF-N)
- Stakeholders identified
- User story completeness

**Output**: Structured report with pass/fail/warning per check

### Plan Validator

**Purpose**: Validate plans for spec alignment, decision rationale, architecture completeness

**Checks**:
- All spec requirements addressed
- Technical decisions have rationale
- Architecture completeness
- Integration points documented
- Requirements traceability matrix

**Output**: Structured report with requirements coverage matrix

### Tasks Validator

**Purpose**: Validate task breakdowns for sizing, independence, acceptance criteria

**Checks**:
- Task sizing (2-8 hours)
- Acceptance criteria defined
- Dependencies documented
- Files identified
- Testing approach specified
- Dependency graph analysis

**Output**: Structured report with task distribution analysis

### Progress Validator

**Purpose**: Validate progress documents for tracking accuracy, deviations, test coverage

**Checks**:
- Task status accuracy
- Deviations documented
- Test coverage tracked
- Current session updated
- Progress completeness vs task breakdown

**Output**: Structured report with completion velocity projection

## Behavior Guidelines

1. **Trust agents**: Validator agents are specialized and comprehensive. Present findings without second-guessing.

2. **Be transparent**: Tell user which agent is being spawned.

3. **Present full reports**: Don't summarize findings. Show complete structured report.

4. **User has final say**: Even if agent reports failures, user can proceed if they choose.

5. **No automatic updates**: Always ask before modifying document status.

## Parent/Child Hierarchy Handling

When reviewing child documents:
1. Mention parent context if applicable
2. Validators check child alignment with parent spec/plan
3. Status updates apply to child document only

## Error Handling

### Document Not Found

```markdown
Could not find [type] document in .sdd/[type]s/

Did you mean to run /spiral-grove:[command] first to create the document?

Available documents:
[List similar documents if any]
```

### Agent Failure

```markdown
Agent Validation Failed

The [agent-name] agent encountered an error:
[Error message]

Options:
1. Try manual review (less comprehensive)
2. Fix document issue and re-run /spiral-grove:review
3. Proceed without validation (not recommended)
```

### Multiple Documents Found

```markdown
Multiple [type] documents found:
1. .sdd/[type]s/feature-a.md
2. .sdd/[type]s/feature-b.md

Which document to review? (Enter number or path)
```

## Key Reminders

- **Agents do validation work**: This skill orchestrates, doesn't duplicate logic
- **Present findings, don't judge**: Agent reports are comprehensive
- **Status updates require approval**: Never modify without user confirmation
- **Verbose mode always**: Spawn agents in verbose mode for full reports
