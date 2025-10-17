# Modular Cognitive Architecture Pattern

## Overview
Decompose agent cognition into specialized, interacting modules each handling specific cognitive functions (memory, planning, evaluation, error monitoring, etc.) rather than using a monolithic LLM.

**Inspiration:** Human brain structure (prefrontal cortex functions), classical cognitive architectures (ACT-R), modular AI systems.

---

## Pattern Structure

```
                    ┌─────────────────┐
                    │  Coordination   │
                    │     Module      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ Memory  │         │ Planning│         │  Error  │
   │ Manager │◄───────►│ Module  │◄───────►│ Monitor │
   └─────────┘         └────┬────┘         └─────────┘
                            │
                    ┌───────┴───────┐
                    │               │
              ┌─────▼─────┐   ┌────▼─────┐
              │   State   │   │  Action  │
              │ Evaluator │   │ Proposer │
              └───────────┘   └──────────┘
```

---

## Core Principle

**Instead of:** Single LLM prompt handling everything
**Use:** Multiple specialized modules that each excel at one cognitive function

**Key Insight:** Large language models can perform many cognitive sub-tasks in isolation, but struggle to coordinate them in a single chain. By assigning each function to an "expert" module that interacts with others, overall performance dramatically improves.

---

## Common Cognitive Modules

### 1. Memory Module
**Function:** Store, retrieve, and manage information
**Capabilities:**
- Working memory (short-term context)
- Long-term memory (persistent knowledge)
- Episodic memory (past experiences)
- Memory consolidation and retrieval

### 2. Planning Module
**Function:** Generate and coordinate action plans
**Capabilities:**
- Goal decomposition
- Action sequencing
- Resource allocation
- Timeline estimation

### 3. Error/Conflict Monitor
**Function:** Detect mistakes and conflicts
**Capabilities:**
- Infeasible action detection
- Contradiction identification
- Constraint violation checking
- Dead-end recognition

### 4. State Predictor
**Function:** Predict future states
**Capabilities:**
- Outcome simulation
- Consequence prediction
- State transition modeling
- What-if analysis

### 5. State Evaluator
**Function:** Assess current/predicted states
**Capabilities:**
- Goal alignment checking
- Progress measurement
- Value assessment
- Preference ordering

### 6. Action Proposer
**Function:** Generate possible actions
**Capabilities:**
- Option generation
- Alternative exploration
- Creative solution finding
- Action parameterization

### 7. Coordination Module
**Function:** Integrate other modules
**Capabilities:**
- Module orchestration
- Information routing
- Conflict resolution
- Decision synthesis

---

## Implementation: MAP (Modular Agentic Planner)

**Source:** Webb et al., 2025 (Nature Communications)

### Architecture:
Separate LLM-based modules for:
- Error/conflict monitoring
- State prediction
- State evaluation
- Task decomposition
- Action proposal
- Central coordination

### Results:
- **Significantly better planning** than monolithic LLM
- **Fewer hallucinations** - error monitor catches invalid steps
- **No looping** - conflict monitor prevents stuck states
- **Transferable** across tasks
- **Works with smaller models** - synergy from specialized skills

### Benchmarks:
- Graph traversal: Substantial improvement
- Tower of Hanoi: Solved complex instances
- Multi-step reasoning: SOTA performance

---

## Key Characteristics

### Advantages:
- **Specialization** - Each module optimized for its function
- **Reliability** - Dedicated error checking prevents failures
- **Interpretability** - Clear which module made each decision
- **Composability** - Modules can be swapped/upgraded independently
- **Robustness** - System continues if one module struggles
- **Efficiency** - Smaller specialized models can replace large generalist

### Challenges:
- **Integration complexity** - Modules must communicate effectively
- **Coordination overhead** - Need mechanism to orchestrate
- **Module boundaries** - Deciding function divisions
- **Latency** - Multiple module calls vs single LLM pass
- **Module agreement** - What if modules disagree?

---

## Communication Patterns

### Message Passing
```
Planning Module: "Propose action: move block A to position B"
Error Monitor: "Checking... position B is occupied"
Planning Module: "Updating plan..."
```

### Shared State
```
All modules read/write to common working memory
Coordination module resolves conflicts
```

### Hierarchical
```
Coordinator queries modules sequentially
Lower modules don't communicate directly
Coordinator synthesizes responses
```

### Blackboard Architecture
```
Shared "blackboard" holds current state
Modules post updates asynchronously
Pattern-matching triggers module activation
```

---

## Example Cognitive Functions → Modules

| Cognitive Function | Module | Purpose |
|-------------------|--------|---------|
| Attention | Focus Controller | Decide what to process |
| Working Memory | Context Manager | Maintain active information |
| Long-term Memory | Knowledge Base | Store/retrieve facts |
| Planning | Task Planner | Generate action sequences |
| Monitoring | Error Detector | Catch mistakes |
| Evaluation | Goal Assessor | Judge progress |
| Execution | Action Controller | Perform actions |
| Learning | Experience Recorder | Update from feedback |

