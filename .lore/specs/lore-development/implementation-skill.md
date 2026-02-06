---
title: Implementation skill (orchestrator model)
date: 2026-02-05
status: draft
tags: [implementation, orchestrator, agents, testing, code-review, notes, skill-design]
modules: [lore-development]
related:
  - .lore/brainstorm/lore-development/implementation-skill-orchestrator.md
  - .lore/retros/lore-development/remove-breakdown-execute.md
  - .lore/retros/lore-development/spec-review-what-vs-how.md
  - .lore/brainstorm/lore-development/plan-implementation-drift.md
---

# Spec: Implementation Skill

## Overview

A skill that orchestrates implementation by delegating code, testing, and review work to sub-agents while maintaining a running record of what happened and why. The orchestrator does not implement code itself. It dispatches, records, routes failures back for correction, and escalates to the human when it can't resolve something autonomously.

## Entry Points

Invoked as `/lore-development:implement <path>` where `<path>` is one of four lore artifact types:

- **Spec** (`.lore/specs/*.md`): Requirements are clear enough to implement directly. No plan needed.
- **Design** (`.lore/design/*.md`): A technical design (single class, algorithm, data structure) that can be implemented from the design alone.
- **Plan** (`.lore/plans/*.md`): When the spec doesn't tell you "do A then B then C," a plan provides sequenced phases. This is the expected path for non-trivial work.
- **Notes** (`.lore/notes/*.md`): Continuation. Context was poisoned or session ended. The user cleaned up the notes file, which still references the source spec/plan/design. Resume from here.

The orchestrator reads the input artifact, identifies its type, and adapts:
- Specs and designs: the orchestrator determines phases itself.
- Plans: phases are already defined; the orchestrator follows them.
- Notes: the orchestrator reads the progress tracker to determine where to resume.

## Requirements

### Orchestrator Core

- REQ-IMPL-1: The orchestrator does not write code, run tests, or perform code review. It dispatches these to sub-agents. It does use Edit/Write to maintain the notes file and Read to load artifacts.
- REQ-IMPL-2: The orchestrator holds the full source artifact (spec, design, or plan) in its context for reference throughout execution.
- REQ-IMPL-3: When the source is a plan, the orchestrator feeds one phase at a time to the implementation agent. The implementation agent does not see the full plan.
- REQ-IMPL-4: When the source is a spec or design, the orchestrator determines phases by reading the artifact and breaking it into implementable chunks. Chunks should be testable independently where possible.

### Agent Delegation

- REQ-IMPL-5: The orchestrator selects agents from the project's `.lore/lore-agents.md` registry. If no registry exists, it uses reasonable defaults from available agents.
- REQ-IMPL-6: Each dispatch to a sub-agent includes: what to do, what files are relevant, and any context from prior phases or failures.
- REQ-IMPL-7: Sub-agents report back to the orchestrator. The orchestrator does not observe their internal process, only their results.

### Implementation Cycle

- REQ-IMPL-8: For each phase, the cycle is: implement, then test, then review. A phase is not complete until all three pass.
- REQ-IMPL-9: Test failures route back to the implementation agent with the failure description. The orchestrator includes what the testing agent reported, not raw logs.
- REQ-IMPL-10: Review concerns route back to the implementation agent with the specific non-conformances. The orchestrator includes what the reviewer reported.
- REQ-IMPL-11: After a fix attempt, the orchestrator re-runs the failing step (test or review), not the entire cycle.

### Notes

