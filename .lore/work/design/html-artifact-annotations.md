---
title: HTML artifact annotation mechanism
date: 2026-05-18
status: draft
tags: [html, annotations, lore-development, artifacts, format]
modules: [lore-development]
related: [.lore/work/brainstorm/html-artifacts.md]
---

# Design: HTML Artifact Annotation Mechanism

## Problem

HTML lore artifacts are opened locally via `file://` URLs -- no server is available. Users need to add notes to artifacts for Claude to read on next ingest. The mechanism must work without any server-side persistence.

See [Brainstorm: HTML as the primary lore artifact format](.lore/work/brainstorm/html-artifacts.md) for broader context.

## Constraints

- Artifacts are opened as `file://` in a browser -- no fetch, no POST, no WebSockets
- `localStorage` is invisible to Claude -- not a valid persistence target
- Claude reads the HTML file from disk on next ingest -- the file is the only shared persistent store
- Annotation content must survive artifact regeneration
- No clutter -- the artifact is a reading document first

## Approaches Considered

### Option 1: Static inline divs only

Annotations are `<div class="user-note">` elements in the HTML. User asks Claude to insert them, or hand-edits the file. No JavaScript involved.

**Pros:**
- Zero JavaScript complexity
- Git diffs show annotation content clearly
- Claude inserts and reads annotations reliably

**Cons:**
- No in-browser authoring -- must go through Claude or hand-edit
- Higher friction for quick notes

### Option 2: Copy-to-clipboard button per section

Each section has a `[Copy as Prompt]` button. Clicking it copies a pre-formatted prompt to the clipboard with the section name and artifact title baked in. User pastes into Claude, types the note, sends. Claude writes a `<div class="user-note">` into the file.

**Pros:**
- In-browser affordance without a text input
- Clean -- no persistent UI clutter
- Pre-fills spatial context (section name) so Claude knows where to place the note
- File stays as source of truth

**Cons:**
- Two-step: click → paste → type in Claude
- Requires JavaScript

### Option 3: Inline text input + copy button

A text input rendered in each section. User types note, clicks copy, gets complete prompt. Slightly more polished flow.

**Pros:**
- User composes note in the artifact before copying
- Complete prompt ready to paste

**Cons:**
- Input fields add visual clutter to a reading document
- Artifact starts to feel like an app rather than a document

## Decision

**Option 2: a single `[Copy as Prompt]` button per artifact, with static divs as the ephemeral storage mechanism.**

User notes are short-lived signals, not permanent annotations. The flow is: user adds a note, Claude reads it on next ingest, acts on it, removes it. A note that survives multiple sessions unaddressed is a smell.

This means no permanent `<section id="user-notes">`, no `data-section`, no `data-date`. Just a `<div class="user-note">` anywhere in the document, placed by the user or Claude, removed by Claude after acting.

Option 3 is rejected on clutter grounds. The artifact is a reading document first.

Users may also add `<div class="user-note">` divs directly by hand-editing the file. Both paths produce the same result.

## Interface/Contract

### Storage: user-note div

```html
<div class="user-note">
  Note content here.
</div>
```

- `class="user-note"` -- Claude's ingest selector
- Content is plain text
- No metadata attributes needed

### UX: single copy button per artifact

One `[Copy as Prompt]` button, rendered in the artifact header or footer. Clicking copies:

```
Add a user note to "[artifact title]": 
```

User pastes into Claude, types the note after the colon, sends. Claude inserts a `<div class="user-note">` and removes it after acting on it.

Button rendering: small, muted. Visually recedes when not needed.

### Claude's ingest and removal rule

On ingest, Claude reads all `<div class="user-note">` elements and treats them as instructions or corrections. After acting on them, Claude removes them from the file. Notes do not accumulate.

## Edge Cases

- **User hand-edits a note div**: Valid. Claude reads it on next ingest regardless of how it got there.
- **Multiple notes**: Multiple divs, Claude reads all of them in document order and removes all after acting.
- **JavaScript disabled**: Button does nothing. User falls back to hand-editing divs or asking Claude directly. Core capability unaffected.
- **Note not yet acted on**: Survives until Claude next reads the file and acts. If a note persists across many sessions, that's a signal it was never read -- worth flagging in `/tend`.

## Open Questions

None.
