---
name: vision
description: This skill defines a project's vision and writes it to `.lore/vision.md`. Use when defining project direction, creating a vision document, bootstrapping vision from existing code, or revisiting project identity. Triggers include "define the project vision", "what should this project become", "create a vision document", "set the project direction", "what are our principles".
---

# Vision

Define what the project is trying to become. The vision document serves as a decision filter that other lore-development skills can reference when evaluating proposals, scoping features, or resolving priority conflicts.

## When to Use

- Starting a new project and wanting to declare its direction
- Bootstrapping a vision from an existing codebase
- Revisiting or revising an existing vision
- Needing a north star for feature prioritization

## Process

### Step 1: Check for Existing Vision

Check whether `.lore/vision.md` already exists.

- **If it exists with `status: approved`**: Ask the user whether they want to revise it or just review it. If revising, load the document and go to Step 5 (Refinement). If reviewing, present the current vision and stop.
- **If it exists with `status: draft`**: Load the draft and go to Step 5 (Refinement) to continue where things left off.
- **If it doesn't exist**: Proceed to Step 2.

### Step 2: Determine Creation Path

Assess whether the project has enough signal for bootstrap or should use guided creation.

A codebase is "meaningful" for bootstrap when it has enough signal to draft at least two of the four vision sections from evidence. Indicators: multiple source files, git history with deliberate commits, existing `.lore/` artifacts, or a `CLAUDE.md` with project-specific guidance. A project with only boilerplate, config files, or a skeleton README should default to guided.

State which path you chose and why. The user can override.

### Step 3a: Bootstrap Path (Existing Code)

Read broadly before drafting. Sources:

- Project source code (structure, patterns, naming conventions)
- `.lore/` artifacts (specs, retros, brainstorms, issues, research)
- `CLAUDE.md` files
- README or similar documentation

Look for implicit values: what gets built, what gets rejected, what wins when priorities conflict.

Draft a vision document based on observable evidence. Where evidence is ambiguous or contradictory, say so rather than inventing coherence. A sparse but honest draft is more useful than a complete but fabricated one.

If the bootstrap draft is too sparse to be useful (fewer than two sections have substantive content), offer to switch to guided questions rather than walking through an empty scaffold.

After drafting, go to Step 4.

### Step 3b: Guided Path (New Projects)

Walk the user through structured questions covering these areas. Adapt based on responses and ask follow-ups:

1. **Identity:** What is this project? Who does it serve? What problem does it solve that isn't solved elsewhere?
2. **Values:** What matters most? If you had to pick three things this project should always be, what are they? What order do they go in when they conflict?
3. **Rejections:** What should this project never become? What reasonable-sounding ideas would you reject on principle?
4. **Tensions:** Where do your values pull in opposite directions? When one value conflicts with another, which wins by default?
5. **Constraints:** What's true now that won't be true forever? What limitations shape current decisions but shouldn't become permanent identity?

Synthesize user responses into a draft vision. The user should see their own words reflected back, shaped into the document format, not replaced by your vocabulary.

After synthesizing, go to Step 4.

### Step 4: Present the Draft

Present the draft section by section. Frame each section as "here's what I see; tell me what's right, what's wrong, and what's missing." Do not present the draft as a finished product.

Then proceed to Step 5.

### Step 5: Refinement

Refinement is the core of the interaction, not a cleanup step. The first draft is a conversation starter.

Probe actively:
- "Does this principle actually describe how you make decisions, or is it aspirational?"
- "Are these anti-goals things you'd genuinely reject, or things you just haven't prioritized yet?"

**Behavioral framing**: Principles must be written as behavioral guidelines, not trait aspirations. If the user says "it should be simple," help reframe: "What does simplicity mean in practice for this project? What would you reject as too complex?" The output should be something like "Every new feature must justify itself against the cost it adds to the mental model" rather than "The system should be simple."

After refining each section, check whether the user wants to continue refining or save. When the full document has been reviewed at least once, offer to write it. The user can always ask to keep refining or defer.

### Step 6: Save or Defer

**Save**: Write the vision document to `.lore/vision.md` using the document format below. Set `status: draft`. The user approves by editing the frontmatter directly or telling you to mark it approved. Do not approve on the user's behalf.

**Defer**: If the user wants to think more, summarize what was discussed so the conversation can be resumed later. Do not write a file.

**Revision**: When revising an existing approved vision, update `status` to `draft` and the `date` field when saving.

## Output

Save to `.lore/vision.md`

### Document Format

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions.

```markdown
---
[frontmatter per schema]
---

# Vision

[One paragraph. What is this project? Who does it serve? What makes it distinct?
This paragraph should be stable across years, not months.]

# Principles

[3-7 principles in priority order. Principle 1 is highest priority.]

## 1. [Principle Name]

[One sentence stating the principle as a behavioral guideline.]

**Looks like:** [Concrete example of this principle in action within this project.]
**Doesn't look like:** [Concrete example of violating this principle.]

## 2. [Principle Name]

...

# Anti-Goals

Things this project deliberately chooses not to pursue, with rationale.

- **[Anti-goal].** [Why we reject this, even though it might seem reasonable.]
- ...

# Tension Resolution

When principles conflict, use these defaults:

| Tension | Default Winner | Exception |
|---------|---------------|-----------|
| [Principle A] vs [Principle B] | [A] | [When B wins instead] |
| ... | ... | ... |

# Current Constraints

(Optional) Temporary limitations that shape what's feasible now.
Each should state what it is and when it should be reviewed or is expected to expire.

- [Constraint with expected expiration or review trigger]
- ...
```

### Frontmatter Tips for Vision

- `title` should be `"<Project Name> Vision"`
- `tags` should always include `vision`
- `status` starts as `draft`; becomes `approved` only when the user says so
- Omit `modules`; the vision applies to the entire project, not specific modules
- See the schema's "Vision-Specific Notes" for details

### Principles Quality Check

Before saving, verify each principle against these criteria:
- **Behavioral, not aspirational**: Describes what to do, not what to be
- **Specific to this project**: Not generic advice that applies to everything
- **Includes examples**: "Looks like" and "Doesn't look like" are concrete, not abstract
- **Ordered by priority**: The user has confirmed the ordering

### What the Vision Document Must NOT Contain

- Implementation details, technology choices, or tactical decisions
- Generic principles that apply to every project ("write good code")
- Motivational language ("we strive to be the best")

## Context

Check `.lore/brainstorm/` and `.lore/research/` for prior thinking about project direction that might inform the vision.

## Downstream Integration

Once `.lore/vision.md` exists, other lore-development workflow skills may reference it as context. The vision is available, not mandatory. Skills that define scope or prioritize work can check for a vision and use it to inform decisions, but they function normally without one.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Invoke relevant agents via Task tool and incorporate their insights.
