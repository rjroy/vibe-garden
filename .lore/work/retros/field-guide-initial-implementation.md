---
title: field-guide initial implementation
date: 2026-05-20
status: open
tags: [field-guide, plugin, skills, spec, review-cycles, CronCreate, lore-wiki]
modules: [field-guide]
---

# field-guide initial implementation

2026-05-20 · retro · field-guide, plugin, skills

## What happened

The session started as pure ideation. The user wanted a new plugin and needed a name. After reviewing Andrej Karpathy's LLM Wiki document, the concept crystallized: a plugin that compiles `.lore/` artifacts into a persistent HTML wiki. The name "field-guide" came out of the naming brainstorm and stuck immediately.

Design decisions came quickly once the domain was fixed. No Obsidian coupling. HTML output, not markdown, consistent with lore-development's 3.0.1 switch. The wiki lives in `.lore/reference/` rather than its own directory, fitting cleanly into the existing three-directory model. The user explicitly declined prep-plan on the grounds that a skills-only plugin doesn't need architecture planning, which turned out to be correct.

The spec went through two rounds. The first draft had a cluster of gaps flagged by the spec-reviewer: CronCreate undefined, fg-type mapping absent, status vs fg-status conflict, schedule config surface unspecified, lint severity unspecified. All real. The CronCreate gap prompted a brief detour where the user pushed back, asking whether CronCreate was actually a harness tool or something invented. It is real. Loading the CronCreate schema resolved the ambiguity and surfaced two things the spec hadn't accounted for: `durable: true` is for session persistence (not expiry), and the 7-day auto-expiry is a separate mechanism. Both ended up in the spec.

Implementation ran as five sequential phases through the orchestrator. Scaffolding was clean. The per-skill review cycles each found something, but the severity varied widely. The most productive false positive was on the ingest skill: the reviewer flagged HTML-only directory walks as a "major" issue, claiming source artifacts are markdown. They are not. lore-development 3.0.1 outputs HTML throughout. No change made. The reviewer's other major finding on `fg-sources` extension fell away for the same reason.

> The init skill reviewer flagged `durable: true` and the 7-day expiry warning as a contradiction, arguing one must be wrong. They are independent: `durable` controls whether the job survives a Claude session restart; the 7-day limit is a separate auto-expiry that applies regardless. The reviewer conflated two orthogonal mechanisms. The spec and skill were both correct.

The idempotency fix on init was the most substantive change during implementation. The original skill read `.field-guide.json` for a job ID, then checked CronList. If the file was missing or corrupt, it bypassed the guard entirely. The fix added a second path: if no ID is found in the file, scan CronList for any job whose prompt is `/field-guide:lint`. Only create a new job if both paths come up empty. This handles the case where the config file was deleted but the job is still running.

The end-of-session plugin-dev validator caught two things the per-skill reviews had missed: ingest was silent on empty directory walks, and contradiction handling during re-ingest was ambiguous enough that a model could stall on the first contradiction rather than finishing the run and batching findings. Both fixed. The lint skill's side effect (writing `fg-status: stale` to files during what presents as a read-only health check) also needed surfacing in the report output, which the final review flagged correctly.

## What drifted from the original shape

The user initially described the scheduled lint as "a hook to trigger lint based on specific events, such as time." Claude Code hooks are event-driven, not time-based. The session redirected toward CronCreate, which is the right mechanism. This wasn't a conflict so much as a clarification of what the harness actually supports.

The spec's schedule configuration went from vague ("configurable; default daily") to concrete only after the conformance review flagged that "daily" and "weekly" as user-facing strings need translation to cron expressions before passing to CronCreate. The init skill gained an explicit translation step.

## What's worth noting for next time

Skill reviewers produce false positives when they assume technology choices that the project has already made differently. The HTML vs markdown confusion on ingest happened because the reviewer had no context about lore-development's output format. The review agent prompt didn't include that context, so it filled the gap with a wrong assumption. Future skill reviews for field-guide should state explicitly that `.lore/work/` artifacts are `.html` files.

> Running the holistic plugin-dev validator after all per-skill reviews completed caught behavioral issues the targeted reviews missed. The per-skill reviews are good at requirement conformance; the plugin-level validator is better at cross-skill coherence and end-to-end user experience. Both are worth running.

Skipping prep-plan for a skills-only plugin was the right call. The five phases (scaffolding + four skill files) were obvious from the spec. Planning would have added a document without changing what got built.
