# Vibe Garden

<img src="logo.png" align="right" width="128" height="128" alt="Vibe Garden Logo">

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Plugins](https://img.shields.io/badge/plugins-3-purple.svg)
![Research](https://img.shields.io/badge/research-active-orange.svg) ![AI Agents](https://img.shields.io/badge/AI-agents-purple.svg)

> A research and development ecosystem for AI agent design patterns, cognitive architectures, and production-ready Claude Code plugins.

Vibe Garden combines emerging AI agent theories with practical implementations: **3 production Claude Code plugins** plus comprehensive research materials on agent architectures and design patterns.

<br clear="right"/>

---

## What's Inside

### Production Claude Code Plugins

**Compass Rose** - GitHub Projects Management
- Skill-based project management integration
- Issue tracking and backlog analysis
- Work prioritization and recommendations
- **Status**: Production-ready

**Courier MCP** - Gmail Integration
- Export Gmail messages as structured markdown files
- Powerful search with full Gmail query syntax
- Concurrent fetching with rate limit handling
- OAuth 2.0 authentication
- **Status**: v1.2.0 (production-ready)

**Wyrd-Gen MCP** - AI Image Generation
- Text-to-image generation via Replicate API
- Support for multiple AI models (Flux, Stable Diffusion, etc.)
- Model parameter discovery
- File collision prevention
- **Status**: v1.1.0 (production-ready)

### Research Materials

- **30+ Agent Types** documented across 6 functional categories
- **8 Major Design Patterns** for building robust AI agent systems
- **Theoretical Foundations** from cutting-edge academic research (2018-2025)
- **Practical Examples** with real-world performance metrics

---

## Quick Start

### Installing Plugins

Install any of the Claude Code plugins:

```bash
# In Claude Code, install plugins from this repository:
/plugin install compass-rose@vibe-garden        # Project management
/plugin install courier-mcp@vibe-garden         # Gmail integration
/plugin install wyrd-gen-mcp@vibe-garden        # Image generation
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

## Agent Categories

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

## Projects

### Compass Rose - Project Management Plugin

**Purpose**: GitHub Projects integration for Claude Code

**Status**: Production Ready
**Location**: `compass-rose/`

**Features**:
- Skill-based project management
- Issue tracking and backlog analysis
- Priority recommendations
- Work item lifecycle management

[Full documentation →](compass-rose/README.md)

---

### Courier MCP - Gmail Integration

**Purpose**: Export Gmail messages as structured markdown files

**Status**: Production Ready (100% complete)
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

[Full documentation →](courier-mcp/README.md) | [Setup guide →](courier-mcp/docs/SETUP.md)

---

### Wyrd-Gen MCP - Image Generation

**Purpose**: AI-powered text-to-image generation via Replicate API

**Status**: Production Ready (100% complete)
**Version**: v1.1.0
**Location**: `wyrd-gen-mcp/`

**Features**:
- Text-to-image generation via Replicate
- Support for multiple models (Flux, Stable Diffusion, etc.)
- Model parameter discovery tool
- File collision prevention with auto-incrementing
- Dual launch scripts (1Password CLI + direct .env)

[MCP server spec →](.sdd/specs/wyrd-gen-mcp-server.md)

---

## Design Patterns

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

## Research Highlights

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

## Repository Structure

```
vibe-garden/
├── compass-rose/              # GitHub Projects management plugin
│   ├── .claude-plugin/        # Plugin metadata
│   ├── skills/                # Skill implementations
│   └── agents/                # Agent definitions
│
├── courier-mcp/               # Gmail integration MCP server
│   ├── .claude-plugin/        # Plugin metadata (v1.2.0)
│   ├── server/                # Python MCP server implementation
│   ├── docs/                  # User guides and API reference
│   └── tests/                 # Test suite (95/95 passing)
│
├── wyrd-gen-mcp/              # Image generation MCP server
│   ├── .claude-plugin/        # Plugin metadata (v1.1.0)
│   └── server/                # Python MCP server implementation
│
├── lore-development/          # Project context and workflow plugin
│   ├── .claude-plugin/        # Plugin metadata
│   ├── skills/                # Workflow skills
│   └── agents/                # Agent definitions
│
├── notify-hook/               # Desktop/mobile notification plugin
│
└── seeds/                     # Research and brainstorming
    ├── brainstorm/
    │   ├── agents/            # 30+ agent types documented
    │   └── patterns/          # 8 major design patterns
    ├── notes/                 # Academic research and theory
    └── scripts/               # Utility scripts (PDF conversion)
```

---

## Core Principles

### Agent Design Philosophy

1. **Functional Abstraction** - Define agents by computational functions, not job titles
2. **Modular Architectures** - Specialized, interacting components over monolithic systems
3. **Feedback Loops** - Enable self-reflection and iterative improvement
4. **Epistemic Delegation** - Leverage specialists for knowledge-intensive tasks
5. **Deviation Detection** - Dedicated error monitoring and quality assurance

---

## Use Cases

### For AI Researchers
- Comprehensive taxonomy of agent types and patterns (30+ documented)
- Academic references and performance metrics from 2018-2025
- Emerging theoretical models and frameworks
- Working examples of multi-agent patterns in production code

### For Claude Code Users
- **Compass Rose**: Manage GitHub Projects from Claude Code
- **Courier MCP**: Export and analyze Gmail conversations
- **Wyrd-Gen MCP**: Generate images directly from Claude Code
- All plugins integrate seamlessly with Claude's workflow

### For Developers
- Reusable agent design patterns from academic research
- Production-ready MCP server implementations
- Full test suites and documentation templates

### For Teams
- Shared vocabulary for agent architectures
- Decision frameworks for agent selection
- Reproducible development workflows

---

## Pattern Selection Guide

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

## Utilities

### PDF Converter

Convert research papers to markdown:

```bash
python seeds/scripts/convert_pdf.py <pdf_file> [output_file]
```

Preserves layout and formatting for integration with Claude Code.

---

## Documentation

- [Agent Types Index](seeds/brainstorm/agents/README.md) - Complete agent taxonomy
- [Design Patterns Guide](seeds/brainstorm/patterns/README.md) - All 8 patterns
- [Emerging Theory](seeds/notes/Emerging-Theory-for-Agents.md) - Theoretical foundations
- [Claude Code Integration](CLAUDE.md) - Guidance for Claude Code instances

---

## Evolution & Future Directions

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

## Contributing

This is a living research and development repository. Contributions welcome:

### Research Contributions
1. **New Agent Types** - Document emerging agent architectures
2. **Design Patterns** - Add proven patterns with academic citations
3. **Research Notes** - Include papers and findings (2018-2025)
4. **Real-World Examples** - Share implementation experiences

### Plugin Contributions
1. **Bug Fixes** - All plugins welcome improvements
2. **New Plugins** - Add Claude Code plugins to the ecosystem
3. **Documentation** - Enhance setup guides and tutorials

Please follow the established documentation format and include academic citations for research contributions.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Resources

### Academic Papers

All patterns and agent types reference academic research from 2018-2025. See individual documentation files for detailed citations.

### Related Projects

- [Claude Code](https://claude.ai/code) - Official Anthropic CLI

---

## Contact

**Author:** Ronald Roy
**Email:** gsdwig@gmail.com
**Repository:** [github.com/rjroy/vibe-garden](https://github.com/rjroy/vibe-garden)

---

<div align="center">

**Built with 🧠 for the future of AI agent design**

*Last Updated: 2026-01-31*

</div>
