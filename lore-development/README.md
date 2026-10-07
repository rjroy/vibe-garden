# Lore Development

A lightweight plugin for building and organizing project context.

<img src="logo.webp" align="right" width="128" height="128" alt="Lore Development Logo">

## Philosophy

Modern LLMs have strong native planning and implementation capabilities. This plugin doesn't teach process - it helps build findable, organized context (the "lore" of your project) that informs better work.

Skills use four `.lore/` zones (`local/`, `work/`, `reference/`, `learned/`) — see **Artifact Storage** below for the full layout.

## Skills

| Skill | Purpose |
|-------|---------|
| `/lore-development:research` | Gather context from outside the project |
| `/lore-development:brainstorm` | Explore ideas, record "what if" thinking |
| `/lore-development:intent` | Think through what to build and why; record conversational intent |
| `/lore-development:vision` | Capture project-level purpose and direction |
| `/lore-development:design` | Make technical decisions when the "how" is the problem |
| `/lore-development:prep-plan` | Discuss an evidence-informed approach; optionally record a disposable working plan |
| `/lore-development:migrate` | Preview and optionally move legacy work specs/plans/tasks/notes into intents and gitignored local paths |
| `/lore-development:refactor` | Diagnose code smells and discuss bounded cleanup options; does not edit code |
| `/lore-development:implement` | Orchestrate implementation from the current request, optionally informed by lore context |
| `/lore-development:simplify` | Execute user-selected behavior-preserving cleanup with tests and review |
| `/lore-development:retro` | Capture what happened in a session as free-form notes |
| `/lore-development:poke-holes` | Challenge ideas adversarially |
| `/lore-development:define-validation` | Define AI validation criteria for work in progress |
| `/lore-development:install-formula` | Install the reusable Beads workflow formula in a project |

## Artifact Storage

Context lives in `.lore/` across four zones. Each has a different purpose, audience, and lifetime. The only file at the `.lore/` root is `lore-agents.md`, a cross-plugin agent registry surface (see below).

```
.lore/
├── local/         # Disposable, gitignored context for current execution
│   ├── plans/          # Optional implementation plans
│   ├── notes/          # Optional implementation/resumption notes
│   └── tasks/          # Generic context only; not execution phases
│
├── work/          # Shared historical conversations and work
│   ├── ideas/          # Captured idea records
│   ├── brainstorm/     # Recorded explorations
│   ├── intents/        # Conversational what/why context
│   ├── specs/          # Legacy historical specs; not active contracts
│   ├── design/         # Technical decisions
│   ├── plans/          # Legacy plans, retained as historical context
│   ├── tasks/          # Historical task artifacts
│   ├── notes/          # Historical session notes
│   ├── research/       # External findings
│   ├── retros/         # Free-form retrospective notes
│   ├── issues/         # Structured issues
│   ├── validation/     # Validation criteria
│   ├── stubs/          # Outstanding stub index from specs
│   ├── diagrams/       # Visual representations (Mermaid) — promote to reference/diagrams/ when stable
│   └── excavations/    # Historical distillation session tracking
│
├── reference/      # Solidified, system-oriented — what the code cannot say
│   ├── vision.md       # Project vision (if defined)
│   ├── <feature>.md    # Distilled feature documentation
│   └── diagrams/       # Promoted, stable diagrams
│
├── learned/        # Operational mistakes worth preserving — worker-oriented
│
└── lore-agents.md  # Agent registry (optional, cross-plugin surface)
```

**Why four zones?** `local/` holds disposable, gitignored plans, notes, and task context for active execution. `work/` preserves shared historical conversations (including intents, brainstorms, and older work artifacts) as searchable, nonbinding context. `reference/` holds selectively maintained descriptions of what code and tests cannot explain. `learned/` is narrowly scoped to operational mistakes and remains unchanged. Each has a different decay rate and reader.

