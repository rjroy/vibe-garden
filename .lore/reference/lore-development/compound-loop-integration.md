---
title: Compound-loop integration contract for skills
date: 2026-04-25
status: approved
tags: [lore-researcher, compound-loop, skill-authoring]
modules: [lore-development]
---

# Compound-loop integration contract for skills

The compound loop closes at the skill, not at the agent. `lore-researcher` is a
search agent: it greps frontmatter and returns findings. It does not enforce
that anyone reads the result.

A skill that wants compound knowledge to surface must:

1. Invoke via Task with `subagent_type: lore-researcher` (not `general-purpose`).
2. Run synchronously — never `run_in_background: true`. The agent's reply is the input to the next step.
3. Pass the work topic, not the artifact type. "user authentication flow,"
   not "spec for auth."
4. Incorporate the findings into the artifact's context section (Context for
   specs, Codebase Context for plans, log entries for implement notes).

Skip any of these and the loop is silently broken: the search runs, costs
tokens, and contributes nothing. The agent has no way to detect this; only the
skill can keep the contract.

Skills that currently honor this: `/specify`, `/prep-plan`, `/implement`. New
skills that consume `.lore/` history should follow the same pattern.
