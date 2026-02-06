---
name: update-stubs
description: Scans specs for stubs and generates outstanding stub index. Use when reviewing spec coverage, before starting new specification work, or after completing a specification. Triggers include "update stubs", "check stubs", "stub index", "outstanding stubs".
artifact_path: .lore/stubs
---

# Update Stubs

Scan all specifications for stubs and generate an index of unresolved ones.

## When to Use

- After completing a specification (to update the known unknowns)
- Before starting new specification work (to see what's already identified)
- Reviewing spec coverage across a project
- Finding what to specify next

## Process

### Step 1: Scan for Stubs

Scan all `.md` files in `.lore/specs/` recursively. Extract all `[STUB: name]` patterns using regex.

Pattern to match: `\[STUB:\s*([^\]]+)\]`

For each stub found, record:
- The stub name (trimmed)
- The source file path

### Step 2: Validate Stub Names

Check each stub name for validity:

**Valid**: kebab-case only (lowercase letters, numbers, hyphens). Must start with a letter.
- Valid: `auth-flow`, `payment-processing`, `user-auth-2`
- Invalid: `Auth Flow` (spaces), `auth_flow` (underscores), `123-start` (starts with number)

Invalid names are flagged as errors.

### Step 3: Check Resolution

For each valid stub, check if it's resolved:

A stub is resolved if `.lore/specs/[stub-name].md` exists (exact match, case-sensitive).

Note: Stubs can also be resolved by nested specs (e.g., `.lore/specs/parent/[stub-name].md`). Scan recursively for matching filenames.

### Step 4: Identify Warnings

Flag these conditions as warnings:
- **Self-referential stub**: A spec contains a stub reference to itself (e.g., `checkout.md` contains `[STUB: checkout]`)

### Step 5: Generate Index

Write the stub index to `.lore/stubs/index.md`. Create the directory if it doesn't exist.

## Output

Save to `.lore/stubs/index.md`

### Document Structure

```markdown
# Outstanding Stubs

Last updated: [timestamp]

## Unresolved Stubs

| Stub | Referenced From | Notes |
|------|-----------------|-------|
| [STUB: auth-flow] | `.lore/specs/login.md` | |
| [STUB: payment-processing] | `.lore/specs/checkout.md`, `.lore/specs/subscription.md` | Referenced by multiple specs |

## Warnings

- Self-referential stub in `checkout.md`: [STUB: checkout]

## Errors

- Invalid stub name in `login.md`: [STUB: Auth Flow] (contains spaces)
- Invalid stub name in `payment.md`: [STUB: 123-id] (starts with number)
```

### Output Rules

- **Resolved stubs**: Simply absent from the index (not listed as "resolved")
- **Duplicate stubs**: When the same stub appears in multiple specs, list all source specs in the "Referenced From" column, separated by commas
- **Self-referential stubs**: Include in the Unresolved Stubs table AND in Warnings section
- **Empty sections**: Omit the Warnings section if no warnings. Omit Errors section if no errors.
- **No stubs**: If no unresolved stubs exist, write a simple message: "All stubs have been resolved. No outstanding specification work identified."

## Example

Given these specs:

**`.lore/specs/login.md`**:
```markdown
## Exit Points
| Exit | Triggers When | Target |
|------|---------------|--------|
| Reset password | User clicks forgot password | [STUB: password-reset] |
| Create account | User clicks sign up | [STUB: registration] |
```

**`.lore/specs/checkout.md`**:
```markdown
## Exit Points
| Exit | Triggers When | Target |
|------|---------------|--------|
| Payment | User submits order | [STUB: payment-processing] |
| Apply coupon | User enters code | [STUB: coupon-system] |
```

**`.lore/specs/payment-processing.md`** (exists)

Running `/update-stubs` produces:

```markdown
# Outstanding Stubs

Last updated: 2026-01-29

## Unresolved Stubs

| Stub | Referenced From | Notes |
|------|-----------------|-------|
| [STUB: password-reset] | `.lore/specs/login.md` | |
| [STUB: registration] | `.lore/specs/login.md` | |
| [STUB: coupon-system] | `.lore/specs/checkout.md` | |
```

Note: `payment-processing` is absent because `.lore/specs/payment-processing.md` exists.

## Context

This skill works with `/specify` which creates specs with stub references. Together they support layer-based specification where:

1. `/specify` creates bounded specs with explicit stubs for undefined areas
2. `/update-stubs` tracks what remains to be specified
3. Use the stub index to decide what to specify next