Work artifacts are historical context, not binding instructions. The user's
current direction takes precedence; call out concrete safety or compatibility
consequences rather than treating disagreement with an old document as a blocker.
Legacy files under `.lore/work/` remain discoverable historical material; do not
delete or untrack them as part of adopting local storage. To initialize local
storage in a project, run `python3 <path-to-lore-development>/scripts/ensure_local.py <project-root>`. It creates `.lore/local/` and adds `/.lore/local/` to the project root's `.gitignore` without replacing existing content. In a Git worktree it verifies effective ignore behavior and fails without rewriting explicit `.lore/local` negations; in a non-Git project it prepares the rule for future Git initialization. If Git is unavailable, the helper warns that effective ignore behavior could not be verified. When invoked from a lore-development skill, resolve the helper relative to that installed skill, not the project working directory. Field-guide's init can invoke it when the plugins are installed as siblings; separately installed plugins do not assume a shared source tree. Static skill guidance cannot force a model to execute the helper; direct setup is available for non-skill workflows.

**Layered reference directories.** When `.lore/reference/` outgrows its flat layout, use the sibling `/field-guide:stratify` skill to group reference pages and repair their links. It changes page locations, not page contents or frontmatter. The `.lore/learned/` zone remains available for operational learning and is maintained explicitly rather than by an active skill.

### Migrating from the old layout

Pre-work-layout projects may have legacy directories directly under `.lore/` (`specs/`, `design/`, `retros/`, `plans/`, and others). Use optional `/lore-development:migrate` to preview moving recognized historical folders into `work/` and local `plans/`, `tasks/`, and `notes/`. Legacy HTML artifacts are converted to Markdown with original-byte backups in ignored local storage. Unmapped data is reported and left untouched; migration requires explicit confirmation and is not needed to use current skills.

## Agents

The plugin ships with these agents for skills to invoke when appropriate:

| Agent | Purpose |
|-------|---------|
| `lore-researcher` | Search `.lore/` for useful historical context before intents or plans |
| `bun-typescript-reviewer` | Review Bun/TypeScript daemon, Unix-socket, CLI, Next.js, and React implementations against requested behavior |
| `design-reviewer` | Review design documents for weak decisions and gaps |
| `plan-reviewer` | Review plans for infeasible steps and scope creep |
| `intent-reviewer` | Check that intent notes faithfully capture what the user wants and why |
| `rust-daemon-cli-reviewer` | Review Rust daemon and CLI implementations against requested behavior |

## Agent Registry

Beyond the built-in agents, skills can leverage project-specific agents for domain concerns (security, performance, architecture, etc.). Instead of hardcoding agent names into every skill, the plugin uses a project-level registry.

**How it works**:
1. Create or update `.lore/lore-agents.md` with agents relevant to your project
2. Other skills check this file and invoke agents when appropriate

**Benefits**:
- Add new agents without updating the plugin
- Each project declares what's relevant to it
- Project-specific notes (e.g., "always use security-guidance for auth specs")

## Usage

Skills can run independently. Use what you need. For the recommended flow when building something new, see the **Workflow** section below.

## Workflow

Skills flow from exploration to implementation. The key decision is when to start a fresh session.

### Explore (same session)

Run `/brainstorm`, `/research`, `/intent`, and `/design` in the same conversation. These phases are conversational. The value is in the back-and-forth, the rejected ideas, the "not that because X" reasoning. Let context accumulate.

When `/design` or `/intent` completes, you have historical context in `.lore/`. Intent records what and why, not a contract. A disposable plan can explore implementation and validation, but is optional; `/implement` follows the user's current request.

### Plan (fresh session)

Start a new session. Run `/prep-plan` with the artifacts from the explore phase as context. Use them as suggestions, then plan in light of current user direction and evidence.

### Implement (fresh session)

Start a new session for substantial work. Run `/implement` with the current request and any useful context; an optional plan can help, but is not required. The implement skill delegates to sub-agents who get their own fresh context. The orchestrator shouldn't carry exploration history when it needs full attention on dispatching, testing, and reviewing.

