---
title: Code cleanup agents in implement workflow
date: 2026-02-14
status: resolved
tags: [implement, code-quality, agents, workflow, simplification]
modules: [lore-development]
related: [.lore/../../lore-development/skills/implement/SKILL.md]
---

# Brainstorm: Code Cleanup Agents in Implement Workflow

## Context

The `/implement` skill orchestrates implementation through delegation (implement → test → review), but implementation agents can sprawl, especially on complex phases or after multiple correction attempts. The `code-simplifier:code-simplifier` agent exists to clean up code for clarity and maintainability. How should cleanup agents integrate into the implement workflow?

## Ideas Explored

### Integration as Phase Step

**What if we added a simplification step after each phase?**

Current cycle: implement → test → review → (fix if needed) → done

Expanded cycle: implement → test → review → **simplify** → done

Questions this raises:
- Does simplification happen before or after the test/review cycle passes?
- If simplification changes code, do we re-run tests?
- Is simplification always worth the agent invocation cost, or only for phases above a certain complexity?

### Conditional Simplification

**What if simplification is conditional rather than universal?**

Dispatch simplification only when:
- The phase touched more than N files
- The implementation agent made multiple correction attempts
- The review agent flagged "works but messy" findings

Trade-off: Avoids overhead on trivial phases but catches sprawl when it happens. Requires orchestrator to track complexity signals.

### Separate Skill vs Integrated Step

**What if it's a standalone skill rather than part of implement?**

`/simplify` as manual invocation: "go through recent changes and clean them up." User invokes after `/implement` completes, or between phases if they notice sprawl.

Trade-offs:
- Keeps `/implement` focused on correctness, `/simplify` focused on clarity
- Manual invocation means it gets skipped
- Automatic invocation means overhead even when code is already clean

### Cleanup as Finalize Sub-Phase

**What if cleanup runs as part of "finalize" rather than during iteration?**

After all phases and validation pass, before marking complete:
1. Dispatch code-simplifier across all changed files
2. Dispatch comment-analyzer if comments were added/modified
3. Re-run tests to confirm simplification didn't break anything
4. Update notes with "simplified" status

This makes cleanup part of the "done" criteria without slowing down the iterate-on-correctness loop.

### Opt-In Via Plan Configuration

**What if plans declare cleanup agents in frontmatter?**

```yaml
cleanup_agents: [code-simplifier, comment-analyzer]
```

Orchestrator reads this and dispatches cleanup when the plan requests it. Projects optimizing for polish configure it; projects optimizing for speed skip it.

### Review Mode Integration

**What if cleanup is part of review feedback rather than a separate step?**

Review agent instruction: "flag non-conformances AND opportunities for simplification." Implementation agent gets both types of feedback in one cycle.

Trade-off: Avoids agent invocation overhead but muddies the review agent's focus (correctness vs clarity).

## Other Cleanup Agent Categories

**Simplification** (code-simplifier): Clarity and maintainability

**Comment validation** (comment-analyzer): Documentation accuracy—could run after simplification to ensure comments still match simplified code.

**Review specializations** (silent-failure-hunter, type-design-analyzer): Correctness concerns, not cleanup. These feel more like review-phase agents than post-implementation polish.

Pattern emerging:
- Non-semantic cleanup: formatting, comment style, import ordering (safe to run last)
- Semantic simplification: refactoring, dead code removal (requires re-test)

Code-simplifier falls into semantic simplification, so it probably needs to run *before* the final test pass, not after.

## Open Questions

- Does simplification justify re-running the full test/review cycle, or just tests?
- Should cleanup agents see the full implementation context (all phases), or just the current phase?
- If cleanup changes break tests, is that a cleanup bug or a test brittleness signal?
- How do we avoid "simplify → review flags issue → re-implement → sprawl again" loops?
- Are there other agent types beyond simplification and comment validation that belong in a cleanup phase?
- Should cleanup be per-phase, per-session, or only at finalize?

## Next Steps

Potential directions:
1. Prototype simplification as a finalize sub-phase (least disruptive to current workflow)
2. Add conditional simplification triggers to orchestrator (complexity heuristics)
3. Create `/simplify` as standalone skill for manual cleanup invocation
4. Research build pipeline patterns for semantic vs non-semantic cleanup ordering
