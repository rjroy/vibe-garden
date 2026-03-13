---
title: Idea Capture and Local Issue Tracking
date: 2026-02-18
status: resolved
tags: [idea-capture, issue-tracking, workflow, compass-rose, lightweight]
modules: [lore-development, compass-rose]
related: [.lore/brainstorm/lore-development/document-lifecycle-and-lore-hygiene.md]
---

# Brainstorm: Idea Capture and Local Issue Tracking

## Context

GitHub issues add ceremony that doesn't match AI-assisted development speed. When the AI closes 20 issues a day, each issue lives for 30 minutes and took 10 minutes to enter. A third of the value is eaten by paperwork. If the process is "talk it out with the AI," why add GitHub issues in the middle?

The gap: you notice something while working on something else. You can't act on it now. There's no low-friction place to capture it. It's not a spec, not research, not a plan. It's a raw observation that *might* become any of those.

## Core Design

A hook and a skill working together:

### `/idea` - Hook-based capture (skips the AI entirely)

A `UserPromptSubmit` hook in the lore-development plugin. When the user types `/idea some text`, the hook intercepts it, appends a bullet to today's file, and the AI never processes it. No context burned, no response to wait for, no conversation interrupted.

```
/idea commit button not visible on mobile in new session dialog
```

The hook:
1. Detects the `/idea` prefix
2. Strips the prefix, takes the rest as the idea text
3. Creates or appends to `.lore/ideas/2026-02-18.md`
4. Done. The user keeps working.

Produces `.lore/ideas/2026-02-18.md`:

```markdown
# 2026-02-18

- commit button not visible on mobile in new session dialog
- research cache check should happen before API calls, not after
- mind-reader baseline could use session length instead of prompt count
```

No frontmatter. No structure. Just a date header and bullets. The ideas file is a **queue**, not an archive. Items leave it when processed.

This is a deliberate break from lore convention (one-document-per-concept with frontmatter). Ideas are cheap and fast. Making each one a separate file with frontmatter kills the speed.

**Why a hook, not a skill:** A skill invokes the AI. The AI reads the prompt, thinks about it, writes a response. That's wasted work for "append a line to a file." The hook operates at the shell layer, pure file I/O. The AI doesn't see it, doesn't respond to it, doesn't lose context over it. This is the lowest possible friction: type, enter, keep working.

This also means `/idea` works mid-conversation without derailing what the AI is doing. You're debugging a test failure, you notice a UI problem, you type `/idea dialog overflow on mobile`, and the AI continues debugging. The idea is captured in the background.

### `/review-ideas` - Conversational refinement, one at a time

Processes ideas into structured issues through dialogue:

1. Present the first unprocessed idea: "You said: 'commit button not visible on mobile in new session dialog.' What was visible instead?"
2. Ask clarifying questions. Talk until the problem is understood.
3. Save a structured issue to `.lore/issues/`.
4. Delete the idea from the daily file.
5. Present the next idea. Repeat.

Key properties:
- **One at a time.** Not batch processing. A conversation about each one.
- **Context-loss resilient.** Unprocessed ideas stay in the file. Clear context, restart, keep going.
- **Stop when you want.** Not when the batch is done.
- **The issue captures reasoning, not just conclusions.** Not a transcript, but the key exchanges that shaped understanding. Future-you reading the issue gets the "why" for free.

### `.lore/issues/` - Lightweight actionable items

Output of the review conversation. Deliberately minimal:

```markdown
---
title: New session dialog overflow hides commit button
date: 2026-02-18
status: open
tags: [ui, mobile, overflow]
modules: [session-dialog]
---

# New session dialog overflow hides commit button

## What happened
Commit button not visible on mobile in the new session dialog.

## Why
The dialog container has overflow: hidden. On small viewports,
the button is below the fold with no way to scroll to it.

## Fix direction
Change overflow-y to auto on the dialog container. May need
min-height on the button area to prevent it from collapsing.
```

No priority. No estimate. No assignee. The AI reads it, understands it, acts on it.

## Ideas vs Tasks vs GitHub Issues

| Source | Direction | Lives in | Created by |
|--------|-----------|----------|------------|
| Ideas | Bottom-up (observed) | `.lore/ideas/` | `/idea` |
| Issues | Bottom-up (refined) | `.lore/issues/` | `/review-ideas` |
| Tasks | Top-down (from plans) | `.lore/tasks/` | `/plan-breakdown` |
| GitHub Issues | Team-visible | GitHub | Compass Rose |

Ideas graduate to issues. Issues don't need to become tasks unless they're part of a larger plan. GitHub issues are for team coordination and multi-day efforts, not tactical fixes.

## Compass Rose Relationship

Compass Rose serves strategic work: what should we build next, backlog health, priority across a body of work. `.lore/issues/` serves tactical work: this is broken, fix it now or soon. If something needs team visibility, `/review-ideas` could offer to graduate it to GitHub via Compass Rose. The local issue becomes the research backing the GitHub issue.

## Completion and Cleanup

Options explored:
- **Delete on completion.** The fix is in the code. The commit explains it. Git has history. Most aggressive, kills hoarding instinct.
- **Archive to `.lore/_archive/issues/`.** Separates active from done. Reduces noise but adds a directory.
- **Mark `status: resolved`, let `tend` clean up.** Consistent with other lore artifacts. Least disruptive.

Leaning toward `status: resolved` with `tend` cleanup, matching existing lore patterns.

## Architecture Decision: Hook + Skill Split

**Decided:** `/idea` is a hook, `/review-ideas` is a skill. This is the clean split.

The hook handles raw capture: you know what you saw, you want to save it, no AI needed. The skill handles refinement: the AI asks questions, you talk it out, the idea graduates to a structured issue.

This means lore-development ships with:
- A `UserPromptSubmit` hook that intercepts `/idea` messages
- A `/review-ideas` skill that processes the captured ideas conversationally
- The `.lore/ideas/` and `.lore/issues/` directory conventions

The hook lives in the plugin (`lore-development/hooks/`), not in user config. It ships with the plugin and works for anyone who installs it.

## Hook Suppression: Confirmed

`UserPromptSubmit` hooks support `decision: "block"`. When the hook returns:

```json
{
  "decision": "block",
  "reason": "Idea captured to .lore/ideas/2026-02-18.md"
}
```

The prompt is erased from context. The AI never sees it. No tokens burned, no response generated. The user sees only the reason string as feedback.

This is what makes `/idea` work as a hook instead of a skill. The entire interaction is: type `/idea something`, see "Idea captured," keep working. The AI continues whatever it was doing with zero interruption.

The hook script:
1. Check if prompt starts with `/idea `
2. If yes: extract text after prefix, append bullet to `.lore/ideas/YYYY-MM-DD.md`, return block decision with confirmation
3. If no: exit 0 with no output, prompt passes through normally

Exit code 0 with the block decision is the correct pattern. Exit code 2 would turn the reason into an error message.

## Open Questions

1. **Does `/review-ideas` offer to immediately work an issue?** Or is review strictly about understanding? Keeping them separate feels right: review 5 ideas, work 2 today.

2. **What about triage across issues?** If `.lore/issues/` accumulates, you need a way to prioritize. Possibly a `/triage-issues` skill that ranks by what matters most. Or maybe that's where Compass Rose re-enters, operating on local issues instead of GitHub.

3. **Does the daily file need cleanup?** If all ideas are processed, the file is empty. Delete it? Leave it? `tend` handles it?

## Next Steps

- Spec the `/review-ideas` conversational flow
- Define `.lore/issues/` document structure formally
- Decide on completion/archive pattern
- Prototype the `/idea` hook implementation