### Refactor (diagnose, then choose)

Use `/refactor` to investigate a bounded area for evidenced maintenance smells
and discuss whether a behavior-preserving cleanup is worthwhile. It is
read-only; no finding is a valid outcome. If you choose to proceed, `/simplify`
executes only the selected scope with tests and review. Behavior changes are
discussed separately rather than bundled into cleanup.

### Capture (same session)

Run `/retro` at the end of any session where something worth capturing happened. Retro produces a free-form notes file with common frontmatter — no template, no demanded sections, no "lessons learned" header. The retro benefits from the messy context: what went wrong, what the LLM got confused by, which assumptions broke. A fresh context would lose exactly the things worth capturing.

Retros aren't only for implement sessions. An explore session that surfaced a surprising constraint, or a plan session that revealed a spec gap, are both worth a `/retro` before closing out.

`.lore/learned/` is reserved for useful operational mistakes worth preserving. `/retro` writes free-form notes to `.lore/work/retros/`; it does not automatically promote material into the learned zone.

### Why break context

Rolling context helps when work is exploratory. It hurts when work is procedural
and artifact-driven. Breaking context before `/prep-plan` can help focus planning;
the artifacts are context to reconsider against the user's present direction, not
a gate that must satisfy an old contract.

### Distilling reference knowledge

Field-guide distillation may use eligible historical brainstorm, design, intent, research, or retro artifacts as leads. Verify claims about current behavior against code/tests and follow current user direction. Plans, notes, and tasks (including local plans) are not reference sources; they may suggest investigation only. Keep only knowledge that code/tests do not adequately communicate and materially helps a future change. Merge or retire redundant pages rather than accumulating summaries; no new page is a valid outcome. See the field-guide ingest skill for the current distillation guidance.

## The Compound Loop

Knowledge compounds when historical context informs new work and retrospectives preserve useful outcomes. The skills support this loop:

```
/intent or /prep-plan
        │
        ├─► lore-researcher agent searches .lore/ for related work
        │
        ▼
   useful historical context considered while shaping intent/plan
        │
        ... work happens ...
        │
        ▼
      /retro
        │
        └─► captures notes → writes to .lore/work/retros/
```

The `lore-researcher` agent runs at the start of `/intent`; `/prep-plan` uses it when prior context would help. It surfaces relevant retros, legacy specs, and brainstorms as historical context, not instructions for current work.

## Frontmatter Schema

All lore documents use YAML frontmatter for searchability. The schema is defined in `shared/frontmatter-schema.md`.

```yaml
---
title: Descriptive title
date: YYYY-MM-DD
status: draft
tags: [relevant, keywords]
modules: [affected-modules]
---
```

The `lore-researcher` can find documents without frontmatter through body-text
search, but treats them as lower-confidence legacy material because lifecycle
and module metadata are unavailable. Do not rewrite project histories en masse.
Use the optional `/migrate` skill for preview-first layout transition and status
normalization of mapped legacy files. Field-guide's `/field-guide:stratify`
organizes reference pages without changing their contents or lifecycle metadata.

Document bodies are Markdown by default. Embed raw inline HTML only where a visual carries meaning Markdown cannot (color-coding, inline-`<svg>` charts, side-by-side comparison) — never inside a fenced code block, and with no `<script>` or external resources. See the "Body Format" section of `shared/frontmatter-schema.md`.

To validate frontmatter across a tree (the schema's field rules and shared four-value lifecycle), run the bundled checker. It scans `.md` files, emits one JSON finding per line, and exits non-zero when any document is invalid:

```bash
python scripts/validate_frontmatter.py .lore
```

## Principles

- **Light touch** - skills guide, they don't dictate
- **Context over process** - build lore, not bureaucracy
- **Independent but connected** - each skill works alone but knows about the others
- **Trust the LLM** - don't over-specify what modern AI already does well
- **Human checkpoints** - distillation gates each promotion candidate by user decision
- **Compound knowledge** - past learnings automatically surface for new work
