---
title: Design the mistake-extraction skill
date: 2026-04-23
status: resolved
tags: [design-needed, extraction, lessons-learned, capture-skills]
modules: [lore-development]
related: [.lore/work/brainstorm/lore-directory-redesign.md, .lore/work/brainstorm/principles-for-capture-skills.md]
---

# Design the mistake-extraction skill

The lore directory redesign names an extraction skill that surfaces mistakes from build artifacts (especially retro notes) at design time, with a human gate, and promotes confirmed mistakes into `.lore/learned/`. The shape is sketched in the redesign brainstorm but not designed.

## What's known

- Fires at the *front* of new work, not at the end of old work.
- Scans `build/` — retro notes especially, but also specs and plans — for evidence of mistakes in the current area.
- Presents candidates. Does not assert mistakes.
- Human decides which candidates graduate to `learned/`.
- Enforces the asymmetric-shape rule (don't / beware only, never do-because-it-worked).

## What's undesigned

- **Trigger model.** Manual invocation only? Auto-invoked by `/specify`, `/design`, `/prep-plan`? Both?
- **Relevance ranking.** How does it decide which retro notes are relevant to the current work? Tags? Modules? Semantic search?
- **Presentation format.** How are candidates shown to the user? One at a time with AskUserQuestion? A batch for review? A draft file?
- **Write mechanics.** Does the skill write learned entries directly, or draft them for user approval?
- **Dedup.** If a mistake is already encoded in `learned/`, does extraction skip it, surface it anyway, or suggest a refinement?
- **Scope of scan.** Just retros? All build artifacts? Historical build from archived sessions too?

## Why this is blocked

The skill can't be spec'd until trigger model and relevance ranking are decided. Both are load-bearing: wrong trigger model means the skill either never fires or fires too noisily; wrong relevance ranking means candidates are either too narrow (user misses real mistakes) or too broad (hallucination risk returns through the back door of "technically related").

## Resolution path

Brainstorm session focused on this skill specifically, informed by the three capture-skill principles (especially principle 3 — observation-interpretation split). Likely needs one or two real retro notes to design against, which means the retro-as-notes skill may need to ship first and produce material.