- REQ-IMPL-12: The orchestrator creates one notes file per invocation at `.lore/notes/<artifact-name>.md`. If continuing from an existing notes file, it appends to that file.
- REQ-IMPL-13: The notes file contains three sections: progress tracker (what's done), implementation log (what happened), and divergence log (where reality deviated from the source artifact).
- REQ-IMPL-14: The implementation log records dispatches and results. Not every round-trip is notable. The orchestrator records: what was dispatched, what the agent reported, and any decisions or discoveries worth preserving. Routine "tests passed" entries are not needed.
- REQ-IMPL-15: The divergence log records cases where the implementation required something the source artifact didn't account for. This should be empty for well-specified work.
- REQ-IMPL-16: Notes reference their source artifact (spec, design, or plan path) so a retro can diff plan vs reality.

### Escalation

- REQ-IMPL-17: The orchestrator escalates to the human (via AskUserQuestion) when the implementation agent cannot resolve a test or review failure after 2 consecutive attempts on the same issue.
- REQ-IMPL-18: The orchestrator escalates to the human when implementation requires diverging from the source artifact. The orchestrator cannot authorize plan changes, only follow the plan.
- REQ-IMPL-19: Outside of these two conditions, the orchestrator operates autonomously. It does not ask for confirmation between phases.

### Continuation

- REQ-IMPL-20: When invoked with a notes file, the orchestrator reads the progress tracker to determine which phases are complete and resumes from the next incomplete phase.
- REQ-IMPL-21: The notes file must contain a reference to the source artifact. If missing, the orchestrator asks the user for the source path before proceeding.

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Complete | All phases pass implementation, testing, and review | Notes file finalized with summary |
| Stuck escalation | 2 consecutive failures on same issue | Human via AskUserQuestion |
| Divergence escalation | Reality requires deviation from source artifact | Human via AskUserQuestion |
| Session end | User stops or context limit approaching | Notes file saved with current progress (resumable) |

## Notes File Structure

```markdown
---
title: Implementation notes: [artifact name]
date: YYYY-MM-DD
status: active | complete
tags: [implementation, notes]
source: [path to spec/design/plan]
---

# Implementation Notes: [Artifact Name]

## Progress
- [x] Phase 1: [description]
- [x] Phase 2: [description]
- [ ] Phase 3: [description]
- [ ] Phase 4: [description]

## Log

### Phase 1: [description]
- Dispatched: [what was sent to implementation agent]
- Result: [what came back]
- Tests: [pass/fail, notable findings]
- Review: [pass/concerns, what was flagged]
- Resolution: [if failures occurred, how they were resolved]

### Phase 2: [description]
...

## Divergence
(Empty if implementation matched the source artifact)

- [description of divergence and why it was necessary]
```

## Success Criteria

- [ ] Orchestrator dispatches to sub-agents for implementation, testing, and review
- [ ] Orchestrator does not write code itself
- [ ] Notes file captures what happened and enables continuation
- [ ] Stuck loops escalate to human after 2 attempts
- [ ] Plan divergence escalates to human
- [ ] Continuation from notes file resumes at correct phase
- [ ] Accepts spec, design, plan, or notes as input

## AI Validation

**Defaults** (apply unless overridden):
- Unit tests with mocked time/network/filesystem/LLM calls
- 90%+ coverage on new code
- Code review by fresh-context sub-agent

**Custom:**
- Integration test: invoke skill with a trivial spec, verify notes file is created with correct structure
- Integration test: invoke skill with a notes file mid-progress, verify it resumes from correct phase
- Verify orchestrator uses Edit/Write only for the notes file, never for code files
- Verify orchestrator does not run tests or execute code directly (delegates to agents)

## Constraints

- The orchestrator is a skill (invoked by human), not an agent (invoked by other skills). It runs in the main conversation context.
- Agent selection is not hardcoded. The orchestrator consults `.lore/lore-agents.md` or uses available agents. This spec does not define which agents to use.
- The notes file is retro fuel. Created during implementation, consumed by `/retro`. The retro skill handles this naturally; no special consumption process is needed.
- This skill replaces the previously removed `/execute`. The critical difference: `/execute` wrapped native implementation with ceremony. This skill adds coordination (agent delegation), enforcement (test/review cycles), and recording (notes) that Claude Code does not natively provide.

## Context

- Brainstorm: `.lore/brainstorm/lore-development/implementation-skill-orchestrator.md`
- Retro (why /execute was removed): `.lore/retros/lore-development/remove-breakdown-execute.md`
- Retro (skills lose control at handoff): `.lore/retros/lore-development/spec-review-what-vs-how.md`
- Brainstorm (plan drift): `.lore/brainstorm/lore-development/plan-implementation-drift.md`
- Research (agent cognitive patterns): `.lore/research/lore-development/agent-cognitive-architectures.md`
