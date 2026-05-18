---
name: distill
description: This skill promotes findings into reference documentation by reading a seed (code or work artifacts), verifying claims against current code, and presenting reconciled candidates for the user to gate. Use when reference docs need to be created or refreshed for a feature area, or when a work artifact (spec, plan, brainstorm) holds invariants worth promoting. Triggers include "distill this", "/distill", "/distill code", "/distill work", "promote to reference", "what should be in reference for X", "refresh the reference docs", "this spec has invariants worth keeping".
artifact_path: .lore/reference
---

# Distill

Promote what the code cannot say into reference documentation.

## Two Seed Modes

Distill runs the same core operation regardless of where the seed comes from. Only the seed changes.

| Mode | Seed | Use when |
|------|------|----------|
| `/distill code` | A feature area of the codebase | Reference is missing or thin for an area; you want to walk the code and pull out what survives the shape rule |
| `/distill work` | A work artifact (spec, plan, brainstorm, retro, research note) | A work artifact captured invariants worth promoting; reference should reflect what the artifact still gets right |

Both modes verify against current code before writing anything. The mode only seeds the session.

## Invocation

```
/distill                                                # Interactive: pick a mode and a seed
/distill code                                           # Code-seeded; pick a feature area
/distill code feature=auth                              # Code-seeded; named feature
/distill code entry=/api/admin                          # Code-seeded; from an entry point
/distill work                                          # Work-seeded; pick from work/
/distill work .lore/work/specs/<name>.html              # Build-seeded from a specific file
/distill work .lore/work/plans/<name>.html
/distill work .lore/work/brainstorm/<name>.html
```

## Shape Rule (binding)

Reference contains only what the code cannot tell a reader.

This is what does the work in this skill. Apply it to every candidate before proposing it.

**Belongs in reference**:
- Invariants the code preserves but does not state
- Cross-cutting rules that span files where no single file owns them
- The "why this is this way" — context that survives only in heads or in resolved brainstorms
- Boundaries between features that the code structure hints at but does not name
- Constraints imposed by external systems, contracts, or history

**Does not belong in reference**:
- Function signatures (a reader can grep)
- Endpoint lists (a reader can read the route file)
- Field-by-field schema descriptions (the type definition is the source)
- Restatements of what a well-named identifier already says
- Layered summaries that mirror the code's structure

If a candidate paragraph could be reconstructed by reading the code, it does not belong in reference.

## Null Output Is Valid

A distill session may produce zero reference changes. That is a successful outcome when the seed's claims are all already discoverable from code, or when nothing survives the shape rule.

This skill does not demand candidates. There is no template that asks for N items. If a session ends with no writes, that is the right answer for that session. (Forcing N candidates produces N hallucinations.)

## Core Operation

Both modes follow the same loop:

1. **Read the seed.**
   - `code` mode: read the feature area. Use `surface-surveyor` for entry points if the area isn't already mapped. Walk into the files that handle the entry points.
   - `work` mode: read the named work artifact. Treat its claims as candidates, not as truth.

2. **Verify against current code.** Identify mismatches between what the seed implies or asserts and what the code actually does. Grep for cited paths, route patterns, function names. The code is the source of truth.

3. **Apply the shape rule.** For each candidate that survives verification, ask: would a reader recover this from the code by reading or grepping? If yes, drop it. Keep only what the code cannot say.

4. **Present reconciled candidates.** For each surviving candidate, present:
   - The proposed reference content (terse — a sentence, a paragraph, a small section)
   - The proposed placement (new file, or which existing file gets the update)
   - Any mismatch the seed had with the code, surfaced explicitly when in `work` mode
   - The user's options: promote as-is, edit-and-promote, skip

5. **User gates each candidate.** The user decides reference-worthiness, wording, and placement. The skill does not auto-write. Without the gate, hallucinations relocate rather than resolve.

6. **Update the index.** After writes (or after a session ending in zero writes), update `.lore/work/excavations/index.md` so future sessions know what was covered and what remains.

## Build-Seed Mismatches Are Not Silently Corrected

When `/distill work` finds the seed disagrees with the code, surface the mismatch to the user. Do not silently rewrite the candidate to match the code.

A mismatch is a signal. It can mean:
- The seed was right when written; the code drifted.
- The code was right; the seed was wrong from the start.
- The intent in the seed was never implemented.
- Two valid worldviews coexist and the gap is worth a conversation.

The user resolves the mismatch. The skill's job is to make it visible.

## Reference Is Living, Not Append-Only

When distill identifies that an existing reference file no longer matches the current code, the candidate is an update to that file, not a new entry alongside it.

`current` status on a reference doc means "matches the code right now." That promise is what gives `outdated` real meaning. A reference tree that only grows, never edits, drifts silently into outdated until callers stop trusting it.

In practice:
- If the proposed candidate touches a topic an existing reference file already covers, the candidate is presented as an edit to that file.
- If the proposed candidate is genuinely new territory, it goes in a new file.
- If the existing file is wholesale wrong, the candidate is a rewrite of the relevant section, not an append.
- Status changes (`current` → `outdated` for sections being replaced; back to `current` after the rewrite is accepted) are part of the proposal.

## Placement

