# Epistemic Delegation Pattern

## Overview
Agent recognizes when it lacks knowledge or certainty and delegates that epistemic task (knowledge-related query or subtask) to a specialized component, tool, or agent better suited to handle it.

**Core Concept:** "I don't know this, but I know who/what does" - delegating knowledge tasks to specialists.

---

## Pattern Structure

```
                   Main Agent
                   Encounters
              Knowledge-Intensive Task
                       │
                       ▼
            ┌──────────┴──────────┐
            │                     │
    Recognize Need for      Delegate to
    Specialized Knowledge    Specialist
            │                     │
            │          ┌──────────┴───────────┐
            │          │                      │
            │    External Tool         Specialized Agent
            │    (Database, API,       (Knowledge Expert,
            │     Calculator, etc.)     Domain Specialist)
            │          │                      │
            │          └──────────┬───────────┘
            │                     │
            └─────────►  Integrate Result
                       Continue with Task
```

---

## Core Principle

**Agent Cognition Should Be Factorized:**
- Main agent handles open-ended reasoning and coordination
- Specialized components handle specific knowledge domains
- Each excels at what it does best
- Together they achieve more than any single component

---

## Types of Delegation

### 1. Tool Delegation
Agent recognizes need for precise computation or data access.

**Examples:**
- **Calculator** - "I need to compute 347 × 892" → Delegates to calculator
- **Database** - "What's the user's purchase history?" → Delegates to SQL query
- **Search Engine** - "Find latest documentation" → Delegates to search API
- **API** - "Get current weather" → Delegates to weather API

**Pattern:**
```
Agent: "I need factual data I don't have"
Agent: Calls appropriate tool/API
Tool: Returns precise result
Agent: Integrates into reasoning
```

---

### 2. Knowledge Agent Delegation
Agent recognizes question requires specialized domain knowledge.

**Examples:**
- **Medical Agent** - General agent delegates health questions to medical specialist
- **Legal Agent** - Legal interpretation delegated to law-trained agent
- **Scientific Agent** - Complex physics delegated to domain expert
- **Code Agent** - Programming questions delegated to coding specialist

**Pattern:**
```
Agent A: "This requires expertise in domain X"
Agent A: Delegates to Agent X (domain specialist)
Agent X: Processes with specialized knowledge
Agent X: Returns expert answer
Agent A: Continues with expert input
```

---

### 3. Reasoning System Delegation
Agent recognizes need for formal logic or symbolic reasoning.

**Examples:**
- **Theorem Prover** - Delegates mathematical proof to formal system
- **Logic Engine** - Delegates logical inference to symbolic reasoner
- **Planning Algorithm** - Delegates optimal path finding to A* algorithm
- **Constraint Solver** - Delegates optimization to SAT/SMT solver

**Pattern:**
```
Agent: "This requires formal reasoning"
Agent: Formulates problem in logical notation
Reasoner: Applies symbolic methods
Reasoner: Returns provably correct result
Agent: Translates back to natural language
```

---

### 4. Memory System Delegation
Agent recognizes need to access stored knowledge.

**Examples:**
- **Vector Database** - Delegates semantic search to embedding system
- **Knowledge Graph** - Delegates relationship queries to graph database
- **Document Store** - Delegates document retrieval to RAG system
- **Episodic Memory** - Delegates to system tracking past interactions

**Pattern:**
```
Agent: "I need to recall relevant information"
Agent: Queries memory system
Memory: Retrieves relevant chunks
Agent: Incorporates into context
```

---

## Key Characteristics

### Advantages:
- **Accuracy** - Specialists provide more reliable answers
- **Hallucination Reduction** - Grounds responses in factual data
- **Efficiency** - Leverage optimized tools for specific tasks
- **Scalability** - Easy to add new specialists
- **Clarity** - Clear separation of concerns
- **Verifiability** - Delegated results often verifiable

### Challenges:
- **Integration** - Agent must know when/how to delegate
- **Interface Design** - Tools need accessible APIs
- **Error Handling** - What if specialist fails or is unavailable?
- **Latency** - External calls add delay
- **Trust** - Agent must trust specialist outputs
- **Coverage** - Need specialists for all important domains

---

## Recognition Patterns

### How Agent Decides to Delegate:

**Pattern Recognition:**
```
"This query contains mathematical formula" → Calculator
"This asks for current information" → Web search
"This requires database lookup" → SQL query
"This needs legal interpretation" → Legal specialist
```

**Uncertainty Signals:**
```
"I'm not confident about this fact" → Knowledge base
"This requires precision I can't guarantee" → Formal tool
"This is outside my training" → Domain expert
```

**Task Analysis:**
```
"Solving this equation requires exact computation" → Symbolic math
"Finding optimal route requires graph algorithm" → Path planner
"Validating this logic requires proof" → Theorem prover
```

---

## Implementation Strategies

### 1. Tool Use (Function Calling)
```python
def agent_thinks():
    thought = "User asked for square root of 1234567"

    # Recognize need for precise calculation
    if requires_calculation(thought):
        result = tools.calculator.sqrt(1234567)
        return f"The square root is approximately {result}"
```

### 2. Agent Network
```python
class MainAgent:
    def __init__(self):
        self.specialists = {
            'medical': MedicalAgent(),
            'legal': LegalAgent(),
            'technical': TechnicalAgent()
        }

    def process(self, query):
        domain = self.classify_domain(query)
        if domain in self.specialists:
            return self.specialists[domain].answer(query)
        return self.general_answer(query)
```

### 3. Neural-Symbolic Integration
```python
# LLM recognizes symbolic task
if is_logical_problem(query):
    # Convert to logical form
    formula = llm.convert_to_logic(query)

    # Delegate to symbolic reasoner
    proof = symbolic_reasoner.prove(formula)

    # Convert back to natural language
    answer = llm.explain(proof)
```

