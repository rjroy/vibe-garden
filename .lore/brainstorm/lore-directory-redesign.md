---
title: "Lore directory redesign: build, reference, learned"
date: 2026-04-23
status: open
tags: [progressive-discovery, retros, directory-structure, methodology, lessons-learned]
modules: [lore-development]
---

# Brainstorm: Lore directory redesign

## Context

Three questions prompted this:

1. Are `.lore/` files work files or persistent data?
2. Are retros really lessons learned, or are we missing a beat?
3. Is the real power a pair of progressive-discovery streams — architecture insights (what the code can't tell you) and institutional knowledge (what only using the system teaches)?

The answer that emerged: the current tree conflates work scaffolding with accumulated knowledge, and the retro skill is the sharpest symptom of the problem.

## The reframe

Collapse the current 13 subdirectories into three:

- **`.lore/build/`** — everything used to produce work. Brainstorms, specs, plans, tasks, notes, stubs, issues, ideas, excavation tracking, retro notes. Session-bound. Dissolves or archives after its work is done.
- **`.lore/reference/`** — anything solidified. Approved vision. Excavated feature docs. Current-state diagrams. Architectural truths you can't recover by reading the code. Oriented at the system: "what is this project? how do I extend it?" Meant to function like a skill — a queryable, progressive-discovery surface, not a pile of documents.
- **`.lore/learned/`** — operational imperatives. Oriented at the worker: "when working in this project, what must I do? what should I never do?" Only mistakes graduate here. Never success.

The build → reference pipeline is the knowledge loop: work produces findings, findings get filed upward. Build → learned is the mistake loop, and it's one-directional because success doesn't teach.

## What the reframe clarifies

- **The compound loop gets a name.** Today it's "lore-researcher searches `.lore/`." Under this model it's "build work produces findings; findings promote to reference or learned." The thing that compounds is finally legible.
- **Vision moves into reference.** `vision.md` is "what is this project?" in the most distilled form. It belongs alongside excavated references and diagrams, not at the root as a special case.
- **Status lifecycles collapse.** Build keeps its complex states (draft → approved → executed → etc). Reference gets `current` / `outdated`. Learned gets something equally short. The frontmatter schema simplifies dramatically.
- **Excavate and retro are mirror operations.** Excavate starts from code and produces reference. Retro starts from experience and produces learned (via extraction, see below). Both are one-unit-at-a-time progressive discovery. Today excavate is a 280-line archaeology practice and retro is a 130-line template. That asymmetry is a bug.

## Retro redesign: notes, not lessons

The current retro is flawed:

- It always finds five things. The template has three named sections demanding to be filled, and the AI fills them.
- It learns from success. Success is overdetermined — you won, so by construction everything you did looks load-bearing. That's survivorship bias, and it produces LinkedIn-infographic output.
- Because it conflates observation and interpretation in one step, the AI invents profundity where none existed.

The fix: retro becomes a witness, not an analyst.

- **Notes only.** What happened, good and bad, in whatever form the session produced. No required sections. No required count. Five lines or fifty. No interpretation. No "we learned." No "lesson."
- **Inverted prompt.** Today's prompt is "capture lessons learned." New prompt is "describe what happened — don't interpret." Probably worth forbidding the vocabulary of analysis outright, otherwise the AI will smuggle it in.
- **Structured metadata, free-form body.** Notes live in `build/` and need frontmatter (modules, tags, date) so the extraction step can find them later. Body is unstructured.

## Extraction: mistake-mining at design time

The extraction step happens at the front of new work, not the end of old work.

- **Trigger.** When designing, planning, or beginning work in an area, ask: "have we made mistakes here before?"
- **Scan.** Walk `build/` — especially retro notes, but also specs and plans — for evidence of mistakes in this area, filtered by module/tag.
- **Surface candidates.** The AI presents what it found. It does not assert mistakes.
- **Human gate.** The user names whether each candidate is actually a mistake worth encoding. AI's job: find evidence. User's job: judge. Without this gate, the hallucination problem relocates rather than resolves.
- **Promote.** For each confirmed mistake, write an entry to `learned/`.

This inverts today's flow. Today: finish session, run retro, graduate lessons. Proposed: record data when fresh, analyze only when the question comes up.

## Learned entries are asymmetric by shape

The asymmetry is load-bearing:

- Valid shapes: "don't do X because Y happened," or "if you find yourself doing X, stop — here's why."
- Invalid shape: "do X because it worked."

Enforcing the shape at the artifact level means the no-success-learning rule isn't just policy during extraction — it's structural. A learned entry that reads like a best-practice tip is malformed by construction.

## What this means for existing pieces

- **Brainstorms and specs keep working.** Same shape, new parent directory (`build/brainstorm/`, `build/specs/`). The lifecycle stays. This file is itself a build artifact under the new scheme.
- **Retros keep being called retros.** The name is fine. The content is what changes.
- **`.lore/reference/` already exists.** Under the new scheme it gets more tenants: vision, diagrams, anything that's solidified. The excavate skill already writes here; that behavior extends.
- **`/tend` gains teeth.** Under the new scheme it can meaningfully archive completed build artifacts without touching reference or learned. The category distinction makes the hygiene rule decidable.

## Open questions

- **The promotion move needs a verb.** Excavate already writes to reference. Retro (new form) writes notes to build. Extraction writes to learned. But there's no named operation for "take this insight from a brainstorm and promote it into the auth reference doc." Without that, build findings accumulate without ever crossing to reference.
- **Reference as a skill, not just a directory.** If `/lore-development:reference "how does auth work?"` is a skill that navigates the reference tree and returns a layered answer, the files are an index, not reading material. Worth deciding: is reference a directory with good frontmatter, or a directory plus a skill that knows how to walk it?
- **Diagrams split by purpose.** Some diagrams are session-bound (a flow sketched to understand a bug, lives in build). Some are current-state (the architecture as it stands, lives in reference). The directory can't be one or the other. The individual diagram decides.
- **Learned structure is undesigned.** The user noted this explicitly: "we'll need to address these separately." How entries are organized, indexed, and retrieved in learned/ is its own design problem.
- **Migration is unaddressed.** An existing `.lore/` tree with the current 13 directories needs a path to the new three. Probably a `/tend` mode. Not in scope here.

## Next steps

Design the retro-as-notes skill and the extraction skill as their own pieces. Both need to be specified before the directory migration makes sense — the skills define what "build" and "learned" hold.