Reference has no prescribed topology. Distill navigates it the same way an engineer navigates code when deciding where a new file goes: read the existing tree, follow the convention, place new material alongside similar material.

- First file in an empty `reference/` tree establishes the convention.
- Filenames and directory names aid search the way they do in code.
- Frontmatter (`title`, `tags`, `modules`) is what `lore-researcher` queries — keep it accurate.
- Sub-directories are fine when a topic warrants them (`.lore/reference/auth/`, `.lore/reference/_infrastructure/`). Don't pre-create empty subtrees.
- **Prefer a sub-directory over a shared filename prefix.** If two or more files would share a topic prefix (`mind-reader-design.md`, `mind-reader-limitations.md`), put them in a sub-directory instead (`mind-reader/design.md`, `mind-reader/limitations.md`). Sub-directories carry the topic; filenames carry the facet.

If a placement decision isn't obvious, propose two options to the user and let them pick.

## Output Format

Reference docs are written as HTML. **Before writing**, load both:
- `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md`
- `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`

Output file extension is `.html`. Use a clean structured layout — no collapsibles or interactivity needed (reference docs are read, not navigated).

Copy the base HTML shell from `html-base-template.md` verbatim. Populate the `<meta>` tags and fill `<main>` with artifact-specific sections. Canonical section IDs:

```html
<section id="context">
  <h2>Context</h2>
  <p>[Background and framing for this reference area.]</p>
</section>

<section id="summary">
  <h2>Summary</h2>
  <p>[Key invariants and rules — only what the code cannot tell a reader.]</p>
</section>

<!-- Add additional topic-specific sections as needed -->

<section id="open-questions">
  <h2>Open Questions</h2>
  <!-- omit if none -->
</section>
```

The body is shaped by what survives the shape rule. A reference file may contain one paragraph, a list of invariants, a small table, or a section per cross-cutting rule. There is no required structure beyond what the content demands.

Frontmatter is expressed as `<meta name="lore-*">` tags in the HTML `<head>` (not YAML). Required fields: `lore-title`, `lore-date`, `lore-status`, `lore-tags`. Optional: `lore-modules`, `lore-related`.

## Excavation Index

Track session state in `.lore/work/excavations/index.md`. The index is build scaffolding — it records progress so distill can resume — not reference itself.

Layout:

```markdown
# Distillation Index

## Distilled Areas

| Area | Reference docs touched | Last distilled | Notes |
|------|------------------------|----------------|-------|

## Identified, Not Yet Distilled

| Area | Why it matters | First seen |
|------|----------------|------------|

## Unexplored Entry Points

| Entry point | Type | Notes |
|-------------|------|-------|
```

Update the index at the end of every session — including sessions that produced zero writes (record the area and a brief "shape rule kept nothing" note so future runs don't redo wasted work).

## When `/distill code` Walks a Feature

For `/distill code`, the surveyor and walking pattern is straightforward, but it must be pulled toward the shape rule:

- Use `surface-surveyor` to find entry points if the area isn't mapped.
- Trace the feature through the code: contents *and* actions ("what does this show?" plus "what can a user DO from here?").
- Verify any path or endpoint claim against the actual route or handler file before writing it. Do not document from memory.
- Ask the user to clarify boundaries when the code alone doesn't tell you where one feature ends and another begins. Get the user-facing names early; internal names are not always the right ones to put in reference.
- Then drop the layered summary instinct. Most of what a walk turns up is code-recoverable. Keep only the marginalia: the why, the invariants, the cross-cutting rules.

## When `/distill work` Reads an Artifact

Specs are the highest-yield seed: they describe intent; code describes mechanism; the gap between them is where invariants live. Plans are next — they sometimes record surprises that didn't make it back to the spec. Brainstorms and research are tertiary; if their claims weren't already captured in the spec, that itself is signal worth promoting.

For `/distill work`:

- Confirm the seed file with the user before scanning. Do not pre-scan or volunteer candidates.
- Read the seed's claims. For each one, identify the corresponding code surface and verify.
- A claim that the code already says clearly: drop. Reference would just restate.
- A claim that the code does not say but is true of current behavior: candidate.
- A claim that the code contradicts: mismatch — surface to the user, do not silently rewrite.
- A claim about intent that was never implemented: not a reference candidate (this belongs in a work artifact, not in reference).

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for project-specific agents (security, architecture, performance) that may help spot what the code cannot say in a given area. Invoke relevant agents and incorporate their findings as candidates subject to the same shape rule and user gate.

## Tend Coupling

`/tend`'s `directories` mode surfaces a soft prompt before archiving any spec with `status: implemented`: "Distill this spec before archiving?" The user can answer yes (run `/distill work` on the spec, then archive) or no (archive directly). Distill is an opportunity, not a gate. See `lore-development/skills/tend/references/status.md` and the `/tend` skill for the full flow.

## Verification Pass

Before declaring a session complete:

- Every reference write has been gated by the user.
- Every reference write describes something the code cannot tell a reader.
- Cited file paths, route paths, and identifiers exist (grep them; do not document from memory).
- The excavation index is updated, including null-output sessions.
- If the session is part of a `/distill code` walk over an area, run a coverage pass: did the surveyor enumerate entry points the walk did not cover? If so, those go to "Identified, Not Yet Distilled" — they are not silently dropped.
