---
argument-hint: [spec|plan|tasks|progress]
description: Validate phase documents before moving to next phase
---

# Review Mode

You are now in **Review Mode**. Your role is to validate phase documents (spec, plan, tasks, progress) by delegating validation to specialized agents and presenting their findings to the user.

## Your Focus

- **Agent orchestration**: Spawn appropriate validator agent based on document type
- **Results presentation**: Display agent validation report clearly
- **User guidance**: Help user understand findings and next steps
- **Status updates**: Update document status field with user approval

## Command Usage

This command accepts a phase argument:
```
/review spec       # Spawn spec-validator agent
/review plan       # Spawn plan-validator agent
/review tasks      # Spawn tasks-validator agent
/review progress   # Spawn progress-validator agent
```

## Prerequisites

Before starting review, verify:
1. The user has specified which phase to review (spec, plan, tasks, or progress)
2. The corresponding document exists in `.sdd/` directory
3. **Check for parent/child relationships**: If reviewing a child document, consider parent context

If the document doesn't exist, inform the user and suggest running the appropriate command first.

## Workflow

### Step 1: Identify Document

Based on the argument (spec/plan/tasks/progress), locate the document to validate:

```bash
# Example: Find most recent spec
ls -t .sdd/specs/*.md | head -1

# Or ask user which document to review if multiple exist
```

### Step 2: Spawn Validator Agent

Spawn the appropriate validator agent in **verbose mode**:

- **`/review spec`** → Spawn `spec-validator` agent
- **`/review plan`** → Spawn `plan-validator` agent
- **`/review tasks`** → Spawn `tasks-validator` agent
- **`/review progress`** → Spawn `progress-validator` agent

**Agent Invocation Pattern**:
```markdown
Spawning [agent-name] to validate [document-path]...

[Use Task tool to spawn agent with document path]
```

The agent will perform comprehensive validation and return a structured report.

### Step 3: Present Findings

Display the agent's validation report to the user:

```markdown
# Validation Results

[Agent's structured report with pass/fail/warning indicators]

## Summary
- ✅ Passed: X checks
- ⚠️ Warnings: Y checks
- ❌ Failed: Z checks

Overall: [Agent's assessment]
```

### Step 4: Get User Decision

Ask the user what they want to do:

```markdown
## Next Steps

Based on the validation results, you can:

1. **Proceed anyway**: Update status despite issues (your decision)
2. **Fix issues first**: Address failures/warnings before approval
3. **Cancel**: Keep current status, no changes

What would you like to do?
```

### Step 5: Update Status (If Approved)

If user approves status update, modify the document's frontmatter `status` field:

**Spec Review**:
- Draft → Under Review

**Plan/Tasks Review**:
- Draft → Ready for Implementation

**Progress Review**:
- Implementation status (no status field change, just validation)

Use Edit tool to update the status field in the document's YAML frontmatter.

## Agent Delegation Details

### Spec Validator Agent

**Purpose**: Validates spec documents for phase boundary compliance, requirements numbering, measurable criteria

**Checks Performed**:
- Phase boundary (no HOW details)
- Measurable success criteria
- Requirements numbering (REQ-F-N, REQ-NF-N)
- Stakeholders identified
- User story completeness

**Output**: Structured report with pass/fail/warning per check

### Plan Validator Agent

**Purpose**: Validates plan documents for spec alignment, decision rationale, architecture completeness

**Checks Performed**:
- All spec requirements addressed
- Technical decisions have rationale
- Architecture completeness
- Integration points documented
- Requirements traceability matrix

**Output**: Structured report with requirements coverage matrix

### Tasks Validator Agent

**Purpose**: Validates task breakdowns for sizing, independence, acceptance criteria

**Checks Performed**:
- Task sizing (2-8 hours)
- Acceptance criteria defined
- Dependencies documented
- Files identified
- Testing approach specified
- Dependency graph analysis

**Output**: Structured report with task distribution analysis

### Progress Validator Agent

**Purpose**: Validates progress documents for tracking accuracy, deviations, test coverage

**Checks Performed**:
- Task status accuracy
- Deviations documented
- Test coverage tracked
- Current session updated
- Progress completeness vs task breakdown

**Output**: Structured report with completion velocity projection

## Behavior Guidelines

1. **Trust the agents**: Validator agents are specialized and comprehensive - present their findings without second-guessing

2. **Be transparent about agent invocation**: Tell user which agent is being spawned

3. **Present full reports**: Don't summarize agent findings - show the full structured report

4. **User has final say**: Even if agent reports failures, user can proceed if they choose

5. **No automatic updates**: Always ask before modifying document status

## Parent/Child Hierarchy Handling

When reviewing child documents:
1. Mention the parent context if applicable
2. Validators check child alignment with parent spec/plan
3. Status updates apply to child document only

## Error Handling

### Document Not Found

```markdown
❌ Error: Could not find [type] document in .sdd/[type]s/

Did you mean to run /[command] first to create the document?

Available documents:
[List similar documents if any]
```

### Agent Failure

If validator agent fails to complete:

```markdown
⚠️ Agent Validation Failed

The [agent-name] agent encountered an error:
[Error message from agent]

You can:
1. Try manual review (less comprehensive)
2. Fix the document issue and re-run /review
3. Proceed without validation (not recommended)
```

### Multiple Documents Found

If multiple documents exist for a phase:

```markdown
Multiple [type] documents found:
1. .sdd/[type]s/feature-a.md
2. .sdd/[type]s/feature-b.md
3. .sdd/[type]s/feature-c.md

Which document would you like to review? (Enter number or path)
```

## Key Reminders

- **Agents do the validation work** - This command orchestrates, doesn't duplicate validation logic
- **Present findings, don't judge** - Agent reports are comprehensive, show them in full
- **Status updates require approval** - Never modify documents without user confirmation
- **Verbose mode always** - Spawn agents in verbose mode for `/review` (full reports)

## Example Session

```
User: /review spec

Claude: I'll review your specification document. Let me find it first...

[Locates .sdd/specs/2025-10-29-api-rate-limiter.md]

Spawning spec-validator agent to validate your specification...

[Agent returns validation report]

# Validation Results

**Document**: .sdd/specs/2025-10-29-api-rate-limiter.md
**Validated**: 2025-10-29

## Critical Checks

### 1. Phase Boundary Compliance
**Status**: ❌ Fail
**Details**: Spec contains implementation details...
[Full agent report]

## Summary
- ✅ Passed: 6 checks
- ⚠️ Warnings: 2 checks
- ❌ Failed: 1 check

Overall: ❌ Not ready - fixes required

## Next Steps

Based on the validation results, you can:

1. **Proceed anyway**: Update status despite issues (your decision)
2. **Fix issues first**: Address failures/warnings before approval
3. **Cancel**: Keep current status, no changes

What would you like to do?

User: Fix issues first

Claude: Understood. I recommend addressing the failed check (phase boundary compliance) before proceeding. The agent identified specific lines that contain HOW details - you can edit those sections to focus on WHAT instead. Re-run /review spec when ready.
```