---
name: resolve-drift
description: Use when checking whether field-guide reference pages still match current code and tests. Reads pages plus fg-evidence anchors, reports or fixes semantic drift, and can use sub-agents for parallel audit batches. Triggers include "resolve drift", "semantic drift", "check accuracy", "verify the reference against code", and "audit the wiki".
---

# Resolve Drift

Check whether reference pages remain useful and whether claims about current behavior match living implementation evidence. Reconcile stale or redundant knowledge without turning historical intent into a mandate.

This is the semantic pass. It is intentionally more expensive than lint.

## Inputs

Read indexed pages from `.lore/reference/index.md` or `.lore/reference/index.html`.

For each page, read evidence metadata:

- Markdown: `fg-evidence` frontmatter
- HTML: `fg-evidence-code`, `fg-evidence-tests`, and `fg-evidence-symbols` meta tags

Treat `fg-sources` as provenance, not authority or proof of currency. If evidence is missing, either:

- run `update-evidence` first, or
- audit manually and report that the page needs evidence

## Audit Method

For each page:

1. Extract concrete claims from the prose.
2. Read the listed code and test evidence.
3. Search nearby code with `rg` when the evidence is incomplete.
4. For claims about current behavior, validate against code/tests and current user direction. Historical rationale may be useful even when code cannot prove it; label it as history, not as an instruction. Decide whether each claim is:
   - current
   - stale prose
   - stale evidence
   - implementation drift from documented intent (report as a fact, not automatic noncompliance)
   - useful historical rationale that cannot be proven from code
   - redundant or no longer useful reference material

Only flag contradictions when code/tests and page make incompatible claims about the same subject. A conflict with an old plan, note, or artifact alone is not drift or a blocker. Current user direction prevails; call out a concrete safety or compatibility consequence when relevant. Do not treat different levels of detail as drift.

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
- report implementation behavior and distinguish it from historical intent when they differ; do not infer a code defect from old design prose alone
- merge, supersede, or retire redundant/obsolete pages and repair index links
- preserve useful rationale proportionately as clearly marked history

Do not delete useful rationale just because implementation changed. Reframe it as history or a superseded decision when it still explains why the system evolved.

## Output

Report grouped results:

- fixed drift
- remaining drift needing user decision
- evidence gaps
- pages audited with no actionable drift

Include validation commands run, if any.
