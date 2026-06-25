---
name: update-evidence
description: Use after ingesting or editing field-guide pages to attach living code/test anchors. Adds or refreshes fg-evidence metadata without trying to prove prose accuracy. Triggers include "update evidence", "wire evidence", "add evidence anchors", and "connect the wiki to code".
---

# Update Evidence

Attach living implementation anchors to field-guide reference pages.

This is the mechanical pass between ingestion and semantic drift review:

1. `ingest` extracts durable knowledge from `.lore/work/`.
2. `update-evidence` connects that knowledge to current code and tests.
3. `resolve-drift` compares the prose against those anchors.

## Scope

Update indexed pages in `.lore/reference/`. Prefer `.lore/reference/index.md`; if it does not exist, read `.lore/reference/index.html`. Links may point to `.md` or `.html` pages.

Do not require `fg-sources` files to exist. Source artifacts are ingestion provenance and may be intentionally deleted after knowledge is extracted.

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

Read the page body and identify concrete implementation claims:

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

If a page is mostly policy or product philosophy and has no honest living implementation anchor, leave it without evidence and report it as intentionally unanchored.

## Output

Report:

- pages updated
- pages intentionally left without evidence
- pages where evidence was uncertain and should be reviewed

Do not rewrite page prose during this skill unless necessary to keep metadata valid. Semantic corrections belong in `resolve-drift`.
