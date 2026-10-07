---
name: simplify
description: Use when the user wants to simplify or clean up code without changing behavior. Accepts standalone scope or user-selected findings from /refactor.
---

# Simplify

Execute a bounded, behavior-preserving cleanup through delegation; do not edit target code directly.

## Scope and contract

Center execution on the scope the user agreed to, behavior to preserve, and enough evidence to verify preservation. For a /refactor handoff, use only the findings the user selected: carry their paths/scope, intended structural improvement, preserved behaviors, and checks. No plan, spec, or behavior matrix is required. Findings are recommendations, not authorization to change behavior. A requested retirement or other behavior change must be handled separately with the user's authorization; do not disguise it as cleanup. The current user's direction governs over any old artifact, which is context rather than binding authority.

Standalone use remains supported. Resolve scope reliably before dispatch. Load `scope-resolution.md` only when determining Git or file scope; it covers committed and pending work, explicit inputs, replacement/deletion references, and when to ask rather than guess. Include necessary adjacent code/tests without absorbing unrelated work. Never recreate deleted files, mutate commits, or revert unrelated changes.

Simplify duplication, unnecessary scaffolding, or incidental tests only when there is a material maintenance cost in the agreed scope. Do not chase every smell or target a test count. Keep relevant contracts protected; do not make automatic behavior changes or assume test count/apparent lack of use makes behavior obsolete.

## Process

Only one agent edits target files at a time. Select the cleanup agent from `.lore/lore-agents.md` when available and invoke it with Claude Code's current `Agent` tool; on older versions use `Task`. Use `lore-development:<agent-name>` for a bundled agent, the registered name for a project agent, or `general-purpose` if no specialist applies. Delegate the agreed scope, improvement, preserved behavior, and verification evidence.

Then run the ordered loop: **cleanup** (delegated edits) → **test** (read-only verification) → **review** (read-only review). Test retained behavior proportionally; test and review return findings, not edits. Give review findings stable IDs. Route bounded corrections to cleanup and request fresh read-only verification with complete finding records and correction diff. Escalate after two failed attempts on an issue, or three total correction rounds.

## Output

Writing a local note is optional. If useful, resolve `../../scripts/ensure_local.py` from this skill's installed directory and run `python3 <resolved-helper-path> <explicit-project-root>` before writing under `.lore/local/notes/`. Write only after setup succeeds; do not fall back to `.lore/work/` if setup fails. Load `../../shared/frontmatter-schema.md` from this skill's base directory for common fields and lifecycle semantics: start `draft`, use `approved` on explicit user approval or a request for the relevant next step, `completed` when work is done, and `archived` when archived. Record scope, files processed, simplifications, and failures/resolutions when useful; no note is mandatory.

## Escalation

Ask when scope cannot be resolved reliably, when behavior change is proposed or detected, or when a correction limit is reached. Keep behavior-changing work separate from this behavior-preserving workflow.
