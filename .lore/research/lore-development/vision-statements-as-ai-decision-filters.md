---
title: Vision Statements as AI Decision Filters
date: 2026-03-16
status: active
tags: [vision, self-evolution, decision-filter, brainstorming, constitutional-ai]
modules: [guild-hall]
related:
  - .lore/research/soul-md-personality-techniques.md
  - .lore/research/agent-native-applications.md
  - .lore/research/agent-memory-systems.md
---

# Vision Statements as AI Decision Filters

Research into how to structure a vision document that an AI brainstorming agent can use to evaluate whether proposed changes move a system in the right direction. The target use case: a scheduled brainstorming worker in Guild Hall proposes improvements, and needs a north star to filter ideas against.

## 1. Precedents: Machine-Consumable Value Documents

Three significant precedents exist for documents that tell AI systems what to value and how to make tradeoff decisions.

### Claude's Constitution (Anthropic, January 2026)

The strongest precedent. Anthropic's constitution for Claude uses a four-tier priority hierarchy: (1) broad safety, (2) broad ethics, (3) Anthropic's guidelines, (4) helpfulness. In cases of conflict, higher priorities generally dominate, but the hierarchy operates "holistically rather than strictly" so lower priorities still receive weight.

Key structural choices:
- **Hard constraints vs. soft defaults.** Hard constraints are absolute prohibitions that override everything. Soft defaults ("instructable behaviors") are adjustable within bounds. This two-tier system prevents the document from being either too rigid (everything is a rule) or too vague (everything is a guideline).
- **Reason-based over rule-based.** The 2026 revision shifted from a list of standalone principles to explanatory prose that gives the reasoning behind each value. The design goal: Claude should be able to "construct any rules by understanding underlying principles." This means the document stays useful in novel situations the authors didn't anticipate.
- **Explicit acknowledgment of incompleteness.** The constitution says it is "likely unclear, underspecified, or even contradictory in certain cases" and asks Claude to use "its best interpretation of the spirit of the document." This is a deliberate choice favoring adaptive judgment over formulaic rule-following.

