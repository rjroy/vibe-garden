---
name: validate
description: This skill defines validation guidelines and records deviations from plans. Use when defining testing approach before implementation, recording what changed during implementation, or documenting why deviations occurred. Triggers include "how do we validate this", "record the deviation", "what changed from the plan", "define testing approach".
---

# Validate

Define how to validate work and record deviations.

## When to Use

- Defining testing or review guidelines before implementation
- Recording deviations from the plan during implementation
- Documenting what changed and why

## Process

### Before Implementation
1. Review the plan in `.lore/plans/`
2. Define validation approach (testing, review criteria)
3. Save guidelines to `.lore/validations/`

### During/After Implementation
1. Record any deviations from the plan
2. Document why the deviation occurred
3. Update the validation document

## Output

Save to `.lore/validations/[feature-name].md`

### Document Structure

```markdown
# Validation: [Feature Name]

Plan: `.lore/plans/[feature-name].md`

## Testing Approach
How this will be validated:
- [ ] Test type 1
- [ ] Test type 2

## Review Criteria
What reviewers should check:
- Criterion 1
- Criterion 2

## Deviations
Changes from the original plan:

### Deviation 1: [Brief description]
**What changed**: Description
**Why**: Reason for the change
**Impact**: Any downstream effects
```

## Keep It Honest

The point is capturing what actually happened, not enforcing rigid adherence. Deviations are information, not failures.
