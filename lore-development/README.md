# Lore Development

A lightweight plugin for building and organizing project context.

<img src="logo.webp" align="right" width="128" height="128" alt="Lore Development Logo">

## Philosophy

Modern LLMs have strong native planning and implementation capabilities. This plugin doesn't teach process - it helps build findable, organized context (the "lore" of your project) that informs better work.

## Skills

| Skill | Purpose |
|-------|---------|
| `/lore-development:research` | Gather context from outside the project |
| `/lore-development:brainstorm` | Explore ideas, record "what if" thinking |
| `/lore-development:specify` | Define requirements and success criteria |
| `/lore-development:design` | Make technical decisions when the "how" is the problem |
| `/lore-development:prep-plan` | Build implementation plans as reviewable lore artifacts |
| `/lore-development:plan-breakdown` | Decompose a plan into task files for `/implement` |
| `/lore-development:implement` | Orchestrate implementation from a plan via sub-agents |
| `/lore-development:simplify` | Orchestrate code cleanup with tests and review |
| `/lore-development:retro` | Capture what happened in a session as free-form notes |
| `/lore-development:learn` | Record a mistake worth not repeating; user-invoked dialog writing to `.lore/learned/` |
| `/lore-development:poke-holes` | Challenge ideas adversarially |
| `/lore-development:distill` | Promote what the code cannot say into reference docs (two seed modes: `code`, `build`) |
| `/lore-development:ddp` | **Draw the Damn Picture** - visualize flows and relationships with Mermaid |
| `/lore-development:define-validation` | Define AI validation criteria for work in progress |
| `/lore-development:tend` | Periodic hygiene to maintain document status accuracy |
| `/lore-development:update-stubs` | Scan specs for stubs and generate an outstanding stub index |
| `/lore-development:update-lore-agents` | Build/update the project's agent registry |
| `/lore-development:review-ideas` | Process captured ideas into structured issues |
| `/lore-development:file-issue` | File a structured issue directly from an observation |

## Idea Capture

The plugin includes a hook that captures ideas without invoking the AI. Start any prompt with `idea:` and the text is appended to `.lore/ideas.md`. Use `/review-ideas` to process accumulated ideas into structured issues.

## Artifact Storage

Context lives in `.lore/` under three top-level directories. Each directory has a different purpose, audience, and lifetime.

```
.lore/
├── build/          # Work scaffolding — session-bound, written during a flow
│   ├── brainstorm/     # Recorded explorations
│   ├── specs/          # Requirements
│   ├── design/         # Technical decisions
│   ├── plans/          # Implementation plans
│   ├── tasks/          # Task files (from /plan-breakdown)
│   ├── notes/          # Session notes (e.g. /implement progress)
│   ├── research/       # External findings
│   ├── retros/         # Free-form retrospective notes
│   ├── issues/         # Structured issues
│   ├── validation/     # Validation criteria
│   ├── stubs/          # Outstanding stub index from specs
│   ├── diagrams/       # Visual representations (Mermaid) — promote to reference/diagrams/ when stable
│   └── excavations/    # /distill session tracking
│
├── reference/      # Solidified, system-oriented — what the code cannot say
│   ├── vision.md       # Project vision (if defined)
│   ├── <feature>.md    # Distilled feature documentation
│   └── diagrams/       # Promoted, stable diagrams
│
├── learned/        # Mistakes worth not repeating — worker-oriented, born on first /learn
│
├── ideas.md        # Captured ideas (via hook)
└── lore-agents.md  # Agent registry (optional)
```

**Why three directories?** `build/` holds the work-in-progress: messy, conversational, tied to a specific session. `reference/` holds what survived: invariants, vision, distilled documentation that informs future work. `learned/` is narrowly scoped to mistakes — not lessons, not insights, not "what went well." Each has a different decay rate and a different reader.

### Migrating from the old layout

Pre-redesign projects had a flat `.lore/` with directories like `specs/`, `plans/`, `retros/` at the top level. Run `/lore-development:tend migrate` to move an existing tree into the three-directory model. The migrate mode rewrites internal links in frontmatter and prose, leaves guild-hall–owned paths alone, and is idempotent on re-run.

## Agents

The plugin ships with agents that skills invoke automatically:

| Agent | Purpose |
|-------|---------|
| `lore-researcher` | Search `.lore/` for related prior work before new specs or plans |
| `design-reviewer` | Review design documents for weak decisions and gaps |
| `plan-reviewer` | Review plans for infeasible steps and scope creep |
| `spec-reviewer` | Review specs for clarity issues and ambiguities |
| `fresh-lore` | Fresh-context analysis when the current session is too deep in the weeds |
| `surface-surveyor` | Quick codebase reconnaissance to find entry points |

