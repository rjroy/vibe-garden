---
name: back-propagate
description: This skill reconciles specs with what was actually built by comparing implementation artifacts (notes, retros, commissions) against specifications. It updates stale specs to reflect reality and generates specs for work that was done without one. Use when specs have drifted, after a feature cycle completes, or when implementation artifacts exist without a corresponding spec. Triggers include "back-propagate", "reconcile specs", "update spec from implementation", "spec drift", "what changed from the spec", "generate spec from notes", "specs out of date".
---

# Back-Propagate

Reconcile specifications with reality. Information normally flows forward (spec, plan, implementation). This skill flows it backward: implementation artifacts tell you what was actually built, and the spec gets updated to match.

## When to Use

- After a feature cycle, when the spec says one thing and the code does another
- When implementation notes document divergences from the plan
- When commissions or retros reference decisions that changed the original design
- When work was done without a spec and you want to generate one retroactively
- During `/tend` when status mode finds specs marked "implemented" that look stale

## Modes

```
/back-propagate [spec-path]       # Reconcile a specific spec against its artifacts
/back-propagate scan              # Find specs that may have drifted
/back-propagate generate [topic]  # Generate a spec from implementation artifacts
```

## Mode 1: Reconcile a Specific Spec

Given a path to a spec (or a topic that resolves to one), compare what the spec says against what happened.

### Process

1. **Read the spec** and extract its requirements, success criteria, and linked artifacts
2. **Find implementation artifacts** that reference this spec:
   - Search `.lore/build/plans/` for plans referencing this spec (check `related:` and body text)
   - Search `.lore/build/notes/` for notes whose `source:` field points to a plan for this spec
   - Search `.lore/build/retros/` for retros referencing this spec or its plan
   - Search `.lore/commissions/` for commissions whose prompt references this spec or plan
   - If `.lore/lore-config.md` exists, check custom directories too
3. **Extract what happened** from those artifacts:
   - Notes: check the Divergence section, Progress log, and Summary
   - Retros: check "What Could Improve" and "Lessons Learned" for design changes
   - Commissions: check `linked_artifacts` for files that were actually changed
   - Plans: check if plan added, removed, or reordered steps vs the spec
4. **Compare** against the spec's requirements and success criteria
5. **Produce a divergence report** (see Output below)
6. **Offer to update the spec** with confirmed changes

### What Counts as Divergence

Not all differences matter. Focus on these:

| Signal | Meaning |
|--------|---------|
| Requirement fulfilled differently than specified | The "what" stayed, the "how we verify" changed |
| Requirement dropped during implementation | Feature scoped down |
| Requirement added during implementation | Feature grew beyond spec |
| New entry/exit points not in the spec | Integration surface changed |
| Success criteria impossible to verify as written | Criteria were aspirational, not testable |
| Stubs resolved but spec not updated | Connections now exist that the spec calls unknown |

Things that are NOT divergences:
- Implementation details (algorithms, data structures, file layout) - those belong in the plan, not the spec
- Refactoring that doesn't change behavior
- Test counts or coverage percentages

### Output: Divergence Report

```markdown
## Divergence Report: [Spec Name]

### Artifacts Reviewed
- Plan: `.lore/build/plans/feature-x.md`
- Notes: `.lore/build/notes/feature-x.md`
- Retro: `.lore/build/retros/feature-x.md`
- Commissions: [N] commission artifacts

### Requirements Drift
| Requirement | Spec Says | Reality | Source |
|-------------|-----------|---------|--------|
| REQ-X-3 | "User sees notification" | Notification was cut for v1 | notes, Divergence section |
| (new) | (not in spec) | Admin dashboard added | commission-Developer-20260305 |

### Entry/Exit Points Changed
| Change | Details | Source |
|--------|---------|--------|
| New entry | REST API added (not in spec) | commission linked_artifacts |
| Exit removed | Webhook integration deferred | retro lessons |

### Stubs Resolved
| Stub | Now Points To |
|------|---------------|
| [STUB: user-auth] | `.lore/build/specs/auth-flow.md` |

### Success Criteria Status
| Criterion | Status | Notes |
|-----------|--------|-------|
| "User can authenticate" | Met | |
| "Supports SSO providers" | Partially met | Only Google, not all providers |

### Recommended Spec Updates
1. Remove REQ-X-3 or mark as deferred
2. Add REQ-X-8: Admin dashboard view
3. Update exit point table
4. Resolve [STUB: user-auth] to link
```

