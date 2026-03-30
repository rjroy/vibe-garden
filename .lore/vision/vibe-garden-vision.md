---
title: Vibe Garden Vision
date: 2026-03-30
status: draft
tags: [vision, project-direction]
---

# Vision

Vibe Garden is a collection of Claude Code plugins that turn an AI coding assistant into a collaborator with memory, judgment, and awareness. Each plugin adds a dimension that raw prompting lacks: knowing what work matters and what's next (Compass Rose), accumulating and retrieving project knowledge across sessions (Lore Development), staying present when the human steps away (Notify Hook), and reading the room when a session goes sideways (Mind Reader). Together they create an environment where the AI's contribution compounds over time instead of resetting with each conversation.

# Principles

## 1. Knowledge Compounds Through Retrieval, Not Just Capture

Every plugin that stores information must also have a path back to it. Capture without retrieval is a write-only log. The lore-researcher closing the loop between past retros and new specs, the codebase-scanner connecting git history to backlog items, the baseline computation informing session nudges: these are the moments where the system earns its complexity.

**Looks like:** A new spec automatically surfaces lessons from retros about the same module. A reprioritization scan finds that three backlog items reference code that was refactored last week.
**Doesn't look like:** A retro that gets written and never read. A brainstorm that sits in `.lore/brainstorm/` without any skill knowing it exists.

## 2. The Human Decides; The System Surfaces

Plugins create affordances for human judgment. They present evidence, recommend options, and explain reasoning. They do not act autonomously on consequential decisions. Compass Rose recommends the next item; the user picks it. Mind Reader nudges when frustration is detected; the user decides whether to stop. Lore Development drafts specs; the user approves them.

**Looks like:** `backlog` presents scored recommendations with rationale and waits. `poke-holes` asks adversarial questions instead of declaring answers. The vision document starts as `status: draft` and only becomes `approved` when the user says so.
**Doesn't look like:** Auto-closing issues based on codebase scans. Silently reordering priorities. Marking specs as approved without explicit user confirmation.

## 3. Structured Text Over Infrastructure

The system runs on markdown files with YAML frontmatter, searched by grep. No databases, no servers, no external services beyond what the user explicitly configures (ntfy.sh, Discord, Slack). Plugins are directories of scripts and markdown. State lives in files that humans can read, edit, and version-control. This is a deliberate constraint, not a limitation to outgrow.

**Looks like:** `.lore/` artifacts are plain markdown that any tool can read. `lore-researcher` finds prior work with grep over frontmatter fields. Hook scripts are stdlib-only Python that exit cleanly on any failure.
**Doesn't look like:** A plugin that requires a running service to function. State stored in binary formats or databases. Dependencies on specific cloud infrastructure.

## 4. Plugins Work Alone, Compose When Present

Each plugin is independently useful. Compass Rose manages backlogs without Lore Development. Notify Hook sends alerts without Mind Reader. But when multiple plugins are present, they become more than the sum: `start-work` escalates large items to Lore Development's `/specify`. The lore-researcher can surface context that informs backlog prioritization. This composition happens through conventions (`.lore/` paths, frontmatter fields, skill invocation) rather than hard dependencies.

**Looks like:** Installing only `notify-hook` gives you working notifications. Adding `lore-development` to a project with `compass-rose` makes both better without requiring either to change.
**Doesn't look like:** A plugin that fails when another plugin is absent. A shared database that all plugins must connect to. Version coupling between plugins.

## 5. Graceful Failure Is a Feature, Not a Fallback

Hooks exit 0. Config loading falls back to defaults. Sentiment analysis is optional. Backend dispatch isolates failures so one broken webhook doesn't prevent other notifications. This isn't defensive programming for its own sake. It's recognition that these plugins run inside someone's active work session, and a plugin that blocks Claude Code is worse than a plugin that silently degrades.

**Looks like:** `notify.py` catches every exception class and exits cleanly. Mind Reader's hook always completes even if VADER isn't installed. A rate-limited backend is skipped without affecting others.
**Doesn't look like:** A hook that raises an uncaught exception and blocks the user's prompt. A missing config file that crashes the plugin. An error in one notification backend that prevents all notifications.

