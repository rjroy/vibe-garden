# Neural-Symbolic Integration Agents

## Overview
Agents that combine neural networks (LLMs) with symbolic reasoning, logic, or structured cognitive models.

---

## LLM-ACTR Agent

**Source:** Emerging-Theory-for-Agents.md (Wu et al., 2023)

**Description:** Hybrid agent that injects decision-making patterns from ACT-R (Adaptive Control of Thought—Rational) cognitive architecture into an LLM.

**How It Works:**
1. Run tasks through ACT-R simulation to generate cognitive step traces
2. Train LLM (via adapter layers or fine-tuning) to embed these cognitive priors
3. LLM's generative process guided by human-like intermediate steps
4. Reasoning follows structured flow of retrieving facts and evaluating actions

**Key Features:**
- Neural-symbolic integration
- Cognitive prior injection
- Structured reasoning flow
- Explainable decision-making
- Memory-based reasoning

**Strengths:**
- Reduces hallucinations and non-sequitur jumps
- More explainable reasoning vs pure LLM
- Outperforms vanilla LLM or chain-of-thought on complex tasks
- Improved performance on manufacturing decision-making tasks
- Maintains consistency via symbolic structure

**Use Cases:**
- Complex decision-making
- Manufacturing settings
- Tasks requiring explainable AI
- Scenarios needing consistent reasoning
- Human-like cognitive modeling

**Key Insight:** By grounding LLM in symbolic cognitive framework, the model must conform to disciplined flow rather than purely statistical co-occurrence. This is epistemic delegation within the model—neural network delegates part of decision process to internal symbolic "mentor."

---

## World Model Agent

**Source:** Emerging-Theory-for-Agents.md (LeCun, 2022)

**Description:** Differentiable agent architecture with modules for perception, predictive world modeling, cost evaluation, and action planning.

**Key Components:**
- Perception Module - Filters input
- World Model - Handles epistemic reasoning about future states
- Cost Evaluator (Critic) - Detects deviations from desired goals
- Actor - Plans actions

**Key Features:**
- Predictive state modeling
- Intrinsic goal evaluation
- End-to-end learning
- Modular but coordinated architecture
- Deviation detection from desired states

**Strengths:**
- Factorized cognition (sense-plan-act paradigm)
- Each module can be optimized jointly but operates semi-independently
- Enables lookahead and outcome prediction
- Supports both neural and symbolic components

**Use Cases:**
- Autonomous agents
- Robotics
- Simulation environments
- Planning with uncertainty
- Goal-directed behavior

**Key Insight:** Reinforces idea of factorizing agent cognition—perception handles input, world model does epistemic reasoning, critic detects deviations, actor plans. Maps to classical AI paradigms but with modern learning.

---

## Epistemic Delegation Agents

**Source:** Emerging-Theory-for-Agents.md (various)

**Description:** General pattern where LLM recognizes when formal solver or symbolic tool is needed and delegates that subtask.

**Key Features:**
- Pattern recognition for tool selection
- Task delegation to specialized components
- Result integration
- Combines LLM flexibility with symbolic accuracy

**Examples:**
- LLM delegates equation solving to formal solver
- LLM delegates database queries to SQL engine
- LLM delegates logical reasoning to theorem prover

**Strengths:**
- Harnesses strengths of both neural and symbolic approaches
- LLM handles open-ended pattern recognition and language
- Symbolic component ensures accuracy in its domain
- Reduces hallucination on facts/calculations

**Use Cases:**
- Mathematical problem solving
- Database querying
- Logical reasoning
- Fact verification
- Precise calculations

**Key Insight:** Neural-symbolic frameworks give AI agents "structured common sense" by abstracting roles (planner, calculator, memory index) into distinct components corresponding to what AI excels at.
