---
title: "Principles for capture skills: retro, extraction, reflection"
date: 2026-04-23
status: resolved
tags: [methodology, retros, lessons-learned, anti-hallucination, design-principles]
modules: [lore-development]
related: [.lore/work/brainstorm/lore-directory-redesign.md]
---

# Principles for capture skills

Three principles emerged while redesigning retros. They generalize beyond retros to any skill that captures experience and produces knowledge. They're load-bearing inputs to the retro-as-notes and extraction skill designs, and they belong in `learned/` once that directory exists.

## 1. Templates that demand N things cause AI to hallucinate N things

When a capture template has named sections with implied counts ("What Went Well," "What Could Improve," "Lessons Learned" with bullet lists under each), the AI fills the slots whether real material exists or not. The output reads profound because the scaffold demands profundity. The fix is structural, not prompt-level.

**Apply:**
- Resist named sections with implied counts in capture skills.
- Structured metadata in frontmatter is fine. Structured body is the trap.
- Output length should vary with what actually happened. Five lines or fifty, both valid.
- Forbid the vocabulary of analysis ("lesson," "we learned," "insight") in capture output. Otherwise interpretation smuggles itself in through word choice.

**Why this is here:** The current `/retro` skill template has three named sections and always produces five or more bullets. Most are hallucinated. The template is the cause, not the prompt.

## 2. Learn from mistakes only, never from success

Success is overdetermined. You won, so by construction everything you did looks load-bearing. Lessons drawn from success are survivorship bias dressed as wisdom, and they read like LinkedIn infographics ("communicate well," "plan ahead," "stay focused"). Mistakes name a specific thing that broke.

**Apply:**
- `learned/` entries are asymmetric by shape. Valid: "don't do X because Y happened." Valid: "if you find yourself doing X, stop — here's why." Invalid: "do X because it worked."
- Enforce at the artifact level, not as policy. A learned entry that reads like a best-practice tip is malformed by construction.
- Test: if a lesson would still be true had the project failed, it's noise. If it only makes sense because a specific thing broke, it's signal.

**Why this is here:** Current retros capture "What Went Well" as a named section. That slot trains the AI to invent success-lessons that don't survive first contact with a different project.

## 3. Separate observation from interpretation across two steps

Conflating "what happened" with "what it means" in one pass invites hallucination. The AI invents meaning to fill the interpretation slot. Split the work.

- **Step one is witness.** Record events, good and bad, neutrally. No analysis. Probably no vocabulary of analysis either.
- **Step two is analyst.** Look across the record with a human gate. Only triggers when a specific question calls for it.

This mirrors scientific method (record data before interpreting) and good incident response (timeline before postmortem).

**Apply:**
- Capture skills produce raw notes. Extraction skills produce encoded lessons. Different skills, different timing.
- Extraction fires when the question is live (starting new work in an area), not when the source material is fresh. Freshness of data is less important than relevance of question.
- The AI's job in extraction: surface candidates from the notes. The user's job: decide whether each candidate is actually a mistake worth encoding. Without the human gate, hallucination relocates rather than resolves.

**Why this is here:** Current `/retro` tries to observe and interpret in one step. The "Lessons Learned" section is the analyst slot, and it fires at the wrong time — end of session, when profundity-pressure is highest, instead of start of next work, when relevance-pressure is highest.

## Scope

These principles bind any skill whose job is "capture what happened" or "extract meaning from what was captured." That includes:

- Retros (current and redesigned)
- The extraction skill we're about to design
- Any future reflection, review, or postmortem skill
- Possibly `/poke-holes` and `/simplify` retro-adjacent outputs

They do not bind skills whose job is to *describe a system as it is* — excavation, architecture references, diagrams. Those are observational by nature and don't face the same hallucination pressure, because the code is the ground truth check.

## Open question

The principles as stated are themselves unvalidated beyond one session of redesign. Worth a second-pass check once the retro-as-notes skill has produced output under a few real sessions. The principle that "success-learning is always noise" might turn out to have edge cases.
