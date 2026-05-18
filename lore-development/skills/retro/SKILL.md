---
name: retro
description: This skill reviews completed work and records what happened as free-form notes with structured frontmatter. The capture is observation only, not interpretation. Use after completing a feature, when capturing context before it fades, or for periodic reflection. Triggers include "let's do a retro", "/retro", "review what happened", "capture what happened", "write up the session".
artifact_path: .lore/work/retros
---

# Retro

Record what happened. The retro is the witness step. Interpretation belongs elsewhere.

## When to Use

- After completing a feature or significant chunk of work
- When wanting to capture session context before it fades
- Periodic reflection on project progress

A retro is worth running on any session that left signal worth preserving — surprises, dead ends, things the user got confused by, assumptions that broke. The fresh-but-messy context is the whole value. A retro produced from a separate, clean session loses what's worth capturing.

## Stance

The retro describes what happened. It does not interpret. The forbidden moves:

- No analysis vocabulary in the body. The words `lesson`, `insight`, `we learned`, and `takeaway` do not appear in retro output.
- No template demanding N items. Named sections with implied counts cause the model to manufacture content that doesn't exist.
- No success-extraction. "What went well" framing trains the model to invent best-practice tips that don't survive the next project. Success is overdetermined.
- No promotion of items to higher scopes from inside the retro. If the user notices something worth recording as a rule, that is a separate step (`/learn`).

The shape is structured frontmatter plus free-form body. Length follows what actually happened — five lines or fifty, both valid.

## Process

1. Read the relevant work artifacts:
   - Spec in `.lore/work/specs/` (if applicable)
   - Plan in `.lore/work/plans/` (if applicable)
   - Implementation notes in `.lore/work/notes/` (if applicable)
2. Write the retro as observation. What was the work? What happened in the doing of it? What surprised, broke, drifted, or unfolded differently than the plan said?
3. Save to `.lore/work/retros/[descriptive-name].html`.

The body is free-form prose. Use whatever structure the actual session calls for — chronological, by component, by surprise — or none. If a heading helps the reader follow, use it. If not, plain paragraphs are fine.

## Output

Save to `.lore/work/retros/[descriptive-name].html`.

### Frontmatter

Common fields only. Load `${CLAUDE_PLUGIN_ROOT}/shared/html-base-template.md` and `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the HTML shell and field definitions.

Copy the HTML base template verbatim. Populate the `<meta name="lore-*">` tags in `<head>`. Replace `<main>` with a single body section:

```html
<!-- <meta> tags in <head>:
  <meta name="lore-title"   content="[Topic as a noun phrase]">
  <meta name="lore-date"    content="YYYY-MM-DD">
  <meta name="lore-status"  content="open">
  <meta name="lore-tags"    content="[problem-types, technologies, patterns]">
  <meta name="lore-modules" content="[affected-modules]">
  <meta name="lore-related" content=".lore/work/specs/<name>.html, .lore/work/plans/<name>.html">
-->

<main>
  <section id="body">
    <h2>[Topic]</h2>
    <!-- Free-form prose body. Use whatever structure the session calls for.
         Headings, paragraphs, and lists are all fine -- or none at all.
         See Body Discipline section for guiding questions. -->
    <p>[Body text]</p>
  </section>
</main>
```

- `status: open` while the work the retro tracks can still be amended. `archived` once the work is fully past.
- `title` describes the work, not an extracted moral. "Auth-flow rollout" is a title; "Why we should always test migrations" is not.
- `tags` cover what the session touched: problem types (`bug`, `performance`, `refactor`), technologies, patterns. Searchable by `lore-researcher`.
- `modules` lists codebase areas touched. Omit for purely process-focused sessions.

Retros are simple artifacts. No collapsibles or interactivity needed.

### Body Discipline

The body answers questions like:

- What was the work?
- What did the plan say versus what actually happened?
- Where did the model or the user get tripped up?
- What surprises came out of the doing?
- What dead ends were tried before the path that worked?
- What context got assembled that's worth preserving for the next session in this area?

Write the answers as prose, not as bullets under preset headings. If a list helps, use a list — but don't reach for the list because a template demands it.

Length should track what happened. A short, smooth session with one notable surprise is two paragraphs. A long, rough session with three blowups is longer. There is no length budget.

If during writing the user notices a rule worth recording, that's a `/learn` invocation — a separate skill, separate file. Retro stays as observation.

## Recording vs Recording-and-Acting

The retro records. It does not act. In particular:

- The retro does not classify items by importance, scope, or universality.
- The retro does not move items to project `CLAUDE.md` or `~/.claude/rules/lessons-learned.md`.
- The retro does not run a follow-on prompt to extract rules from the body.

If the user wants to record an operational rule that came out of the session, they invoke `/learn` separately. Lessons live in `.lore/learned/`. The retro stays as a record of what happened.

## Frontmatter Tips

- **title**: Describe the work, not a takeaway. "N+1 in brief generation" describes; "Always test for N+1" interprets.
- **tags**: Keep grep-discoverable. Include problem types, technologies, and patterns the session actually touched.
- **modules**: Match codebase structure. Omit for methodology-only sessions.
- `related`: Link the spec, plan, and notes the retro references. `lore-researcher` follows these links. Use `.html` extensions.

## Specialized Agents

If `.lore/lore-agents.md` exists, project-specific agents (security, architecture, performance) can be useful for assembling context the user wants to record. Their job is to surface what the session touched, not to assert what the takeaways are.

## Verification Pass

Before declaring the retro complete:

- The body does not contain `lesson`, `insight`, `we learned`, or `takeaway`.
- The body has no "What Went Well", "What Could Improve", or "Lessons Learned" section heading (or any analysis-style heading filling that role).
- The body describes what happened, not what should be done next time.
- Length follows the session's actual content. No padding to fill a template that no longer exists.
- Frontmatter status is `open` or `archived`.