Source: [Claude's Constitution](https://www.anthropic.com/constitution), [Claude's New Constitution (announcement)](https://www.anthropic.com/news/claude-new-constitution)

### OpenAI Model Spec (December 2025)

Uses a five-level authority hierarchy (Root > System > Developer > User > Guideline) where higher levels override lower ones in conflict. Each principle carries metadata about its authority level and scope.

Key structural choices:
- **Illustrative pairs.** Every principle includes compliant/violation examples with reasoning. This grounds abstract values in concrete behavior.
- **Explicit vs. implicit overrides.** Some defaults require direct instruction to change; others can be contextually overridden. This distinction prevents both over-rigidity and accidental drift.
- **Side-effect accounting.** Requires deliberate assessment of reversibility and unintended consequences before acting.

Source: [OpenAI Model Spec (2025-12-18)](https://model-spec.openai.com/2025-12-18.html)

### C3AI Framework (ACM Web Conference 2025)

Academic research on how to craft and evaluate constitutional principles for AI. Found that positively framed, behavior-based principles align more closely with human preferences than negatively framed or trait-based principles. The framework involves: selecting relevant items, converting them into standardized statements, and curating a final set.

Also developed stress-testing methodology: generating scenarios that force explicit tradeoffs between competing principles, using a taxonomy of value conflicts where the system "must choose between pairs of legitimate principles that cannot be simultaneously satisfied."

Source: [C3AI paper (ACM 2025)](https://dl.acm.org/doi/10.1145/3696410.3714705), [Stress-testing model specs (Anthropic Alignment)](https://alignment.anthropic.com/2025/stress-testing-model-specs/)

### Design Tokens (W3C Design Tokens Format Module)

Not an AI precedent, but a relevant structural pattern. Design systems use "tokens" as machine-readable named values that encode design decisions. Tokens are the single source of truth: when a decision changes, it propagates everywhere. The W3C format includes `$value`, `$type`, and `$deprecated` properties. Periodic reviews identify tokens that have drifted from their original purpose.

The analogy: vision principles are decision tokens. Each one encodes a judgment call. When the vision evolves, the change propagates to all future brainstorming sessions.

Source: [Design Tokens (Material Design 3)](https://m3.material.io/foundations/design-tokens), [W3C Design Tokens Format Module](https://goodpractices.design/articles/design-tokens)

## 2. What Structures Make a Vision Statement Actionable for AI?

Five structural properties emerged across all precedents.

### 2.1 Ordered priority hierarchy, not flat lists

Every effective precedent uses a ranked list, not an unordered set. When the Claude constitution says "prioritize these in the order listed," it gives the AI a deterministic tiebreaker. A flat list of equally weighted principles ("we value simplicity, power, extensibility, consistency") gives the agent no way to resolve conflicts.

**Verified pattern:** Both Claude's constitution and the OpenAI model spec use explicit ordering. The C3AI research found that unordered principle sets produce inconsistent behavior under stress testing.

### 2.2 Principles with concrete examples, not abstract aspirations

The OpenAI model spec pairs every principle with compliant/violation examples. SOUL.md uses "calibration pairs" (flat vs. alive examples). Both patterns work because they give the AI a reference point for what the principle looks like in practice.

**Why this matters for brainstorming:** An agent evaluating "should we add a plugin system?" needs to see what "simplicity" means concretely for this project. Does it mean "few moving parts" or "easy to use despite internal complexity"? Examples disambiguate.

### 2.3 Anti-goals alongside goals

What you reject is often more informative than what you accept. An anti-goal like "we do not build features for imagined future users" provides a sharper decision boundary than "we build for real users." The constitution precedents use hard constraints (never-do) as one form of this, but for a vision statement, anti-goals don't need to be absolute prohibitions. They're strategic choices about what the project chooses not to be.

**Inferred from code:** Guild Hall's worker identity spec already uses this pattern. REQ-WID-16 says: "Workers do not evolve their personality during execution, self-modify their soul file, or adapt personality per commission." The design note explains why. This is an anti-goal with rationale.

### 2.4 Tension resolution rules, not tension avoidance

The stress-testing research (Anthropic Alignment, 2025) explicitly generates scenarios where principles conflict. The finding: systems that have pre-declared how to resolve common tensions outperform those that leave resolution to runtime judgment.

For a vision statement, this means identifying the 3-5 most likely value tensions and declaring which side wins by default. Not "simplicity is good and power is good" but "when simplicity and power conflict, we prefer simplicity unless the power unlocks a capability that's inaccessible any other way."

### 2.5 Behavioral framing over trait framing

The C3AI research found that "be helpful" (trait) is less effective than "provide accurate information even when it's not what the user wants to hear" (behavior). Behavior-based principles are more actionable because they describe what to do, not what to be.

For a brainstorming agent, "the system should be simple" is trait framing. "Every new feature must justify itself against the cost it adds to the mental model of a new contributor" is behavior framing.

## 3. Minimum Viable Structure

Based on the precedents, here is the minimum structure that provides meaningful filtering power per unit of complexity.

### Required sections (high filtering power)

| Section | Purpose | Format |
|---------|---------|--------|
| **Identity** | What this system is and who it serves. One paragraph. | Prose |
| **Ordered Principles** | 3-7 values in priority order. Each with a one-line statement, a behavioral example, and a counter-example. | Numbered list with subsections |
| **Anti-goals** | What this system deliberately chooses not to be. 3-5 items with rationale. | Bulleted list |
| **Tension Resolution** | Pre-declared winners for the most common value conflicts. | Table: "When X conflicts with Y, prefer X unless [condition]" |

### Optional sections (useful but not load-bearing)

| Section | Purpose | When to add |
|---------|---------|-------------|
| **Evaluation Rubric** | Scoring criteria an agent can apply to a specific proposal. | When proposals need quantitative filtering, not just pass/fail |
| **Current Constraints** | Temporary limitations that shape what's feasible now but won't apply forever. | When the project is in a specific phase that constrains options |
| **Evolution Protocol** | How this document itself changes. | When multiple agents or humans might update it |

### What to leave out

- **Implementation details.** The vision is about direction, not method. "How to build it" belongs in specs and plans.
- **Exhaustive values.** More than 7 principles creates decision paralysis. If everything is a priority, nothing is.
- **Motivational language.** The audience is an AI agent, not a team in a kickoff meeting. Cut anything that doesn't help filter a decision.

## 4. Handling Tension Between Competing Values

Three patterns emerged, in order of evidence strength.

### Pattern 1: Ordered hierarchy with contextual exceptions (strongest evidence)

Claude's constitution: values are ordered, but the hierarchy is "holistic, not strict." Higher values generally win, but the agent weighs all considerations. For a project vision, this looks like:

```
1. Understandable (highest priority)
2. Capable
3. Extensible
4. Polished

When 1 conflicts with 2: prefer understandable unless the capability
is critical to the core use case.
When 2 conflicts with 3: prefer capable unless the extensibility
enables user-created capabilities.
```

The explicit exception clauses are what make this pattern useful. Without them, the hierarchy is too rigid. With too many, it's meaningless.

### Pattern 2: Hardcoded vs. softcoded (strong evidence)

Some values are non-negotiable ("hardcoded") and others are adjustable ("softcoded"). This maps to the brainstorming use case: certain principles should never be violated by a proposed improvement, while others represent current preferences that could change.

### Pattern 3: Stress-test scenarios (moderate evidence, research only)

Pre-generate scenarios where principles conflict and document the expected resolution. This is the C3AI approach. Useful for calibration but expensive to maintain. Better suited for periodic review than for the initial document.

## 5. Decay Resistance

How to write a vision statement that stays useful as the system evolves.

### What causes vision documents to decay

1. **Specificity rot.** Concrete examples become outdated as the system changes. The principle "we don't build plugin systems" becomes wrong the day you add plugins.
2. **Priority drift.** What mattered at founding ("get it working") stops being the top priority later ("keep it maintainable"). But the document still lists the old priorities.
3. **Scope creep.** New sections accumulate without old ones being pruned. The document becomes a changelog of values, not a filter.
4. **Abstraction escape.** Principles written so abstractly they never decay also never filter. "We value quality" is immortal and useless.

### Decay-resistant patterns

**Separate the timeless from the timely.** The identity and ordered principles should be durable (change rarely, with deliberation). Current constraints should be explicitly marked as temporary with review triggers.

**Version the document.** Include a date and a short changelog. When someone reads the vision, they know when it was last affirmed. A vision statement from two years ago that was never reviewed is a document, not a commitment.

**Write principles at the right abstraction level.** Not so specific they break when implementation changes ("we use markdown files"), not so abstract they filter nothing ("we value good design"). The sweet spot: principles that constrain strategy without constraining tactics. "User-visible state lives in files, not databases" constrains strategy. "We use gray-matter for parsing" constrains tactics.

**Include a sunset mechanism.** The W3C design token format has a `$deprecated` property. A vision document should have an equivalent: principles that are being phased out are marked, not silently dropped. This prevents confusion when old brainstorming outputs reference principles that no longer exist.

**Build review into the lifecycle.** The Claude constitution is explicitly described as "a continuous work in progress." Guild Hall's vision statement should include a trigger for review: either time-based (quarterly) or event-based (after a major architectural change).

## 6. Recommended Format for Guild Hall's Vision Document

Based on all findings, here is a recommended structure. This is formatted as a template the brainstorming agent would consume.

```markdown
---
title: Guild Hall Vision
version: 1
last_reviewed: YYYY-MM-DD
review_trigger: quarterly or after major architectural change
---

# Vision

[One paragraph. What is this system? Who does it serve? What makes it
distinct from alternatives? This paragraph should be stable across
years, not months.]

# Principles (ordered by priority)

## 1. [Principle Name]

[One sentence stating the principle as a behavioral guideline.]

**Looks like:** [Concrete example of this principle in action.]
**Doesn't look like:** [Concrete example of violating this principle.]

## 2. [Principle Name]
...

# Anti-Goals

Things this project deliberately chooses not to pursue, with rationale.

- **[Anti-goal].** [Why we reject this, even though it might seem
  reasonable.]
- ...

# Tension Resolution

When principles conflict, use these defaults:

| Tension | Default winner | Exception |
|---------|---------------|-----------|
| [Principle A] vs [Principle B] | [A] | [When B wins instead] |
| ... | ... | ... |

# Current Constraints

Temporary limitations that shape what's feasible now. These will
change and should be reviewed at each review cycle.

- [Constraint with expected expiration or review trigger]
- ...
```

### Why this format

- **YAML frontmatter** matches the project's existing artifact format and is machine-parseable for version tracking and review automation.
- **Ordered principles with examples** give the brainstorming agent both priority ranking and calibration. The examples are the most important part: they turn abstract values into pattern-matching targets.
- **Anti-goals** provide the sharpest filtering. A brainstorming agent can check "does this proposal move us toward something we explicitly rejected?" faster than "does this align with our values?"
- **Tension resolution table** prevents the brainstorming agent from generating proposals that optimize one principle at the expense of a higher-priority one without acknowledging the tradeoff.
- **Current constraints** separated from timeless principles prevents the constraints from calcifying into values. When the constraint expires, it's removed without touching the core vision.
- **No evaluation rubric in v1.** Quantitative scoring adds complexity without evidence that it improves filtering over a well-structured qualitative filter. Add it later if pass/fail filtering proves insufficient.

### Usage by the brainstorming agent

The brainstorming agent would read this document at session start, then evaluate each proposed improvement against it:

1. Does this proposal violate any anti-goal? If yes, reject.
2. Does this proposal serve the highest-priority principle it touches? If it optimizes a lower principle at the expense of a higher one, flag the tension.
3. Does this proposal respect current constraints? If not, note the constraint and whether it's still valid.
4. Present the proposal with its alignment analysis for human review.

## Sources

- [Claude's Constitution](https://www.anthropic.com/constitution) (Anthropic, January 2026)
- [Claude's New Constitution announcement](https://www.anthropic.com/news/claude-new-constitution) (Anthropic)
- [OpenAI Model Spec (2025-12-18)](https://model-spec.openai.com/2025-12-18.html) (OpenAI)
- [C3AI: Crafting and Evaluating Constitutions for Constitutional AI](https://dl.acm.org/doi/10.1145/3696410.3714705) (ACM Web Conference 2025)
- [Stress-testing model specs reveals character differences](https://alignment.anthropic.com/2025/stress-testing-model-specs/) (Anthropic Alignment)
- [Design Tokens (Material Design 3)](https://m3.material.io/foundations/design-tokens)
- [How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/) (Addy Osmani)
- [SoulSpec](https://soulspec.org)
- Guild Hall internal: `.lore/specs/workers/worker-identity-and-personality.md` (soul/posture boundary test, REQ-WID-16)
- Guild Hall internal: `.lore/research/agent-native-applications.md` (self-modification patterns)
- Guild Hall internal: `.lore/specs/infrastructure/daemon-application-boundary.md` (target-state vision framing)
