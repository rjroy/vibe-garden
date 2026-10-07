---
name: update-evidence
description: Use after ingesting or editing field-guide pages to attach living code/test anchors. Adds or refreshes fg-evidence metadata without trying to prove prose accuracy. Triggers include "update evidence", "wire evidence", "add evidence anchors", and "connect the wiki to code".
---

# Update Evidence

Attach living implementation anchors to field-guide reference pages.

This is the mechanical pass between ingestion and semantic drift review:

1. `ingest` distills useful candidates from eligible historical `.lore/` artifacts and verifies current claims against code/tests.
2. `update-evidence` adds honest anchors for claims about current behavior.
3. `resolve-drift` reviews prose against those anchors and current user direction.

## Scope

Update indexed pages in `.lore/reference/`. Prefer `.lore/reference/index.md`; if it does not exist, read `.lore/reference/index.html`. Links may point to `.md` or `.html` pages.

Do not require `fg-sources` files to exist. Source artifacts are provenance only and may be intentionally deleted; their presence, status, or age does not establish that page claims are current or binding.

## Evidence Metadata

For Markdown pages, add or refresh YAML frontmatter:

```yaml
fg-evidence:
  code:
    - src/core/model/types.ts
  tests:
    - src/core/tests/model.test.ts
  symbols:
    - CardEffect
```

For HTML pages, add or refresh meta tags in `<head>`:

```html
<meta name="fg-evidence-code" content="src/core/model/types.ts">
<meta name="fg-evidence-tests" content="src/core/tests/model.test.ts">
<meta name="fg-evidence-symbols" content="CardEffect">
```

## How To Choose Evidence

Read the page body and identify concrete claims about current implementation that merit verification:

- named modules, files, APIs, data files, and tests
- symbols in backticks
- world ids, feature ids, schema names, and settings keys
- statements about ownership, runtime flow, persistence, validation, UI behavior, or test coverage

Search the repository for those anchors with `rg`. Evidence should point to files that would naturally change if the page became stale.

Good evidence:

- code paths that implement the claim
- data files that contain the authored truth
- tests that assert the behavior
- stable symbols that should exist while the claim remains true

Weak evidence:

- files that only mention the same words incidentally
- generated artifacts
- stale work artifacts under `.lore/work/`
- broad project files such as `package.json` unless the page is specifically about tooling or stack choice

If a page is historical rationale, policy, or product philosophy that code/tests cannot prove, leave it without a fabricated anchor and report it as intentionally unanchored. An evidence link supports investigation; it does not by itself prove the whole page or make old intent binding. Do not add evidence to an implementation summary that should instead be merged or retired.

## Output

Report:

- pages updated
- pages intentionally left without evidence
- pages where evidence was uncertain and should be reviewed

Do not rewrite page prose during this skill unless necessary to keep metadata valid. Semantic corrections belong in `resolve-drift`.
