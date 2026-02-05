---
title: Agent Cognitive Architecture Patterns
date: 2025-02-01
status: active
tags: [agent-design, cognitive-architecture, multi-agent]
modules: [lore-development]
---

# Agent Cognitive Architecture Patterns

Core thesis: Design agents around computational functions (planner, critic, memory manager) rather than human job analogies (developer, tester). Modular specialized components outperform monolithic prompting.

## Patterns That Proved Out

### Modular Cognitive Architecture

Break agent cognition into specialized, interacting components:
- **Error monitor** - Catches invalid actions, prevents loops
- **State evaluator** - Assesses current position toward goal
- **Task decomposer** - Breaks complex goals into substeps
- **Action proposer** - Generates candidate next steps
- **Coordinator** - Integrates module outputs for decisions

Key finding: Individual LLMs can perform these subtasks but struggle to coordinate them in a single chain. Separate modules with explicit handoffs work better.

Reference: Modular Agentic Planner (MAP), Webb et al. 2025

### Self-Reflection Loop (Reflexion Pattern)

Agent maintains episodic memory of past actions and outcomes. After each significant action:
1. Generate natural language self-reflection on what went wrong
2. Store reflection in memory
3. Consult reflections on next attempt

This enables "learning" without weight updates by updating context instead. The pattern is now standard in agent frameworks.

Reference: Shinn et al. 2023

### Deliberative Search (Tree-of-Thoughts)

Instead of single-stream reasoning, branch into multiple possible "thoughts" at decision points:
1. Generate candidate approaches
2. Use LLM to evaluate which branches are promising
3. Expand promising branches, prune dead ends
4. Backtrack when stuck

Reintroduces classical AI search into LLM reasoning. Useful for problems requiring lookahead (puzzles, multi-step planning, constraint satisfaction).

Reference: Yao et al. 2023

### Active Memory Management

Context windows are finite. Active curation beats passive retrieval:
- **Hierarchical buffers** - Short-term scratchpad vs longer-term store
- **Task-driven optimizer** - Decides what to keep/discard based on current goal
- **Deliberate persistence** - Explicitly save insights rather than hoping RAG finds them

Key insight: Treating memory as "extended mind" (external working memory) rather than just retrieval corpus.

Reference: Cognitive Workspace, An 2025

### Multi-Agent Collaboration

Divide cognitive labor across specialized agents:
- **Manager** - Plans strategy, assigns subtasks
- **Specialists** - Domain-focused analysis (user behavior, item data, etc.)
- **Searcher** - Epistemic actions (queries external knowledge)
- **Reflector** - Monitors for errors/inconsistencies, feeds back corrections

Agents communicate in natural language. Specialization + communication handles complexity that overwhelms single agents.

## Key Concepts

**Epistemic delegation**: Delegating knowledge-intensive subtasks to specialized components rather than handling everything in one context.

**Deviation detection**: Dedicated monitoring for when reasoning goes off-track. Can be a module within an agent or a separate agent in multi-agent systems.

**Feedback loop optimization**: Agents improving via self-reflection or iterative feedback rather than one-shot generation.

## Patterns That Didn't Take Off

- **Debate paradigm** - Two agents argue, human judges. Elegant theory, no practical implementations at scale.
- **Iterated amplification** - Recursive delegation to weaker sub-agents. Academically interesting, not widely used.
- **ACT-R integration** - Bolting cognitive architecture constraints onto LLMs. Field moved toward emergent reasoning instead.

## Application

When designing agents:
1. Identify the cognitive functions needed (not job titles)
2. Consider which functions benefit from separation vs integration
3. Design explicit handoffs and feedback loops between components
4. Include deviation detection somewhere in the system
