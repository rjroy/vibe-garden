---
title: Retro skill evolution for Guild Hall workflows
date: 2026-03-12
status: open
tags: [retro, guild-hall, multi-agent, lessons-learned, knowledge-management, commissions]
modules: [lore-development]
related:
  - .lore/brainstorm/lore-development/lessons-graduation.md
  - .lore/brainstorm/lore-development/compound-loop-lore-development.md
  - .lore/retros/lore-development/compound-loop-implementation.md
---

# Brainstorm: Retro Skill Evolution for Guild Hall Workflows

## Context

The existing `/retro` skill was designed for single-session work: one developer, one feature, one conversation that ends with a retro. Guild Hall changes the shape. A feature now involves multiple workers (Dalton writing code, Octavia writing lore, Verity reviewing), each running in isolated commission contexts, none of them sharing a conversation. The commission logs that remain are activity records, not insight records. When the feature is done, nobody has asked "what did we learn?"

This brainstorm examines whether `/retro` can stretch to cover this use case, or whether something new is needed.

## What the Current Retro Skill Actually Does

Reading the SKILL.md confirms it assumes a live session with human access. The process is:

1. Review `.lore/specs/` and `.lore/plans/` from the current session
2. Reflect on what happened vs. what was expected (in conversation)
3. Write a retro to `.lore/retros/`
4. Run a lessons graduation flow that prompts the human for classification

The graduation flow explicitly uses `AskUserQuestion`, which means it requires a human in the loop at the point of graduation. That's by design: the lessons brainstorm concluded that LLMs aren't reliable enough to classify lesson significance autonomously.

Two problems for Guild Hall:

**Problem 1: Context is fragmented.** No single worker has seen the full commission chain. Dalton wrote the code but didn't read the meeting notes. Octavia wrote the spec but didn't see the test results. The retro agent would need to synthesize across artifacts it wasn't present for.

**Problem 2: The graduation step needs a human.** In a commission context, there may not be a human watching. Or the retro commission could complete, produce a draft retro, and leave graduation for a later audience with the Guild Master.

## The Gap Between Commission Logs and Lessons Learned

Commission logs (`.lore/commissions/`) are surprisingly rich. Looking at real examples:

- They record decisions with explicit reasoning ("Used unittest instead of pytest because the sandbox has no pip/pytest available")
- They record what was built and what tests passed
- They record blockers and their resolution (commission-Dalton-20260312-221309 shows the dependency chain: blocked → pending → dispatched when a prior commission completed)

What they don't capture:

- Whether the approach chosen was the right one in hindsight
- Patterns that span multiple commissions ("this worker type consistently struggles with X")
- Process observations ("the plan was ambiguous on Y and that caused Z")
- Surprises, either good or bad

The decisions recorded in commissions are decisions-made, not decisions-reviewed. The commissioner dispatching the work doesn't synthesize across the results; they move to the next commission.

Meeting files are even thinner. The audience-Guild-Master examples read like summaries written by an observer: "no decisions were finalized," "open items remain." They're accurate but flat. No "this meeting would have gone faster if X" or "we discovered mid-session that the spec had a gap in Y."

The lesson extraction problem is real. It's not just that no tool exists to extract lessons — it's that the artifacts don't contain lessons to extract. They contain facts. Turning facts into lessons requires interpretation.

## Can the Existing Retro Skill Handle This?

The answer depends on what "handle" means.

**Could a retro commission read commission logs and produce a retro document?** Yes, technically. A retro commission could be given a list of commission file paths, read them, synthesize across them, and produce a `.lore/retros/` document. This is pure file I/O + summarization. No new tooling needed.

**Would the output be meaningful?** Uncertain. The commission logs capture what happened, but the retro agent would be inferring lessons from outcomes, not from lived experience. "Dalton ran 13 tests that passed" doesn't tell you whether the test suite was adequate or whether a particular testing approach was a good choice. The retro agent would be guessing.

**What about the graduation step?** The interactive `AskUserQuestion` flow breaks in a commission context. Options:

- Skip graduation in the retro commission, produce only the raw retro document, and leave graduation for a human to run manually later
- Run graduation as a separate commission that the Guild Master triggers after reviewing the draft
- Make graduation async: the retro commission writes candidate lesson classifications to the retro frontmatter, and a subsequent interaction reviews them

