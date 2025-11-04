# Spiral Grove Project Charter

**Version**: 1.0.0
**Created**: 2025-10-30
**Status**: Living Document

---

## About This Charter

This charter defines how Spiral Grove implements Spec-Driven Development methodology through the Claude Code plugin architecture.

**New to SDD?** Start with [SDD-FOUNDATIONS.md](./SDD-FOUNDATIONS.md) for academic background, historical context, and theoretical foundations of the methodology itself.

**This document focuses on**: Spiral Grove's specific implementation decisions, plugin architecture choices, and operational principles for building and extending this plugin.

**For practical how-to guidance**: See [SDD-QUICK-REFERENCE.md](./SDD-QUICK-REFERENCE.md) for command usage, decision trees, and checklists.

---

## Mission

Spiral Grove addresses the need for a paradigm shift in development. AI can be the tool which provides the implementation. The user can now focus on the specifications and the architecture. They can direct the implementation, but don't need to treat the implementation as the source of truth. With this paradigm shift, a bad generated implementation can just be deleted outright, and regenerated from the plan.

Spiral Grove addresses the **"vibe coding" problem** in AI-assisted development—where to have consistent results the user must focus and refine at the generated implementation level. In reality the new paradigm should have the user focusing on the specification and architecture level and not at the detailed implementation. Shifting the focus there allows the implementation be less precious. If there's something wrong with the implementation, but the specs are sound, simply start over from the plan.

**Our Mission**: Provide a structured, four-phase methodology where **specifications serve as the source of truth** for AI-assisted development, enabling predictable, validatable, and coherent outcomes through explicit requirements, living documents, and phase-gated validation.

---

## Core Pillars

### 1. Specifications as Source of Truth

If the specification is the source of truth then everyone on the team can understand what the system does. There is no more "let me check what was actually implemented". The implementation can just be re-generated.

---

### 2. Explicit Over Implicit Knowledge

Defining all requirements, constraints, and assumptions within the documentation disambiguates what the system does and what the AI needs to implement. If the AI needs to answer a design or architecture question then it needs to be documented.

---

### 3. Living Documents with Phase-Gated Evolution

Each phase of the documentation process is scoped: specification (WHAT), plan (HOW), task breakdown (STEPS), and implementation (BUILD). This constrains the problem space allowing for documentation to be focused and concise. As the scope changes through the phases of the system, the questions and answers can reveal changes that need to be made to previous scopes. Each of the documents is living long after the implementation is complete.

---

### 4. Delegation Over Inline Execution

Context engineering is one of the most important benefits a plugin can provide the user. This is done by controlling the scope of each of the types of prompts involved.

**User requests**: The user initiates a command to enter a phase.
**Commands orchestrate**: Commands manage the steps of a phase and communicate to the user, agents, and skills as needed.
**Agents do discrete work**: Agents provide context isolation to keep the main context concise. This is especially useful when mass documentation is needed for say 100+ modules. They also provide a fresh look at the problem when a validation step is needed.
**Skills serve resources**: Skills are a new feature which interacts nicely with plugins. These allow us to keep reference documentation out of the command prompts. They also allow us to hard code scripts when that allows us to have consistent implementation.

---

### 5. Composability

Each tool within the plugin should be written concisely and allowed to be used in different contexts. Agents invoke commands, commands spawn agents, and both use skills as reference material. This composability enables reuse and consistency across workflows.


---

## Design Philosophy

These principles guide architectural decisions and emerged from v2.0.0 implementation:

### 1. Templates = Scaffolding, Not Documentation

Templates provide consistency in structure not in detail. By leaving the templates as just structure this allows for variation by the LLM. It also allows for improvements in the LLM to improve the results.

---

### 2. Validate Continuously with Fresh Eyes

If peer reviews are good then agents should do them. Using sub-agents allows the agents to have a peer without needing to go to a fully external resource because sub-agents have their own context.

---

### 3. T-Shirt Sizes Over Time Estimates

AI is trained on existing data. Time estimates are based on human development times. This doesn't translate to what the actual development time will be for the AI. Using T-Shirt sizes allows the user to have a glimpse into how complicated the AI thinks the problem is.

---

### 4. Declarative Requirements (WHAT, Not HOW)

