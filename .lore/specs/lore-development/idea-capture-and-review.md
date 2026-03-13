---
title: Idea Capture Hook and Review Skill
date: 2026-02-18
status: implemented
tags: [idea-capture, issue-tracking, hook, workflow, lightweight]
modules: [lore-development]
related: [.lore/brainstorm/lore-development/idea-capture-and-review.md, .lore/brainstorm/lore-development/document-lifecycle-and-lore-hygiene.md]
req-prefix: IDEA
---

# Spec: Idea Capture and Review

## Overview

A `UserPromptSubmit` hook that captures raw ideas without invoking the AI, paired with a skill that refines those ideas into structured issues through conversation. The hook provides zero-friction capture mid-session. The skill provides one-at-a-time conversational refinement.

## Entry Points

- `/idea some text` typed during any session (triggers hook, AI never sees it)
- `/review-ideas` invoked by user (triggers skill)

## Requirements

### `/idea` Hook

- REQ-IDEA-1: A `UserPromptSubmit` hook intercepts any prompt starting with `/idea ` (with trailing space)
- REQ-IDEA-2: The hook returns `{"decision": "block", "reason": "..."}` so the prompt never reaches the AI and is erased from context
- REQ-IDEA-3: The hook extracts everything after `/idea ` as the idea text
- REQ-IDEA-4: The hook appends the idea as a markdown bullet (`- idea text`) to `.lore/ideas/YYYY-MM-DD.md`, using today's date
- REQ-IDEA-5: If the daily file doesn't exist, create it with a `# YYYY-MM-DD` header before appending
- REQ-IDEA-6: If the daily file exists, append to it (no duplicate headers)
- REQ-IDEA-7: The reason message confirms capture: `"Idea saved to .lore/ideas/YYYY-MM-DD.md"`
- REQ-IDEA-8: The hook always exits 0. Errors go to stderr and produce an empty `{}` response (pass-through, don't block the user)
- REQ-IDEA-9: Ideas files have no frontmatter. They are queues, not lore documents.
- REQ-IDEA-10: The hook creates `.lore/ideas/` if it doesn't exist

### `/review-ideas` Skill

- REQ-IDEA-11: The skill reads all `.lore/ideas/*.md` files, collecting bullets still present in the files (deletion is the only state transition; there is no in-progress marker)
- REQ-IDEA-12: The skill presents one idea at a time to the user
- REQ-IDEA-13: For each idea, the skill asks clarifying questions to understand what was observed and why it matters
- REQ-IDEA-14: After the conversation clarifies the idea, the skill saves a structured issue to `.lore/issues/`
- REQ-IDEA-15: After saving an issue, the skill removes that bullet from the source ideas file
- REQ-IDEA-16: If removing the last bullet leaves only a date header, delete the ideas file
- REQ-IDEA-17: After processing one idea, the skill presents the next and asks if the user wants to continue
- REQ-IDEA-18: The user can stop at any time. Unprocessed ideas remain in their files for next session.
- REQ-IDEA-19: If no ideas exist in `.lore/ideas/`, the skill reports that and exits
- REQ-IDEA-20: The skill can also discard an idea if the user decides it's not worth pursuing. Remove the bullet without creating an issue.

### `.lore/issues/` Convention

- REQ-IDEA-21: Issue files use standard lore frontmatter (title, date, status, tags, modules)
- REQ-IDEA-22: Issue filenames are kebab-case derived from the issue title (e.g., `session-dialog-overflow.md`)
- REQ-IDEA-23: Valid issue status values: `open`, `resolved`, `wontfix`
- REQ-IDEA-24: Issue structure is minimal: What happened, Why, Fix direction
- REQ-IDEA-25: The frontmatter schema must be updated to include the `issue` document type with its status values
- REQ-IDEA-26: `tend` recognizes `.lore/issues/` and follows its standard process on the files

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Hook capture | User types `/idea ...` | Idea appended, session continues uninterrupted |
| Review complete | All ideas processed or user stops | Session continues |
| No ideas | `/review-ideas` with empty `.lore/ideas/` | Skill reports "no ideas to review" |
| Discard | User decides idea isn't worth pursuing | Bullet removed, no issue created, next idea |

## Success Criteria

- [ ] `/idea some text` appends to daily file without the AI responding
- [ ] The conversation is not interrupted (block decision works)
- [ ] `/review-ideas` presents ideas one at a time with clarifying questions
- [ ] Completed ideas are removed from the source file
- [ ] Issues are saved with valid frontmatter to `.lore/issues/`
- [ ] User can stop review mid-stream and resume later
- [ ] User can discard ideas without creating an issue
- [ ] Empty ideas files are cleaned up

## AI Validation

**Defaults**:
- Unit tests with mocked filesystem
- Code review by fresh-context sub-agent

**Custom**:
- Test hook with `/idea` prefix detection (match `/idea text`, don't match `/ideas` or `/idea` without trailing space)
- Test hook creates daily file when missing, appends when existing
- Test hook returns correct block decision JSON
- Test hook error handling (malformed input, filesystem errors) never blocks the user
- Test review skill processes and removes individual bullets correctly
- Test review skill handles multi-day idea files
- Test empty file cleanup after last bullet removed

## Constraints

- The hook is pure file I/O. No network, no AI, no dependencies beyond Python stdlib.
- The hook must not interfere with other `/` commands. Only exact `/idea ` prefix triggers capture.
- The review skill does not work the issue. It refines understanding and saves. Acting on issues is a separate concern.
- Ideas files are not lore documents. They don't participate in `tend`, don't have frontmatter, and aren't searched by lore-researcher.
- Issue files are lore documents. They participate in `tend`, have frontmatter, and are searchable.

## Plugin Changes

The `/idea` hook requires adding a hooks directory and registration to lore-development:

- `lore-development/hooks/hooks.json` (new file, hook registration)
- `lore-development/scripts/idea-hook.py` (new file, hook script)
- `lore-development/skills/review-ideas/SKILL.md` (new file, skill definition)
- `lore-development/shared/frontmatter-schema.md` (update, add issue type)

## Context

- Brainstorm: `.lore/brainstorm/lore-development/idea-capture-and-review.md`
- Prior art for hook pattern: mind-reader plugin (`mind-reader/scripts/hook.py`)
- Prior art for graduation flow: lessons graduation spec (`.lore/specs/lore-development/lessons-graduation.md`)
- Retro lesson: "Specs for AI-guided skills should be lighter than application specs" (`.lore/retros/lore-development/implementation-skill.md`)
