---
skill: excavate
description: This skill should be used when the user asks to "document this codebase", "excavate features", "what does this code do", "map out the system", "create specs from code", or needs to progressively discover and document features in an existing codebase. Invoked via /lore-development:excavate.
artifact_path: .lore/reference
---

# Excavate: Progressive Design Discovery

## Purpose

Document an existing codebase **one feature at a time**. Each excavation produces one spec file. Features link to other features, building a map incrementally.

This is the opposite of trying to understand everything at once.

## When to Use

- Onboarding to an unfamiliar codebase
- Documenting features that lack specs
- Understanding how a system works before modifying it
- Building a map of what exists

## Invocation

```
/lore-development:excavate                    # Interactive: show progress, pick next
/lore-development:excavate feature=products   # Excavate specific feature
/lore-development:excavate entry=/api/admin   # Start from specific entry point
/lore-development:excavate continue           # Continue with first undocumented
```

## Process

### Step 1: Check Excavation State

**Action**: Check for existing excavation work.

1. Look for `.lore/excavations/index.md` to see what's been documented
2. Look for existing reference docs in `.lore/reference/`
3. Determine if this is a fresh start or continuation

If continuing, present:
- What features are documented
- What features were discovered but not yet documented
- Any unexplored entry points

If fresh start, proceed to Step 2.

### Step 2: Scan for Entry Points

**Action**: Use the surface-surveyor agent to find entry points in the codebase.

Entry points are places where users/systems interact with the code:
- API routes (REST endpoints, GraphQL resolvers)
- CLI commands
- UI pages/components
- Message handlers
- Scheduled jobs

Present the discovered entry points and ask which the user wants to excavate.

### Step 3: Trace the Feature

**Action**: Starting from the chosen entry point, trace the feature through the code.

Investigate:
- What files are involved?
- What data does it touch?
- What other features does it call/depend on?
- What can the user DO with this feature?

**Trace both contents AND actions**: "What does this show?" finds widgets and sub-views. "What can you DO from here?" finds connected features like edit buttons, action menus, and navigation links. Each feature should be traced for both.

**Verify endpoints against code**: Don't document endpoint paths from memory. Grep the actual route files to confirm paths match reality (e.g., `/api/vaults/:vaultId/files/*` not simplified `/files/*`).

### Step 4: Clarify Boundaries

**Action**: Ask the user questions to establish feature boundaries.

The code alone doesn't tell you where one feature ends and another begins. Ask:
- "Is X part of this feature or separate?"
- "Should Y be its own spec?"
- "Are these two capabilities the same feature?"
- "What are the user-facing names vs internal names?" (e.g., "Ground" tab vs "home" mode in code)

**Ask about naming early**: Getting naming conventions upfront prevents rework when internal code names don't match user-facing terminology.

### Step 5: Document the Feature

**Action**: Write a reference document to `.lore/reference/[feature-name].md`

Use the document structure below.

### Step 6: Update the Index

**Action**: Update `.lore/excavations/index.md` with:
- The newly documented feature
- Any discovered (not yet documented) features
- Remaining unexplored entry points

### Step 7: Verify Coverage (Before Declaring Complete)

**Action**: Before ending an excavation session, run the verification checklist.

The UI structure doesn't reveal backend-only features, and discovery can miss entry points that aren't visually prominent. This step catches gaps.

**Verification Checklist**:
- [ ] Run surface-surveyor to enumerate all entry points
- [ ] Compare entry points against documented specs (any undocumented?)
- [ ] Grep route files for undocumented endpoints
- [ ] Check for backend-only features (API exists but no UI entry point)
- [ ] Verify documented API paths match actual route definitions

If gaps found, return to Step 3 for missed features before declaring the session complete.

**When to run verification**: After documenting several features (not after every single spec), or when the user indicates they think excavation is complete.

## Output

### Feature Reference (`.lore/reference/[feature-name].md`)

```markdown
# Feature: [Name]

## What It Does

One paragraph describing the feature from a user perspective.

## Capabilities

Bullet list of what users can DO with this feature:
- **Capability name**: Brief description

## Entry Points

| Entry | Type | Handler |
|-------|------|---------|
| GET /path | API | src/routes/file.ts:function |
| /page | Page | src/pages/Page.tsx |

## Implementation

### Files Involved

| File | Role |
|------|------|
| src/path/file.ts | Description of role |

### Data

- **table_name**: Brief description of what it stores
- **other_table**: Brief description

### Dependencies

- Uses: [other-feature] (why)
- Called by: [another-feature] (why)

## Connected Features

| Feature | Relationship |
|---------|-------------|
| [feature-name](./feature-name.md) | How it connects |

## Implementation Status

| Layer | Status | Notes |
|-------|--------|-------|
| Backend API | Complete/Partial/None | Location of routes/handlers |
| Frontend UI | Complete/Partial/None | Components involved |
| Tests | Complete/Partial/None | Test coverage notes |

Status values:
- **Complete**: Fully implemented and functional
- **Partial**: Some implementation exists but incomplete
- **None**: Layer not implemented

## Notes

Implementation details, gotchas, or context worth preserving.
```

### Excavation Index (`.lore/excavations/index.md`)

```markdown
# Excavation Index

## Documented Features

| Feature | Spec | Excavated | Connected To |
|---------|------|-----------|--------------|
| feature-name | [feature-name.md](../reference/feature-name.md) | YYYY-MM-DD | other, features |

## Discovered (Not Yet Documented)

| Feature | Discovered From | Entry Point |
|---------|-----------------|-------------|
| feature-name | source-feature | route or path |

## Unexplored Entry Points

| Entry Point | Type | Notes |
|-------------|------|-------|
| /path | API | Brief description |
| command | CLI | Brief description |
```

## Feature Boundaries

A feature is:
- **User-centric**: Defined by what users can DO, not by code structure
- **Cohesive**: The parts belong together conceptually
- **Bounded**: Has clear entry points and dependencies

Signs you've found a feature boundary:
- It has its own entry points (routes, commands, pages)
- It has its own data (tables, entities)
- It could theoretically be removed without breaking unrelated things
- Users would describe it as "a thing the app does"

Signs you should split:
- "This feature does two very different things"
- Entry points serve different user goals
- Data is unrelated

Signs you should merge:
- "These are really the same capability"
- Always used together
- Share all the same data

## Feature Hierarchy

Features naturally form a hierarchy:

```
.lore/reference/
├── home-dashboard.md        # Container: links to main features
├── authentication.md        # Leaf: login, logout, register
├── authentication/
│   └── password-reset.md    # Sub-feature of auth
├── products.md              # Container: browsing products
├── products/
│   ├── search.md            # Sub-feature
│   └── reviews.md           # Sub-feature
└── shopping-cart.md         # Leaf: cart management
```

A container feature lists what it contains. Sub-features are excavated separately.

## Cross-Cutting Concerns

Some code isn't a feature, it's infrastructure:
- Logging
- Error handling
- Authentication middleware
- Database connections
- Caching

Document these separately as infrastructure docs in `.lore/reference/_infrastructure/`.

## The Progressive Discovery Model

Each excavation cycle:
1. Documents one node (feature)
2. Discovers edges to other nodes (connected features)
3. Makes the next excavation easier (you know what you're looking for)

Over time, you build a complete map without ever trying to hold it all at once.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents beyond surface-surveyor. Domain experts can help identify patterns, security concerns, or architectural boundaries during excavation. Invoke relevant agents via Task tool and incorporate their insights.
