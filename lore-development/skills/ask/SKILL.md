---
name: ask
description: Answer a specific question from project lore. Use when you need a direct answer grounded in `.lore/` content, not a map of what exists. Differs from /research (external sources) and from invoking lore-researcher directly (which returns a directory of candidates, not an answer). Triggers include "ask lore", "/ask", "what does lore say about", "according to lore", "is X documented", "does the project have a position on".
---

# Ask

Answer a question using only what is in `.lore/`. Cite the source. Refuse to fabricate.

## When to Use

- A specific factual question whose answer should already be in lore ("how does the auth session expire?", "what's our position on background jobs?", "do we have a spec for billing?")
- An agent needs a one-shot answer it can act on, not a list of candidates to interpret
- The asker wants to know whether lore has a position before they form one

Do **not** use for:
- Open exploration of a topic — that's lore-researcher directly, or `/brainstorm`
- Questions about external libraries, APIs, or prior art — that's `/research`
- Questions about current code state — read the code

## Authority Hierarchy

Reference and learned answer different kinds of questions: reference is ground truth for *what the system should be*, learned is ground truth for *what actually happened during development*. When they agree, cite both and lead with reference. When they disagree, report both and name the question being asked — do not pick one.

1. **`.lore/reference/`** — canonical. What the system should be. Highest authority for design-intent questions.
2. **`.lore/learned/`** — operational lessons from development. Highest authority for "what bites us" questions. A learned entry that contradicts reference may mean reference is stale; surface the conflict, never silently reconcile it.
3. **`.lore/work/`** — in-flight artifacts. Often stale. Use only when nothing in reference or learned answers the question, and flag the staleness risk.

## Process

1. **Receive the question.** Do not rephrase it for the user. Do not split it into sub-questions on your own; if the question genuinely contains two, answer both and label which is which.

2. **Invoke lore-researcher.** Pass the question verbatim. The researcher does its own keyword extraction and expansion. Add a hint only when a domain-specific term in the question is unlikely to expand naturally (e.g., "this is about EOS SDK auth flows"). The researcher returns candidates grouped by directory. Do not stop here — candidate summaries are not an answer.

3. **Read the candidates in priority order, with a stopping rule.** Read all `reference/` and `learned/` candidates in full. Read `work/` candidates only when reference and learned do not answer the question, and only as many as needed to cite the answer. Skim is not enough on the files you do read; the answer may be in a paragraph the summary skipped. If the candidate set is unmanageably large, say so in the answer and recommend a narrower question.

4. **Synthesize.** Compose the answer in the asker's frame. Cite each claim with `path/to/file.md` (and a line reference when the claim is a specific sentence). Lead with reference material, then learned, then work. When work artifacts are the only source, say so.

5. **Refuse honestly when the answer is not in lore.** Do not fill the gap from training data, intuition, or the surrounding code. Say what is missing and point at the closest adjacent material so the asker knows where to look or what to write next.

## Output Format

```markdown
## Answer

[Direct answer to the question, in 1-3 short paragraphs. No preamble.]

## Sources

- `.lore/reference/...` — [what this source contributed]
- `.lore/learned/...` — [what this source contributed]
- `.lore/work/...` — [what this source contributed; note if likely stale]

## Confidence

**[High | Mixed | Low | Not in lore]**

[One-sentence justification matching the label:]
- **High** — reference and learned agree; sourced from canonical material.
- **Mixed** — sources conflict. Name the conflict. Do not resolve it silently.
- **Low** — only work artifacts speak to this; the answer may be stale.
- **Not in lore** — no source answers the question. Name the closest adjacent material, or "nothing adjacent found".
```

The label appears alone on the line under `## Confidence` so a calling agent can match exactly. The justification follows on the next line.

When the answer is "not in lore," the Sources section lists what *was* searched and what *was* close, so the asker can decide whether to write a spec, run `/research`, or check the code.

## Refusal Posture

This is load-bearing. The skill's value is honesty about what lore contains.

- Never invent a source path. If a citation cannot be produced, the claim does not belong in the answer.
- Never paraphrase external knowledge as if it were a project position. "I think the project does X" is not an answer; "lore says X at `path:line`" is.
- Never silently reconcile a conflict between reference and learned. Report both and let the asker decide.
- "Not in lore" is a complete answer. It is more useful than a confident guess.

## Invocation

```
/ask <question>
```

The question is free text. Examples:
- `/ask how does session expiry work?`
- `/ask do we have a spec for the billing module?`
- `/ask what's the position on running tests against a real database?`

Agents may invoke this skill via the Task tool when they need a grounded answer before proceeding. The output format is stable enough to parse: the `## Confidence` line tells the calling agent whether to trust the answer or escalate.