Each phase is scoped and the prompts for the command tell the AI this. The specification is WHAT not HOW. The plan contains HOW and WHY, but not details. This scope constraint allows the AI to specialize and focus. There is a lot of reason why this is important for the LLM, but it also helps to keep the documentation clearer. Constraint is a good thing.

---

### 5. Document Trade-offs with Rationale

Knowing why a task needs to be done a certain way is as helpful to an LLM as it is a human. It'll help the AI get to the proper implementation. All decisions need to be documented. This will also help if the implementation needs to be scrapped.

---

### 6. Track Discoveries and Changes

If it wasn't clear, decisions made during any phase of the process that might lead to revisiting previous phases need to be documented. This is an extension of "documenting trade-offs with rationale". This includes changes as well as newly discovered requirements.

---

### 7. Stay in Phase

Each phase is scoped. Complete a phase before revisiting other phases. Note open questions, discoveries, and changes. Then `/spiral-grove:review` the phase and decide how this impacts the current or previous phases.


---

### 8. Commands ARE Orchestrators

The main entry point into this system are the commands. These commands can and should be the orchestrators, not skills or agents. This is primarily a user driven system and needs to stay that way.


---

## Boundaries: What Spiral Grove Is NOT

Understanding what we're **not** building is as important as what we are:

- ❌ **Not Waterfall**: Rerunning past phases should be allowed and encouraged. Real world development doesn't go in a straight line.
- ❌ **Not Formal Methods**: This is not a "provable" methodology. There are gaps to allow for both user and AI inspiration and growth.
- ❌ **Not Anti-Agile**: This is a tool for working with AI not to replace project management.
- ❌ **Not a Replacement for Testing**: This improves consistency not fixes it. The specs help define what the tests should test for but doesn't replace them.
- ❌ **Not for Simple Tasks**: Each document adds context. The more context the larger the final output. Using this for simple tasks will lead the AI to over engineer.
- ❌ **Not About Automation**: This is not about replacing the human, but about placing them in the right point of the development process.

---

## The Two-Minute Pitch

**Spiral Grove shifts where you spend your energy in AI-assisted development.** Instead of refining generated code line-by-line, you focus on specifications and architecture. When implementation goes wrong but the specs are sound, just regenerate from the plan. The methodology uses four phases—spec, plan, tasks, implementation—where documentation serves double duty: it instructs the AI and clarifies understanding for everyone on the team. AI agents validate each other's work through peer review. Commands orchestrate, agents execute, and skills provide resources. The result? Choices that work well for humans work well for AI too, and context stays manageable throughout.

---

## Using This Charter

### For Architectural Decisions

Ask: "Does this align with our core pillars? Which design philosophy principle applies?"

When considering changes to plugin architecture, check alignment with:
- Pillar 4 (Delegation): Commands orchestrate, agents execute discrete work, skills provide resources
- Principle 8 (Commands ARE Orchestrators): User-driven entry points that coordinate workflows
- Principle 2 (Fresh Eyes): Agent delegation enables peer review with fresh context

---

### For Feature Design

Filter through boundaries: "Is this Spiral Grove's responsibility?"

When evaluating feature requests, apply the boundaries test:
- Check against "Not About Automation" - human judgment drives decisions
- Check against "Not a Replacement for Testing" - specs define test requirements, don't replace them
- Check against plugin scope - does this belong in SDD methodology or elsewhere?

---

### For Onboarding Contributors

**Reading Path**: Mission → Core Pillars → Boundaries → Design Philosophy

**After reading**: Ask Claude any questions about Spiral Grove implementation details, technical approaches, or workflow specifics. The `spiral-grove-guide` skill loads these reference documents (including this CHARTER) to provide informed answers grounded in the project's philosophy and decisions.

---

### For Evolving the Charter

This is a living document. Update when:
- New architectural principles emerge from implementation
- Boundaries need clarification based on user feedback

Process: Propose change → Review against existing pillars → Update with rationale → Bump version

---

## Document History

**Version**: 1.0.0
**Created**: 2025-10-30
**Author**: Ronald Roy <gsdwig@gmail.com>
**Based On**: Spiral Grove v2.0.0 refactor (spec, plan, tasks, progress with 9 discoveries) + SDD-FOUNDATIONS.md analysis
**Status**: Approved

**Next Review**: After v2.1.0 or significant architectural changes

---

**End of Charter**
