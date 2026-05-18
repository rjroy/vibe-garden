# Status Mode Reference

Verify and update document status fields across `.lore/`.

## Status Values

**Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`** for the canonical list of status values by document type.

The schema partitions valid status values into three sets, keyed by zone:

- **Work set** (per-type, under `.lore/work/<type>/`): each work subdirectory has its own lifecycle (e.g., specs use `draft / approved / implemented / superseded / archived`; plans use `draft / approved / executed / archived`; brainstorms use `open / parked / resolved / archived`). Use the schema for the exact list per type.
- **Reference set** (under `.lore/reference/`): `current / outdated / archived`. Solidified knowledge that callers cite.
- **Learned set** (under `.lore/learned/`): `active / superseded`. Mistakes-only entries; supersession is the only lifecycle that applies.

**Project-specific types**: If `.lore/lore-config.md` exists, its `custom_directories` field defines additional directory types and their valid status values. Documents in those directories use the config's status list instead of the schema defaults. Documents in directories that appear in neither the schema nor the config should be flagged as "unknown type" for user decision (and feed into the config suggestion step).

## Frontmatter Validation Pre-check

Before any manual verification, run the bundled validation script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_frontmatter.py .lore/
```

The script handles both formats: `.md` files (YAML frontmatter between `---` delimiters) and `.html` files (`<meta name="lore-*">` tags in `<head>`). Findings are emitted as JSON lines regardless of file format.

Capture stdout (JSON lines) and the exit code. Parse each JSON line into a structured finding.

**Exit code handling**:

- `0`: No validation errors. Proceed to three-pass verification.
- `1`: Errors found. Parse findings into report categories (see "Malformed Frontmatter" and "Invalid Frontmatter" under Output Report). Proceed with three-pass verification on passing files only.
- `2`: PyYAML not installed. Log a note in the status report: "Frontmatter validation skipped: PyYAML not installed." Proceed to three-pass verification without the pre-check.

**Mapping script findings to report categories**:

| Script `error_type` | Report category |
|----------------------|-----------------|
| `parse_error` | Malformed Frontmatter |
| `structural_error` | Malformed Frontmatter |
| `missing_field` | Invalid Frontmatter |
| `invalid_type` | Invalid Frontmatter |
| `invalid_status` | Invalid Frontmatter |

Files that appear in "Malformed Frontmatter" are excluded from the subsequent three-pass verification. Their YAML doesn't parse, so field-level checks and status verification can't run against them. Note the count in the report: "N files excluded from status verification due to malformed frontmatter."

## Verification Approach

Don't trust claimed status. Verify using these techniques:

**For "implemented" specs**:
- Use Glob to find a plan with the same name in `.lore/work/plans/`
- Check if that plan's status is `executed`
- If no plan exists or it isn't executed, the spec likely isn't implemented
- **Archive coupling (soft prompt)**: when an `implemented` spec is later surfaced as an archive candidate by `directories` mode, prompt "Distill this spec before archiving?" before archiving. The prompt is soft — the user can answer no and archive directly. See the "Distill-Before-Archive" section of `tend/SKILL.md`. Without this prompt, the reference-promotion opportunity captured in `/distill work <spec>` is silently lost when the spec is archived.

**For "executed" plans**:
- Check if implementation appears done (code exists, tests pass)
- Look for retro documents referencing this plan

**For "implemented" designs**:
- Check if a plan exists that references this design
- Check if that plan's status is `executed`
- If no plan exists, the design likely isn't implemented yet

**For "resolved" brainstorms**:
- Use Grep to search for the brainstorm filename or key terms in `.lore/work/specs/`
- If no references found, status should be `parked` or `open`

**For "active" research or learned entries**:
- Research: check last modified date; documents marked `active` but not modified in 30+ days are likely stale and should be `archived`
- Learned: an `active` entry is current advice; flag for `superseded` only when a follow-up entry exists that replaces it

**For "current" reference docs**:
- Reference is solidified knowledge. `current` should match what callers can actually rely on. If the underlying system has changed, the entry is `outdated` and needs refresh or archive

**For req-prefix collisions** (specs only):
- For each spec, determine its prefix (explicit `req-prefix` field, or auto-generated from filename)
- Auto-generation: first 2 segments of kebab-case filename, uppercase, max 12 chars
- Flag any specs that would share the same prefix
- Suggest adding explicit `req-prefix` to one or both to disambiguate

## Honest Status

Status can be descriptive and honest. When simple values don't capture reality, use phrases:

- `status: incorporated incorrectly` - Ideas made it to spec but were misunderstood
- `status: partially complete` - Some requirements met, others dropped
- `status: blocked` - Can't proceed due to external dependency
- `status: unclear` - Need investigation to determine actual state

Truth over optimism. A status of "unclear" is better than a false "complete".

## Progressive Discovery

Status mode works progressively. **Use TaskCreate for each pass** to maintain structure:

1. **First pass**: Identify documents without status fields
   - Create task, mark in_progress, complete when scan is done
2. **Second pass**: Surface documents with status that looks stale
   - Create task, mark in_progress, complete when stale candidates identified
3. **Third pass**: Verify claimed statuses against evidence
   - Create task, mark in_progress, complete when verification done

Skip files listed under "Malformed Frontmatter" during all three passes. Those files can't be verified at field level.

Don't try to fix everything at once. Surface findings, get confirmation, then update. Task tracking prevents collapsing phases and missing documents in the rush.

## Output Report

Report findings in categories:

```markdown
## Status Report

### Missing Frontmatter
- `.lore/work/retros/auth-fix.md` - no YAML frontmatter
- `.lore/work/specs/old-feature.md` - no YAML frontmatter

### Malformed Frontmatter
- `.lore/work/specs/broken.md` - YAML parse error: mapping values are not allowed here (line 3)
- `.lore/work/retros/old.md` - structural: missing closing delimiter

### Invalid Frontmatter
- `.lore/work/specs/auth.md` - missing required field: tags
- `.lore/work/plans/migration.md` - invalid status "wip" (valid: draft, approved, executed, archived)
- `.lore/work/brainstorm/ideas.md` - field type: tags should be a list, got string

### Missing Status
- `.lore/work/specs/user-profiles.md` - has frontmatter, no status field
- `.lore/work/brainstorm/caching-ideas.md` - has frontmatter, no status field

### Potentially Stale
- `.lore/work/plans/auth-flow.md` - marked "draft", last modified 30 days ago
- `.lore/work/specs/notifications.md` - marked "approved", no plan exists
- `.lore/reference/api-conventions.md` - marked "current", underlying system changed

### Verified Accurate
- `.lore/work/specs/auth-flow.md` - implemented (plan executed, work done)
- `.lore/work/brainstorm/early-ideas.md` - resolved (found in auth-flow spec)

### Updated
- `.lore/work/retros/auth-fix.md` - added frontmatter
- `.lore/work/specs/user-profiles.md` - added status: draft
- `.lore/work/plans/auth-flow.md` - changed draft -> executed

### Needs Decision
- `.lore/work/brainstorm/caching-ideas.md` - no spec references it. Mark as parked?

### Prefix Collisions
- `.lore/work/specs/auth-flow.md` and `.lore/work/specs/auth-feature.md` both resolve to AUTH-F*
  - Suggestion: Add `req-prefix: AUTHFLOW` to auth-flow.md
```

## Acting on Findings

After generating the report, handle each category. **Create tasks for actionable work:**

1. **Malformed Frontmatter**: Read only the files the script flagged. Read the raw frontmatter text for each and propose corrected YAML. For structural errors (missing delimiters, tabs in indentation), the fix is usually mechanical. For parse errors, examine the raw text and propose valid YAML that preserves the author's intent.
   - TaskCreate: "Repair malformed frontmatter in N documents"

2. **Invalid Frontmatter**: Propose the correct field value from the schema. Handle sub-types:
   - `missing_field`: Add the field with a sensible default (e.g., `status: draft`, `tags: []`).
   - `invalid_type`: Coerce to the correct type (e.g., convert `tags: "foo, bar"` to `tags: [foo, bar]`).
   - `invalid_status`: Check whether the value looks like an intentional honest-status phrase (e.g., "partially complete", "blocked", "incorporated incorrectly"). If it does, present it as "flagged by script, may be intentional" rather than a definitive error. The user decides whether to change it.
   - TaskCreate: "Repair invalid frontmatter in N documents"

3. **Missing Status**: Add status automatically using best-guess default (usually `draft` or `open`). Include in "Updated" section.
   - TaskCreate: "Add missing status to N documents"

4. **Verified Accurate**: No action needed. Document is correct.

5. **Potentially Stale / Needs Decision**: Present to user and wait for confirmation before updating. User responds with "update [filename] to [status]" or "leave as-is".
   - TaskCreate: "Get user decisions on stale/unclear documents"
   - Do NOT mark complete until user has responded

6. After user decisions, make confirmed updates and report final state.
   - TaskCreate: "Apply confirmed status updates"

**Repair confirmation flow**: Present all proposed fixes from steps 1 and 2 together before applying any. Follow tend's dry-run, confirm, apply pattern:

1. Present each proposed fix with the file path, current value, and proposed value.
2. Wait for user confirmation: accept all, accept some (by number or name), or reject.
3. Apply only confirmed fixes.
4. Report what was changed in the "Updated" section.

Use `TaskList` before moving between phases to confirm prior work is actually complete.

## Behavior

**Update only status**: Don't rewrite documents. Add or modify only the status field.

**Auto-update vs ask**: Missing status can be auto-added (with report). Changing existing status requires confirmation unless clearly verifiable.

**Preserve history**: If a document has no status, add one. Don't delete or archive documents (that's a separate decision).

**Be honest**: If you can't determine status, say so. "unclear" is a valid status.

## Frontmatter Retrofitting

Documents should have metadata for searchability. Reference `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for field definitions.

- **`.md` files**: Check for YAML frontmatter (`---` block). If missing, offer to add it.
- **`.html` files**: Check for `<meta name="lore-*">` tags in `<head>`. If missing, offer to add them using the base template's `<meta>` structure.

When a `.md` document lacks frontmatter entirely, offer to add it:

```markdown
---
title: [Extract from document heading]
date: [File creation or today's date]
status: [appropriate value]
tags: [infer from content]
modules: [infer from content, if applicable]
---

# Document Title

[rest of document]
```

### Retrofit Process

1. **Identify documents without frontmatter** - Look for files that don't start with `---`
2. **Extract metadata from content**:
   - Title: Use the first `# ` heading
   - Date: Use file creation date or today
   - Status: Use existing inline `**Status**:` or infer from document state
   - Tags: Infer 2-4 keywords from content
   - Modules: Identify codebase areas mentioned
3. **Present proposed frontmatter** to user for confirmation
4. **Add frontmatter** and remove redundant inline status if present

### Why This Matters

The `lore-researcher` agent searches frontmatter fields to find related prior work. Documents without frontmatter won't be surfaced, breaking the compound loop.

## Adding Status to Documents

When a document has frontmatter but lacks a status field, add it to the existing frontmatter:

```yaml
---
title: Existing Title
date: 2026-01-30
status: draft  # Added
tags: [existing, tags]
---
```

If a document uses inline status (`**Status**: draft`), migrate it to frontmatter for consistency.
