---
title: "Learn dialog: user-invoked lesson recording"
date: 2026-04-24
status: open
tags: [capture-skills, lessons-learned, learn, anti-hallucination, dialog]
modules: [lore-development]
related: [.lore/brainstorm/lore-directory-redesign.md, .lore/brainstorm/principles-for-capture-skills.md, .lore/issues/design-extraction-skill.md, .lore/issues/roadmap-lore-redesign.md]
---

# Brainstorm: Learn dialog

## Context

Step 2 of the lore redesign roadmap. `/learn` is the second half of the retro rewrite — retro becomes notes-only (witness), and `/learn` is the analyst. The `design-extraction-skill.md` issue framed this as an automated scan over build artifacts. That framing was wrong.

The real problem being solved: the current `/retro` produces verbose-plausible output — 100 words where 10 would do, the same concept restated three ways, AI convinced the restatements are distinct lessons. The rewrite attacks that failure directly.

## The reframe

`/learn` is not an extractor. It's a dialog for the user to record institutional knowledge in the moment they recognize it. The AI doesn't scan, doesn't propose candidates, doesn't assert. The user names the lesson. The AI helps find the pattern and writes the entry.

Key shift from the earlier framing:

- **Trigger:** user-invoked only. Not fired at the front of new work. Not auto-invoked by `/specify` or `/prep-plan`. The user decides when a lesson wants to be captured.
- **Input:** whatever the user brings. A debug session, a stack of Thorne reviews, a pattern noticed across many sessions. Not a fixed source.
- **Abstraction layer:** individual findings (bugs Thorne flagged, specific retro entries) are not lessons. The lesson is the pattern across them. `/learn` helps the user make that leap without inventing it.
- **Nothing asserted:** the skill never claims something *is* a lesson. User judges. "Nothing" is a valid answer from the user — the session can end without writing a file.

## Dialog shape

**Opening: two-path question.** `/learn` asks whether the user has specific material in mind or is describing a felt pattern. Both paths are valid. The first maps to "I just finished something rough, capture it while fresh." The second maps to "I keep hitting the same wall across sessions."

**Question-first progression.** After the opening, AI asks, user articulates. AI does not propose candidates from a scan. If the user names material, `/learn` can fetch it on request (pull retros by tag, open a specific artifact) but doesn't volunteer.

**Mistakes-only gate as a question, not a block.** Something like "what does following this prevent?" or "what happens if you don't?" — asked to help the user articulate, not to gatekeep. If the user can't name a failure, that's a signal (probably survivorship learning), but the user still decides whether to record. Soft, not hard.

**Nothing ends clean.** If the user says "never mind" or "nothing, actually" at any point, the session closes without a file. Not every invocation produces output.

## Write discipline

This is where the retro pathology gets attacked directly.

- **Terse default.** The lesson is the kernel. One sentence is often enough. No "this is important because" framing — the user already named why.
- **Content-driven length.** No budget. No "aim for N sentences." Any named count becomes the target and the AI fills to it. Length follows what the lesson actually needs. Sometimes that's ten words. Sometimes it's a code sample showing the wrong shape.
- **Mixed content allowed.** Prose, code blocks, whatever the lesson requires.
- **No restating.** One articulation of the mistake. Not three framings of the same idea.
- **Active dedup.** Before writing, `/learn` checks `learned/` for related entries and surfaces them. User decides: update existing, or new. This directly attacks the "three entries for one concept, AI convinced they're distinct" failure.
- **User can cut.** Draft exists for the user to trim, not just approve. AI's expansion instinct needs a human counterweight.

## What's deliberately not specified

The roadmap step is a brainstorm, not a spec. Several mechanics are left to the spec or to implementation judgment:

- Exact dedup search (tags, modules, keyword grep, something else).
- File-per-lesson vs append-to-topic-file; naming; frontmatter fields beyond the common schema.
- Lifecycle of learned entries (supersession, retirement).
- Relationship to the existing graduation path to project CLAUDE.md and `~/.claude/rules/lessons-learned.md`.

Over-specifying here would reproduce the exact failure the skill is meant to prevent — naming slots that then demand to be filled.

## Coupling with other roadmap steps

- **Step 3 (strip `/retro` to event recording)** is still coupled. If `/retro` ships first, there's a window where retros produce notes with no capture path — users who want to record a lesson have nowhere to put it. Sequencing options: ship step 2 before step 3, or ship step 3 with a pointer that says "capture lessons via `/learn` once it lands."
- **Learned-structure (step 5 prerequisite)** is less blocking than I first thought. Lessons are not uniform in shape — each takes the form the mistake requires. The structure question (flat vs categorized, frontmatter fields, retrieval model) can be answered when `/learn` is spec'd, not before.

## Open questions

- How does dedup actually search? The spec step needs to pick a mechanism. Grep on keywords from the user's articulation is the obvious start; whether that's enough is an implementation question.
- Do code samples in learned entries need any convention (language fences, filename hints) or is it fully free-form?
- When the user says "look at my recent Thorne reviews," is that a file-path fetch, a tag/module query, or both? Probably both, handled by lore-researcher patterns.

## Next steps

This brainstorm and the redesign brainstorm together give enough shape to spec `/learn`. The spec step comes after step 3's principles are locked and the `learned/` directory exists to write into (step 4 in the roadmap sequence).
