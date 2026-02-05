---
title: Document Lifecycle and Lore Hygiene
date: 2026-01-29
status: resolved
tags: [lifecycle, hygiene, status-tracking, tend]
modules: [lore-development]
---

# Brainstorm: Document Lifecycle and Lore Hygiene

## Context

`.lore/` fills up with artifacts: specs, plans, brainstorms, diagrams, research. Some are actively driving work. Some were stepping stones. Some are orphaned thoughts. Right now there's no way to distinguish "this plan is complete, we did it" from "this plan is still guiding work" from "this was an idea we abandoned."

## The Core Tension

**What if status is baked into each skill?**
- Specify and plan skills already create documents. They could add a `Status:` field in frontmatter
- When work completes, you'd... what? Manually edit the status? Run the skill again?
- Problem: The skill that creates isn't naturally the skill that closes

**What if there's a dedicated lifecycle skill?**
- A "close" or "complete" skill that marks documents as done
- Or a "triage" skill that reviews all documents and prompts for status updates
- Problem: Extra ceremony. Will it actually get used?

**What if it's a cleanup/hygiene skill?**
- Periodic review of `.lore/` to identify stale artifacts
- Could surface: specs with no plans, plans with no progress, brainstorms never referenced, orphaned diagrams
- Problem: Reactive rather than proactive. Mess accumulates before cleanup.

## Ideas Explored

**Idea 1: Frontmatter status in all documents**

Every `.lore/` document gets a status field:
```yaml
---
status: active | complete | abandoned | archived
---
```

- Specs: `draft` → `active` → `complete` (or `abandoned`)
- Plans: `draft` → `active` → `complete` (or `superseded`)
- Brainstorms: `open` → `incorporated` | `parked`
- Research: `reference` (always available) | `stale`

The creating skill sets initial status. A separate action marks completion.

*What if* we made completion part of the retro skill? You do a retro, and it prompts "which specs/plans should be marked complete?"

**Idea 2: Implicit status through linking**

Don't track status explicitly. Instead, infer it:
- A spec is "active" if a plan references it
- A plan is "active" if work breakdown references it
- A brainstorm is "incorporated" if a spec references it

A hygiene skill could walk the reference graph and identify orphans.

*What if* this is too clever? Reference tracking is fragile. Documents drift. Links break.

**Idea 3: The "garden" metaphor taken literally**

Lore is a garden. Gardens need tending:
- A `tend` or `prune` skill that runs periodically
- Surfaces documents by age and activity
- Asks: "Is this still relevant? Mark it or archive it."
- Could move truly dead things to `.lore/archive/`

*What if* this becomes a chore nobody runs? Then we're back to accumulating mess.

**Idea 4: Completion is baked into the workflow**

After implementation completes (via execute skill or manually), you're prompted:
- "Implementation done. Mark the plan as complete?"
- "Spec requirements met. Close the spec?"

This ties lifecycle to natural workflow moments rather than requiring separate action.

*What if* the moment passes and you forget? At least you had the prompt.

**Idea 5: Status lives in a manifest, not each file**

A single `.lore/manifest.md` or `.lore/status.yaml` tracks all documents:
```yaml
specs:
  auth-flow.md: complete
  user-profiles.md: active
plans:
  auth-flow.md: complete
brainstorm:
  early-ideas.md: parked
```

One place to see everything. One place to update.

*What if* it drifts from reality? Files get added, manifest doesn't update.

## Trade-offs Grid

| Approach | Pros | Cons |
|----------|------|------|
| Frontmatter status | Self-contained, grep-able | Requires discipline to update |
| Implicit linking | No extra work | Fragile, hard to query |
| Periodic hygiene skill | Catches everything | Reactive, becomes a chore |
| Workflow-integrated prompts | Natural moments | Easy to dismiss |
| Central manifest | Single source of truth | Sync drift |

## Open Questions

1. **How often do you actually need to know status?** Is this solving a real friction or a theoretical one?

2. **What triggers "complete"?** Is it when code ships? When tests pass? When you feel done? The trigger affects where the prompt belongs.

3. **Should archived/abandoned documents be hidden or just marked?** Moving to `.lore/archive/` reduces clutter but loses grep-ability.

4. **Is this the same problem as the execute-skill tracking?** That brainstorm was about chunk-level progress. This is document-level. Are they one system or two?

5. **What about brainstorms specifically?** They're inherently messy. Forcing status on them might kill the value.

## Direction (from discussion)

The solution has two parts:

1. **Every document gets a status line.** The presence of status matters more than the specific values. It's a cue to both humans and AI that "this needs updating." Values can be descriptive and honest: `status: incorporated incorrectly`, `status: partially incorporated`, `status: incorrectly marked complete`.

2. **A `tend` skill for periodic hygiene.** This skill puts the AI into a mode of:
   - Ensuring all documents have status
   - Verifying status accuracy (did the work doc actually complete its tasks?)
   - Updating only the status field, nothing else
   - Following the excavate progressive discovery philosophy
   - Possibly maintaining a tend-log to track when files were last reviewed

The tend skill is about truthful status, not optimistic status. It can mark things as incomplete even if they claim otherwise.

## Next Steps

1. Update skill templates to include status field
2. Design the tend skill (spec it separately)