The existing skill isn't wrong for Guild Hall; it just needs its scope adjusted. It was written for a conversational context where human judgment is always available. In a commission context, some steps must be deferred.

## Are Octavia's Writer Cleanup Skills Enough?

The `guild-hall-writer:cleanup-commissions` skill (from the system skill listing) reviews completed commission artifacts as a batch, extracts loose threads into a retro, and deletes the commission files. This is the closest existing tool to a "Guild Hall retro."

But there's a distinction worth naming: **cleanup is about artifact hygiene; retro is about lesson extraction.**

Cleanup-commissions produces a retro as a side effect of deleting commission files. The retro it creates is a record of what happened, organized for persistence. That's different from a retro designed to surface what could improve.

The question is whether the two goals can co-exist in one artifact or need to be separated. My lean: they can co-exist, but the cleanup skill shouldn't be expected to produce graduation-ready lessons. It can produce a draft retro with a "Patterns Observed" or "Flags for Review" section, but the human judgment step happens separately.

Retro-as-cleanup and retro-as-insight are complementary, not interchangeable.

## What Would a Guild Hall Retro Actually Look Like?

Working from first principles, given the constraints:

**Inputs**: Commission files (completed), meeting notes (closed), git log since last retro, any linked artifacts (specs, plans, test results)

**Who runs it**: Either a dedicated retro worker (a new agent type focused on pattern recognition across artifacts), or an augmented Octavia commission. Octavia's domain is documentation; synthesizing across a commission chain is within that domain.

**When it triggers**: Three plausible models:

1. *Manually*, after a feature cycle completes, triggered by the Guild Master. Same as the current retro skill but for multi-worker work. Risk: retros get skipped when things are busy.

2. *Cleanup-triggered*, piggybacking on `cleanup-commissions`. When a commission cleanup runs, the cleanup skill produces a retro draft as part of its output. The draft is lower quality than a dedicated retro but has zero additional overhead.

3. *Scheduled*, as a periodic commission (weekly? per-sprint?). The retro commission reads all commissions and meetings since the last retro and synthesizes across them. Risk: the periodic cadence may not align with natural feature boundaries; the retro covers a time slice, not a coherent piece of work.

**What it produces**:

A `.lore/retros/` document structured differently from the current template. The current template is feature-focused: "What went well with X feature?" A Guild Hall retro is process-focused: "What patterns emerged across these commissions?"

Proposed sections for a Guild Hall retro:
- Commission summary (which commissions, which workers, what was built)
- Process observations (what worked in the multi-worker workflow)
- Plan vs. reality gaps (where commission results differed from the plan)
- Worker patterns (patterns in how specific worker types performed — not judgment, just observation)
- Flags for human review (items that need graduation or decisions)

**Where the output lives**: Still `.lore/retros/`, but perhaps with a subdirectory convention. The current `.lore/retros/lore-development/` pattern is by module. A Guild Hall retro might use a `guild-hall/` subdirectory or a `commissions/` subdirectory to distinguish it from feature-level retros.

## Retro as a Scheduled Commission

This is the most interesting design option and the one with the most unknowns.

**What it would look like**: A commission dispatched weekly (or on some cadence) to a retro-focused worker. The commission prompt is auto-generated from the commission log since the last retro. The retro worker synthesizes, produces a draft retro, and submits it. The draft goes into `.lore/retros/` with status `draft`. A subsequent human interaction reviews and graduates lessons.

**The appeal**: Lessons learned don't decay if the retro happens automatically. No "we'll do a retro after this sprint" that never happens.

**The risks**:

- Retro quality may be low without human input shaping what to look for. A retro commission prompt would need to be specific enough to produce useful output ("look for plan vs. reality gaps, look for commission failures, look for surprises") rather than a generic summary.
- If commissions are sparse, the retro is thin. Periodic retros work best when there's a consistent volume of work. A week with no commissions produces a retro that says "nothing happened."
- Lessons graduation still requires human judgment. A scheduled retro produces a draft; it doesn't replace the conversation about what matters.

**The tend precedent**: `/tend` is the closest existing model for scheduled hygiene. It runs on a cadence, produces a report, waits for confirmation before applying changes. A scheduled retro could follow the same pattern: retro commission produces a draft, Guild Master audience reviews the draft, graduation happens in that audience.

