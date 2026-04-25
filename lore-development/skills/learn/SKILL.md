---
name: learn
description: User-invoked dialog for recording institutional or tribal knowledge — a rule, example snippet, configuration trick, command sequence, or pattern the user wants to keep. The skill never asserts that something is worth capturing, never scans work artifacts on its own, and never fires from another skill. Use when the user wants to write down something worth not losing. Triggers include "learn", "/learn", "record a lesson", "capture a learning", "I want to write down a lesson".
artifact_path: .lore/learned
---

# Learn

Record a lesson the user has already noticed. Write it once, terse, in the user's words.

## Invocation

User-invoked only. `/learn` is never auto-triggered by `/specify`, `/prep-plan`, `/design`, `/retro`, or any other skill. The user decides when a lesson wants to be captured.

```
/learn                                      # Open dialog; the user names what they want to capture
/learn .lore/work/retros/<name>.md         # Optional: name a starting artifact
```

If invoked with a path, that artifact is the seed for the dialog. The skill still asks the opening question; it does not pre-scan the artifact for candidates.

## Stance

The user names the lesson. The skill helps shape the articulation, runs dedup against existing entries, and writes the file. The skill does not propose what counts as a lesson.

- The skill never asserts "this is a lesson."
- The skill never volunteers candidates from artifacts the user did not point at.
- "Nothing, actually" is a valid user answer at any step. The session ends without writing a file.

This is load-bearing. A capture skill that proposes candidates produces hallucinated lessons. See `.lore/work/brainstorm/principles-for-capture-skills.md` and `.lore/work/brainstorm/learn-dialog.md`.

## Opening: Two-Path Question

Ask the user one question to set the path:

> Are you recording from specific material in front of you (a retro, a Thorne review, a spec, a debug session), or describing a felt pattern you keep hitting across sessions?

Both paths are valid.

- **Specific material** — the user has a concrete source. The lesson will be grounded in that source.
- **Felt pattern** — the user has noticed something recurring across sessions: a failure they keep hitting, a workaround they keep applying, a snippet they keep rewriting, a config they keep looking up. There may be no single source.

If the user answers "nothing" or backs out at the opening, close the session without writing a file.

## Question-First Progression

After the opening, the skill asks; the user articulates. The skill does not volunteer what counts as a lesson, and does not pull mistakes out of artifacts on its own. It surfaces only what the user names.

Useful questions to keep the dialog moving:

- "What's worth recording about this?"
- "What would you tell yourself or a teammate before doing this?"
- "What did you figure out that took longer than it should have?"
- "What would have helped if you'd known it earlier?"
- "Is there a snippet, command, or example that captures it better than prose?"

The questions are open. They don't presume the entry is shaped like a rule. If the knowledge is example code, the draft is example code. If it's a configuration trick or a command sequence, the draft is the trick or the sequence. The user names the form.

At any step, "nothing" or "never mind" closes the session without a file.

## Specificity Over Shape

A `/learn` entry has no required shape. It can be a rule ("don't do X because Y"), a code snippet that took hours to get right, a configuration the docs got wrong, a command sequence that has to run in a specific order, a pattern worth repeating, a piece of tribal knowledge about how the system actually behaves. Institutional knowledge doesn't fit one template, and forcing one filters out most of what's worth keeping.

What an entry needs is specificity — it must be grounded in something the user actually hit or actually figured out, not advice that could appear in any blog post. "Write good tests" is noise. "`bun test` infinite-loops with `mock.module()` over more than N modules — pass the dependency in instead, here's the shape" is signal. The first survives only as a slogan; the second survives because someone hit the wall and now the wall is mapped.

The test: would this entry still help a teammate sitting where the user was sitting? If yes, write it. If it reads like advice that could appear anywhere, reshape it toward the specific situation, snippet, or knowledge that prompted it, or close the session.

Specificity is checked at the artifact level. The opening question does not pre-filter material. The check happens when the draft is in front of the user.

## On-Request Fetch

When the user names material — "look at my recent Thorne reviews," "open the auth retro," "everything tagged `migration`" — the skill fetches it on request. Patterns:

- **File path**: read directly with `Read`.
- **Tag query / module query**: delegate to `lore-researcher` patterns (grep frontmatter `tags:` or `modules:` across `.lore/work/` and `.lore/learned/`).
- **Recent-N pattern**: list-by-date under a named subdirectory (e.g., recent retros under `.lore/work/retros/`).

Fetch is on-request only. The skill does not pre-scan artifacts the user did not name. After fetching, the skill surfaces what it read; it does not assert which fragment is a lesson.

## Active Dedup Before Writing

Before writing a file, search `.lore/learned/` for related entries.

1. Pull keywords from the user's articulation (the verbs and nouns of the mistake — what they're doing wrong, what the failure mode is, the affected module).
2. Grep `.lore/learned/` on those keywords. Include frontmatter (`title:`, `tags:`, `modules:`) and body.
3. If `.lore/learned/` does not yet exist, skip dedup — there are no entries to match against. Note this and proceed to write.
4. Surface every match to the user with a short excerpt and the file path.
5. The user decides:
   - **Update existing**: open the matching file and propose an edit.
   - **Supersede existing**: change the old entry's status to `superseded` and write a new one. Add the new entry's path to the old entry's `related:` list.
   - **Write new**: the existing entries are about a different failure; write a new file.
   - **Cancel**: close without writing.

Dedup directly attacks the verbose-restatement failure: three entries for one concept, each convinced it's distinct. If the user is creating that pattern, surface it.

## Write Discipline

