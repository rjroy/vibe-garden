---
name: resolve-drift
description: Use when checking whether field-guide reference pages still match current code and tests. Reads pages plus fg-evidence anchors, reports or fixes semantic drift, and can use sub-agents for parallel audit batches. Triggers include "resolve drift", "semantic drift", "check accuracy", "verify the reference against code", and "audit the wiki".
---

# Resolve Drift

Compare reference prose against living implementation evidence and reconcile drift.

This is the semantic pass. It is intentionally more expensive than lint.

## Inputs

Read indexed pages from `.lore/reference/index.md` or `.lore/reference/index.html`.

For each page, read evidence metadata:

- Markdown: `fg-evidence` frontmatter
- HTML: `fg-evidence-code`, `fg-evidence-tests`, and `fg-evidence-symbols` meta tags

If evidence is missing, either:

- run `update-evidence` first, or
- audit manually and report that the page needs evidence

## Audit Method

For each page:

1. Extract concrete claims from the prose.
2. Read the listed code and test evidence.
3. Search nearby code with `rg` when the evidence is incomplete.
4. Decide whether each claim is:
   - current
   - stale prose
   - stale evidence
   - implementation drift from intended design
   - unverifiable policy or philosophy

Only flag contradictions when the code/tests and page make incompatible claims about the same subject. Do not treat different levels of detail as drift.

## Parallel Review

For large wikis, split indexed pages into independent batches and use sub-agents when the user has allowed agent delegation. Each batch should return findings in this format:

```text
Page:
Claim:
Evidence:
Verdict:
Suggested resolution:
```

Do not duplicate page batches across agents.

## Fixing Drift

Prefer the smallest correction that restores truth:

- update stale reference prose when code/tests are clearly current
- update `fg-evidence` when the prose is true but anchors are incomplete
- report a code/test issue when the page documents intended design and implementation contradicts it
- mark historical pages as non-current when they are no longer meant to describe live behavior

Do not delete useful rationale just because implementation changed. Reframe it as history or a superseded decision when it still explains why the system evolved.

## Output

Report grouped results:

- fixed drift
- remaining drift needing user decision
- evidence gaps
- pages audited with no actionable drift

Include validation commands run, if any.