The difference: tend is about file hygiene (is this document stale?), which has relatively objective answers. Retro is about learning (was this approach good?), which requires subjective judgment. Tend can be almost fully automated; retro can't be.

## The Three-Level Problem

One thing this brainstorm is surfacing: retro in Guild Hall probably needs to operate at three levels, each with different inputs and different outputs.

**Level 1: Commission-level retro.** "What happened in this commission?" Currently: not captured at all. Could be embedded in the commission artifact itself — a "lessons" section that workers fill in before submitting a result. Low overhead, happens automatically if the commission template includes it. The problem: workers don't have a comparison point (they ran one commission, not a series). They can capture "this was harder than expected" but not "this pattern keeps coming up."

**Level 2: Feature-level retro.** "What happened across this set of commissions?" This is what the current `/retro` skill does for single-session work. For Guild Hall, it needs an aggregation step: read all commissions for a feature, synthesize across them, produce one retro document. This is tractable as a commission. It needs a trigger (cleanup? manual?) and a dedicated agent with the right synthesis posture.

**Level 3: Process-level retro.** "What patterns are we seeing across features over time?" This is the "weekly retro" idea. Much harder. The agent needs to look across multiple feature-level retros and identify meta-patterns. This requires pattern recognition that's genuinely hard to do well without significant human input shaping what to look for. Don't build this first.

Build Level 2 before Level 3. Level 1 could be added as a template change (no new skill needed).

## Open Questions

1. **Where does interpretation come from?** A commission log records facts. A retro records lessons. Turning facts into lessons requires judgment: "this decision caused X delay" is an interpretation, not a fact. Who makes that interpretation in a multi-agent workflow? The retro agent (inference, may be wrong), the Guild Master (requires a human), or nobody (lessons get lost)?

2. **Should commission templates include a lessons section?** Workers submitting a commission result could be prompted: "Any observations about this commission that future commissioners should know?" Low overhead, captures fresh insight at the moment of highest recall. But it adds friction to every commission submission. Decision needed.

3. **What's the trigger for a feature-level retro?** Cleanup-commissions is the natural trigger, but it's a hygiene operation, not a synthesis operation. Tying them together may produce rushed retros. Keeping them separate requires deliberate invocation. What's the failure mode if retros are consistently skipped?

4. **Can the graduation step be deferred asynchronously?** The current retro skill requires a live human for graduation. Could a Guild Hall retro write candidate lessons with proposed classifications to the retro frontmatter (`candidate_lessons: [{text: "...", proposed_scope: "critical"}]`), and a later human review approves or changes them? This separates the extraction step (commission, can be automated) from the judgment step (human, can be deferred).

5. **Octavia as retro agent vs. dedicated retro worker?** Octavia's posture is documentation-first, reader-oriented. Synthesis across commission artifacts is within that domain. But a dedicated retro agent might have a different posture — more analytical, more focused on pattern recognition, less on prose quality. Is that worth a new agent type?

6. **How does the retro surface to the Guild Master?** A retro commission that produces a file and submits a result is invisible unless the Guild Master checks `.lore/retros/`. Notify hook? A meeting summary that mentions the retro artifact? Something needs to close the loop.

## What Can Be Experimented With vs. What Needs Decisions

**Experiment without deciding:**
- Add a "Lessons Observed" section to commission templates. Workers fill it in voluntarily. See if the signal is valuable before making it required.
- Commission a feature-level retro after the frontmatter validation work completes. Use the existing Dalton/Octavia commission artifacts as input. Assess quality.
- Try cleanup-commissions as the trigger for a retro draft. Does cleanup-produced retros have enough depth, or does synthesis require a dedicated pass?

**Needs decisions before building:**
- Whether graduation can be deferred (requires deciding what the frontmatter field looks like and how a human reviews it)
- Whether Level 1 (commission-level lessons) should be added to the commission template (adds friction to every commission)
- Whether a scheduled retro commission is worth building (requires deciding on cadence, trigger mechanism, and how the Guild Master reviews the output)
- Whether a dedicated retro worker type is needed or Octavia's domain covers it

## Next Steps

If worth pursuing:
- Commission a trial feature-level retro using the frontmatter validation commissions as input material. Assess output quality before designing a process.
- Brainstorm the commission template change (Lessons Observed section). Is the added field worth the overhead?
- Spec the feature-level retro skill extension (new invocation mode: `/retro commissions/...`) once the trial confirms the approach.
