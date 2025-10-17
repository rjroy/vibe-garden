# Vibe Garden

<img src="logo.png" align="right" width="128" height="128" alt="Vibe Garden Logo">

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Research](https://img.shields.io/badge/research-active-orange.svg)
![AI Agents](https://img.shields.io/badge/AI-agents-purple.svg) ![SDD](https://img.shields.io/badge/methodology-SDD-teal.svg)

> A research repository exploring AI agent design patterns, cognitive architectures, and Spec-Driven Development methodology.

Vibe Garden is a curated collection of emerging AI agent theories, design patterns, and a practical implementation of Spec-Driven Development (SDD) through the **Spiral Grove** Claude Code plugin.

<br clear="right"/>

---

## 🌱 What's Inside

### 📚 Research Materials

- **30+ Agent Types** documented across 6 functional categories
- **8 Major Design Patterns** for building robust AI agent systems
- **Theoretical Foundations** from cutting-edge academic research (2018-2025)
- **Practical Examples** with real-world performance metrics

### 🛠️ Spiral Grove Plugin

A Claude Code plugin that implements Spec-Driven Development:
- Structured 4-phase development workflow
- Separation of WHAT (specs) from HOW (plans) from STEPS (tasks)
- Built-in progress tracking and deviation documentation
- Seamless integration with Claude Code

---

## 🎯 Quick Start

### Using the Research

Explore agent design patterns and types:

```bash
# Agent categories and selection guide
cat seeds/brainstorm/agents/README.md

# Design patterns overview
cat seeds/brainstorm/patterns/README.md

# Theoretical foundations
cat seeds/notes/Emerging-Theory-for-Agents.md
```

### Using Spiral Grove (SDD Plugin)

Start a new feature with Spec-Driven Development:

```bash
# 1. Create specification (WHAT to build)
/spec-writing

# 2. Generate technical plan (HOW to build)
/plan-generation

# 3. Break down into tasks (STEPS to execute)
/task-breakdown

# 4. Implement with tracking
/implementation
```

---

## 📖 Agent Categories

| Category | Emoji | Focus Area | Implementation Readiness |
|----------|-------|------------|-------------------------|
| **Cognitive Planning** | 🤔 | Multi-step reasoning, planning | Custom agent design |
| **Memory Management** | 🤔 | Context retention, knowledge synthesis | Custom MCP/processor |
| **Self-Reflective** | 👍 | Self-critique, iterative improvement | Ready to implement |
| **Multi-Agent Collaboration** | 👍 | Specialized teams, orchestration | Ready to implement |
| **Software Development** | ⛔ | Traditional SDLC roles | Reference only |
| **Neural-Symbolic** | 👎 | Hybrid reasoning systems | Long-term research |

**Legend:** 👍 Ready now · 🤔 Future development · 👎 Long-term · ⛔ Avoiding

---

## 🎨 Design Patterns

### Structural Patterns
- **Assembly Line** - Sequential specialized pipeline for repeatable workflows
- **Modular Cognitive** - Specialized interacting modules for complex reasoning
- **Multi-Agent Collaboration** - Team of specialists cooperating toward common goals

### Interaction Patterns
- **Complementary Pair** - Balanced dual perspectives (e.g., tech + UX)
- **Adversarial Debate** - Truth-seeking through competitive scrutiny
- **Epistemic Delegation** - Task delegation to specialized components

### Process Patterns
- **Self-Reflective Loop** - Iterative self-critique and refinement
- **Active Memory Management** - Context curation and intelligent persistence

[See full pattern documentation →](seeds/brainstorm/patterns/README.md)

---

## 🔬 Research Highlights

### Real-World Results

| Implementation | Metric | Improvement |
|----------------|--------|-------------|
| Reflexion | Code generation accuracy | **+11%** (91% vs 80%) |
| MAP | Planning hallucinations | **Near-zero** vs many |
| Cognitive Workspace | Memory reuse | **58%** vs 0% |
| Code Review Agent | PRs reviewed/week | **1000+** at Indeed |

### Key Insights

> "We must move beyond one-shot prompt→response paradigms and equip agents with internal structure and interactions that mirror the complexities of reasoning."

The research converges on a clear trend: **architectural modularity, feedback-rich loops, and role abstraction grounded in computational functions** rather than human job titles.

---

## 🌊 Spec-Driven Development (SDD)

Spiral Grove implements a rigorous four-phase methodology:

### Phase 1: Specification
Define **WHAT** to build
- User stories and success criteria
- Functional/non-functional requirements
- Explicit constraints

### Phase 2: Planning
Design **HOW** to build it
- Technical architecture
- Decision rationale
- Integration points

### Phase 3: Task Breakdown
Create **STEPS** to execute
- Discrete, independent tasks
- Dependencies and ordering
- Acceptance criteria

### Phase 4: Implementation
Execute and **TRACK** progress
- One task at a time
- Continuous validation
- Deviation documentation

[Learn more about SDD →](.sdd/README.md)

---

## 🗂️ Repository Structure

```
vibe-garden/
├── seeds/                       # Research and brainstorming
│   ├── brainstorm/
│   │   ├── agents/             # 30+ agent types documented
│   │   └── patterns/           # 8 major design patterns
│   ├── notes/                  # Academic research and theory
│   └── scripts/                # Utility scripts
├── spiral-grove/               # SDD Claude Code plugin
│   ├── .claude-plugin/         # Plugin configuration
│   └── commands/               # SDD phase implementations
└── .sdd/                       # Active SDD artifacts
    ├── specs/                  # Feature specifications
    ├── plans/                  # Technical plans
    ├── tasks/                  # Task breakdowns
    └── progress/               # Implementation tracking
```

---

## 🧩 Core Principles

### Agent Design Philosophy

1. **Functional Abstraction** - Define agents by computational functions, not job titles
2. **Modular Architectures** - Specialized, interacting components over monolithic systems
3. **Feedback Loops** - Enable self-reflection and iterative improvement
4. **Epistemic Delegation** - Leverage specialists for knowledge-intensive tasks
5. **Deviation Detection** - Dedicated error monitoring and quality assurance

### SDD Methodology

1. **Specs Define Success** - Specification is source of truth
2. **Document Trade-offs** - Always explain WHY, not just WHAT
3. **Stay in Phase** - Complete one phase before moving to next
4. **Validate Continuously** - Map implementation to spec acceptance criteria
5. **Track Deviations** - Document when/why implementation differs

---

## 🚀 Use Cases

### For AI Researchers
- Comprehensive taxonomy of agent types and patterns
- Academic references and performance metrics
- Emerging theoretical models and frameworks

### For Developers
- Structured development methodology (SDD)
- Reusable agent design patterns
- Claude Code plugin for systematic feature development

### For Teams
- Shared vocabulary for agent architectures
- Decision frameworks for agent selection
- Documented rationale for technical choices

---

## 📊 Pattern Selection Guide

### By Project Type

**Software Development:** Assembly Line + Complementary Pair + Self-Reflective

**Research & Analysis:** Multi-Agent + Epistemic Delegation + Active Memory

**Decision Making:** Modular Cognitive + Adversarial Debate + Self-Reflective

**User-Facing Products:** Complementary Pair + Active Memory + Self-Reflective

### By Challenge

- **Hallucinations/Errors** → Epistemic Delegation, Adversarial Debate
- **Complex Multi-Step Tasks** → Modular Cognitive, Assembly Line
- **User Experience** → Complementary Pair with Empathy Agent
- **Learning from Mistakes** → Self-Reflective Loop, Active Memory
- **Long Context** → Active Memory Management
- **Coordination** → Multi-Agent with Manager/Orchestrator

---

## 🛠️ Utilities

### PDF Converter

Convert research papers to markdown:

```bash
python seeds/scripts/convert_pdf.py <pdf_file> [output_file]
```

Preserves layout and formatting for integration with Claude Code.

---

## 📚 Documentation

- [Agent Types Index](seeds/brainstorm/agents/README.md) - Complete agent taxonomy
- [Design Patterns Guide](seeds/brainstorm/patterns/README.md) - All 8 patterns
- [Emerging Theory](seeds/notes/Emerging-Theory-for-Agents.md) - Theoretical foundations
- [SDD Workflow](.sdd/README.md) - Spec-Driven Development guide
- [Claude Code Integration](CLAUDE.md) - Guidance for Claude Code instances

---

## 🌟 Evolution & Future Directions

### Trajectory

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
Self-improving agent societies  ← We are here (2024-2025)
```

### Emerging Trends

- Learned coordination strategies
- Dynamic team formation
- Hierarchical agent systems
- Agent societies and ecosystems
- Seamless human-AI collaboration
- Formal verification of agent behavior

---

## 🤝 Contributing

This is a living research repository. Contributions welcome:

1. **New Agent Types** - Document emerging agent architectures
2. **Design Patterns** - Add proven patterns with examples
3. **Research Notes** - Include academic papers and findings
4. **SDD Improvements** - Enhance the Spiral Grove plugin
5. **Real-World Examples** - Share implementation experiences

Please follow the established documentation format and include academic citations where applicable.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Resources

### Academic Papers

All patterns and agent types reference academic research from 2018-2025. See individual documentation files for detailed citations.

### Related Projects

- [Claude Code](https://claude.ai/code) - Official Anthropic CLI

---

## 📮 Contact

**Author:** Ronald Roy
**Email:** gsdwig@gmail.com
**Repository:** [github.com/rjroy/vibe-garden](https://github.com/rjroy/vibe-garden)

---

<div align="center">

**Built with 🧠 for the future of AI agent design**

*Last Updated: 2025-10-16*

</div>