## Agent Registry

Beyond the built-in agents, skills can leverage project-specific agents for domain concerns (security, performance, architecture, etc.). Instead of hardcoding agent names into every skill, the plugin uses a project-level registry.

**How it works**:
1. Run `/lore-development:update-lore-agents` to scan available agents
2. The skill creates `.lore/lore-agents.md` with agents relevant to your project
3. Other skills check this file and invoke agents when appropriate

**Benefits**:
- Add new agents without updating the plugin
- Each project declares what's relevant to it
- Project-specific notes (e.g., "always use security-guidance for auth specs")

## Usage

Skills can run independently. Use what you need. For the recommended flow when building something new, see the **Workflow** section below.

## Workflow

Skills flow from exploration to implementation. The key decision is when to start a fresh session.

### Explore (same session)

Run `/brainstorm`, `/research`, `/specify`, and `/design` in the same conversation. These phases are conversational. The value is in the back-and-forth, the rejected ideas, the "not that because X" reasoning. Let context accumulate.

When `/design` or `/specify` completes, you have written artifacts in `.lore/`. The exploration phase is done.

### Plan (fresh session)

Start a new session. Run `/prep-plan` pointing at the artifacts from the explore phase. The planner synthesizes from the documents, not from conversational memory. This is intentional: if the written artifacts aren't clear enough for a fresh context to produce a good plan, they need revision before implementation.

### Build (fresh session)

Start a new session. Run `/implement` pointing at the plan. The implement skill delegates to sub-agents who get their own fresh context. The orchestrator shouldn't carry exploration history when it needs full attention on dispatching, testing, and reviewing.

### Capture (same session)

Run `/retro` at the end of any session where something worth capturing happened. Retro produces a free-form notes file with common frontmatter — no template, no demanded sections, no "lessons learned" header. The retro benefits from the messy context: what went wrong, what the LLM got confused by, which assumptions broke. A fresh context would lose exactly the things worth capturing.

Retros aren't only for build. An explore session that surfaced a surprising constraint, or a plan session that revealed a spec gap, are both worth a `/retro` before closing out.

If a specific mistake is worth not repeating, run `/learn` to record it. `/learn` is a user-invoked dialog that writes to `.lore/learned/`. It does not auto-trigger from `/retro` or any other skill, and it does not propose candidates from notes — the user names the mistake. See the skill itself for the framing.

### Why break context

Rolling context helps when work is exploratory. It hurts when work is procedural and artifact-driven. Breaking context before `/prep-plan` also serves as a forcing function: if the specs and designs can't stand on their own without the conversation that produced them, they aren't ready.

### Distilling existing code

Use `/distill code` when inheriting or joining an existing codebase, or `/distill build` when a spec, plan, or brainstorm holds invariants worth promoting. Both seeds run the same loop: read the seed, verify against current code, present reconciled candidates, let the user gate each one. Output goes to `.lore/reference/` and only contains what the code cannot tell a reader. Null output is a valid outcome.

## The Compound Loop

Knowledge compounds when past learnings inform new work. The plugin closes this loop automatically:

```
/specify or /prep-plan
        │
        ├─► lore-researcher agent searches .lore/ for related work
        │
        ▼
   findings included in new spec/plan
        │
        ... work happens ...
        │
        ▼
      /retro
        │
        └─► captures notes → writes to .lore/build/retros/
```

The `lore-researcher` agent runs automatically at the start of `/specify` and `/prep-plan`, surfacing relevant retros, specs, and brainstorms before new work begins.

## Frontmatter Schema

All lore documents use YAML frontmatter for searchability. The schema is defined in `shared/frontmatter-schema.md`.

```yaml
---
title: Descriptive title
date: YYYY-MM-DD
status: draft|approved|complete|etc
tags: [relevant, keywords]
modules: [affected-modules]
---
```

Documents without frontmatter won't be found by `lore-researcher`. Use `/tend` to retrofit old documents, and `/tend migrate` to move a flat-layout `.lore/` into the three-directory model.

## Principles

- **Light touch** - skills guide, they don't dictate
- **Context over process** - build lore, not bureaucracy
- **Independent but connected** - each skill works alone but knows about the others
- **Trust the LLM** - don't over-specify what modern AI already does well
- **Human checkpoints** - distillation gates each promotion candidate by user decision
- **Compound knowledge** - past learnings automatically surface for new work
