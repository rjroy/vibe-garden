# AI Agent Patterns - Complete Guide

Comprehensive documentation of patterns for designing, combining, and deploying AI agents. Extracted from cutting-edge research and real-world implementations.

---

## Quick Navigation

| Pattern | Best For | Key Benefit |
|---------|----------|-------------|
| [Assembly Line](#assembly-line) | Repeatable workflows | Efficiency through specialization |
| [Complementary Pair](#complementary-pair) | User-facing products | Balances tech + UX |
| [Self-Reflective Loop](#self-reflective-loop) | Iterative refinement | Learns from mistakes |
| [Modular Cognitive](#modular-cognitive) | Complex reasoning | Specialized cognitive functions |
| [Adversarial Debate](#adversarial-debate) | High-stakes decisions | Truth through competition |
| [Epistemic Delegation](#epistemic-delegation) | Knowledge-intensive tasks | Accuracy through specialists |
| [Active Memory](#active-memory) | Long conversations | Maintains context efficiently |
| [Multi-Agent Collaboration](#multi-agent-collaboration) | Complex projects | Collective intelligence |

---

## Pattern Categories

### Structural Patterns (How to Organize)

#### [Assembly Line Multi-Agent Pattern](./assembly-line-pattern.md)
**Sequential specialized agents passing work down a pipeline**

```
Requirements → Design → Code → Review → Test → Deploy
```

**When:** Repeatable processes, high volume, clear steps
**Example:** Sourcegraph's 1000+ PR/week code review agent
**Impact:** Work that would take humans years, automated

---

#### [Modular Cognitive Architecture Pattern](./modular-cognitive-architecture-pattern.md)
**Decompose cognition into specialized interacting modules**

```
Memory + Planning + Error Monitor + Evaluator = Robust Reasoner
```

**When:** Multi-step reasoning, reliability critical
**Example:** MAP (Modular Agentic Planner) - 0 hallucinations vs many in monolithic LLM
**Impact:** Dramatically better planning, no getting stuck in loops

---

#### [Multi-Agent Collaboration Pattern](./multi-agent-collaboration-pattern.md)
**Team of specialists cooperating toward common goal**

```
Manager coordinates Analysts + Searcher + Reflector
```

**When:** Complex projects, diverse expertise needed
**Example:** MACRec (6 specialized agents for recommendations)
**Impact:** Outperforms single agents on complex tasks

---

### Interaction Patterns (How Agents Work Together)

#### [Complementary Agent Pair Pattern](./complementary-pair-pattern.md)
**Two agents with different perspectives collaborating**

```
Integration Continuity Agent ↔ User Empathy Agent
(Technical Excellence)      ↔  (User-Centric Design)
```

**When:** User-facing products, need balance
**Example:** Tech agent ensures feasibility, empathy agent ensures usability
**Impact:** Prevents both "technically perfect but awful UX" and "beautiful but unworkable"

---

#### [Adversarial Debate Pattern](./adversarial-debate-pattern.md)
**Two agents debate, judge decides truth**

```
Proponent defends ↔ Critic attacks → Judge decides
```

**When:** High-stakes decisions, truth-seeking
**Example:** AI Safety via Debate
**Impact:** Surfaces truth beyond judge's ability through competitive scrutiny

---

#### [Epistemic Delegation Pattern](./epistemic-delegation-pattern.md)
**Agent recognizes limits, delegates to specialists**

```
Main Agent: "I need precise calculation"
  → Delegates to Calculator
  → Integrates result
```

**When:** Tasks requiring factual accuracy, formal reasoning
**Example:** LLM delegates math to symbolic solver, queries to database
**Impact:** Reduces hallucinations, ensures accuracy

---

### Process Patterns (How Agents Improve)

#### [Self-Reflective Loop Pattern](./self-reflective-loop-pattern.md)
**Agent critiques and refines own outputs iteratively**

```
1. Attempt → 2. Feedback → 3. Reflect → 4. Store → 5. Retry (Better)
```

**When:** Iterative refinement, learning from failures
**Example:** Reflexion agent - 91% vs 80% on code generation
**Impact:** +11% accuracy through self-reflection, no retraining needed

---

#### [Active Memory Management Pattern](./active-memory-management-pattern.md)
**Agent actively curates memory, discards distractions**

```
Continuous: Evaluate relevance → Keep/Discard → Optimize buffer
```

**When:** Long conversations, complex multi-step tasks
**Example:** Cognitive Workspace - 58% memory reuse vs 0% in passive RAG
**Impact:** 17% efficiency gains, maintains coherence over time

---

## Thematic Patterns

### Key Themes Across Research

#### 1. Architectural Modularity
**Break monolithic systems into specialized parts**
- Modular Cognitive Architecture
- Assembly Line
- Multi-Agent Collaboration

#### 2. Feedback-Rich Loops
**Agents improve through self-critique and cross-checking**
- Self-Reflective Loop
- Adversarial Debate
- Reflector agents in teams

#### 3. Role Abstraction
**Functions not job titles**
- "Error Monitor" not "Tester"
- "State Evaluator" not "Manager"
- Cognitive functions, not human roles

#### 4. Epistemic Delegation
**Delegate knowledge tasks to specialists**
- Epistemic Delegation Pattern
- Searcher agents
- Tool use and API calling

#### 5. Deviation Detection
**Dedicated error monitoring**
- Error Monitor module
- Reflector agent
- Critic in debate

#### 6. Adaptive Planning
**Dynamic adjustment with lookahead**
- Tree-of-Thoughts
- Modular planning modules
- Self-reflective iteration

---

## Pattern Combinations

### Powerful Synergies

#### Assembly Line + Complementary Pair
```
Pipeline of stages, each monitored by Tech + Empathy pair
Result: Efficient workflow with balanced output
```

#### Modular Cognitive + Self-Reflective
```
Specialized modules, plus reflection module that improves others
Result: Robust reasoning that learns
```

#### Multi-Agent + Adversarial
```
Team includes Proponent + Critic for key decisions
Result: Collaborative yet scrutinized
```

#### Active Memory + Epistemic Delegation
```
Memory manager delegates to specialists, curates results
Result: Efficient knowledge integration
```

---

## Selection Guide

### By Project Type:

**Software Development:**
1. Assembly Line (pipeline: plan → code → test → deploy)
2. + Complementary Pair (tech + empathy oversight)
3. + Self-Reflective (iterate on bugs)

**Research & Analysis:**
1. Multi-Agent Collaboration (diverse specialists)
2. + Epistemic Delegation (query knowledge sources)
3. + Active Memory (synthesize findings)

**Decision Making:**
1. Modular Cognitive (systematic reasoning)
2. + Adversarial Debate (scrutinize options)
3. + Self-Reflective (learn from outcomes)

**User-Facing Products:**
1. Complementary Pair (tech + UX)
2. + Active Memory (remember user context)
3. + Self-Reflective (improve from feedback)

---

### By Key Challenge:

**Challenge: Hallucinations/Errors**
→ Use: Epistemic Delegation, Adversarial Debate, Modular with Error Monitor

**Challenge: Complex Multi-Step Tasks**
→ Use: Modular Cognitive, Assembly Line, Multi-Agent

**Challenge: User Experience**
→ Use: Complementary Pair (with Empathy Agent)

**Challenge: Learning from Mistakes**
→ Use: Self-Reflective Loop, Active Memory

**Challenge: Long Context**
→ Use: Active Memory Management

**Challenge: Coordination**
→ Use: Multi-Agent with Manager/Orchestrator

---

## Design Principles

### Universal Best Practices

#### 1. Specialize
Each agent/module has clear, focused responsibility

#### 2. Communicate
Structured protocols for information exchange

#### 3. Verify
Cross-check important outputs (multiple agents or modules)

#### 4. Adapt
Build in feedback loops for improvement

#### 5. Remember
Maintain relevant context efficiently

#### 6. Delegate
Recognize limits, use specialists

#### 7. Human-in-Loop
Keep humans involved for critical decisions

---

## Historical Context

### From Research:

**Classical AI → Modern LLMs → Hybrid Future**

1. **1980s-90s:** Symbolic AI, cognitive architectures (SOAR, ACT-R)
   - Structured but brittle
   - Explicit rules and reasoning

2. **2010s-20s:** Deep learning, large language models
   - Flexible but opaque
   - Pattern recognition, generation

3. **2020s+:** Neural-symbolic integration, modular agents
   - Best of both worlds
   - LLMs + structure + specialization

**Key Insight:** We're rediscovering classical AI wisdom (modularity, cognitive functions, multi-agent systems) but implementing with flexible neural components.

---

## Real-World Impact

### Documented Results:

| Implementation | Metric | Result |
|----------------|--------|--------|
| Reflexion | Code generation accuracy | +11% (91% vs 80%) |
| MAP | Planning hallucinations | Near-zero vs many |
| Cognitive Workspace | Memory reuse | 58% vs 0% |
| Code Review Agent | PRs reviewed/week | 1000+ at Indeed |
| MACRec | Complex task performance | Beat single agents |

---

## Evolution of Agent Design

### Trajectory:

```
Monolithic LLM
    ↓
Single LLM with tools
    ↓
Pipeline of specialized agents
    ↓
Modular cognitive architecture
    ↓
Multi-agent teams with diverse roles
    ↓
Self-improving agent societies
```

**We are here** ↑ (2024-2025)

---

## Common Antipatterns

### What NOT to Do:

❌ **One Agent Does Everything**
Problem: Overwhelmed, makes errors, no specialization
Solution: Use multiple specialized agents

❌ **No Error Checking**
Problem: Mistakes propagate
Solution: Dedicated error monitor or reflector agent

❌ **Passive Memory**
Problem: Context overflow, forgotten details
Solution: Active memory management

❌ **Ignoring User Perspective**
Problem: Technically sound but unusable
Solution: User empathy agent or complementary pair

❌ **No Human Oversight**
Problem: Agents make critical errors unsupervised
Solution: Human-in-loop for important decisions

❌ **Agents Can't Communicate**
Problem: Duplication, inconsistency
Solution: Structured communication protocols

---

## Implementation Checklist

### For Any Agent System:

- [ ] Define clear agent roles and responsibilities
- [ ] Establish communication protocols
- [ ] Build in error detection/correction
- [ ] Include human oversight points
- [ ] Implement feedback loops
- [ ] Manage memory/context efficiently
- [ ] Delegate to specialists when appropriate
- [ ] Monitor performance metrics
- [ ] Plan for failure modes
- [ ] Document agent behaviors

---

## Future Directions

### Emerging Trends:

1. **Learned Coordination** - Agents learn optimal collaboration strategies
2. **Dynamic Teams** - Agents form/reform based on task
3. **Hierarchical Agents** - Agents containing sub-agents
4. **Agent Societies** - Large-scale ecosystems
5. **Human-AI Teams** - Seamless human-agent collaboration
6. **Formal Verification** - Provable guarantees on agent behavior
7. **Meta-Learning** - Agents that learn how to learn
8. **Neuromorphic Implementation** - Specialized hardware for agents

---

## Key Insights Summary

### From the Research:

> **"We must move beyond one-shot prompt->response paradigms and equip agents with internal structure and interactions that mirror the complexities of reasoning."**

> **"Rethinking agent design around computational and epistemic functions is a fruitful path. By abstracting agent 'roles' to things like planner, critic, memory, or model, we tap into the intrinsic competencies of AI."**

> **"History shows industrial progress comes from humans and machines working together. Embracing that lesson, we can design AI-driven workflows to amplify human creativity and empathy, not replace it."**

---

## Resources

### Further Reading:

- **Agents Directory:** [../agents/](../agents/) - Detailed agent type documentation
- **Source Notes:** [../../notes/](../../notes/) - Original research materials
- **Academic Papers:** See citations in individual pattern files

---

## Contributing

This is a living document. As new patterns emerge from research and practice, they should be documented here using the established format:

1. Pattern name and overview
2. Structure diagram
3. Key characteristics (advantages/challenges)
4. Real-world examples
5. When to use
6. Combining with other patterns
7. Key insights

---

**Last Updated:** 2025-10-08
**Sources:** Academic research (2018-2025) + Industry implementations
**Pattern Count:** 8 major patterns documented
