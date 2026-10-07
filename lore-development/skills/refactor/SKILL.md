---
name: refactor
description: Use to inspect a bounded area for code smells and discuss whether a behavior-preserving cleanup is worthwhile. Diagnosis only; implementation happens separately through simplify when the user asks to proceed.
---

# Refactor

Begin with read-only diagnosis. The goal is to help the user decide whether a
concrete refactoring is worth doing, not to produce a checklist or change code.

## Scope and investigation

Establish the area or upcoming change from the user's request and conversation.
If it is unclear, ask one bounded question before exploring. Do not infer a
large scope from Git state or sweep the repository by default.

Inspect the relevant implementation, tests, callers, and consumers to understand
what the code does and where maintenance friction occurs. Use code search,
exploration, or a suitable review agent in proportion to the scope. Treat old
plans, designs, and other work artifacts as context only; current user intent
governs.

Use Fowler's code-smell vocabulary as a set of diagnostic cues, not a required
catalog to complete. For example, duplication can cause fixes to diverge;
shotgun surgery can make one change touch many places; speculative generality
can impose abstraction costs without a demonstrated need; lazy elements,
middle men, data clumps, and primitive obsession can obscure responsibilities
or concepts. Long methods, feature envy, message chains, global or mutable
state, and other familiar smells may also be relevant. A loop, switch, data
class, comment, or simple name is not inherently a defect. Consider conflicting
cues and the actual design context rather than treating any pattern as proof.

## Findings and user choice

Report only findings supported by concrete file and code evidence. Explain the
actual maintenance or future-change cost, then offer a bounded,
behavior-preserving correction option. Ordinary naming or formatting concerns
are not findings unless they cause meaningful cost. No finding is a valid
result; do not invent work to fill a quota.

Present findings to the user and let them choose whether, and which, to address.
Do not edit files, apply fixes, or begin implementation during this diagnosis.
If the user asks to proceed, hand `/simplify` only the selected findings and
compact scope: affected files/surface, evidence, behavior to preserve, and any
explicitly accepted change. Do not create a spec, matrix, or approval document.

If investigation shows that behavior must change, or behavior is unknown in a
way that affects the proposed correction, pause and discuss that separately;
never bundle it quietly into a behavior-preserving cleanup.
