---
title: YAML frontmatter validation and repair in tend
date: 2026-03-10
status: resolved
tags: [tend, yaml, validation, frontmatter, reliability]
modules: [lore-development, tend-skill]
related:
  - .lore/brainstorm/tend-discovery-modes.md
  - .lore/brainstorm/lore-development/document-lifecycle-and-lore-hygiene.md
---

# Brainstorm: YAML Frontmatter Validation in Tend

## Context

The tend skill maintains `.lore/` document health through four modes: status, tags, filenames, directories. The status mode detects documents with no frontmatter at all ("Missing Frontmatter") and offers to retrofit it. But there's a gap between "has frontmatter" and "has parseable frontmatter." A document with a `---` block that contains malformed YAML is invisible to lore-researcher, breaks tend's own status/tags modes, and silently degrades the compound loop.

The triggering observation: `title` values containing colons break YAML parsing when unquoted. This is common in lore artifacts because titles naturally describe relationships (`Implementation notes: auth-flow`, `Phase 1: Setup`). The frontmatter schema's own examples include `title: Implementation notes: auth-flow` (unquoted, colon-containing) as valid, which works in most YAML parsers but creates a false sense of safety. The moment someone writes `title: Note: a key: value-looking thing` or uses `#`, `&`, `*`, or `!` in a value, parsing breaks silently.

## Ideas Explored

### What actually breaks (a taxonomy of errors)

Not all YAML errors are equally likely in lore frontmatter. Ordered by observed frequency in real `.lore/` directories:

**Tier 1: Common, seen in practice**
- Unquoted strings with colons followed by spaces: `title: Phase 1: Do the thing` (works accidentally in most parsers but fragile)
- Missing closing `---` delimiter (document body gets swallowed into frontmatter)
- Tab characters mixed with spaces in indentation (especially in `related:` or `tags:` lists)

**Tier 2: Occasional, usually from hand-editing**
- Broken array syntax: `tags: [one, two` (missing closing bracket)
- Inconsistent indentation in multi-line values or nested structures (meeting_log entries, commission timelines)
- Boolean coercion: `status: yes` parsed as `true` instead of string "yes" (YAML 1.1 legacy)

**Tier 3: Rare but catastrophic when they happen**
- Hash character starting a comment mid-value: `title: Something #with a note` (truncated to "Something")
- Anchor/alias characters: `title: *asterisk-started` (parsed as alias reference)
- Unescaped special characters in machine-generated fields (commission `prompt:` with backticks, newlines, colons)

**Tier 4: Structural, not per-field**
- Duplicate keys (two `status:` lines, only last one wins silently)
- Frontmatter that's actually markdown (starts with `---` but the block contains `## Heading`)

### Where does this fit in the tend flow?

Three options. I think the answer is clear but worth examining all three.

**Option A: New mode ("syntax" or "parse")**

Add a fifth mode to the dependency chain: `syntax → status → tags → filenames → directories`. Frontmatter must be parseable before any other mode can meaningfully inspect it.

Pros: Clean separation. Each mode does one thing. Follows the existing pattern.
Cons: Adds overhead to every tend run. Might feel heavy for what's mostly a "check and fix typos" operation.

**Option B: Pre-check phase within status mode**

Status mode already handles "Missing Frontmatter." Extend it: before looking at field values, verify the frontmatter block parses at all. Report "Malformed Frontmatter" alongside "Missing Frontmatter" in the same report.

Pros: Natural extension of existing work. Status mode is already where frontmatter problems surface. No new mode to document or maintain.
Cons: Mixes structural validation (is this valid YAML?) with semantic validation (is this status value correct?). But the existing status mode already mixes "has frontmatter" with "has correct status," so the precedent exists.

**Option C: Inline logic in every mode**

Each mode tries to parse frontmatter, catches failures, and reports them. No centralized validation.

Pros: None, really.
Cons: Duplicated error handling. Inconsistent reporting. Same error surfaced four times if running all modes.

**My lean: Option B.** Status mode is the right home. It already owns the "is this document's metadata in order?" question. Adding "is the metadata parseable?" is a natural precursor to "is the status field correct?" The report format already has a "Missing Frontmatter" category; "Malformed Frontmatter" slots in right next to it.

The dependency chain stays the same. Status just gains an earlier internal step: parse check, then field checks.

### How does Claude validate YAML without a parser?

This is the interesting technical question. Claude Code reads files as text. There's no `yaml.safe_load()` to call. Three approaches:

**Approach 1: Heuristic line-by-line checks**

Claude reads the raw frontmatter text and applies pattern checks:
- First line is `---`
- Last line before content is `---`
- No tab characters
- Each line either: a `key: value` pair, a list item (`  - item`), a continuation of a multi-line value, or empty
- Values containing `: ` (colon-space) after the key are flagged as potential problems if unquoted
- Values starting with `[` have matching `]`
- Values starting with `{` have matching `}`

Pros: Predictable. Can be described in the reference file. Doesn't depend on Claude's YAML knowledge being perfect.
Cons: Heuristics miss edge cases. Risk of false positives on valid but unusual YAML.

**Approach 2: Claude-as-parser (natural language understanding)**

The tend prompt says: "Read the frontmatter block. Can you extract each field as a key-value pair? If any field is ambiguous, malformed, or would fail in a strict YAML parser, flag it."

Pros: Claude actually understands YAML pretty well. It can identify problems that heuristics would miss (semantic issues like `status: yes` being boolean-coerced). More flexible.
Cons: Non-deterministic. Different model calls might flag different things. Harder to test or predict.

**Approach 3: Bash YAML linter**

Invoke a YAML linter via Bash (if available). `python3 -c "import yaml; yaml.safe_load(open('file'))"` or `yq` or similar.

Pros: Definitive answer on parseability. No heuristic guessing.
Cons: Depends on tool availability. Different systems have different tools. The tend skill is a markdown prompt, not a script, so calling out to bash adds complexity.

**My original lean: Approach 1 (heuristics) with Approach 2 (Claude judgment) as fallback.** This was wrong. Revisited during audience review (2026-03-09) with three counter-arguments that invert the ranking:

**Counter-argument 1: Token cost.** Reading every file and having Claude analyze each frontmatter block is N tool calls plus N judgment calls. A single `python3` invocation across all `.lore/` files is one Bash call. The cost difference isn't marginal, it's orders of magnitude.

**Counter-argument 2: Circular review.** Claude Code generates this frontmatter. Asking the same model to review its own output is asking the student to grade their own test. If the generator produces broken YAML, it may have the same blind spots when reviewing. A parser doesn't care who wrote it. It either parses or it doesn't. Objective truth beats self-review.

**Counter-argument 3: Right tool for each job.** The detection step needs objectivity and cheapness (parser). The fix step needs context and intelligence (Claude). Splitting find-vs-fix across tools means each does what it's good at: Python tells tend "these files have broken frontmatter, here's the parse error." Claude reads only those specific files, understands the error, and proposes fixes.

**Revised lean: Approach 3 (Python linter) as the primary detection mechanism.** Approach 1 (heuristics) becomes unnecessary because the parser gives a definitive answer. Approach 2 (Claude judgment) remains, but only for the fix step after broken files are identified.

**Correction (2026-03-09):** PyYAML is NOT in Python's standard library. It's a third-party package (`pip install pyyaml`). Commonly pre-installed on Linux (package managers depend on it) but not guaranteed. The validation script should be bundled with the plugin and handle the import gracefully.

**Extended scope (2026-03-09):** Schema validation (required fields, valid status values, field types) is also deterministic and belongs in the script, not in Claude. The same arguments apply: cheaper, objective, and Claude shouldn't grade its own test. The script should validate both parseability and schema conformance in a single pass.

### Auto-fix vs. report: what's safe?

The core principle: auto-fix only when the fix is unambiguous and reversal is trivial.

**Safe to auto-fix (with confirmation in the report):**
- Missing closing `---`: add it before the first blank line or heading
- Tab characters in indentation: replace with spaces (2-space indent, matching YAML convention)
- Unquoted string values containing `: `: wrap in double quotes
- Trailing whitespace on frontmatter lines

**Report but don't auto-fix:**
- Broken array syntax (missing bracket): could be a typo or could indicate the author meant something different
- Duplicate keys: which one is correct? Only the human knows.
- Boolean coercion (`yes`/`no`/`on`/`off`): might be intentional (unlikely in lore, but possible)
- Values with `#` that might be comments or might be literal: context-dependent
- Structural problems (frontmatter contains markdown headings): might mean the closing `---` is in the wrong place, or the whole block needs rewriting

**Never touch:**
- Machine-generated frontmatter that's complex but valid (commission timelines, meeting logs with nested structures). If it parses, leave it alone.
- Quoted strings that are already quoted. Don't double-quote.
- Values in flow sequences `[a, b, c]` or flow mappings `{key: val}` where the structure is valid.

