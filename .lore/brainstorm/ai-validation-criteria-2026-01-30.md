# Brainstorm: AI Validation Criteria

**Status**: complete

## Context

The user observed that success criteria in specifications aren't truly validatable by the AI. Specs say "the system should handle errors gracefully" but don't tell the AI *how to verify* that it achieved this.

The key insight: validation criteria here is specifically for the AI. How will the AI validate its own work before declaring "done"?

And critically: 9 out of 10 times, the answer is standard:
- Run code review (sub-agent with fresh context)
- 90%+ test coverage with unit tests
- Mocked external resources and time

## Ideas Explored

### What Makes Validation Criteria Different from Success Criteria

- **Success criteria**: "Users can recover from errors without data loss"
- **Validation criteria**: "When a save fails mid-operation, reload shows last-committed state. Tested by: kill process during write, verify file integrity."

Validation criteria includes:
- Observable outcome
- Specific scenario
- Method to verify (that the AI can execute)

### Where Validation Criteria Should Live

**Option A: Baked into implementation phase**
- Before marking task complete, run validation checklist
- Default checklist always applies; custom items added from spec/plan

**Option B: Section in spec/plan templates**
- "AI Validation Approach" section with sensible default
- Author overrides or extends when needed
- Implementation phase reads and follows it

**Option C: Standalone skill for gap-filling**
- `/define-validation` analyzes spec/plan and proposes validation approach
- Useful when defaults aren't enough or formal process was skipped

### Decided Direction

Combine approaches:
1. Update `/lore-development:specify` to include AI Validation section with defaults
2. Update `/lore-development:prep-plan` similarly (for those who skip to planning)
3. Create `/lore-development:define-validation` as gap-filler skill

### Default Validation (Applied Unless Overridden)

```
- Unit tests with mocked time/network/filesystem
- 90%+ coverage on new code
- Code review by sub-agent before marking complete
```

### Custom Validation (Feature-Specific)

Examples of when you need more:
- "Verify CLI output matches expected format in examples/"
- "Run integration test against staging API"
- "Check generated files parse without errors"

### Three Entry Points for Gap-Fill Skill

1. User completes full spec via `/specify`, runs `/define-validation` for explicit criteria
2. User skips spec, goes to Plan Mode, saves plan, runs `/define-validation` before executing
3. User has small idea, describes it, runs `/define-validation` before starting work

## Questions Resolved

- **Name**: `define-validation` - action-oriented, clear intent
- **Output**: Offers to append to existing spec/plan if one exists, otherwise saves standalone to `.lore/validation/`
- **Code review integration**: Code review by fresh-context sub-agent is one of the defaults, so it's baked in

## Completed

1. Updated `/lore-development:specify` - added AI Validation section with defaults, added process step to probe for custom validation
2. Updated `/lore-development:prep-plan` - added AI Validation section with note about inheriting from spec
3. Created `/lore-development:define-validation` skill for gap-filling when formal docs don't exist

**Key addition**: Defaults now explicitly include "LLM calls (including Agent SDK `query()`)" as an external resource to mock.

## Files Changed

- `lore-development/skills/specify/SKILL.md`
- `lore-development/skills/prep-plan/SKILL.md`
- `lore-development/skills/define-validation/SKILL.md` (new)
