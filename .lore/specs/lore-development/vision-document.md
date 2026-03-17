---
title: Vision Document
date: 2026-03-16
status: draft
tags: [vision, self-evolution, brainstorming, artifacts, lifecycle]
modules: [guild-hall-core]
related:
  - .lore/research/vision-statements-as-ai-decision-filters.md
  - .lore/specs/infrastructure/guild-hall-system.md
  - .lore/specs/commissions/guild-hall-scheduled-commissions.md
  - .lore/specs/workers/worker-identity-and-personality.md
req-prefix: VIS
---

# Spec: Vision Document

## Overview

Guild Hall projects accumulate decisions over time. Those decisions carry implicit values: what matters, what gets rejected, what wins when priorities conflict. But nothing makes those values explicit. When a brainstorming worker proposes improvements, it has no north star to filter against. Every idea is equally plausible because the system has no stated opinion about what it wants to become.

This spec introduces the vision document: a per-project artifact that declares the project's identity, ordered principles, anti-goals, and tension resolution rules. It serves one primary consumer: a scheduled brainstorming worker that evaluates proposed improvements against it. The vision is also available to any worker or human who needs to understand what the project values and where it's heading.

Two paths produce a vision document. For existing projects, an excavation commission reads the codebase, lore, issues, and memory, then drafts a vision from what the project's decisions already reveal. For new projects, a guided creation meeting walks the user through structured questions and synthesizes responses into a draft. Both paths end the same way: the user reviews, corrects, and approves. No vision is authoritative until the user signs off.

The vision is a living document. It gets reviewed periodically and after major architectural changes, but changes go through the same approval flow as creation. The document's anchoring function depends on stability; frequent rewrites undermine the filtering it provides.

Depends on: [Spec: Guild Hall System](guild-hall-system.md) for artifact conventions (REQ-SYS-2, REQ-SYS-3) and storage layout. [Spec: Guild Hall Scheduled Commissions](../commissions/guild-hall-scheduled-commissions.md) for the recurring brainstorming commission that consumes the vision. [Spec: Worker Identity and Personality](../workers/worker-identity-and-personality.md) for the soul/posture boundary, which the vision document parallels at the project level.

Informed by: [Research: Vision Statements as AI Decision Filters](../../research/vision-statements-as-ai-decision-filters.md), which identifies structural patterns from Claude's constitution, OpenAI model spec, C3AI framework, and design token systems.

## Entry Points

- User asks to create a vision for an existing project (triggers excavation commission)
- User starts a new project and wants to define its direction (triggers guided creation meeting)
- Brainstorming worker reads the vision at session start to filter proposals (from scheduled commission)
- User reviews and approves a vision draft (from meeting or commission result)
- User or worker initiates a vision review after a major change or scheduled trigger (from review cycle)

## Requirements

### Document Format

- REQ-VIS-1: The vision document is a markdown file with YAML frontmatter, conforming to the artifact schema (REQ-SYS-2). It lives at `.lore/vision.md` in the project root. One vision per project. The path is a convention, not configurable.

  > **Why `.lore/vision.md` and not `.lore/specs/vision.md`:** The vision is not a feature spec. It sits above specs in the hierarchy. Specs define what to build; the vision defines what the project is trying to become. Placing it at the `.lore/` root reflects its scope: it applies to the entire project, not to a subdomain.

- REQ-VIS-2: The frontmatter MUST include the following fields:

  ```yaml
  ---
  title: "<Project Name> Vision"
  version: <integer, starting at 1>
  status: draft | approved
  last_reviewed: <ISO 8601 date>
  approved_by: <"user" or null>
  approved_date: <ISO 8601 date or null>
  review_trigger: "<human-readable condition for next review>"
  changelog:
    - version: 1
      date: <ISO 8601 date>
      summary: "<what changed>"
  ---
  ```

  `version` is an integer that increments on each approved revision. `status` is `draft` until the user approves it, then `approved`. `approved_by` is always `"user"` (vision approval is never delegated to a worker). `review_trigger` is a human-readable string like "quarterly" or "after major architectural change" that tells the review system when to prompt re-evaluation.

  The standard artifact `modules` field (REQ-SYS-2) is omitted intentionally. The vision applies to the entire project, not to specific modules. Including an empty `modules: []` would suggest the vision is unscoped, which is misleading. The vision's scope is the project itself.

