---
title: Excavation Process (Full Codebase)
date: 2026-01-28
status: complete
tags: [excavate, progressive-discovery, verification, memory-loop]
modules: [lore-development]
---

# Retro: Excavation Process

## Summary

Completed a full excavation of the Memory Loop codebase, producing 13 feature specs across 7 commits. The process took one day and covered all four tabs, six infrastructure components, and three sub-features. A verification pass at the end caught four gaps that the initial excavation missed.

## What Went Well

- **Progressive discovery worked**: Starting from entry points (tabs) and tracing dependencies naturally uncovered infrastructure components without trying to understand everything at once.

- **Feature boundaries clarified thinking**: Asking "what can users DO with this?" forced cleaner separation than code-structure-based grouping would have.

- **Connected Features tracking**: Each spec's "Connected To" section made it easy to identify what to excavate next without losing context.

- **Infrastructure-first ordering**: Excavating infrastructure (vault-selection, configuration, communication-layer) before features meant the feature specs could reference them cleanly.

- **Verification caught real issues**: Running surface-surveyor after "completion" found gaps that manual review missed.

## What Could Improve

- **Initial entry point scan was incomplete**: The first excavation run didn't use the surface-surveyor agent to scan for all entry points. It relied on the obvious UI structure (tabs) and missed backend-only features like the Tasks API and Setup Wizard.

- **Documentation vs implementation drift**: The Capture spec documented meeting endpoints that didn't match the actual code (`/meetings/start` vs `POST /meetings`). This suggests the spec was written from memory or outdated notes rather than verified against the routes file.

- **Partial implementations weren't flagged**: The Tasks feature has complete backend + hook but no UI widget. The initial excavation didn't distinguish "feature exists in code" from "feature is user-accessible."

- **REST endpoints needed systematic enumeration**: Features like health issue dismissal and setup wizard exist as REST endpoints but don't have obvious UI entry points. A route-by-route scan would have caught these earlier.

## Lessons Learned

1. **Always run surface-surveyor before declaring excavation complete.** The UI structure doesn't reveal backend-only features. A systematic scan of entry points (routes, handlers, WebSocket messages) is the verification step.

2. **Verify documented APIs against actual code.** When documenting endpoints, grep the routes file rather than relying on understanding. `grep "POST /meetings" backend/src/routes/` takes 2 seconds and prevents embarrassing errors.

3. **Distinguish implementation layers in specs.** A feature can be:
   - Fully implemented (backend + frontend UI)
   - API-only (backend complete, no UI)
   - Partial (some layers exist, others don't)

   The spec should note this. "Implementation Note: Backend complete, UI not yet built" saves future confusion.

4. **Backend route files are the ground truth for REST features.** The comment headers in route files (like `routes/config.ts` with its REQ-F-29 through REQ-F-34 list) are often more accurate than any other documentation.

5. **Excavation is verification, not just documentation.** The act of tracing code paths reveals inconsistencies between what exists and what's described. This is valuable even if you think you know the codebase.

## Process Improvement

For future excavations, add this verification step before marking complete:

```
## Verification Checklist

- [ ] Run surface-surveyor to enumerate all entry points
- [ ] Compare entry points against documented specs
- [ ] Grep route files for any undocumented endpoints
- [ ] Check for backend-only features (no UI entry point)
- [ ] Verify documented API signatures match actual code
```

## Artifacts

- `.lore/work/excavations/index.md` - Master index of all documented features
- `.lore/work/specs/` - 13 feature specs (7 features, 6 infrastructure)
- Gap-fix commit: `6f69ba5` - Fixed 4 documentation gaps found in verification
