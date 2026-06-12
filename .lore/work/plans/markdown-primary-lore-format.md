---
title: "Implementation plan: Markdown-primary lore format with embedded-HTML escape hatch"
date: 2026-06-10
status: approved
tags: [lore-development, document-format, markdown, html, schema, migration]
modules: [lore-development]
related: [.lore/work/specs/compass-rose-rework.md]
---

# Markdown-primary lore format with embedded-HTML escape hatch

**Goal.** Lore documents become Markdown by default (prose, lists, requirement tables, decisions, roughly 90% of any document). Raw inline HTML is reserved as an escape hatch for the cases where visuals carry meaning: color-coding, charts via inline `<svg>`, and side-by-side visual comparison. Embedded HTML is written raw and inline so it renders; never inside a ```` ``` ```` fence (a fence shows it as source). No `<script>`, no external dependencies.

**Render target.** Obsidian / local editors (VS Code preview, pandoc, browser). Inline `style=` and `<svg>` render fully, so no GitHub-sanitizer constraints apply.

**Why now.** Commit `c9ea6ab (#141)` "lean skill set, HTML output, visual-first documents" moved the whole format to full HTML. At ~80% success the cost shows up on prose-heavy documents, where the blanket "the output is HTML, use it" instruction makes the model scaffold a full CSS/JS document for content that is mostly text. This plan keeps the visual-first capability (#141's actual goal) but gates it to where it earns its place, and restores Markdown as the low-friction default the model authors reliably.

## Source of truth this plan validates against

The goal statement above, plus the repo facts gathered during inspection:

- `lore-development/shared/frontmatter-schema.md` (formerly `document-schema.md`) — the single source all skills load.
- `lore-development/scripts/frontmatter_schema.py` + `validate_frontmatter.py` — already encode the schema as YAML frontmatter and already scan for `.md` files. The pre-#141 format.
- Repo-root `.lore/` was a **mixed corpus**: older research/reference/learned/issues already `.md`; only recent notes/specs/retros were `.html`.

## Step sequence

This strip is the one genuinely-visual element in the plan: the dependency flow reads faster as a diagram than as prose, so it stays as embedded HTML.

<p style="font-family:system-ui;font-size:.8rem;display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;">
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">1 Schema doc</span> →
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">2 Format rule</span> →
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">3 Skills ×11</span> +
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">4 lore-researcher</span> +
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">5 reviewers</span> →
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">6 Validators</span> →
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">7 Migration</span> →
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">8 Version+docs</span> →
<span style="background:#eef;border:1px solid #ccd;border-radius:4px;padding:.2rem .5rem;">9 Final validation</span>
</p>

Category badges below use color to encode step type at a glance: <span style="background:#2c5f2d;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">FOUNDATION</span> <span style="background:#1d6fb8;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">EDITS</span> <span style="background:#b8860b;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">VERIFY</span> <span style="background:#8b1a1a;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">DECISION</span>

### Step 1 — Rewrite the schema doc as frontmatter-based &nbsp;<span style="background:#2c5f2d;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">FOUNDATION</span>

_Depends on: nothing. Blocks: 2, 3, 4, 6._

Rewrite `shared/document-schema.md` to describe **YAML frontmatter** instead of `<head><meta>`. **Rename (git mv, do not copy)** to `frontmatter-schema.md` — the name `frontmatter_schema.py` and README line 170 already reference. README lines 170/182 already describe the frontmatter target state (never reverted at #141), so the rename realigns the docs rather than fighting them.

**Loader-reference fan-out (the discrete first action).** `grep -rln 'document-schema.md' lore-development/skills lore-development/agents` returns **12 files** (11 skills + `lore-researcher.md`), each carrying `Load ${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md`. Every one must be repointed. If the rename happens without this fan-out, the renamed file is unreachable from every skill and agent.

- Metadata moves from `<meta name="x" content="y">` to top-of-file YAML.
- Keep the three-directory model, per-type status tables, and tag/module guidance verbatim. Only the container changes, not the field set or status values.
- Replace each HTML example block with the Markdown+frontmatter equivalent.
- `title` still appears twice: frontmatter `title:` and the body `# H1`.

> **Validation gate.** Diff the field list and every status set against the constants in `frontmatter_schema.py` (`REQUIRED_FIELDS`, `OPTIONAL_FIELDS`, `FIELD_TYPES`, `STATUS_VALUES`, `TYPE_SPECIFIC_REQUIRED`). They must match exactly.

### Step 2 — Author the tiered body-format rule, once &nbsp;<span style="background:#2c5f2d;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">FOUNDATION</span>

_Depends on: 1. Blocks: 3._

Add a short **"Body Format"** section to the schema doc (single source; all skills already load this file). It states the 90/10 contract: Markdown by default; reach for embedded HTML only for color-coding, inline-`<svg>` charts, or side-by-side comparison; write it raw and inline, never fenced; no `<script>`, no external resources, no whole-document CSS scaffolding.

> **Validation gate.** The rule names the three escalation triggers, the no-fence requirement, and the no-script/no-external/no-scaffold constraints. It reads as "Markdown by default," not "HTML when you feel like it."

### Step 3 — Update the 11 artifact-saving skills &nbsp;<span style="background:#1d6fb8;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">EDITS</span>

_Depends on: 1, 2. Parallelizable across skills._

Each `skills/<name>/SKILL.md` carries up to three things: an `.html` save path, an "output is HTML, use it" paragraph, and the `Load .../document-schema.md` line from Step 1's fan-out. Update all present. **poke-holes saves nothing and is excluded.**

| Skill | Save path change | Format paragraph rewrite |
|-------|------------------|--------------------------|
| specify | `specs/[name].html → .md` | embedded HTML for per-requirement status badges and anchor links when scannability needs it |
| design | `design/[topic].html → .md` | embedded HTML for inline-SVG architecture/flow diagrams and side-by-side trade-off comparison |
| prep-plan | `plans/[name].html → .md` | embedded HTML for a visual step sequence with dependency indicators and distinguished validation gates |
| vision | `reference/vision.html → .md` | generic tiered rule |
| brainstorm | `brainstorm/[name].html → .md` | generic tiered rule |
| research | `research/…html → .md` | generic tiered rule |
| retro | `retros/[name].html → .md` | generic tiered rule |
| define-validation | `validation/[topic].html → .md` (standalone, line 12) | generic tiered rule |
| plan-breakdown | `tasks/NNN-[name].html → .md` | generic tiered rule |
| implement | `notes/[name].html → .md` | generic tiered rule |
| simplify | **two** edits: save line 30 `notes/simplify-<id>.html → .md` and resume-read pattern line 18 `notes/*.html → *.md` | generic tiered rule |

For each skill, replace the bespoke "the output is HTML, use it" sentence with a one-line pointer to the schema doc's Body Format section plus the doc-type-specific visual hint reframed as "_when_ you reach for HTML, it's for X."

**Delegation.** This step plus Steps 4–5 touch 14+ files. Split across 2–3 fresh-context sub-agents (per the >5-file swarming rule): agent A = skills group 1 (specify/design/prep-plan/vision/brainstorm/research), agent B = skills group 2 (retro/define-validation/plan-breakdown/implement/simplify), agent C = lore-researcher + reviewers.

> **Validation gate.** `grep -rni 'html' lore-development/skills` returns only intentional references. No skill still says "the output is HTML" or saves to `.html`.

### Step 4 — Update `lore-researcher` search &nbsp;<span style="background:#1d6fb8;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">EDITS</span>

_Depends on: 1. Parallel with 3, 5._

This is a **paragraph-by-paragraph rewrite** of the search-strategy section, not a grep-token swap. In `agents/lore-researcher.md`:

- The Step-1 loader line → `frontmatter-schema.md`.
- "Lore documents are HTML files (`.html`)... `**/*.html`" → frontmatter Markdown and a **dual-extension glob** (`**/*.md` and `**/*.html`). Non-negotiable regardless of the step-7 decision: dropping `.html` orphans the existing specs/notes/retros.
- Field patterns `<title>` / `<meta name="tags"` / `<meta name="modules"` → frontmatter keys `title:` / `tags:` / `modules:`.
- "Documents without this HTML structure won't be found" → "without frontmatter."
- All result-path examples → `.md`.

> **Validation gate.** A dry-run finds a known `.md` artifact and a known `.html` artifact by tag. Both surface.

### Step 5 — Fix reviewer-agent format references &nbsp;<span style="background:#1d6fb8;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">EDITS</span>

_Depends on: 1. Parallel with 3, 4._

Only `agents/spec-reviewer.md` has stray refs: `.lore/reference/glossary.html` at lines 40 and 95 → `.md`. `plan-reviewer.md` and `design-reviewer.md` contain no format references; confirm with a grep, change nothing if clean.

> **Validation gate.** `grep -rni '\.html' lore-development/agents` returns only intentional matches.

### Step 6 — Reactivate and verify the validators &nbsp;<span style="background:#b8860b;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">VERIFY</span>

_Depends on: 1. Blocks: 9._

`validate_frontmatter.py` already scans a tree for `.md` files and validates YAML frontmatter against the schema constants. It is referenced only by its own test, i.e. orphaned, not broken.

- Run `pytest lore-development/scripts/tests/`; confirm green against the step-1 schema.
- Its docstring mentions "tend's status mode" — there is no `tend` skill in the current lean set. Document the standalone CLI in the README; defer hook wiring.
- The docstring cites `frontmatter-schema.md` as source of truth — step 1 restores that filename, closing the drift.

> **Validation gate.** From repo root, `python lore-development/scripts/validate_frontmatter.py .lore` (the script is not on PATH) runs clean on the `.md` docs after conversions, and flags a deliberately-malformed fixture with exit 1.

### Step 7 — Existing `.html` corpus migration &nbsp;<span style="background:#8b1a1a;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">DECISION</span>

_Depends on: 4 (dual-extension search). Blocks: 9._

**LOCKED 2026-06-10: Option C + A.** Convert this repo's dogfood `.html` files for internal consistency, and make "leave mixed, search both extensions" the documented policy for downstream projects.

The dogfood set is exactly 5 existing files plus this plan: `notes/compass-rose-rework.html`, `notes/field-guide-plugin.html`, `retros/field-guide-initial-implementation.html`, `specs/compass-rose-rework.html`, `specs/field-guide-plugin.html`, and `plans/markdown-primary-lore-format.html` (this document, convert last). Each converted file must pass `validate_frontmatter.py`.

Alternatives considered and rejected: **A-only** (leave everything mixed) keeps this repo internally inconsistent; **B** (convert every downstream corpus) risks lossy translation of visual-first specs for little gain.

> **Validation gate.** `lore-researcher` still finds every pre-existing artifact, and `validate_frontmatter.py` passes on all converted `.md` docs.

### Step 8 — Version bump, README, changelog &nbsp;<span style="background:#8b1a1a;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">DECISION</span> <span style="background:#1d6fb8;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">EDITS</span>

_Depends on: 3–7._

**LOCKED 2026-06-10: minor bump to 3.1.0.** The field set and status values are unchanged, only the container flips, and dual-extension search keeps old docs readable, so nothing is removed and search stays backward-compatible. Bump `.claude-plugin/plugin.json` 3.0.2 → 3.1.0.

README is mostly already correct: lines 170/182 already cite `shared/frontmatter-schema.md` and "documents without frontmatter won't be found." Verify it for residual `.html` references rather than assuming a big rewrite. (Separately, the README mentions `/tend` and `/stratify` skills absent from the current set — pre-existing drift, out of scope.)

> **Validation gate.** `grep -rni 'html' lore-development/README.md CLAUDE.md` returns only intentional matches; version bumped in `.claude-plugin/plugin.json`.

### Step 9 — End-to-end validation against the goal &nbsp;<span style="background:#b8860b;color:#fff;font-size:.72rem;padding:.12rem .5rem;border-radius:10px;">VERIFY</span>

_Depends on: all prior._

- **Authoring check.** Run one real skill end-to-end (e.g. `/specify` on a throwaway feature). Confirm it saves `.md`+frontmatter, body is Markdown, visuals are raw inline HTML, not fenced.
- **Render check.** Open that output in Obsidian / VS Code preview. Confirm embedded `style=` and `<svg>` render, and that a fenced HTML sample (negative control) shows as source.
- **Schema check.** `validate_frontmatter.py` green on the new doc.
- **Search check.** `lore-researcher` finds the new doc by tag.
- **Goal diff.** Re-read the goal: Markdown-default ✓, HTML gated to the three triggers ✓, no-fence ✓, no-script/external ✓, renders in target ✓.

> **Final gate.** Every bullet passes. Any miss returns to the owning step, not a patch here.

## Out of scope

- Changing the field set, status values, or three-directory model — container-only change.
- Wiring the validator into a hook (deferred; CLI documentation only).
- Converting downstream consumer projects' `.lore/` corpora (policy = leave-mixed, dual-search).
- Pre-existing status-value drift in the back-catalog (`approved`/`shipped`/`complete` used outside their allowed directory sets) surfaced by the validator. Separate cleanup.