### Applying Updates

After presenting the divergence report:

1. Walk through each recommended update with the user
2. User confirms, modifies, or rejects each
3. Apply confirmed updates to the spec using Edit
4. Update the spec's `date:` to today
5. If the spec's status was `implemented` but divergences were found, suggest `status: revised`

Preserve the spec's voice and structure. Don't rewrite sections that haven't changed. Add a brief revision note at the bottom:

```markdown
## Revision History
- YYYY-MM-DD: Back-propagated from implementation. [brief summary of changes]
```

## Mode 2: Scan for Drift

Find specs that may have drifted without checking a specific one.

### Process

1. **List all specs** in `.lore/build/specs/` with status `implemented` or `approved`
2. **For each spec**, check whether implementation artifacts exist:
   - Plans that reference it
   - Notes with divergence sections that aren't empty
   - Retros that mention it
3. **Score drift likelihood**:
   - Notes with non-empty Divergence section: high
   - Spec marked `implemented` but no retro exists: medium (can't verify)
   - Spec modified long before its plan was completed: medium
   - Retro mentions design changes: high
   - Multiple commissions for the same feature (iteration signal): medium
4. **Present ranked list** of specs that likely need reconciliation

### Output

```markdown
## Drift Scan Results

### High Likelihood
| Spec | Signal | Artifacts |
|------|--------|-----------|
| build/specs/feature-x.md | Notes divergence section non-empty | notes, retro |
| build/specs/auth-flow.md | Retro mentions dropped requirement | retro |

### Medium Likelihood
| Spec | Signal | Artifacts |
|------|--------|-----------|
| build/specs/views.md | 6 commissions (heavy iteration) | commissions |
| build/specs/workers.md | Implemented, no retro | plan, notes |

### No Drift Detected
| Spec | Status |
|------|--------|
| build/specs/checkout.md | Notes divergence empty, retro clean |
```

User picks which specs to reconcile. Run Mode 1 on each selected spec.

## Mode 3: Generate Spec from Implementation

For work done without a spec. Generates one retroactively from what was built.

### Process

1. **Find unspecced work**: Search for implementation artifacts that don't trace back to a spec:
   - Notes whose `source:` plan has no corresponding spec
   - Plans with no `related:` link to a spec
   - If a topic is provided, search for artifacts matching that topic
2. **Gather evidence** from all related artifacts (notes, plans, retros, commissions, code)
3. **Draft a spec** following the `/specify` document structure, but written in past tense where appropriate:
   - Requirements extracted from what was actually built
   - Entry/exit points from what actually exists
   - Success criteria from what was actually tested
4. **Present draft** to user for review
5. **Save to `.lore/build/specs/`** after confirmation
6. Set status to `implemented` (it already is)
7. Add revision history noting this was generated retroactively

### Tone

A retroactive spec describes what exists, not what should exist. Use present tense for current behavior: "The system validates input before processing" not "The system shall validate input."

Don't invent requirements that weren't built. If the code does three things, the spec has three requirements, not five aspirational ones.

## Searching for Artifacts

Use the `lore-researcher` agent via Task tool to find related artifacts. Provide the spec name, feature topic, or plan path as the search query. The researcher searches frontmatter fields (title, tags, modules) and body text.

For commissions and meetings (custom directories), search by:
- Grepping for the spec filename or plan filename in commission `prompt` fields
- Grepping for feature keywords in commission titles
- Checking `linked_artifacts` for overlap with files the spec's plan would touch

## Relationship to Other Skills

- `/specify` creates specs forward (before building)
- `/back-propagate` updates specs backward (after building)
- `/retro` captures lessons; back-propagate uses those lessons to fix the spec
- `/tend status` flags stale specs; back-propagate resolves them
- `/distill` promotes invariants the code can't say into reference; back-propagate updates build artifacts (specs) from what was actually built