- REQ-VIS-3: The document body MUST contain these four sections in order. The section names and ordering are fixed; the vision's value as a decision filter depends on agents being able to locate each section reliably.

  1. **Vision** (prose paragraph). What the project is, who it serves, what makes it distinct. This paragraph should be stable across years, not months. It constrains direction without constraining implementation.

  2. **Principles** (ordered numbered list, 3-7 items). Each principle is a behavioral guideline, not a trait aspiration. Each includes:
     - A one-sentence statement of the principle
     - **Looks like:** a concrete example of the principle in action within this project
     - **Doesn't look like:** a concrete example of violating the principle within this project

     Principles are ordered by priority: Principle 1 is the highest priority, Principle 2 is next, and so on. When two principles conflict, the lower-numbered (higher-priority) principle wins.

  3. **Anti-Goals** (bulleted list, 3-5 items). Things the project deliberately chooses not to pursue, with rationale. Anti-goals are strategic rejections, not prohibitions. They declare what the project is choosing not to be, even if those choices might seem reasonable from outside.

  4. **Tension Resolution** (table). Pre-declared defaults for the most common value conflicts between principles. Format: "When [Principle A] conflicts with [Principle B], prefer [winner] unless [exception condition]."

- REQ-VIS-4: The document body MAY contain an optional **Current Constraints** section after Tension Resolution. Current constraints are temporary limitations that shape what's feasible now but are expected to change. Each constraint should state what it is and when it should be reviewed or is expected to expire. Constraints are explicitly separated from principles to prevent temporary limitations from calcifying into permanent values.

- REQ-VIS-5: Principles MUST be written as behavioral guidelines, not trait aspirations. "Every new feature must justify itself against the cost it adds to the mental model" is behavioral. "The system should be simple" is a trait. Behavioral framing is actionable because it describes what to do, not what to be. This distinction is the difference between a principle an agent can evaluate against a concrete proposal and one it can only nod at.

  > **Informed by research:** C3AI found that positively framed, behavior-based principles align more closely with human preferences than trait-based or negatively framed principles.

- REQ-VIS-6: The document MUST NOT contain implementation details, technology choices, or tactical decisions. The vision constrains direction, not method. "User-visible state lives in files, not databases" is a strategic principle. "We use gray-matter for parsing" is a tactic that belongs in CLAUDE.md or a spec.

### Approval Flow

- REQ-VIS-7: A vision document begins life with `status: draft`. It becomes authoritative only when the user explicitly approves it, at which point `status` changes to `approved`, `approved_by` is set to `"user"`, and `approved_date` records the timestamp. No worker may approve a vision. The vision represents the user's intent for the project; delegation of authorship is fine, delegation of approval is not.

  Approval is a manual edit: the user changes `status: draft` to `status: approved` and fills in `approved_by` and `approved_date`. This matches the agent-native principle (REQ-SYS-39): the artifact is the interface, not a special command. The user can make this edit in any text editor, through the web UI's artifact editor, or via CLI. No dedicated approval endpoint exists; the frontmatter is the mechanism.

- REQ-VIS-8: Workers MUST treat a `draft` vision as non-authoritative. A brainstorming worker that encounters a draft vision SHOULD note its existence and flag that the project lacks an approved vision, but MUST NOT use draft content as a decision filter. The absence of an approved vision is itself useful information: it tells the brainstorming worker that proposals cannot yet be evaluated against project direction.

- REQ-VIS-9: When a vision is revised, the document returns to `status: draft` until the user approves the revision. During this window, the brainstorming worker treats the project as having no approved vision (per REQ-VIS-8 and REQ-VIS-16). The previous approved version exists in git history but consumers do not attempt to recover it; the simpler behavior is to note that a revision is in progress and proceed without vision-based filtering. The changelog records what changed and why, so the user can see the delta between the current draft and the last approved state.

  > **Why not "previous version remains in effect":** Requiring consumers to read git history for the last approved state adds complexity for minimal benefit. Revision windows should be short (the user reviews and approves promptly). During the gap, the brainstorming worker operates without a vision filter, which is safe: it still generates proposals, they just lack alignment analysis. The incentive structure is correct: an unapproved revision creates a visible gap in filtering quality, motivating the user to approve quickly.

### Creation Path: Excavation (Existing Projects)

- REQ-VIS-10: For projects with existing history, the vision is created through an excavation commission. An excavation is a commission whose purpose is to read existing artifacts and surface implicit structure, rather than produce new features (see `/lore-development:excavate`). The worker reads the project's codebase, `.lore/` artifacts (specs, retros, brainstorms, issues), CLAUDE.md, memory, and git history to identify the implicit values already embedded in the project's decisions. The output is a draft vision document at `.lore/vision.md`.

