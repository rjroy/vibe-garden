---
name: retro
description: Records what happened in a session so future specs and plans can learn from it. Observation only — what happened, what surprised, what broke, what drifted. Triggers: "let's do a retro", "review what happened", "capture what happened", "write up the session".
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

Read relevant work artifacts first (spec, plan, notes) to reconstruct context before writing. Save to `.lore/work/retros/[descriptive-name].md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields.

Title describes the work, not a takeaway. "Auth-flow rollout" is a title. "Why we should always test migrations" is not. Tags and modules are how `lore-researcher` finds this later — keep them grep-discoverable.