- **Terse default.** The lesson is the kernel. One sentence is often enough.
- **No length budget.** Do not aim for N sentences, paragraphs, or bullets. Any named count becomes a target the model fills toward, and the entry inflates.
- **No restating.** One articulation of the mistake. Not three framings of the same idea, not a "this is important because" gloss after the user already said why.
- **Mixed content allowed.** Prose, code blocks, a small example showing the wrong shape — whatever the lesson actually requires. No forced structure.
- **The body has no section scaffold.** No "What", "Why", "When". Frontmatter holds metadata; the body is free-form.
- **Draft is for trimming.** Present the draft to the user with the explicit option to cut. The model's expansion instinct needs a human counterweight.

Forbid the vocabulary of analysis in the body: `lesson`, `insight`, `we learned`, `takeaway`. The entry describes the failure and the rule, not the act of learning.

## File Layout

Default: one file per entry, flat under `.lore/learned/`. Filename is kebab-case, derived from the entry's title.

- `dont-mock-the-database.md`
- `if-you-find-yourself-rewriting-the-config-stop.md`
- `git-stash-doesnt-reset-node-modules.md`
- `json-dumps-default-str-for-dates.md`
- `staging-deploy-port-forward-sequence.md`

Do not pre-create `.lore/learned/`. The directory is materialized by the first `/learn` write. If the directory does not exist when the user accepts the draft, create it then.

This default is revisable. The internal structure of `.lore/learned/` (categorized vs flat, file-per-entry vs append-to-topic-file, full lifecycle) is owned by `.lore/work/issues/design-learned-structure.md`. Adopt revisions when that issue resolves.

## Frontmatter

Common fields only. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for definitions.

```markdown
---
title: [The mistake or imperative, in the user's words]
date: YYYY-MM-DD
status: active
tags: [problem-type, affected-area]
modules: [affected-modules]
---

[Body — free-form. The mistake, the rule, what it prevents. No section headings unless the lesson actually needs them. No analysis vocabulary.]
```

- `status: active` for new entries. `superseded` only when a later entry replaces this one (see Dedup).
- `title` should read as the knowledge itself: "Don't ship the same path string in two places", or "Use `json.dumps(default=str)` for dataclasses with dates", or "Staging deploy needs `--force` after the port-forward step". Not "Path duplication retro" or "JSON serialization notes".
- `tags` and `modules` follow the standard kebab-case conventions.

## Examples

### Specific-material path

User: `/learn`
Skill: *(opening question)*
User: I just finished a Thorne review. He flagged that I caught and swallowed an integration error.
Skill: Want me to pull the review? What's the file path or tag?
User: `.lore/work/retros/2026-04-22-deploy-flake.md`
Skill: *(reads the file)* What did the swallowed error cause downstream?
User: A silent retry loop. Took an hour to find because nothing logged.
Skill: *(runs dedup against `.lore/learned/`)* No related entries. Drafting:

```
---
title: Don't catch integration errors silently
date: 2026-04-24
status: active
tags: [error-handling, integration, logging]
modules: [deploy-system]
---

Silent catch blocks at integration points hide failures and turn one-step bugs
into hour-long debugging sessions. If the call can fail, log the failure and
surface it.
```

User: Cut the second sentence — first one is enough.
Skill: *(applies cut, writes file)*

### Felt-pattern path

User: `/learn`
Skill: *(opening question)*
User: Felt pattern. I keep over-engineering early in a project and then having to rip it out.
Skill: What does following "don't over-engineer early" prevent?
User: Two days of refactoring before the spec stabilizes.
Skill: *(dedup; no matches)* Drafting:

```
---
title: If you find yourself adding abstractions before the spec stabilizes, stop
date: 2026-04-24
status: active
tags: [over-engineering, planning]
---

The abstraction will be wrong because the requirements are still moving. Cost is
two days of refactor when the spec lands.
```

User: Looks right.

### Snippet path

User: `/learn`
Skill: *(opening question)*
User: Specific. I just spent an hour figuring out how to serialize a dataclass with date fields through `json.dumps`. The default serializer chokes on `date`, but `default=str` handles it.
Skill: *(dedup against `.lore/learned/`)* No related entries. Drafting:

````
---
title: Use json.dumps(default=str) for dataclasses with date fields
date: 2026-04-25
status: active
tags: [serialization, json, dataclasses]
modules: []
---

```python
import json
from dataclasses import asdict, dataclass
from datetime import date

@dataclass
class Event:
    name: str
    when: date

json.dumps(asdict(Event("launch", date(2026, 4, 25))), default=str)
# '{"name": "launch", "when": "2026-04-25"}'
```

`default=str` falls through for any non-serializable value, so it also covers
`datetime`, `Decimal`, `UUID`, and `Path` without per-type encoders.
````

User: Looks right.

### Nothing-to-record path

User: `/learn`
Skill: *(opening question)*
User: Actually, never mind. I don't have anything specific.
Skill: Closing without writing. *(no file is created)*

## Verification Pass

Before writing, the skill verifies:

- The entry is grounded in something specific — a real situation, snippet, command, or piece of knowledge the user actually has — not generic best-practice advice. If it reads like it could appear in any blog post, reshape with the user or close the session.
- Dedup ran against `.lore/learned/` (or was skipped because the directory doesn't exist yet).
- The body does not contain `lesson`, `insight`, `we learned`, or `takeaway`.
- The body has no forced section scaffold and no length-padding.
- The user has seen the draft and explicitly accepted it (or the user trimmed it and accepted the trimmed version).
