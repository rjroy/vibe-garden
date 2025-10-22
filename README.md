# Vibe Garden

<img src="logo.png" align="right" width="128" height="128" alt="Vibe Garden Logo">

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Plugins](https://img.shields.io/badge/plugins-3-purple.svg)
![Research](https://img.shields.io/badge/research-active-orange.svg) ![AI Agents](https://img.shields.io/badge/AI-agents-purple.svg) ![SDD](https://img.shields.io/badge/methodology-SDD-teal.svg)

> A research and development ecosystem for AI agent design patterns, cognitive architectures, and production-ready Claude Code plugins.

Vibe Garden combines emerging AI agent theories with practical implementations: **3 production Claude Code plugins** built using Spec-Driven Development (SDD) methodology, plus comprehensive research materials on agent architectures and design patterns.

<br clear="right"/>

---

## 🌱 What's Inside

### 🔌 Production Claude Code Plugins

**Spiral Grove** - Spec-Driven Development (SDD) workflow
- Structured 4-phase development: Specification → Planning → Task Breakdown → Implementation
- Parent/child hierarchies for complex projects
- Built-in validation via `/review` command
- Documentation synthesis for code-spec alignment
- **Status**: v1.0.0 (production-ready ✅)

**Courier MCP** - Gmail Integration
- Export Gmail messages as structured markdown files
- Powerful search with full Gmail query syntax
- Concurrent fetching with rate limit handling
- OAuth 2.0 authentication
- **Status**: v1.2.0 (100% complete, production-ready ✅)

**Wyrd-Gen MCP** - AI Image Generation
- Text-to-image generation via Replicate API
- Support for multiple AI models (Flux, Stable Diffusion, etc.)
- Model parameter discovery
- File collision prevention
- **Status**: v1.1.0 (production-ready ✅)

### 📚 Research Materials

- **30+ Agent Types** documented across 6 functional categories
- **8 Major Design Patterns** for building robust AI agent systems
- **Theoretical Foundations** from cutting-edge academic research (2018-2025)
- **Practical Examples** with real-world performance metrics

---

## 🎯 Quick Start

### Installing Plugins

Install any of the three Claude Code plugins:

```bash
# In Claude Code, install plugins from this repository:
/plugin install spiral-grove@vibe-garden      # SDD workflow
/plugin install courier-mcp@vibe-garden        # Gmail integration
/plugin install wyrd-gen-mcp@vibe-garden       # Image generation
```

### Using Spiral Grove (SDD Workflow)

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

# Meta-phase: Validate before progressing
/review [spec|plan|tasks|progress]
```

### Using Courier MCP (Gmail Export)

Export Gmail messages to markdown:

```
You: Export my last 10 unread emails to ~/notes/emails

Claude: [Uses courier-mcp to export messages]
✓ Exported 10 messages in 3.2 seconds
```

[Full setup guide →](courier-mcp/README.md)

### Using Wyrd-Gen MCP (Image Generation)

Generate images with AI:

```
You: Generate an image of a serene mountain landscape at sunset

Claude: [Uses wyrd-gen-mcp to generate image via Replicate]
✓ Image saved to: ./mountain-sunset.png
```

### Exploring the Research

Browse agent design patterns and types:

```bash
# Agent categories and selection guide
cat seeds/brainstorm/agents/README.md

# Design patterns overview
cat seeds/brainstorm/patterns/README.md

# Theoretical foundations
cat seeds/notes/Emerging-Theory-for-Agents.md
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

## 🚀 Projects

### Spiral Grove - SDD Plugin

**Purpose**: Structured development methodology for Claude Code projects

**Status**: ✅ Production Ready (100% complete)
**Version**: v1.0.0
**Location**: `spiral-grove/`

**Features**:
- Four-phase workflow: Specification → Planning → Tasks → Implementation
- Parent/child hierarchies for organizing complex projects
- `/review [phase]` command for validation before progression
- Documentation synthesis agent (in development)
- Spec-code drift detection (planned)

**Built Using SDD**: Yes (dogfooded - the plugin developed itself!)

[Full documentation →](spiral-grove/README.md) | [SDD Methodology →](.sdd/README.md)

---

### Courier MCP - Gmail Integration

**Purpose**: Export Gmail messages as structured markdown files

**Status**: ✅ Production Ready (100% complete)
**Version**: v1.2.0
**Location**: `courier-mcp/`

**Features**:
- Powerful Gmail search with full query syntax support
- Export up to 100 messages per request
- Markdown output with YAML frontmatter
- Concurrent fetching (20s timeout enforcement)
- Rate limit handling with exponential backoff
- Attachment metadata extraction
- Export path resolution from invocation directory
- OAuth 2.0 authentication

**Quality Metrics**:
- Test Coverage: 95/95 tests passing (100%)
- Unit Tests: 59 passing
- Acceptance Tests: 10/10 passing

**Built Using SDD**: Yes - Full spec/plan/tasks/progress tracked in `.sdd/`

[Full documentation →](courier-mcp/README.md) | [Setup guide →](courier-mcp/docs/SETUP.md)

---

### Wyrd-Gen MCP - Image Generation

**Purpose**: AI-powered text-to-image generation via Replicate API

**Status**: ✅ Production Ready (100% complete)
**Version**: v1.1.0
**Location**: `wyrd-gen-mcp/`

**Features**:
- Text-to-image generation via Replicate
- Support for multiple models (Flux, Stable Diffusion, etc.)
- Model parameter discovery tool
- File collision prevention with auto-incrementing
- Dual launch scripts (1Password CLI + direct .env)

**Built Using SDD**: Partial - Spec and plan exist, needs task breakdown

[MCP server spec →](.sdd/specs/wyrd-gen-mcp-server.md)

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
├── spiral-grove/               # Spec-Driven Development plugin
│   ├── .claude-plugin/         # Plugin metadata (v1.0.0)
│   ├── commands/               # SDD workflow commands
│   ├── agents/                 # Reusable agent definitions
│   └── docs/                   # Format specs and guides
│
├── courier-mcp/                # Gmail integration MCP server
│   ├── .claude-plugin/         # Plugin metadata (v1.2.0)
│   ├── server/                 # Python MCP server implementation
│   ├── docs/                   # User guides and API reference
│   └── tests/                  # Test suite (95/95 passing)
│
├── wyrd-gen-mcp/               # Image generation MCP server
│   ├── .claude-plugin/         # Plugin metadata (v1.1.0)
│   └── server/                # Python MCP server implementation
│
├── seeds/                      # Research and brainstorming
│   ├── brainstorm/
│   │   ├── agents/             # 30+ agent types documented
│   │   └── patterns/           # 8 major design patterns
│   ├── notes/                  # Academic research and theory
│   └── scripts/                # Utility scripts (PDF conversion)
│
└── .sdd/                       # SDD artifacts (methodology in action)
    ├── specs/                  # Feature specifications
    │   ├── spiral-grove.md     # Main SDD plugin spec (approved)
    │   ├── spiral-grove/       # Child features
    │   │   └── documentation-synthesis.md
    │   ├── courier-mcp.md      # Gmail MCP spec (approved)
    │   └── wyrd-gen-mcp-server.md
    ├── plans/                  # Technical architecture plans
    ├── tasks/                  # Task breakdowns with dependencies
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
- Comprehensive taxonomy of agent types and patterns (30+ documented)
- Academic references and performance metrics from 2018-2025
- Emerging theoretical models and frameworks
- Working examples of multi-agent patterns in production code

### For Claude Code Users
- **Spiral Grove**: Structured development with built-in validation
- **Courier MCP**: Export and analyze Gmail conversations
- **Wyrd-Gen MCP**: Generate images directly from Claude Code
- All plugins integrate seamlessly with Claude's workflow

### For Developers
- Structured development methodology (SDD) with real project examples
- Reusable agent design patterns from academic research
- Production-ready MCP server implementations
- Full test suites and documentation templates

### For Teams
- Shared vocabulary for agent architectures
- Decision frameworks for agent selection
- Documented rationale for technical choices (specs/plans in `.sdd/`)
- Reproducible development workflow via SDD methodology

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

This is a living research and development repository. Contributions welcome:

### Research Contributions
1. **New Agent Types** - Document emerging agent architectures
2. **Design Patterns** - Add proven patterns with academic citations
3. **Research Notes** - Include papers and findings (2018-2025)
4. **Real-World Examples** - Share implementation experiences

### Plugin Contributions
1. **Spiral Grove Enhancements** - Improve SDD workflow commands
2. **Bug Fixes** - All plugins welcome improvements
3. **New Plugins** - Add Claude Code plugins to the ecosystem
4. **Documentation** - Enhance setup guides and tutorials

### Development Process
- Use SDD methodology for new features (see `.sdd/README.md`)
- Follow branch naming conventions (see `CLAUDE.md`)
- Include test coverage for code contributions
- Document rationale in specs and plans

Please follow the established documentation format and include academic citations for research contributions.

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

*Last Updated: 2025-10-20*

</div>
