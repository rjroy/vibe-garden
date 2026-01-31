# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**Vibe Garden** is a research and development repository focused on AI agent design patterns and cognitive architectures. The repository contains:

- **Research notes** on emerging AI agent theories and patterns
- **Agent type taxonomy** documenting 30+ agent types across 6 categories
- **Agent design patterns** (8 major patterns documented)
- **Claude Code plugins** for project management and development workflows

## Repository Structure

```
vibe-garden/
├── seeds/                       # Research materials and brainstorming
│   ├── brainstorm/
│   │   ├── agents/             # Agent type documentation (30+ types)
│   │   └── patterns/           # Agent design patterns (8 patterns)
│   ├── notes/                  # Research papers and theory
│   └── scripts/                # Utility scripts (PDF conversion, etc.)
├── compass-rose/               # GitHub Projects management plugin
├── notify-hook/                # Desktop/mobile notification plugin
└── lore-development/           # Project context and workflow plugin
```

## Key Principles

### Agent Design Philosophy

The research in this repository emphasizes:

1. **Functional abstraction over job titles** - Define agents by computational functions (planner, critic, memory manager) rather than human roles (developer, tester)

2. **Modular architectures** - Break monolithic systems into specialized, interacting components

3. **Feedback-rich loops** - Enable self-reflection, self-correction, and iterative improvement

4. **Epistemic delegation** - Delegate knowledge-intensive tasks to specialized components

5. **Deviation detection** - Include dedicated error monitoring and quality assurance mechanisms

## Working with Research Materials

### Agent Categories

Located in `seeds/brainstorm/agents/`:
- **Cognitive Planning Agents** - Planning and decision-making (MAP, Tree-of-Thoughts)
- **Memory Management Agents** - Context retention and knowledge synthesis
- **Self-Reflective Agents** - Self-critique and iterative improvement (Reflexion)
- **Multi-Agent Collaboration** - Specialized teams with orchestration
- **Software Development Agents** - Traditional SDLC agents (reference only)
- **Neural-Symbolic Integration** - Hybrid neural-symbolic systems

### Design Patterns

Located in `seeds/brainstorm/patterns/`:
- Assembly Line Pattern - Sequential specialized pipeline
- Complementary Pair Pattern - Balanced dual perspectives
- Self-Reflective Loop Pattern - Iterative refinement
- Modular Cognitive Architecture - Specialized cognitive modules
- Adversarial Debate Pattern - Truth-seeking through competition
- Epistemic Delegation Pattern - Task delegation to specialists
- Active Memory Management - Context curation and persistence
- Multi-Agent Collaboration - Cooperative specialist teams

## Utility Scripts

```bash
# Convert PDF research papers to markdown
python seeds/scripts/convert_pdf.py <pdf_file> [output_file]
```

## Package Metadata Guidelines

When creating package configuration files (pyproject.toml, package.json, setup.py, etc.):

- **Author**: Ronald Roy
- **Email**: gsdwig@gmail.com
- **Repository URLs**: Use paths under `rjroy/vibe-garden` (e.g., `https://github.com/rjroy/vibe-garden`)
- **Do NOT** use Anthropic as author or include Anthropic URLs in code artifacts
- **Commit messages**: Anthropic attribution in commit messages is acceptable

## Anti-Patterns to Avoid

- **Monolithic agents** - Prefer specialized, modular components
- **Job title analogies** - Use computational function abstractions instead

## Research Integration

When designing new agents or systems:

1. Review agent taxonomy in `seeds/brainstorm/agents/README.md`
2. Check applicable patterns in `seeds/brainstorm/patterns/README.md`
3. Reference theoretical foundations in `seeds/notes/Emerging-Theory-for-Agents.md`

## Notes

- This repository is primarily research and methodology focused
- Research materials in `seeds/` are documentation and reference
