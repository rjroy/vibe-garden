# Self-Reflective Loop Pattern

## Overview
Agent critiques and refines its own outputs through iterative feedback, maintaining memory of past attempts and using self-generated reflections to improve performance without model retraining.

**Core Concept:** Close the feedback loop by having the agent act as both student (generates) and teacher (critiques).

---

## Pattern Structure

```
1. Attempt Task → 2. Receive Feedback → 3. Generate Reflection
       ↑                                           ↓
       └────────── 4. Store in Memory ← ──────────┘
                          ↓
                 5. Try Again (Improved)
```

---

## Key Components

### 1. **Task Execution**
- Agent attempts to solve problem/complete task
- Generates output based on current understanding

### 2. **Feedback Collection**
- Environmental feedback (test results, error messages)
- Self-evaluation (agent judges own output)
- External validation (human/system feedback)

### 3. **Reflection Generation**
- Agent analyzes what went wrong or could improve
- Creates natural language self-critique
- Example: "I see the error, next time I should handle edge-case X"

### 4. **Memory Storage**
- Reflections stored in episodic memory
- Past actions and results catalogued
- Retrieved for future attempts

### 5. **Iterative Improvement**
- Next attempt incorporates learned lessons
- Context includes previous reflections
- Performance improves over iterations

---

## Implementation: Reflexion Framework

**Source:** Shinn et al., 2023 (Emerging-Theory-for-Agents.md)

### How It Works:

```python
# Pseudocode
episodic_memory = []

for trial in range(max_trials):
    # Attempt task with current context
    output = agent.generate(task, context=episodic_memory)

    # Execute and get feedback
    result, feedback = environment.execute(output)

    if result.success:
        break

    # Generate reflection
    reflection = agent.reflect(output, feedback, result)

    # Store in memory
    episodic_memory.append({
        'action': output,
        'result': result,
        'reflection': reflection
    })
```

### Real Performance:
- **HumanEval (code generation):** 91% success vs 80% for GPT-4 without reflection
- **+11% accuracy improvement** through self-reflection
- Learns from failures without gradient updates
- Updates context rather than weights

---

## Key Characteristics

### Advantages:
- **No retraining required** - Works with frozen models
- **Rapid learning** - Improves within single session
- **Explainable** - Reflections are human-readable
- **Failure tolerance** - Explicitly learns from mistakes
- **Transferable** - Lessons apply to similar tasks
- **Efficient** - Leverages LLM's existing reasoning ability

### Challenges:
- **Context window limits** - Too many reflections may overflow
- **Reflection quality** - Depends on agent's self-evaluation accuracy
- **Repetitive failures** - May get stuck if reflection doesn't identify root cause
- **Hallucinated lessons** - Agent might draw wrong conclusions
- **Computational cost** - Multiple attempts required

---

## Variations

### Internal Reflection (Self-Critique)
Agent evaluates its own output without external feedback.
```
Agent: [generates code]
Agent: "Reviewing my code, I notice I didn't handle null values..."
Agent: [generates improved code]
```

### External Feedback Reflection
Agent receives environmental signals and analyzes them.
```
Agent: [submits code]
System: "Test failed: NullPointerException at line 42"
Agent: "The null check is missing. Reflection: Add validation..."
Agent: [fixes code]
```

### Comparative Reflection
Agent generates multiple solutions and compares them.
```
Agent: [generates solution A]
Agent: [generates solution B]
Agent: "Solution B is better because it handles edge case..."
Agent: [adopts solution B approach]
```

---

## Applications

### Code Generation
```
1. Write function
2. Test fails
3. Reflect: "I see - forgot to handle empty list"
4. Rewrite with edge case handling
5. Tests pass
```

### Problem Solving
```
1. Attempt solution approach
2. Gets stuck/produces error
3. Reflect: "This approach doesn't work because..."
4. Try alternative approach based on reflection
5. Success
```

### Creative Writing
```
1. Draft text
2. Self-evaluate coherence, tone
3. Reflect: "Opening is weak, needs stronger hook"
4. Revise with improvements
5. Better output
```

---

## Comparison to Related Patterns

| Pattern | Feedback Source | Memory | Learning Method |
|---------|----------------|---------|-----------------|
| Self-Reflective Loop | Self + Environment | Episodic | Context updates |
| Tree-of-Thoughts | Self-evaluation | Search tree | Pruning/backtracking |
| Multi-Agent | Other agents | Shared state | Collaboration |
| Neural-Symbolic | Symbolic rules | Knowledge base | Rule guidance |