### The quoting question deserves more thought

The most common auto-fix would be quoting unquoted strings with colons. But which quoting style?

```yaml
# Original (broken)
title: Phase 1: Do the thing

# Fix option A: double quotes
title: "Phase 1: Do the thing"

# Fix option B: single quotes (preserves backslashes literally)
title: 'Phase 1: Do the thing'
```

Double quotes are the right default. They match what most lore artifacts already use (the commission file uses `title: "Commission: ..."`, the meeting file uses `title: "Audience with Guild Master"`). Single quotes only matter when the value contains backslashes, which is rare in lore metadata.

But here's a subtlety: `title: Phase 1: Do the thing` actually parses correctly in most YAML implementations. The colon-space after "1" is within the scalar value, not starting a new key, because the parser already found the first key-value separator. So should tend flag it?

I think yes, with a light touch. Flag it as "fragile" rather than "broken." The report says: "This value contains `: ` which works in most YAML parsers but is technically ambiguous. Quoting it makes intent explicit." Auto-fix only when the user confirms.

### How strict should validation be?

Three tiers of strictness, each catching different things:

**Structural (always check):** Does the frontmatter block have opening and closing `---`? Are there tab characters? Do brackets match? These are unambiguous errors.

**Semantic (check against schema):** Does the `status` value match the valid list for this document type? Is `date` in YYYY-MM-DD format? Are `tags` an array, not a string? These have clear right answers defined in the frontmatter schema and lore-config.

**Stylistic (suggest, don't enforce):** Are strings with special characters quoted? Is indentation consistent? Is the field order conventional (title, date, status, tags, modules, related)? These are preferences, not errors.

Tend should always run structural checks. Semantic checks should run when the schema is available (it always is, since it's in the plugin's shared directory). Stylistic suggestions should be opt-in or at least clearly labeled as suggestions.

### What about the lore-config interaction?

The config system (`lore-config.md`) already defines `custom_fields` for custom directory types. Frontmatter validation should respect this:
- Don't flag `worker:` as unexpected in a commission if `custom_fields.commissions` includes `worker`
- Don't flag custom status values as invalid if `custom_directories` defines them
- Do flag YAML syntax errors in custom fields (a syntactically broken `prompt:` value is still broken, regardless of whether `prompt` is a valid field name)

The config suggestion step at the end of tend could also learn from validation findings. If tend finds a field it doesn't recognize but the YAML is valid, that's a config suggestion ("should `worker` be added to custom_fields for commissions?"). If the YAML is broken, that's a fix, not a config item.

### What about documents outside `.lore/`?

Tend currently scans `.lore/` only. But YAML frontmatter exists in other places: skill files (`SKILL.md`), agent files (`AGENT.md`), even `CLAUDE.md` in some projects. Should validation extend there?

Probably not. Tend's scope is `.lore/`. Skill and agent frontmatter are part of the plugin development workflow, not the lore workflow. If those need validation, it belongs in the plugin-validator agent, not in tend.

## Open Questions

1. **Should the validation report include a "confidence" level?** Some issues are definite errors (missing closing `---`). Others are fragile patterns that might work fine. Distinguishing "will break" from "could break" helps the user prioritize.

2. **What about performance on large `.lore/` directories?** Scanning 50+ documents and reading each one's frontmatter block adds tool calls. Should tend batch-read (cat multiple files via bash) or read sequentially? The existing modes already read every document, so this isn't a new problem, but adding a parse-check step multiplies the per-document work.

3. **Should there be a `--fix` flag?** Something like `/tend status --fix` that auto-applies safe fixes without confirmation. This goes against tend's current philosophy (always confirm), but for "obviously right" fixes like adding quotes around colon-containing strings, the confirmation step might feel like busywork on the tenth document.

4. **What about preventing errors at creation time?** Instead of (or in addition to) fixing broken frontmatter in tend, should the skill templates that generate frontmatter (brainstorm, specify, etc.) be more defensive? For example, always quoting the `title:` value in the template. Prevention is cheaper than repair. But that's a separate concern from tend's hygiene role.

## Next Steps

If this direction is worth pursuing:
- Spec the validation behavior as an extension to the status mode reference (`references/status.md`)
- Define the exact heuristic checks and their severity levels
- Add "Malformed Frontmatter" and "Fragile Frontmatter" categories to the status report format
- Consider whether creation-time prevention (quoting templates) is worth a separate brainstorm