---

## Real-World Examples

### HuggingGPT
LLM orchestrates multiple expert models:
- Image tasks → Vision models
- Audio tasks → Speech models
- Text tasks → Language models
- LLM acts as coordinator, delegating to specialists

### Toolformer
LLM learns when to call external tools:
- Recognizes "what is 347*892" → Calls calculator
- Recognizes "current weather" → Calls weather API
- Learns delegation through training

### LLM-ACTR (Neural-Symbolic)
LLM delegates decision patterns to ACT-R cognitive architecture:
- Neural network handles pattern recognition
- Symbolic system handles structured reasoning
- Hybrid achieves better performance than either alone

---

## Delegation Protocols

### Explicit Delegation
```
Agent: "I will now query the database for user information"
[Calls database]
Agent: "Based on database result..."
```

### Implicit Delegation
```
Agent internally recognizes need
Silently calls appropriate tool
Returns integrated answer
User sees seamless response
```

### Negotiated Delegation
```
Agent: "This requires specialized knowledge. Should I consult expert X?"
User: "Yes, please do"
Agent: [Consults expert]
Agent: "Expert X says..."
```

---

## Comparison to Related Patterns

| Pattern | Knowledge Source | Agent Role | Integration |
|---------|-----------------|------------|-------------|
| Epistemic Delegation | External specialists | Coordinator | Tool/Agent calls |
| Multi-Agent Collab | Other team agents | Participant | Communication |
| Self-Reflective | Agent's own analysis | Self-improver | Memory |
| Neural-Symbolic | Symbolic reasoner | Neural interface | Tight coupling |

---

## Quality Assurance

### Verification Strategies:
1. **Cross-check** - Consult multiple sources
2. **Confidence scores** - Specialists return certainty
3. **Provenance** - Track where information came from
4. **Validation** - Check specialist answers when possible
5. **Human oversight** - Critical decisions reviewed

### Error Handling:
```python
try:
    result = specialist.query(question)
    if result.confidence < threshold:
        result = fallback_method(question)
except SpecialistUnavailable:
    result = agent.best_guess(question)
    result.mark_uncertain()
```

---

## When to Use This Pattern

### Ideal For:
- Tasks requiring factual accuracy
- Domains with specialized knowledge
- Problems needing formal reasoning
- Scenarios with available tools/APIs
- Multi-domain applications

### Not Ideal For:
- Simple general knowledge queries
- Purely creative tasks
- Real-time critical paths (latency concern)
- Domains without good specialists
- Exploratory open-ended reasoning

---

## Combining with Other Patterns

### + Assembly Line
Each pipeline stage can delegate to specialists as needed.

### + Multi-Agent
Specialized agents form pool available for delegation.

### + Self-Reflective
Agent reflects on when delegation was appropriate.

### + Tree Search
At each node, delegate to specialist to evaluate options.

---

## Design Principles

### 1. Know Your Limits
Agent must recognize boundaries of its knowledge.

### 2. Know Your Resources
Maintain registry of available specialists and tools.

### 3. Clear Interfaces
Specialists must have well-defined input/output formats.

### 4. Graceful Failure
Handle specialist unavailability or errors.

### 5. Trust but Verify
Use specialist results but validate when critical.

---

## Specialist Selection Strategy

### Criteria:
1. **Domain match** - Does specialist cover this topic?
2. **Reliability** - Is specialist trustworthy?
3. **Availability** - Is specialist accessible now?
4. **Cost** - What's the resource/time cost?
5. **Precision** - Does task require specialist's accuracy?

### Decision Tree:
```
Is this in my confident knowledge?
  Yes → Answer directly
  No → Is specialist available?
    Yes → Delegate
    No → Best effort + flag uncertainty
```

---

## Key Insights

### From Research:

> "This kind of epistemic delegation harnesses the strengths of both worlds: the LLM handles open-ended pattern recognition and language interface, while the symbolic component ensures accuracy or logical validity in its domain."

> "An LLM agent that encounters a question outside its knowledge can delegate to a specialized knowledge agent (e.g. a wiki browser or a domain-specific model), then integrate the answer."

### Core Themes:
- **Division of Labor** - Each component does what it does best
- **Complementary Strengths** - Neural + symbolic > either alone
- **Epistemic Humility** - Knowing what you don't know
- **Structured Common Sense** - Factorize roles into distinct components

---

## Historical Context

### Classical AI
- Expert systems (MYCIN, DENDRAL) - Domain specialists
- Blackboard architectures - Specialist modules cooperating
- Multi-agent systems - Distributed expertise

### Modern Revival
- LLMs provide flexible interface layer
- Can coordinate specialists through natural language
- Combines classical AI structure with neural flexibility

---

## Metrics for Success

1. **Delegation Accuracy** - How often agent correctly identifies need to delegate
2. **Answer Quality** - Improvement in accuracy when using specialists
3. **Hallucination Rate** - Reduction in false information
4. **Coverage** - Percentage of queries handled appropriately
5. **Efficiency** - Cost/time vs benefit of delegation
6. **User Satisfaction** - Trust in answers increases

---

## Future Directions

- **Learned Delegation** - Agent learns when to delegate through experience
- **Dynamic Specialist Discovery** - Agent finds new tools/specialists as needed
- **Multi-hop Delegation** - Specialists can delegate to other specialists
- **Confidence Calibration** - Better uncertainty quantification
- **Specialist Recommendation** - System suggests which specialist for query
- **Automatic Tool Integration** - LLMs learn to use tools without explicit training