---

## Combining with Other Patterns

### + Assembly Line
Add reflection step after each pipeline stage:
```
Code → Review → Test → Reflect → Iterate
```

### + Multi-Agent
Dedicated Reflector Agent monitors others:
```
Worker agents do tasks → Reflector analyzes → Feedback to workers
```

### + Tree-of-Thoughts
Reflect on why branches failed:
```
Try branch A → Fails → Reflect on failure → Prune similar branches
```

---

## Memory Management Strategies

### Rolling Window
Keep N most recent reflections to avoid context overflow.

### Hierarchical Memory
- Short-term: Recent reflections
- Long-term: Generalized lessons

### Importance Weighting
Store most impactful reflections, discard minor ones.

### Semantic Clustering
Group similar reflections, store representative examples.

---

## Quality Assurance

### Good Reflections:
✅ Specific: "Add null check at line 42"
✅ Actionable: "Use try-catch for error handling"
✅ Causal: "Function failed because input wasn't validated"

### Poor Reflections:
❌ Vague: "Something went wrong"
❌ Non-actionable: "This is hard"
❌ Incorrect diagnosis: "API is broken" (when code has bug)

### Improving Reflection Quality:
- Prompt engineering for structured reflections
- Few-shot examples of good reflections
- Verification step: "Does this reflection identify root cause?"

---

## Real-World Example: Code Debugging

### Iteration 1:
```python
# Agent's first attempt
def process(data):
    return data.split(',')[0]

# Test: process(None)
# Result: AttributeError: 'NoneType' has no attribute 'split'

# Reflection: "Function assumes data is string but doesn't handle None.
# Next time, add input validation for None values."
```

### Iteration 2:
```python
# Agent's improved attempt (includes reflection context)
def process(data):
    if data is None:
        return None
    return data.split(',')[0]

# Test: process(None)
# Result: Success - returns None

# Test: process('')
# Result: IndexError: list index out of range

# Reflection: "Now handles None, but empty string creates empty list
# after split. Need to check if list has elements."
```

### Iteration 3:
```python
# Agent's final attempt
def process(data):
    if data is None:
        return None
    parts = data.split(',')
    return parts[0] if parts else None

# All tests pass!
```

---

## Design Principles

### 1. Structured Feedback
Provide clear, actionable feedback signals to reflect on.

### 2. Explicit Memory
Make reflections visible and accessible, not implicit.

### 3. Iteration Limits
Set max attempts to prevent infinite loops.

### 4. Reflection Prompts
Guide agent to generate useful reflections:
- "What went wrong?"
- "What can be improved?"
- "What should I do differently next time?"

### 5. Success Criteria
Clear definition of when task is complete.

---

## When to Use This Pattern

### Ideal For:
- Tasks with clear success/failure feedback
- Iterative refinement scenarios
- Learning from mistakes
- Code generation and debugging
- Problems with trial-and-error nature

### Not Ideal For:
- One-shot tasks (no iteration possible)
- Tasks without clear feedback signals
- Real-time constraints (reflection takes time)
- Tasks where mistakes are catastrophic (need to get it right first time)

---

## Metrics for Success

1. **Improvement Rate** - Performance gain per iteration
2. **Convergence Speed** - Trials needed to reach success
3. **Lesson Transfer** - Whether reflections help on new tasks
4. **Reflection Accuracy** - Do reflections identify actual issues?
5. **Final Quality** - Success rate after N iterations vs baseline

---

## Key Insights

### From Research:
> "The key innovation is leveraging the LLM's own capacity to evaluate and modify its reasoning – closing the feedback loop with textual critique, which serves as an internal guide to avoid repeating mistakes."

### Embodied Themes:
- **Feedback Loop Optimization** - Continually refining output with feedback
- **Deviation Detection** - Agent explicitly notes when outcome deviated from goal
- **Pattern-Mismatch Detection** - Noticing when current reasoning doesn't fit requirements

### The Student-Teacher Dynamic:
The agent is both:
- **Student** - Generates proposals and attempts
- **Teacher** - Critiques and guides improvement

This interplay drives learning without external training, a departure from static role-play prompts.

---

## Future Directions

- **Multi-level reflection** - Reflect on reflections
- **Cross-task learning** - Store reflections in persistent database for future sessions
- **Collaborative reflection** - Multiple agents reflect together
- **Confidence-weighted** - Weight reflections by agent's confidence in diagnosis
- **Human-in-loop** - Validate reflections before incorporating
