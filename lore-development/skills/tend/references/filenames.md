# Filenames Mode Reference

Audit filename consistency and suggest improvements based on content.

## Purpose

Filenames are the first layer of findability. Consistent naming makes files predictable. Content-aligned naming makes them discoverable.

## Checks

### Convention Consistency

All `.lore/` filenames should follow kebab-case:

| Pattern | Problem | Example |
|---------|---------|---------|
| `camelCase.md` | Wrong case style | `authFlow.md` → `auth-flow.md` |
| `snake_case.md` | Wrong separator | `auth_flow.md` → `auth-flow.md` |
| `spaces in name.md` | Spaces in filename | `auth flow.md` → `auth-flow.md` |
| `UPPERCASE.md` | Shouting | `README.md` is fine; `AUTH-FLOW.md` is not |

**Dates belong in frontmatter**, not filenames. Use the `date:` field for temporal metadata. Filenames should describe content, not when it was created.

**Filename exemptions**: If `.lore/lore-config.md` exists and defines `filename_exemptions`, check each filename against those regex patterns before applying convention rules. Files matching any exemption pattern skip case-style, date-in-filename, and tag-alignment checks entirely. This covers machine-generated filenames (e.g., `commission-Worker-20260305-210147.md`) that use timestamps as unique identifiers.

When a filename is flagged but the user says it's intentional (typically because it's machine-generated), record the pattern for the config suggestion step rather than asking again next run.

### Tag-Informed Naming

Filenames should reflect primary tags:

1. Extract document's tags and title
2. Check if filename aligns with primary concept
3. Flag mismatches

Example:
```
File: .lore/build/specs/feature-x.md
Tags: [authentication, oauth, security]
Title: "OAuth 2.0 Authentication Flow"

Suggestion: Rename to auth-oauth-flow.md (aligns with content)
```

### Collision Detection

Filenames that differ only by small variations can cause confusion:

| Collision Type | Example | Problem |
|----------------|---------|---------|
| Numeric suffix | `auth-flow.md`, `auth-flow-2.md` | Which is current? |
| Date variant | `auth-flow.md`, `auth-flow-jan.md` | Temporal confusion |
| Abbreviation | `authentication.md`, `auth.md` | Same topic, different files |

Flag collisions. User decides which to keep or how to differentiate.

## Output Report

```markdown
## Filenames Report

### Convention Violations
| File | Issue | Suggested |
|------|-------|-----------|
| specs/authFlow.md | camelCase | auth-flow.md |
| brainstorm/user_ideas.md | snake_case | user-ideas.md |

### Name-Content Mismatch
| File | Primary Tags | Suggested Name |
|------|--------------|----------------|
| specs/feature-x.md | auth, oauth | auth-oauth-flow.md |
| research/notes.md | websocket, realtime | websocket-research.md |

### Potential Collisions
| Files | Issue |
|-------|-------|
| specs/auth.md, specs/authentication.md | Same topic? |
| plans/v2-plan.md, plans/v2-plan-revised.md | Which is current? |
```

## Applying Changes

**Renaming requires dependency updates**:

1. Find all documents that reference the old filename
2. Present rename plan: old → new + affected files
3. On confirmation:
   - Rename the file
   - Update all `related:` fields referencing it
   - Update any markdown links `[text](./old-name.md)`

Use Grep to find references before renaming:
```
grep -r "old-filename" .lore/
```

**Batch renames**:
- Present full batch before any changes
- Apply all or none (atomic from user perspective)
- Report final state after completion

## Progressive Discovery

Filenames mode works in passes:

1. **Scan pass**: List all filenames with metadata
2. **Analysis pass**: Check conventions, extract tags, detect collisions
3. **Report pass**: Present categorized findings
4. **Apply pass**: Rename with dependency updates

Use TaskCreate for each pass.
