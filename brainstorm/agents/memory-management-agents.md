# Memory Management Agents

## Overview
Agents specialized in managing memory, context, and information persistence across interactions.

---

## Cognitive Workspace Agent

**Source:** Emerging-Theory-for-Agents.md (An, 2025)

**Description:** Active memory architecture inspired by human working memory and extended mind thesis. Actively curates and maintains external memory buffer rather than passive retrieval.

**Key Features:**
- Hierarchical "cognitive buffers" (short-term scratchpads, longer-term stores)
- Task-driven context optimizer
- Deliberate information curation and persistence
- Metacognitive control to prevent context overflow
- Decides what information to keep or discard based on current goals

**Strengths:**
- ~58% memory reuse vs 0% in standard RAG
- ~17% efficiency gains despite overhead
- Improves long-range context handling
- Addresses LLMs' tendency to forget earlier details
- More effective than passive retrieval-augmented generation

**Use Cases:**
- Long-running conversations
- Complex multi-step tasks requiring context retention
- Tasks with evolving requirements
- Information synthesis across multiple sources

**Key Insight:** Treats external memory like humans use notepads or diagrams as extensions of thought, actively managing what to remember rather than passively retrieving.

---

## Memory Manager (CoALA Component)

**Source:** Emerging-Theory-for-Agents.md (Sumers et al., 2024)

**Description:** Part of Cognitive Architectures for Language Agents (CoALA) framework. Manages modular memory components analogous to working vs. long-term memory.

**Key Features:**
- Modular memory systems
- Working memory component
- Long-term memory component
- Memory recall actions
- Integration with decision-making loop

**Strengths:**
- Provides unified framework for agent memory design
- Contextualizes modern LLM agents in broader AI history
- Emphasizes memory management as core to general intelligence

**Use Cases:**
- General-purpose language agents
- Multi-step reasoning
- Knowledge-intensive tasks
- Tasks requiring historical context

**Key Insight:** By explicitly modeling memory systems similar to cognitive architectures, agents can achieve more structured and reliable information management.
