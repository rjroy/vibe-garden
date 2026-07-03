---
name: stratify
description: Use when the wiki has outgrown its flat layout and pages need grouping into category directories. Reorganizes .lore/reference/ into category and subcategory trees, rewrites the index, and repairs every referrer. Triggers include "stratify the wiki", "organize the reference directory", "group the wiki into categories", "the wiki is too flat", and "reorganize the field guide".
---

# Stratify

Reorganize `.lore/reference/` into topical category directories once the flat layout stops scanning well. Move pages, keep every link working, and keep the index authoritative.

Stratify changes where pages live, never what they say. Page bodies, frontmatter, `fg-type`, `fg-sources`, and `fg-evidence` all stay untouched except for link path repairs.

## Thresholds

- A directory earns stratification when it holds more than ~12 pages (`index.*` and dotfiles don't count).
- Split an overgrown directory into 3-4 groups. As the wiki grows, adjust toward 6-7 top-level categories.
- Never create a directory that would hold fewer than ~3 pages; leave those pages where they are until siblings accumulate.
- Apply the rule recursively: a category gets subcategories only when it exceeds the threshold itself. Categories under the threshold stay flat.
- After the first stratification, later runs are incremental: split only the directories that outgrew the threshold. Don't reshuffle pages that already fit or rename categories without cause — every move has a link-repair cost.

## Steps

**1. Inventory and design the taxonomy.**

Read the index (`.lore/reference/index.md`, or `index.html` if that's all there is) and list every page on disk, recursively. Pages may be `.md` or `.html`; both move the same way. Note any page on disk the index doesn't list — those are orphans; adopt them into the new index during this run rather than leaving them invisible.

Group pages by topic, not by `fg-type` — type is already recorded in each page's frontmatter, and a category mixing decisions, lessons, and architecture about the same subject is the point. Derive topics from titles, index descriptions, and tags; skim page bodies only where those are ambiguous. Use short kebab-case directory names.

Present the proposed mapping as a table (category, subcategories, page count) before moving anything, and adjust if the user objects.

**2. Survey referrers.**

Before moving, find everything that links to pages about to move:

- Wiki-internal cross-links: relative links between pages under `.lore/reference/`.
- Repo-wide referrers: search the whole repository for `reference/<page-name>.md` (and `.html`). Matching on that suffix catches repo-rooted paths (`.lore/reference/page.md`) and relative ones (`../../reference/page.md`) in docs, work artifacts, code comments, and READMEs alike.

**3. Move pages.**

Create the category directories and move pages with `git mv` when in a git repository, so history follows the file. Only `index.*` and `.field-guide.json` stay at the wiki root.

**4. Repair links.**

- Rewrite wiki-internal relative links whose source and target ended up in different directories. Links between pages in the same directory survive unchanged.
- Update every external referrer found in step 2 to the new path.

Do not touch `fg-sources` (repo-relative ingestion provenance, unaffected by page moves) or `fg-evidence` (points at code, unaffected).

**5. Rewrite the index.**

The index must keep listing **every page**. Lint discovers pages only through index links, so a categories-only index would orphan the entire wiki.

Structure: one heading per category, a subheading per subcategory, each entry linking with a path relative to `.lore/reference/` and keeping its one-line description. Add or refresh a short "Layout" section at the top of the index recording the stratification policy, so future ingest runs place new pages correctly.

**6. Verify.**

Run both checks before reporting; a missed link repair is silent breakage.

- Link integrity: every relative `.md`/`.html` link in every wiki page resolves to a file on disk.
- Index coverage: the set of pages on disk (excluding `index.*`) exactly equals the set of pages the index links — nothing missing, nothing dangling.

A small throwaway script is the reliable way to check this; eyeballing dozens of pages is not.

**7. Report.**

Tell the user: the final category table with counts, how many external referrers were updated and where, any orphans adopted into the index, and the verification result.
