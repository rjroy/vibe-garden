# Claude Code Usage Report

**Analysis Period**: September 30, 2025 - January 3, 2026 (95 days)
**Total Interactions**: 6,169 prompts across 858 sessions
**Topics Discovered**: 69 (via BERTopic)

---

## Executive Summary

This analysis reveals a developer with a distinctive bimodal work pattern: highly productive mornings and evenings, with weekend deep-work sessions driving nearly 40% of total activity. The work spans professional development (Claude Agent SDK, EOS SDK) and an ambitious creative portfolio including music production, tabletop RPG engines, and interactive fiction.

Key characteristics:
- **Weekend warrior**: Saturday alone accounts for 21% of all activity
- **Methodology-driven**: Heavy investment in Spec-Driven Development (327 SDD commands)
- **AI skeptic**: Systematic auditing of Copilot PR suggestions rather than blind acceptance
- **Terse communicator**: 63% of prompts under 50 characters, median just 27 chars
- **Context-conscious**: `/clear` is the most-used command (895 times, 32.5% of all commands)

---

## When You Work

### Daily Rhythm

The data reveals a clear bimodal work pattern with two distinct productive windows:

| Time Block | Activity Share | Peak Hour |
|------------|---------------|-----------|
| Morning (06:00-12:00) | 35.1% | 08:00 |
| Midday (12:00-17:00) | 22.2% | --- |
| Evening (17:00-21:00) | 42.7% | **19:00 (13.1%)** |

**Peak hour is 7 PM**, with the 6-8 PM window representing a third of all activity. Morning activity starts as early as 5-6 AM, suggesting an early riser who codes before the traditional workday.

### Weekly Pattern

| Day | Share | vs Average |
|-----|-------|------------|
| **Saturday** | **21.2%** | **+48.6%** |
| Sunday | 15.9% | +11.5% |
| Monday | 15.5% | +8.4% |
| Thursday | 13.1% | -8.3% |
| Tuesday | 12.0% | -15.6% |
| Wednesday | 12.0% | -15.8% |
| Friday | 10.2% | -28.5% |

**Saturday is nearly twice as active as Friday**. Weekend activity (37.1% total) suggests Claude Code is primarily used for personal/side projects rather than day-job work.

### Usage Trends

Activity peaked in Week 41 (1,068 prompts), dipped mid-November (Week 45: 165 prompts), then surged again in December. Holiday week (W52) showed a dip, with a new-year recovery in Week 0, 2026.

---

## What You Build

### Project Focus Distribution

Four projects account for nearly two-thirds of all activity:

| Project | Count | Share | Type |
|---------|-------|-------|------|
| rowan-wyrd | 989 | 16.9% | Creative/Media Management |
| pi-controller | 975 | 16.7% | IoT/Raspberry Pi |
| adventure-engine-corvran | 914 | 15.7% | Interactive Fiction |
| vibe-garden | 904 | 15.5% | AI Research/SDD |

**61 total projects** were touched, but the top 4 represent 64.8% of activity. 38 projects had fewer than 10 interactions, including many git feature branches (feat-24, feat-26, etc.).

### Project Categories

| Category | Projects | Key Examples |
|----------|----------|--------------|
| AI/ML Development | 9 | vibe-garden, investigator, waystone |
| Creative/Media | 8 | rowan-wyrd, wyrd-gen, music-engine-rowan |
| Interactive Fiction | 7 | adventure-engine-corvran, virelan, kaels-story |
| IoT/Hardware | 3 | pi-controller, pi-gallery |
| Knowledge Management | 6 | memory-loop, second-brain |

### Lifecycle Patterns

**Long-running active**: vibe-garden (88 days, still active)
**Intensive bursts**: shelf-judge (64 interactions in 1 day)
**Rapid development**: adventure-engine-corvran averaged 61 prompts/day during active development

---

## How You Interact

### Command Usage

| Command | Count | Share |
|---------|-------|-------|
| `/clear` | 895 | 32.5% |
| `/plugin` | 488 | 17.7% |
| `/mcp` | 219 | 8.0% |
| `/compact` | 139 | 5.0% |
| `/compass-rose:start-work` | 120 | 4.4% |

**Context management dominates**: `/clear` + `/compact` represent 37.5% of all commands, indicating active management of conversation context.

### SDD Methodology Adoption

All four Spiral Grove phases see consistent use:
- `/spiral-grove:implementation`: 96
- `/spiral-grove:task-breakdown`: 73
- `/spiral-grove:plan-generation`: 72
- `/spiral-grove:spec-writing`: 65
- `/spiral-grove:review`: 21

**Total: 327 SDD commands** representing systematic methodology adoption.

### Communication Efficiency

| Metric | Value |
|--------|-------|
| Median prompt length | 27 characters |
| Average prompt length | 94 characters |
| Under 50 characters | 63.3% |
| Over 500 characters | 2.5% |

**Highly efficient communication style**: Most interactions are terse commands or confirmations. Verbose prompts (2.5%) typically involve pasting logs for debugging or detailed requirements.

### Short Response Patterns