- REQ-VIS-11: The excavation commission prompt MUST instruct the worker to:
  1. Read broadly before writing. The implicit vision lives in what was built, what was rejected, and what was deferred. Specs, retros, brainstorms, issues, and the CLAUDE.md all carry signal.
  2. Identify patterns of decision-making, not just features. What gets prioritized when priorities conflict? What proposals have been rejected and why? What constraints are treated as permanent versus temporary?
  3. Draft the vision in the format defined by REQ-VIS-3, applying the behavioral framing rule from REQ-VIS-5 and the tactical content exclusion from REQ-VIS-6.
  4. Flag uncertainty. Where the evidence is ambiguous or contradictory, the draft should say so rather than inventing coherence. The user's review is where ambiguity gets resolved.
  5. Submit the draft as a commission result. The draft is written to `.lore/vision.md` with `status: draft`.

- REQ-VIS-12: The excavation worker MUST NOT invent principles that aren't supported by evidence in the project artifacts. The excavation surfaces what's already there; it doesn't create a vision from scratch. If the project's decisions don't reveal enough implicit direction to fill all four required sections, the worker should produce what the evidence supports and note what's missing. A sparse but honest draft is more useful than a complete but fabricated one.

### Creation Path: Guided Creation (New Projects)

- REQ-VIS-13: For new projects without existing history, the vision is created through a guided creation meeting. A worker walks the user through structured questions that elicit the project's intent, audience, constraints, and aspirations. The worker synthesizes the responses into a draft vision document.

- REQ-VIS-14: The guided creation meeting MUST cover at minimum these areas (the worker may ask follow-up questions based on responses):

  1. **Identity:** What is this project? Who does it serve? What problem does it solve that isn't solved elsewhere?
  2. **Values:** What matters most? If you had to pick three things this project should always be, what are they? What order do they go in when they conflict?
  3. **Rejections:** What should this project never become? What reasonable-sounding ideas would you reject on principle?
  4. **Tensions:** Where do your values pull in opposite directions? When [value A] and [value B] conflict, which one wins by default?
  5. **Constraints:** What's true now that won't be true forever? What limitations shape current decisions but shouldn't become permanent identity?

- REQ-VIS-15: The guided creation worker synthesizes user responses into a draft vision in the format defined by REQ-VIS-3 (applying the behavioral framing rule from REQ-VIS-5 and the tactical content exclusion from REQ-VIS-6), then presents the draft for immediate feedback within the same meeting. The user can refine the draft interactively before the meeting closes. The meeting output is a `.lore/vision.md` file with `status: draft`.

  > **Why a meeting, not a commission:** Guided creation is inherently interactive. The worker needs to respond to user answers, ask follow-ups, and present a draft for real-time refinement. This is what meetings are for (REQ-SYS-7: "purposeful, bounded, productive").

### Downstream Usage: Brainstorming Worker

- REQ-VIS-16: The brainstorming worker (the scheduled commission that proposes improvements) MUST read `.lore/vision.md` at session start, before generating any proposals. If the file does not exist or has `status: draft`, the worker MUST include a visible note in its output stating that no approved vision exists and that proposals were not filtered against project direction. The worker proceeds without vision-based filtering in this case.

  When an approved vision exists, the worker MUST also check `last_reviewed` against `review_trigger`. If the review condition appears to be met (e.g., `review_trigger: "quarterly"` and `last_reviewed` is more than three months old), the worker MUST flag this in its output as a recommendation to review the vision. This is informational, not blocking: the worker still applies the vision as a filter.

- REQ-VIS-17: When an approved vision exists, the brainstorming worker MUST evaluate each proposal against the vision using this sequence:

  1. **Anti-goal check.** Does the proposal move the project toward something it explicitly rejected? If yes, reject the proposal or flag the tension.
  2. **Principle alignment.** Which principles does the proposal serve? Does it advance a lower-priority principle at the expense of a higher-priority one? If so, flag the tradeoff.
  3. **Tension resolution.** Does the proposal trigger a known tension? Apply the pre-declared default from the tension resolution table.
  4. **Constraint check.** Does the proposal respect current constraints? If it violates one, note the constraint and whether it's still valid.

  The brainstorming worker presents each proposal with its alignment analysis. It does not autonomously reject proposals based on vision misalignment (that's the user's call), but it surfaces the conflicts clearly.

