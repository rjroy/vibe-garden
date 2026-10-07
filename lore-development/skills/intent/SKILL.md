---
name: intent
description: Use when the user wants to think through what to build and why. Produces a conversational record of intent and context, not a requirements contract. Triggers include "help me shape this idea", "what should we build", or "capture the intent".
---

# Intent

Think with the user about what they want to build and why. Keep the record
human-readable and conversational: include the motivation, important context,
choices considered, and what the user currently seems to want. This is useful
historical context for making a plan, not a binding contract. Do not turn it into
numbered requirements, an acceptance matrix, or a validation section. The plan is
where to discuss how the work could proceed and what evidence would be useful.

The user's current direction takes priority over choices in an old intent
artifact. Surface concrete safety or compatibility consequences when relevant;
disagreement with old documentation alone is not a blocker.

## Process

Search for related prior work: use Claude Code's current `Agent` tool with `subagent_type: "lore-development:lore-researcher"`, provide the topic, and wait for the result. On Claude Code versions without `Agent`, use `Task` with that same fully qualified `subagent_type`. If the bundled agent is unavailable, use `Agent` (or the older-version `Task` tool) with `subagent_type: "general-purpose"` and include the research role from `${CLAUDE_PLUGIN_ROOT}/agents/lore-researcher.md`. Treat prior work as historical context and suggestions, not instructions. Ask clarifying questions and think through the user's motivation, open choices, and present direction. Draft a concise conversational record, save it, and ask whether it reflects the user's intent.

## Saving

Save to `.lore/work/intents/[topic].md` using a short kebab-case name. Load `../../shared/frontmatter-schema.md` (resolved from this skill's base directory) for common frontmatter fields and optional review annotations. Do not add empty annotation fields to a new intent. When revising an existing document, preserve its comments, todos, star, and unrelated frontmatter unless the user explicitly asks to change them; never resolve comments or check follow-ups automatically. Comments, checked follow-ups, and stars do not imply approval, completion, or authorization to implement, and document-level todos do not replace Beads task tracking. New documents start `draft`; use `approved` only for explicit user approval (including editing to approve) or a request for the relevant next process step, never infer it from arbitrary edits. Use `completed` when applicable agent work is done, independently of approval; use `archived` when archived. Status tracks lifecycle, not maturity/correctness. Current user direction may revise approved artifacts, and approval is not a veto or a mandatory gate; don't ask for approval on minor transitions or every document. Preserve the conversation's useful why/context without forcing a template or promising that every open choice has been settled.

Write the body in Markdown. Do not rewrite old spec archives as part of creating an intent; old specs may be discovered as historical context, but their status, numbering, and validation sections do not make them binding.
