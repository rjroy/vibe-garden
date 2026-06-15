---
name: init
description: Use when setting up field-guide on a project for the first time, or to refresh the scheduled lint job after it expires. Triggers include "init field-guide", "set up field-guide", "refresh field-guide lint schedule", and "bootstrap the wiki".
---

# Init

Bootstrap the project wiki and register a durable scheduled lint job.

## Dependencies

This skill requires CronCreate and CronList to be available in the Claude Code harness. If those tools are not present, the wiki directory and index.md will still be created, but the scheduled lint job cannot be registered — inform the user that scheduling is unavailable.

## Steps

**1. Create the wiki directory.**

Check whether `.lore/reference/` exists. If not, create it. Then check whether `.lore/reference/index.md` exists. If not, write a minimal Markdown file there:

```markdown
---
title: Field Guide Index
date: YYYY-MM-DD
status: current
tags: [index, field-guide]
---

# Field Guide Index
```

Never overwrite an existing `index.md`.

**2. Check for an existing lint job.**

CronCreate jobs auto-delete when they expire, so any job present in CronList is by definition active. The check is simply: is the job ID present in the CronList results?

Proceed as follows:

1. Read `.lore/reference/.field-guide.json`. If it contains a `lint_job_id`, call CronList and check whether that ID appears in the results. If it does, skip to the summary step — do not create a second job.
2. If `.field-guide.json` is absent, unreadable, or contains no `lint_job_id`, call CronList and scan for any job whose prompt is `/field-guide:lint`. If one is found, write its ID to `.field-guide.json` (preserving any existing `schedule` value, or omitting it if unknown), then skip to the summary step.
3. Only proceed to CronCreate if no matching job was found by either path.

**3. Translate the schedule value.**

Before calling CronCreate, convert the user's requested schedule to a 5-field cron expression:

- `daily` → `"3 8 * * *"` (08:03 every day)
- `weekly` → `"3 8 * * 1"` (08:03 every Monday)
- A raw 5-field cron expression → pass through unchanged
- No schedule provided → default to `"3 8 * * *"`

**4. Register the lint job.**

If no active job was found, call CronCreate with:

- `prompt`: `/field-guide:lint`
- `durable`: `true`
- `schedule`: the translated cron expression from step 3

Store the returned job ID in `.lore/reference/.field-guide.json`:

```json
{ "lint_job_id": "<id>", "schedule": "<schedule>" }
```

**5. Tell the user what happened.**

Confirm whether the directory and index were created or already existed. Confirm whether a new lint job was registered or an existing one was found. Report the job ID and schedule.

Include this notice: recurring CronCreate jobs expire after 7 days. Re-run `/field-guide:init` to refresh the scheduled lint job before it lapses.