| Response | Count | Context |
|----------|-------|---------|
| "branch + PR" | 63 | Git workflow |
| "1" (menu selection) | 48 | Option picking |
| "commit" | 40 | Git workflow |
| "doit" | 26 | Confirmation |
| "please" | 25 | Polite confirmation |

**47.9% of short responses are git-related** (branch, commit, PR). The distinctive "doit" (26 uses) and vim-style `:qa` commands reveal terminal muscle memory.

---

## Session Behavior

### Session Distribution

| Session Size | Count | Share |
|--------------|-------|-------|
| Quick (1-5 prompts) | 627 | 73.1% |
| Working (6-15 prompts) | 203 | 23.7% |
| Deep (16-30 prompts) | 25 | 2.9% |
| Marathon (31+ prompts) | 3 | 0.3% |

**Average session**: 4.7 prompts, 41 minutes
**Longest session**: 56 prompts over 14 hours (debugging wyrd-gateway)

### What Triggers Long Sessions

Analysis of the 5 longest sessions reveals consistent patterns:

1. **Implementation debugging** (wyrd-gateway, 56 prompts, 14 hours): Started with `/spiral-grove:implementation`, hit real-time issues, spent hours on logging and server behavior.

2. **Plugin creation with scope negotiation** (waystone, 53 prompts, 13 hours): Iterative design refinement, scope creep identification, requirements negotiation.

3. **Test debugging and knowledge capture** (pi-controller, 37 prompts, 3 hours): "wait... if it passes in isolation, why is that?" followed by meta-reflection.

4. **Cross-browser debugging** (adventure-engine-corvran, 27 prompts, 11 hours): Hours on Safari-specific WebSocket issues.

### Workflow Patterns

- **Command-driven starts**: Many sessions begin with slash commands (`/spiral-grove:implementation`, `/compass-rose:start-work`)
- **Debugging escalation**: Long sessions follow hit issue -> add logging -> iterate pattern
- **Context cycling**: Repeated `/clear` commands in extended sessions

---

## Discovered Topics

BERTopic identified **69 distinct topic clusters** from 2,683 meaningful prompts.

### Major Topic Categories

| Topic | Count | Focus |
|-------|-------|-------|
| Spec-Driven Development | 94 | SDD methodology refinement |
| Claude Agent SDK | 87 | Professional SDK work |
| Frontend TSX | 74 | React component development |
| Git Workflow | 67 | Commits, branches, PRs |
| Pi Dashboard | 61 | News/research dashboard |
| Testing Strategy | 61 | Unit tests, coverage |
| UI Styling (Nord) | 49 | Color schemes, buttons |
| Database Debugging | 48 | SQLite corruption issues |

### Topic Evolution Over Time

**October (W40-43)**: Database debugging, Claude Agent SDK, Courier MCP development, SDD methodology heavy use

**November (W44-47)**: Ruff linting focus, Python services architecture, pre-commit hooks, story writing begins

**December (W48-51)**: **Major creative pivot**: Christmas music production (23 prompts Week 48), adventure engine development, Daggerheart RPG system, cover art generation

**January 2026 (W0)**: Frontend work, Claude Agent SDK resurgence, Copilot auditing

### Surprising Discoveries

1. **Christmas Music Production Pipeline**: An unexpected workflow emerged around Christmas songs in the fictional world of "Valdris", with Suno AI integration, MIDI analysis, and cover art generation.

2. **Tabletop RPG Engine**: Full implementation of Daggerheart system, D20 rules, GM AI state management, and adventure world persistence.

3. **GitHub Copilot Skepticism**: 58+ prompts about "copilot reviewed, audit and validate comments" showing systematic skepticism toward AI-generated PR feedback.

4. **SQLite Corruption Debugging**: 48 prompts concentrated in weeks 40-42 about B-tree page corruption on Raspberry Pi, a persistent infrastructure pain point.

---

## Key Takeaways

1. **Dual Professional/Creative Focus**: Work spans professional SDK development (on-call incident tooling) and ambitious creative projects (music, games, fiction). The December creative sprint shows significant investment in non-work projects.

2. **Methodology Matters**: Heavy investment in Spec-Driven Development (327 commands) and disciplined workflows (feature branches, PR reviews, pre-commit hooks). The SDD topic alone represents the largest single cluster.

3. **AI Tools with Skepticism**: Uses AI extensively but maintains healthy skepticism. The Copilot audit pattern (58+ prompts) demonstrates critical evaluation rather than blind acceptance.

4. **Efficient Communication Style**: Most interactions are short (median 27 chars) with context dumps reserved for debugging. High use of `/clear` shows active context management.

5. **Weekend Deep Work**: Saturday/Sunday account for 37% of activity. Complex debugging sessions and creative work happen on weekends when extended focus time is available.

6. **Infrastructure Pain Points**: Database corruption and deployment scripts represent recurring friction. Long debugging sessions (10+ hours) often involve environmental/tooling issues.

7. **Claude Code Plugin Ecosystem Builder**: Multiple Claude Code plugins in development: Spiral Grove, Compass Rose, Courier MCP, Wyrd-Gen MCP, Adventure Engine Corvran. This represents significant investment in extending Claude Code's capabilities.

---

*Report generated January 3, 2026*
*Analysis powered by BERTopic (all-MiniLM-L6-v2 embeddings)*
