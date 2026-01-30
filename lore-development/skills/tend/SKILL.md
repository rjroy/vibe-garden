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
2. Check each document for status field presence
3. For documents with status, verify accuracy
4. Update only the status field (nothing else)
5. Report findings and updates

## Status Values by Document Type

Each document type has appropriate status values:

### Specs (`.lore/specs/`)
- `draft` - Still being written
- `active` - Driving current work
- `complete` - All requirements met
- `abandoned` - Work stopped, not completing

### Plans (`.lore/plans/`)
- `draft` - Still being designed
- `active` - Guiding current implementation
- `complete` - All planned work done
- `superseded` - Replaced by a newer plan

### Brainstorms (`.lore/brainstorm/`)
- `open` - Ideas still being explored
- `incorporated` - Ideas moved into specs/plans
- `parked` - Not pursuing now, might revisit

### Research (`.lore/research/`)
- `reference` - Useful ongoing reference
- `stale` - Information likely outdated

### Validations (`.lore/validations/`)
- `active` - Testing guidelines in use
- `complete` - Testing phase done

### Retros (`.lore/retros/`)
Retros don't need status - they're historical records.

### Excavations (`.lore/excavations/`)
Excavation layers track their own completion state. Treat as `reference`.

## Verification Approach

Don't trust claimed status. Verify using these techniques:

**For "complete" specs**:
- Use Glob to find a plan with the same name in `.lore/plans/`
- Check if that plan's status is also complete
- If no plan exists, the spec likely isn't complete

**For "complete" plans**:
- Check if implementation appears done (code exists, tests pass)
- Look for retro or validation documents referencing this plan

**For "incorporated" brainstorms**:
- Use Grep to search for the brainstorm filename or key terms in `.lore/specs/`
- If no references found, status should be `parked` or `open`

**For "active" anything**:
- Check last modified date (via Bash `ls -l` or file metadata)
- Documents marked "active" but not modified in 30+ days are likely stale or abandoned

## Honest Status

Status can be descriptive and honest. When simple values don't capture reality, use phrases:

- `status: incorporated incorrectly` - Ideas made it to spec but were misunderstood
- `status: partially complete` - Some requirements met, others dropped
- `status: blocked` - Can't proceed due to external dependency
- `status: unclear` - Need investigation to determine actual state

Truth over optimism. A status of "unclear" is better than a false "complete".

## Progressive Discovery

Like the excavate skill, tend works progressively:

1. **First pass**: Identify documents without status fields
2. **Second pass**: Surface documents with status that looks stale
3. **Third pass**: Verify claimed statuses against evidence

Don't try to fix everything at once. Surface findings, get confirmation, then update.

## Output

Report findings in categories:

```markdown
## Tend Report

### Missing Status
- `.lore/specs/user-profiles.md` - no status field
- `.lore/brainstorm/caching-ideas.md` - no status field

### Potentially Stale
- `.lore/plans/auth-flow.md` - marked "active", last modified 30 days ago
- `.lore/specs/notifications.md` - marked "active", no plan exists

### Verified Accurate
- `.lore/specs/auth-flow.md` - complete (plan complete, work done)
- `.lore/brainstorm/early-ideas.md` - incorporated (found in auth-flow spec)

### Updated
- `.lore/specs/user-profiles.md` - added status: draft
- `.lore/plans/auth-flow.md` - changed active → complete

### Needs Decision
- `.lore/brainstorm/caching-ideas.md` - no spec references it. Mark as parked?
```

## Acting on Findings

After generating the report, handle each category:

1. **Missing Status**: Add status automatically using best-guess default (usually `draft` or `open`). Include in "Updated" section.

2. **Verified Accurate**: No action needed. Document is correct.

3. **Potentially Stale / Needs Decision**: Present to user and wait for confirmation before updating. User responds with "update [filename] to [status]" or "leave as-is".

4. After user decisions, make confirmed updates and report final state.

## Behavior

**Update only status**: Don't rewrite documents. Add or modify only the status field.

**Auto-update vs ask**: Missing status can be auto-added (with report). Changing existing status requires confirmation unless clearly verifiable.

**Preserve history**: If a document has no status, add one. Don't delete or archive documents (that's a separate decision).

**Be honest**: If you can't determine status, say so. "unclear" is a valid status.

## Adding Status to Documents

When a document lacks a status field, add it at the top after any existing frontmatter:

```markdown
# Document Title

**Status**: [appropriate value]

[rest of document]
```

Or in YAML frontmatter if the document uses it:

```yaml
---
status: draft
---
```

Prefer the inline format (`**Status**:`) for consistency with other lore-development patterns.
