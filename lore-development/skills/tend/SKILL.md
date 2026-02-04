---
name: tend
description: This skill performs periodic hygiene on the .lore/ directory. Use when documents have accumulated, status fields are missing or stale, or you need to understand what's active vs complete vs abandoned. Triggers include "tend the lore", "check document status", "lore hygiene", "what's stale", "review lore health".
---

# Tend

Maintain hygiene across `.lore/` documents.

## When to Use

- Documents have accumulated and status is unclear
- Before starting new work, to understand what's active
- Periodically, to keep lore healthy
- When something feels "off" about the project state

## Process

1. Scan all documents in `.lore/`
2. Check each document for YAML frontmatter presence
3. Check each document for status field presence
4. For documents with status, verify accuracy
5. Update frontmatter or status as needed
6. Report findings and updates

## Task Tracking

Use `TaskCreate` to make the tending process visible and structured. Create tasks for each phase of work:

```
TaskCreate: "Scan .lore/ for documents without frontmatter"
TaskCreate: "Identify documents with missing or stale status"
TaskCreate: "Verify claimed statuses against evidence"
TaskCreate: "Present findings and get user decisions"
TaskCreate: "Apply confirmed updates"
```

Mark tasks `in_progress` before starting work, `completed` when done. This forces deliberate pacing through each phase.

**Why task tracking matters here:**
- Rushing through phases causes missed documents and skipped verification
- Each pass requires different tools and checks; collapsing them loses thoroughness
- Task boundaries force you to finish one thing before starting the next
- A task marked complete is a claim that the work was done properly

## Status Values

**Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`** for the canonical list of status values by document type.

The schema defines valid status values for each document type (specs, plans, brainstorms, research, retros, diagrams). Use those values when adding or updating status fields.

## Verification Approach

Don't trust claimed status. Verify using these techniques:

**For "complete" specs**:
- Use Glob to find a plan with the same name in `.lore/plans/`
- Check if that plan's status is also complete
- If no plan exists, the spec likely isn't complete

**For "complete" plans**:
- Check if implementation appears done (code exists, tests pass)
- Look for retro documents referencing this plan

**For "implemented" designs**:
- Check if a plan exists that references this design
- Check if that plan's status is executed
- If no plan exists, the design likely isn't implemented yet

**For "incorporated" brainstorms**:
- Use Grep to search for the brainstorm filename or key terms in `.lore/specs/`
- If no references found, status should be `parked` or `open`

**For "active" anything**:
- Check last modified date (via Bash `ls -l` or file metadata)
- Documents marked "active" but not modified in 30+ days are likely stale or abandoned

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

Like the excavate skill, tend works progressively. **Use TaskCreate for each pass** to maintain structure:

1. **First pass**: Identify documents without status fields
   - Create task, mark in_progress, complete when scan is done
2. **Second pass**: Surface documents with status that looks stale
   - Create task, mark in_progress, complete when stale candidates identified
3. **Third pass**: Verify claimed statuses against evidence
   - Create task, mark in_progress, complete when verification done

Don't try to fix everything at once. Surface findings, get confirmation, then update. Task tracking prevents collapsing phases and missing documents in the rush.

## Output

Report findings in categories:

```markdown
## Tend Report

### Missing Frontmatter
- `.lore/retros/auth-fix.md` - no YAML frontmatter
- `.lore/specs/old-feature.md` - no YAML frontmatter

### Missing Status
- `.lore/specs/user-profiles.md` - has frontmatter, no status field
- `.lore/brainstorm/caching-ideas.md` - has frontmatter, no status field

### Potentially Stale
- `.lore/plans/auth-flow.md` - marked "active", last modified 30 days ago
- `.lore/specs/notifications.md` - marked "active", no plan exists

### Verified Accurate
- `.lore/specs/auth-flow.md` - complete (plan complete, work done)
- `.lore/brainstorm/early-ideas.md` - incorporated (found in auth-flow spec)

### Updated
- `.lore/retros/auth-fix.md` - added frontmatter
- `.lore/specs/user-profiles.md` - added status: draft
- `.lore/plans/auth-flow.md` - changed active → complete

### Needs Decision
- `.lore/brainstorm/caching-ideas.md` - no spec references it. Mark as parked?

### Prefix Collisions
- `.lore/specs/auth-flow.md` and `.lore/specs/auth-feature.md` both resolve to AUTH-F*
  - Suggestion: Add `req-prefix: AUTHFLOW` to auth-flow.md
```

## Acting on Findings

After generating the report, handle each category. **Create tasks for actionable work:**

1. **Missing Status**: Add status automatically using best-guess default (usually `draft` or `open`). Include in "Updated" section.
   - TaskCreate: "Add missing status to N documents"

2. **Verified Accurate**: No action needed. Document is correct.

3. **Potentially Stale / Needs Decision**: Present to user and wait for confirmation before updating. User responds with "update [filename] to [status]" or "leave as-is".
   - TaskCreate: "Get user decisions on stale/unclear documents"
   - Do NOT mark complete until user has responded

4. After user decisions, make confirmed updates and report final state.
   - TaskCreate: "Apply confirmed status updates"

Use `TaskList` before moving between phases to confirm prior work is actually complete.

## Behavior

**Update only status**: Don't rewrite documents. Add or modify only the status field.

**Auto-update vs ask**: Missing status can be auto-added (with report). Changing existing status requires confirmation unless clearly verifiable.

**Preserve history**: If a document has no status, add one. Don't delete or archive documents (that's a separate decision).

**Be honest**: If you can't determine status, say so. "unclear" is a valid status.

## Frontmatter Retrofitting

Documents should have YAML frontmatter for searchability. Reference `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for field definitions.

When a document lacks frontmatter entirely, offer to add it:

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