## 6. Ceremony Scales With Consequence

A quick idea gets captured as a one-line `idea:` prefix with no frontmatter. A feature that will take a week gets a spec, a plan, and a review. The system supports both without forcing the heavy path on small work or the light path on large work. Size-based escalation in `start-work` (XL/L items trigger spec writing) is the pattern: match the process to the stakes.

**Looks like:** Ideas flow in with zero friction and get refined later through `/review-ideas`. Large items automatically escalate to specification. `/tend` runs periodically to clean up what accumulated informally.
**Doesn't look like:** Requiring frontmatter on every captured thought. Skipping specs on large features because they "slow things down." A single workflow that treats a typo fix and a new subsystem identically.

# Anti-Goals

- **Not a project management platform.** Compass Rose integrates with GitHub Projects; it doesn't replace it. The backlog lives in GitHub. The analysis and recommendations live in the plugin. Duplicating the source of truth would create drift, and drift in project management is how teams lose track of what matters.

- **Not an autonomous agent framework.** Plugins observe, recommend, and surface. They do not take actions on behalf of the user without explicit approval. The generation effect (learning through doing, not watching) matters. An AI that does the work for you teaches you nothing about the work.

- **Not a knowledge base.** Lore Development stores project context, not documentation. Artifacts are working memory for the development process: specs that drove implementation, retros that captured lessons, plans that coordinated work. They are inputs to future decisions, not outputs for external readers.

- **Not infrastructure.** No servers to run. No databases to maintain. No containers to deploy. The plugins are scripts and markdown that live alongside the code. If a plugin requires infrastructure, it has exceeded its mandate.

- **Not a monolith.** The plugins share a repository for convenience, not because they share a runtime. Each plugin declares its own dependencies, defines its own hooks, and ships its own skills. A user who wants only notifications should never encounter the concept of a spec.

# Tension Resolution

When principles conflict, use these defaults:

| Tension | Default Winner | Exception |
|---------|---------------|-----------|
| Compounding knowledge vs. Zero ceremony | Ceremony scales with consequence | Raw ideas and quick captures skip ceremony entirely; only graduated artifacts need structure |
| Human decides vs. Graceful failure | Graceful failure | When the failure mode is "block the user's active session," degrade silently even if it means the human doesn't see a recommendation |
| Structured text vs. Plugins compose | Structured text | If composition would require a shared service or binary protocol, keep plugins independent and accept the duplication |
| Human decides vs. Knowledge compounds | Human decides | Automated retrieval surfaces context, but automated action on that context requires explicit approval |
| Plugins work alone vs. Ceremony scales | Plugins work alone | A plugin must never require another plugin's ceremony (e.g., frontmatter format) to function independently |

# Current Constraints

- **Claude Code plugin API is early.** The hook system, skill format, and agent conventions are still evolving. Design decisions that depend on specific API behaviors (hook input format, stdin JSON structure, exit code semantics) may need revisiting as the platform matures. Review trigger: Claude Code plugin API breaking changes or major version releases.

- **Single-user assumption.** All four plugins assume a single developer working on a single machine. Multi-user collaboration (shared backlogs, team notifications, collaborative lore) is not currently supported and would require rethinking state management. Review trigger: if the user base grows beyond solo developers, or if Guild Hall's multi-worker patterns surface team-level needs.

- **No cross-session state for Mind Reader.** Temporal and sentiment baselines are computed from Claude Code's local history, which means the system needs initialization and doesn't carry session-to-session learning about the user's patterns beyond what the baseline captures. Review trigger: if Claude Code exposes richer session metadata or persistent state APIs.

- **Lore Development dominates the version history.** At v1.11.2 compared to Compass Rose v1.3.0, Notify Hook v1.0.0, and Mind Reader v1.2.0, Lore Development receives the vast majority of development attention. This is appropriate for now (it's the most complex plugin and the most actively used), but the other plugins' maturity gaps may become limiting. Review trigger: when users report that Compass Rose or Mind Reader capabilities don't keep pace with Lore Development's workflow integration.
