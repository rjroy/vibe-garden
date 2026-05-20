---
name: retro
description: This skill should be used when completed work needs to be recorded as a lore artifact — what happened, what surprised, what broke, what drifted. Observation only, not interpretation. Triggers: "let's do a retro", "/retro", "review what happened", "capture what happened", "write up the session".
---

# Retro

Record what happened. The retro is the witness, not the analyst.

Future sessions will find this via `lore-researcher`. Make it searchable: tag the problem types, technologies, and patterns the session touched. That's what surfaces a retro when someone plans similar work later.

## Stance

The body describes what happened. It does not interpret. Forbidden:

- Analysis vocabulary: `lesson`, `insight`, `we learned`, `takeaway` don't appear in retro output.
- "What went well / what could improve" structure — this trains toward invented best-practice tips that don't survive the next project.
- Padding to fill a template. Five lines or fifty, both valid. Length follows the session.

What happened? What did the plan say versus what actually happened? Where did things get tripped up? What surprised? What dead ends were tried? What context is worth preserving for the next session in this area?

Write it as prose. Use structure only when it helps the reader follow.

## Saving

Read relevant work artifacts first (spec, plan, notes) to reconstruct context before writing. Save to `.lore/work/retros/[descriptive-name].html`. Load `${CLAUDE_PLUGIN_ROOT}/shared/document-schema.md` for the meta tag fields.

Title describes the work, not a takeaway. "Auth-flow rollout" is a title. "Why we should always test migrations" is not. Tags and modules are how `lore-researcher` finds this later — keep them grep-discoverable.

The output is HTML — let the structure reflect the session. A chronological timeline of what happened, visual callouts for surprises or dead ends, and a clear distinction between what the plan said and what actually occurred. Prose is the default; structure only where it helps the reader follow. Inline CSS and JS are fine; no external dependencies.
