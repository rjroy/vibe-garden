# Multi-Agent Collaboration Agents

## Overview
Agents designed to work in teams, with specialized roles that cooperate or compete to solve complex problems.

---

## Manager Agent

**Source:** Emerging-Theory-for-Agents.md (Wang et al., 2024 - MACRec)

**Description:** Oversees overall strategy, plans workflows, and assigns subtasks to other specialized agents.

**Key Features:**
- Strategic planning
- Task decomposition and assignment
- Workflow coordination
- Resource allocation
- High-level decision making

**Strengths:**
- Provides coherent direction to multi-agent systems
- Prevents agents from working at cross-purposes
- Optimizes task distribution

**Use Cases:**
- Complex multi-step projects
- Multi-agent orchestration
- Resource management
- Strategic planning

---

## Searcher Agent

**Source:** Emerging-Theory-for-Agents.md (MACRec)

**Description:** Performs epistemic actions by querying external knowledge sources. Specialized in information retrieval and knowledge gathering.

**Key Features:**
- External knowledge querying
- Information retrieval
- Database searches
- API interactions
- Knowledge source integration

**Strengths:**
- Brings external information into agent system
- Handles epistemic delegation
- Reduces hallucination by grounding in real data

**Use Cases:**
- Research tasks
- Fact-checking
- Data gathering
- Knowledge-intensive problem solving

---

## Analyst Agents (User/Item)

**Source:** Emerging-Theory-for-Agents.md (MACRec)

**Description:** Specialized agents that focus on understanding specific aspects like user profiles or item characteristics.

**Key Features:**
- Domain-specific analysis
- Pattern recognition in specialized data
- Profile understanding
- Characteristic extraction

**Strengths:**
- Deep expertise in specific domains
- More nuanced understanding than generalist agents
- Can focus computational resources on specific analysis types

**Use Cases:**
- Recommendation systems
- User behavior analysis
- Product analysis
- Domain-specific insights

---

## Task Interpreter Agent

**Source:** Emerging-Theory-for-Agents.md (MACRec)

**Description:** Translates high-level tasks into actionable subtasks and coordinates understanding across agents.

**Key Features:**
- Task decomposition
- Requirement interpretation
- Communication facilitation
- Subtask definition

**Strengths:**
- Ensures all agents understand objectives
- Bridges gap between high-level goals and specific actions
- Facilitates agent coordination

**Use Cases:**
- Complex task management
- Multi-agent coordination
- Requirement analysis
- Workflow planning

---

## Proponent Agent (Debate)

**Source:** Emerging-Theory-for-Agents.md (Irving et al., 2018)

**Description:** In adversarial debate systems, proposes and defends answers, attempting to convince a judge.

**Key Features:**
- Argument construction
- Answer proposal
- Persuasive reasoning
- Evidence gathering

**Strengths:**
- Forces rigorous thinking
- Must defend against criticism
- Produces well-reasoned outputs

**Use Cases:**
- AI safety via debate
- Truth-seeking
- Argument evaluation
- Decision making under uncertainty

---

## Critic Agent (Debate)

**Source:** Emerging-Theory-for-Agents.md (Irving et al., 2018)

**Description:** In adversarial debate systems, identifies flaws and counterarguments to proposed answers.

**Key Features:**
- Flaw detection
- Counterargument generation
- Critical analysis
- Error identification

**Strengths:**
- Surfaces hidden problems
- Prevents acceptance of weak arguments
- Theoretically surfaces truth through adversarial process
- Catches deceptive reasoning

**Use Cases:**
- AI safety and alignment
- Quality assurance
- Argument validation
- Truth verification

**Key Insight:** Zero-sum debate between proponent and critic can surface truth because any incorrect or deceptive argument by one agent can be highlighted by the other. Human judge decides based on arguments presented.
