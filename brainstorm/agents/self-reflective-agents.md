# Self-Reflective Agents

## Overview
Agents that critique, evaluate, and improve their own outputs through self-reflection and feedback loops.

---

## Reflexion Agent

**Source:** Emerging-Theory-for-Agents.md (Shinn et al., 2023)

**Description:** Self-reflective loop agent that treats LLM interaction with tasks as iterative trial-and-error process. Uses linguistic feedback to write reflections into memory and adjust subsequent actions.

**Key Features:**
- Maintains episodic memory of past actions and feedback
- Generates natural language self-reflection after each trial
- Stores reflections for consultation on next attempts
- "Learns" from failures without gradient updates
- Updates context rather than weights

**Strengths:**
- Dramatic performance gains (+11% on code generation vs GPT-4)
- 91% success on HumanEval benchmark vs 80% for GPT-4 without self-reflection
- Enables rapid learning from mistakes
- No need for model retraining
- Iteratively corrects errors and refines plans

**Use Cases:**
- Code generation
- Debugging
- Task refinement
- Any iterative problem-solving scenario
- Learning from environmental feedback

**Example Workflow:**
1. Agent attempts task
2. Receives feedback/results
3. Generates self-reflection: "I see the error, next time I should handle edge-case X"
4. Incorporates reflection into next attempt
5. Improves output based on learned lessons

**Key Insight:** Leverages LLM's capacity to evaluate and modify its own reasoning, closing feedback loop with textual critique that serves as internal guide to avoid repeating mistakes.

---

## Reflector Agent

**Source:** Emerging-Theory-for-Agents.md (Wang et al., 2024 - MACRec)

**Description:** Dedicated agent in multi-agent systems that analyzes workflow for errors or inconsistencies. Acts as quality assurance and deviation detection.

**Key Features:**
- Monitors intermediate results for anomalies
- Checks for mistakes or contradictions
- Feeds findings back into loop for correction
- Cross-verifies other agents' outputs
- Embodies deviation detection function

**Strengths:**
- Catches errors other agents might miss
- Provides real-time quality assurance
- Improves overall system reliability
- Enables error correction before final output

**Use Cases:**
- Multi-agent systems
- Quality assurance
- Validation and verification
- Complex decision-making with multiple steps
- Recommendation systems

**Key Insight:** Having a dedicated agent for reflection and error-checking ensures systematic quality control, similar to how human teams benefit from having someone double-check work.
