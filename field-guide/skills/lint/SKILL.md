---
name: lint
description: "This skill is used when the project wiki needs a health check. Triggers include 'lint the wiki', 'check wiki health', 'run field-guide lint', 'are there stale wiki pages', 'find orphaned pages', 'check for contradictions in the wiki'."
---

# Lint

Health-check the wiki. Find what's broken, what's stale, what's drifted. Produce a report the maintainer can act on.

## Steps

**1. Load the index.**

Read `.lore/reference/index.html`. Collect every relative link it lists — these are the indexed pages. If the index doesn't exist or contains no links, report that and stop.

**2. Run four checks.**

Run all four checks before reporting. Each check has a defined severity; do not promote or demote.

---

### [error] Contradictions

Read every indexed wiki page in full. Look for pages that make conflicting claims about the same concept, entity, or decision. Two pages contradict each other when they assert incompatible facts about the same subject — not merely when they discuss it differently or at different levels of detail.

For each contradiction found, record:
- Both page paths
- The specific claim each page makes
- The subject they disagree on

---

### [warning] Orphans

List every `.html` file in `.lore/reference/`. Exclude `index.html`. Any file not listed in the index is an orphan.

For each orphan, record its path.

---

### [warning] Stale sources

For each indexed wiki page, read its `<meta name="fg-sources">` tag. The value is a comma-separated list of relative paths.

For each source path:
1. Check whether the file exists on the filesystem.
2. If it exists, compare its modification time against the wiki page's modification time.
3. If the source is newer than the wiki page, the page is stale.

For each stale page:
- Set the `<meta name="fg-status">` tag value to `stale`.
- Record the page path and which source files triggered the flag.

After updating all stale pages, include the list of modified files in the report output under the stale sources section: `Modified: [path list]`.

If a source file no longer exists, record it as a missing source (also a warning).

---

### [info] Missing concept pages

Scan all indexed wiki page bodies for terms that appear across multiple pages. A term is a candidate if it recurs in at least two pages and has no dedicated page with `fg-type` set to `concept`.

Flag all candidates found.

For each candidate, record the term and which pages reference it.

---

**3. Produce the report.**

Group findings by severity in this order: errors, warnings, info. Within each group, list findings individually with enough detail to act on them.

Format:

```
[error] Contradiction
  Pages: .lore/reference/auth-decision.html, .lore/reference/auth-architecture.html
  Subject: whether JWT tokens are stateless
  Claim A: "tokens are stateless and require no server-side storage"
  Claim B: "tokens are validated against a server-side revocation list"

[warning] Orphan
  Path: .lore/reference/old-spike.html

[warning] Stale page
  Page: .lore/reference/auth-decision.html
  Newer sources: .lore/work/retros/auth-rollout.html

[warning] Missing source
  Page: .lore/reference/deploy-config.html
  Missing: .lore/work/specs/deploy-spec.html

[info] Missing concept page
  Term: "revocation list"
  Referenced in: .lore/reference/auth-decision.html, .lore/reference/auth-architecture.html, .lore/reference/session-management.html
```

If a severity bucket is empty, omit it. If no findings at all, say so.

Close with a one-line count: `N errors, N warnings, N info`.
