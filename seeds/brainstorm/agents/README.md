# Agent Types - Complete Index

This directory contains comprehensive documentation of AI agent types identified from research notes, organized by functional category.

## Quick Stats
- **Total Agent Types Documented:** 30+
- **Categories:** 6
- **Sources:** Academic research + industry implementations

---

## Categories

### 1. 🤔 [Cognitive Planning Agents](./cognitive-planning-agents.md)
Agents focused on planning, decision-making, and cognitive functions.

*NOTES:* This could work as just a custom agent design. I've done this with just a prompt in a GPT before.

**Agents:**
- Modular Agentic Planner (MAP) - with 6 specialized modules
- Tree-of-Thoughts (ToT) Agent

**Key Use Cases:** Multi-step reasoning, complex planning, puzzle solving

---

### 2. 🤔 [Memory Management Agents](./memory-management-agents.md)
Agents specialized in managing memory, context, and information persistence.

*NOTES:* This will require a custom MCP or even its own agent processor.

**Agents:**
- Cognitive Workspace Agent
- Memory Manager (CoALA Component)

**Key Use Cases:** Long-running conversations, context retention, knowledge synthesis

---

### 3. 👍 [Self-Reflective Agents](./self-reflective-agents.md)
Agents that critique, evaluate, and improve their own outputs.

*NOTES:*
- This could easily be setup, but its still more than a simple agent prompt. Is this an agent SDK integration? LangChain?
- This is very similiar to what I did for the Task Loop.

**Agents:**
- Reflexion Agent
- Reflector Agent

**Key Use Cases:** Code generation, debugging, quality assurance, iterative refinement

---

### 4. 👍 [Multi-Agent Collaboration Agents](./multi-agent-collaboration-agents.md)
Agents designed to work in teams with specialized roles.

*NOTES:* This is will require special orchestration.  Or at least a well defined manager agent.

**Agents:**
- Manager Agent
- Searcher Agent
- Analyst Agents (User/Item)
- Task Interpreter Agent
- Proponent Agent (Debate)
- Critic Agent (Debate)

**Key Use Cases:** Complex projects, orchestration, adversarial truth-seeking

---

### 5. ⛔ [Software Development Agents](./software-development-agents.md)
Agents specialized for software development lifecycle tasks.

*NOTES:* This is the current pattern and what I'm trying to avoid.  But its a good reference. There is still likely bits of it that are of interest. And I can see a future where a hybrid approach is used.

**Agents:**
- Requirements/Planning Agent
- Design/Architecture Agent
- Coding/Implementation Agent
- Code Review Agent
- Testing Agent
- Integration & Continuity Agent
- Documentation Agent
- Monitoring/Maintenance Agent
- User Empathy Agent

**Key Use Cases:** Full software development lifecycle, from planning to maintenance

---

### 6. 👎 [Neural-Symbolic Integration Agents](./neural-symbolic-agents.md)
Agents combining neural networks with symbolic reasoning.

*NOTES:* This is a very interesting area.  But its not something I can implement right now due to how entangled with the LLM it is.  Worth keeping an eye on.

**Agents:**
- LLM-ACTR Agent
- World Model Agent
- Epistemic Delegation Agents

**Key Use Cases:** Explainable AI, complex decision-making, precise reasoning

---

## Takeaways

### 👍 What we can/should do now:
- [Self-Reflective Agents](./self-reflective-agents.md)
- [Multi-Agent Collaboration Agents](./multi-agent-collaboration-agents.md)

Both are relatively straightforward to implement with existing tools and frameworks. They offer immediate benefits in quality assurance and complex task management.

### 🤔 What we can explore for future development:
- [Cognitive Planning Agents](./cognitive-planning-agents.md)
- [Memory Management Agents](./memory-management-agents.md)

These require more sophisticated design and integration but hold promise for enhancing reasoning and context handling.

### 👎 What to monitor for long-term innovation:
- [Neural-Symbolic Integration Agents](./neural-symbolic-agents.md)

This area is still emerging and may need significant advancements in both AI research and tooling before practical application.

### ⛔ What we are trying to avoid:
-[Software Development Agents](./software-development-agents.md)

These are too closely tied to current job roles and may not generalize well. They also risk becoming overly complex and rigid.


---

## Agent Selection Guide

### For Software Development Projects:
- **Start:** Requirements/Planning → Design/Architecture → Coding
- **Quality:** Code Review + Testing + Integration & Continuity
- **User Focus:** User Empathy Agent (throughout)
- **Maintenance:** Documentation + Monitoring/Maintenance

### For Complex Problem Solving:
- **Planning:** Modular Agentic Planner or Tree-of-Thoughts
- **Learning:** Reflexion Agent for iterative improvement
- **Memory:** Cognitive Workspace for long-context tasks

### For Multi-Agent Systems:
- **Coordination:** Manager + Task Interpreter
- **Information:** Searcher + Analyst Agents
- **Quality:** Reflector Agent
- **Truth-seeking:** Proponent + Critic (debate)

### For Explainable AI:
- **Neural-Symbolic:** LLM-ACTR or World Model
- **Delegation:** Epistemic Delegation pattern

---

## Design Principles Across All Agents

1. **Specialization** - Each agent has clear, focused responsibility
2. **Modularity** - Agents can be combined and reconfigured
3. **Communication** - Agents exchange information via structured protocols
4. **Feedback Loops** - Many agents incorporate self-improvement mechanisms
5. **Complementarity** - Different agents cover different aspects (technical vs user-centric)
6. **Human Oversight** - All systems assume human-in-the-loop for critical decisions

---

## Real-World Impact Examples

**Sourcegraph (Indeed):** Code Review Agent processes 1000+ PRs weekly, saving hundreds of hours

**ChatDev Research:** Multi-agent system with Designer, Coder, Tester agents successfully built software autonomously

**MAP Architecture:** Achieved significantly better planning with fewer hallucinations than monolithic LLM

**Reflexion:** +11% accuracy improvement on code generation tasks (91% vs 80%)

**Cognitive Workspace:** 58% memory reuse vs 0% in passive systems, 17% efficiency gains

---

## Evolution & Future Directions

The agent landscape is rapidly evolving from:
- **Single monolithic LLMs** → **Specialized modular agents**
- **Human job title analogies** → **Computational function abstractions**
- **One-shot responses** → **Iterative feedback loops**
- **Passive retrieval** → **Active memory management**
- **Pure neural** → **Neural-symbolic integration**

---

## See Also
- [Patterns Documentation](../patterns/) - How to combine and deploy these agents
- [Source Notes](../../notes/) - Original research materials
