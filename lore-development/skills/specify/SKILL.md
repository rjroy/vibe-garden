---
name: specify
description: This skill should be used when the user wants to define the requirements of a feature or project. Produces numbered requirements and validation criteria. Triggers include "write a spec for", "define the requirements", "what should this do", "capture the requirements".
---

# Specify

Define what to build and how to know it's done. Requirements, numbered. Validation, explicit. Not how to build it — that's the plan.

## Process

Search for related prior work: invoke the `lore-researcher` agent via Task tool with the topic description — wait for the result. Review any relevant lore context. Ask clarifying questions. Draft. Save. Then run a fresh-eyes review.

After saving, invoke the `spec-reviewer` agent via Task tool on the saved spec. Present findings and offer to address issues before moving on.

## Requirements

Number requirements with a namespaced prefix to avoid collisions across specs: `REQ-{PREFIX}-N`

Derive the prefix from the spec filename — take the first 1-2 segments of the kebab-case name, uppercase. `auth-flow.md` → `REQ-AUTH-FLOW`. `checkout.md` → `REQ-CHECKOUT`. Override with a `req-prefix` frontmatter field when the auto-generated prefix is awkward or shorter IDs are preferred.

## Validation

Every spec needs an AI Validation section. It answers: how will the AI verify this is done? It must be behavioral and actionable — something the AI can run or observe. When in doubt, invoke `/define-validation` to work through it.

## Saving

Save to `.lore/work/specs/[feature-name].md` using kebab-case. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields. The document body is freeform — what matters is that requirements are numbered and validation is explicit.

Write the body Markdown-first per the "Body Format" section of `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`. Reach for embedded inline HTML only where scannability needs it — per-requirement status badges and anchor links per requirement ID so cross-references work.
