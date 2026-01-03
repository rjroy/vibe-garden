# Claude Code Usage Analysis

**Period**: September 30, 2025 - January 2, 2026 (94 days)
**Total Interactions**: 6,025 prompts
**Sessions Tracked**: 820

---

## Executive Summary

You're a senior engineering manager with 20+ years experience who uses Claude Code as both a technical pair programmer and organizational thinking partner. Your usage reveals a disciplined, evening-focused developer who works intensely on weekends, manages context deliberately, and communicates with remarkable terseness during active work.

---

## When You Work

**Peak Hours**: 6-8 PM dominates, with hour 19 (7 PM) seeing the highest activity (778 entries). A secondary peak occurs 8-10 AM (400-465 entries). Activity drops sharply after 9 PM and is minimal overnight.

**Day of Week**: Surprisingly, Saturday leads with 1,173 entries (19%), followed by Sunday (982). Weekend usage exceeds weekday by 35%. Friday trails at 622.

**Notable Spike**: October 18 saw 469 entries in a single day, your busiest session ever.

**Interpretation**: You're an evening-focused developer with disciplined sleep habits (6 AM start, 10 PM cutoff). The heavy weekend usage suggests personal projects or flexible work arrangements. Low mid-afternoon activity (2-3 PM) indicates breaks or meetings.

---

## What You Build

### Top Projects (77% of usage)
| Project | Entries | Description |
|---------|---------|-------------|
| rowan-wyrd | 989 | Personal branding, logo generation, plugin development |
| pi-controller | 975 | Raspberry Pi remote management for home dashboard |
| adventure-engine-corvran | 914 | Claude Code plugin for tabletop RPG adventures |
| vibe-garden | 891 | Spec-driven development (SDD) methodology tooling |
| wyrd-gateway | 424 | Plugin marketplace (music/story/judgment engines) |

### Work Categories
- **AI Tooling** (45%): Claude Code plugins, SDD workflows, agent development
- **Creative Tools** (25%): RPG engines, story/music generators, image generation
- **Home Automation** (15%): Pi dashboard, gallery displays
- **Personal Knowledge** (15%): Obsidian vaults, second-brain systems

### Project Lifecycle
Most projects span 2-3 months. Some show short intense bursts (shelf-judge: 14 hours, bad-idea: 2 hours). Multiple worktrees (feat-24, feat-26) on memory-loop indicate disciplined branch-based development.

---

## How You Interact

### Command Style
- `/clear` dominates at 892 uses (34% of slash commands), showing deliberate context management
- Heavy plugin development: `/plugin` (478), `/mcp` (219)
- SDD workflow deeply integrated: implementation (96), task-breakdown (73), plan-generation (72), spec-writing (65), review (21)
- Git operations delegated to Claude: "branch + PR" (63), "commit" (40)

### Communication Efficiency
Your prompts are remarkably terse:
- Median: 27 characters
- 37% are tiny (<10 chars): "y", "doit", "continue"
- 3% are very long (500+): log dumps or specifications

You rely on Claude's file-reading rather than pasting code (only 37 prompts with code blocks). When verbose, you paste raw console output (longest: 19,821 chars of debug logs).

### Working Style
Directive and iterative. Prompts include mid-stream corrections ("stop... you're making stuff up"), pivots ("okay you've messed this all up"), and context dumps. You think out loud and expect Claude to keep up without hand-holding.

---

## Session Behavior

- Average: 4.8 prompts per session, 41.6 minutes
- 72% of sessions have 5 or fewer prompts (quick tasks)
- Only 3% exceed 15 prompts (deep work)

**Long sessions involve**:
- Debugging complex integration issues (WebSocket, Safari quirks)
- Iterative creative work (theme systems, lyrics workflows)
- The longest prompt-dense session: 835 minutes, 56 prompts (15 min average between interactions, contemplative debugging)

---

## Themes & Patterns

### Recurring Topics
1. **Pi Dashboard**: Flask, SQLite, Fortnite metrics (think mini fortnite.gg), weather, AQI, news feeds
2. **Knowledge Management**: Obsidian, PARA methodology, note-taking friction

### Notable Self-Insights from Your Prompts
- "I don't suffer fools and people shouldn't suffer me when I'm being one"
- "In my experience if you don't at least try to put timelines on things nothing happens"
- "These are current problems, assume we get past this"

### Vim Muscle Memory
`:wqa` (3) and `:qa` (2) appear in your prompts.

---

## Key Takeaways

1. **You're a power user**: 892 context clears, heavy slash command usage, custom plugin ecosystem
2. **Weekend warrior**: 35% more usage on weekends than weekdays
3. **Terse communicator**: 27-char median, verbose only for context dumps
4. **Deliberate context management**: Frequent clears suggest methodical resets between work streams
5. **Trust in Claude**: Git operations, file reading, and creative work delegated freely
6. **Deep work capable**: Extended debugging sessions spanning hours with focused interaction

---

*Generated: 2026-01-02*