---

## Real-World Applications

### Problem Solving
```
Task: Solve complex puzzle
- Planner: Break into sub-goals
- Proposer: Suggest moves
- Predictor: Simulate outcomes
- Evaluator: Score each option
- Monitor: Reject invalid moves
- Coordinator: Select best valid move
```

### Code Generation
```
Task: Write complex function
- Planner: Outline algorithm structure
- Memory: Recall similar patterns
- Coder: Generate implementation
- Evaluator: Check logic correctness
- Monitor: Detect syntax errors
- Tester: Verify with examples
```

---

## Comparison to Monolithic LLM

| Aspect | Monolithic LLM | Modular Architecture |
|--------|---------------|---------------------|
| Complexity | Single prompt | Multiple modules |
| Error handling | Hallucinations common | Dedicated error module |
| Planning | Often gets stuck | Systematic decomposition |
| Interpretability | Black box | Clear module roles |
| Optimization | General purpose | Task-specific tuning |
| Failure mode | Total failure | Graceful degradation |

---

## Frameworks & Implementations

### CoALA (Cognitive Architectures for Language Agents)
**Source:** Sumers et al., 2024

Conceptual blueprint organizing LLM agents around:
- Modular memory components
- Internal vs external actions
- Interactive decision loop

Provides taxonomy to compare and design agents with explicit cognitive structure.

### ACT-R Integration (LLM-ACTR)
**Source:** Wu et al., 2023

Injects patterns from ACT-R cognitive architecture into LLM:
- Symbolic cognitive model generates decision traces
- LLM trained to embed these patterns
- Result: More structured, explainable reasoning

---

## Design Principles

### 1. Single Responsibility
Each module has one clear purpose.

### 2. Loose Coupling
Modules interact through well-defined interfaces.

### 3. Information Hiding
Internal module workings hidden from others.

### 4. Explicit Communication
Module interactions documented and observable.

### 5. Graceful Degradation
System functions even if modules fail.

---

## Module Selection Guide

### For Your Task, Do You Need:
- **Memory across turns?** → Memory Module
- **Multi-step planning?** → Planning Module
- **Error prevention?** → Error Monitor
- **Outcome prediction?** → State Predictor
- **Quality assessment?** → State Evaluator
- **Creative options?** → Action Proposer
- **Integration of above?** → Coordination Module

---

## When to Use This Pattern

### Ideal For:
- Complex, multi-step reasoning tasks
- Problems requiring diverse cognitive skills
- Scenarios where reliability is critical
- Tasks benefiting from specialized optimization
- Interpretable AI requirements

### Not Ideal For:
- Simple, single-shot queries
- Real-time latency-critical applications
- Tasks with unclear cognitive decomposition
- Small-scale problems (overhead exceeds benefit)

---

## Combining with Other Patterns

### + Self-Reflective
Add reflection module that critiques other modules' outputs.

### + Multi-Agent
Each module could be separate agent in multi-agent system.

### + Assembly Line
Modules arranged in pipeline rather than fully connected.

### + Memory Management
Dedicated sophisticated memory module using active curation.

---

## Historical Context

### Classical Cognitive Architectures:
- **SOAR** (1980s) - Problem-solving via problem spaces
- **ACT-R** (1990s) - Adaptive control of thought-rational
- **Sigma** (2010s) - Integrated cognitive architecture

### Modern Revival:
LLMs provide flexible "cognitive processors" that can be arranged into classical cognitive patterns, combining:
- **Symbolic AI** - Structured, interpretable, rule-based
- **Neural AI** - Flexible, learning-based, pattern-matching

---

## Key Insights

### From Research:

> "By assigning each function to an LLM-based 'expert' and having them interact, MAP yields substantially improved performance on multi-step reasoning benchmarks compared to a monolithic LLM agent."

> "Brain-inspired modular design reduced hallucinated or invalid steps (the error-monitor module catches infeasible actions) and avoided getting stuck in loops during planning."

### Core Themes:
- **Architectural Modularity** - Decompose intelligence into parts
- **Feedback-Rich Loops** - Modules provide checks on each other
- **Role Abstraction** - Functions rather than human job titles
- **Complementary Strengths** - Each module excels at its specialty

---

## Metrics for Success

1. **Task Performance** - Accuracy, success rate
2. **Error Rate** - Mistakes that escape detection
3. **Efficiency** - Computational cost vs monolithic
4. **Interpretability** - Clarity of decision-making process
5. **Robustness** - Performance under module failures
6. **Transfer** - Performance on new related tasks

---

## Future Directions

- **Learned Coordination** - Train coordinator to optimize module orchestration
- **Dynamic Modules** - Activate modules on-demand based on task
- **Hierarchical Modules** - Modules containing sub-modules
- **Shared Representations** - Modules learn common internal representations
- **Neuromorphic Implementation** - Map to specialized hardware