- REQ-VIS-18: The brainstorming worker's output MUST include a vision alignment section for each proposal. The section captures the results of all four evaluation steps from REQ-VIS-17: anti-goal conflicts, principle alignment (which principles served, which tensioned), tension resolution defaults applied, and constraint interactions. This section is the primary value of having a vision document: it transforms "here's an idea" into "here's an idea and here's how it fits the direction you declared."

### Review and Evolution

- REQ-VIS-19: The vision document includes a `review_trigger` field in its frontmatter (REQ-VIS-2). The review trigger is a human-readable condition, not an automated mechanism. Examples: "quarterly", "after major architectural change", "when a new worker type is added". The trigger serves as a reminder that the vision needs periodic re-evaluation, not as an enforcement mechanism.

  > **Why not automated:** Automating vision review creates noise. A quarterly reminder that fires when nothing has changed trains people to ignore it. The trigger is documentation of intent: "this is when we should think about whether the vision still holds." Enforcement comes from the brainstorming worker, which will naturally surface proposals that strain the vision.

- REQ-VIS-20: Vision revisions follow the same approval flow as initial creation (REQ-VIS-7). A revision returns the document to `status: draft`, adds a changelog entry with the version number, date, and summary of changes, and increments the version number. The user must approve the revised draft before it becomes authoritative again.

  A revision can be initiated by: (a) the user editing `.lore/vision.md` directly and changing `status` back to `draft`, (b) a worker commissioned to update the vision producing a new draft, or (c) the brainstorming worker flagging in its output that the vision appears stale or strained, prompting the user to commission a revision. All three paths converge on the same artifact and the same approval flow.

- REQ-VIS-21: When a principle is removed from the vision, it MUST be recorded in the changelog with rationale. Principles are not silently dropped. The changelog entry should explain why the principle was removed: was it wrong from the start, did the project outgrow it, or was it absorbed into a broader principle? This prevents confusion when older brainstorming outputs reference principles that no longer exist.

  > **Informed by research:** The W3C design token format uses a `$deprecated` property for this purpose. The changelog approach is lighter-weight and fits the existing artifact conventions better than adding deprecation metadata to individual principles.

- REQ-VIS-22: Vision evolution should be conservative. The vision's value as an anchor depends on stability. A vision that changes every month is not a north star; it's a weather vane. Revisions should reflect genuine shifts in project direction, not routine refinement. Routine refinement belongs in specs, plans, and CLAUDE.md, which are designed to change frequently.

### Interaction with Other Artifacts

- REQ-VIS-23: The vision document does not replace CLAUDE.md, specs, or any existing artifact type. The relationship is hierarchical: the vision states what the project wants to become; CLAUDE.md states how to work in it today; specs define what to build; plans define how to build it. The vision informs all of these but does not duplicate their content.

- REQ-VIS-24: Workers other than the brainstorming worker MAY read the vision for context but are not required to. The vision is optimized for the brainstorming use case (filtering improvement proposals). A developer worker implementing a specific feature gets its direction from the commission prompt and relevant specs, not from the vision. The vision is strategic context, not operational instruction.

- REQ-VIS-25: The vision document SHOULD be referenced in the project's CLAUDE.md documentation map once it exists, so that workers and humans can discover it. The entry belongs alongside the existing documentation map entries for `.lore/specs/`, `.lore/plans/`, etc.

## Open Questions

1. **Should the excavation path be a commission or a meeting?** This spec prescribes a commission (REQ-VIS-10) because the excavation is primarily a research task: the worker reads artifacts and produces a draft. The user reviews the output after. But a meeting would allow real-time course correction during drafting. The commission approach is simpler and matches the "read, draft, review" pattern. If users find the review-after-the-fact flow too disconnected, a meeting variant could be added later.

2. **Should the brainstorming worker be a new worker or an existing one?** This spec refers to "the brainstorming worker" without specifying which worker it is. That's intentional: the vision document format is worker-agnostic. A future spec for the self-evolution system will define the brainstorming worker's identity, posture, and scheduled commission configuration. This spec only defines the document that worker consumes.

3. **What happens when a project has no vision and no lore history?** The guided creation path (REQ-VIS-13) handles new projects, but "new project" might also mean a project registered in Guild Hall with an existing codebase but no `.lore/` directory. This edge case falls to the excavation path, which should still work (it reads codebase and git history, not just lore). If neither path produces enough signal, the worker drafts what it can and flags gaps (REQ-VIS-12).
