---
title: Bounded Specification with Explicit Stubs
date: 2026-01-29
status: resolved
tags: [specification, layers, stubs, progressive-discovery]
modules: [lore-development]
related: [.lore/specs/lore-development/bounded-specification.md]
---

# Brainstorm: Bounded Specification with Explicit Stubs

## Context

Examining gaps in the lore-development plugin. Initial concerns:
1. Validation is available but not encouraged as part of the natural flow
2. Specify is single-pass while excavate uses progressive discovery
3. Plan (via PlanMode) rushes to implementation; may need multi-pass breakdown

The conversation evolved toward a cleaner model: **bounded specification with explicit stubs**.

## Ideas Explored

### Validation Encouragement

The plugin provides validation capability but nothing prompts you toward it. Compare to excavate's Step 7 ("Verify Coverage") which is built into the cycle.

What if each skill had a hand-off moment? A single question at the end could create the habit without adding friction.

### Layer-Based Specification

Using Memory Loop as example, features naturally form layers:

```
Layer 0: Vault Select (entry point)
Layer 1: Nav Bar (Ground / Capture / Think / Recall)
Layer 2: Individual tab features
Layer 3: Recall's toggle states (File-vs-Task, View-vs-Edit)
Layer 4: Edit modes (Simple vs AI-powered)
```

The natural development rhythm isn't "specify everything, then build." It's:

1. Specify Layer 0 → Implement Layer 0
2. Specify Layer 1 → Implement Layer 1
3. Specify ONE Layer 2 feature → Implement it
4. Go deeper or fan out as needed

**Implementation is the gate between layers, not the end of specification.**

### Bounded Specification with Explicit Stubs

The key insight: layers aren't defined by the AI figuring out depth. They're defined by the user drawing the boundary.

```
AI: "What happens when you select a vault?"
User: "That's to be defined later."
AI: [Records stub, moves on]
```

The spec documents:
- What's **in scope** (fully specified)
- What's **connected** (exit points exist)
- What's **out of scope** (stubs, not specifications)

Example spec structure:

```markdown
# Spec: Vault Select

## Entry Points
- App launch (initial screen)
- "Switch vault" action (from anywhere)

## Requirements
- User can see list of existing vaults
- User can create a new vault
- User can configure vault settings
- User can select a vault to enter

## Exit Points
| Exit | Triggers When | Target |
|------|---------------|--------|
| Vault Selected | User taps a vault | [STUB: vault-interior] |
| Settings Opened | User taps configure | [STUB: vault-settings] |

## Success Criteria
- User can complete all actions within this layer
- Exit points are reachable (transitions happen, even if target undefined)
```

### The AI's Role in Bounded Specification

1. Help define what's IN the layer
2. Probe for connections: "What happens when X?"
3. **Accept "to be defined later" as a valid, complete answer**
4. Record the stub with a name
5. Stop probing that direction

The discipline: don't chase exit points. Document them, name them, move on.

### Stubs as Backlog

Each `[STUB: name]` is a known unknown. When ready:

```
/specify vault-interior
```

The new spec knows it has an entry point from `vault-select`.

### Connection to Excavate

Excavate discovers layers going backward: "I found this entry point, what's behind it?"

Specify creates layers going forward: "I'm defining this layer, here's what exits to undefined."

Both produce the same artifact shape: documented features with known connections. One discovers existing stubs, one creates intentional stubs.

### Plan's Role (Revised)

If specs are layer-scoped, PlanMode's "rush to implementation" becomes appropriate. The multi-pass work happened in specify, not plan.

```
specify(layer N) → breakdown(layer N) → plan(layer N) → implement
                                                            ↓
                                              specify(layer N+1) → ...
```

## Open Questions

1. How to track stubs across specs? Need a stub index (like excavation's index) so nothing gets lost.

2. Does each layer get its own spec file, or do layers accumulate with sections?

3. When do you "fan out" (specify multiple Layer 2 tabs) vs. "drill down" (go deeper into one)? User judgment or process guidance?

4. How does validation weave in? Checkpoint at each layer completion?

5. Should breakdown operate within a layer (smaller, clearer chunks) rather than across layers?

## Next Steps

- Draft updated specify skill with bounded specification model
- Add entry points / exit points / stubs to spec template
- Consider stub index for tracking known unknowns
- Revisit validation's role as layer completion checkpoint
