---
title: Promoting mind-reader to a plugin
date: 2026-01-31
status: open
tags: [plugin-design, usage-analysis, hooks, cron, ml-dependencies]
modules: [mind-reader]
---

# Brainstorm: Promoting mind-reader to a Plugin

## Context

mind-reader is currently a standalone analysis tool that generates usage reports from Claude Code history. It requires manually copying `~/.claude/history.jsonl`, runs Python scripts (including BERTopic with heavy ML deps), and outputs a static USAGE_REPORT.md.

Question: Should this become a vibe-garden plugin? What form would that take?

## Ideas Explored

### Split: Lightweight Plugin + Heavy Analysis

**Lightweight plugin (no ML):**
- `/mind-reader:quick-stats` - Temporal patterns, command usage, session behavior
- `/mind-reader:projects` - Project focus distribution
- `/mind-reader:style` - Communication efficiency analysis

Runs purely from preprocessing, which is fast and dependency-free.

**Heavy analysis stays external:**
- Topic modeling remains a manual step or runs via cron
- Plugin reads pre-computed results

### Reflection Over Analysis

The value isn't the report; it's the *dialogue* about the data.

- `/mind-reader:reflect` - "What have I been working on this week?"
- `/mind-reader:patterns` - "What triggers my long sessions?"
- `/mind-reader:compare` - "How does this month differ from last?"

### Hook-Based Active Feedback (Most Promising)

Instead of retrospective reports, catch patterns *while they're happening*:

**Session behavior hooks:**
- "You've been in this session for 2 hours with 40+ prompts. Checkpoint?"
- "5 `/clear` commands in 30 minutes. Context thrashing?"
- "This is your 4th debugging session on [project] this week."

**Temporal awareness:**
- "It's 11 PM on a weeknight. You usually stop at 9."
- "Saturday deep-work window detected."

**Project patterns:**
- "You haven't touched [project] in 3 weeks. Last time you left it mid-debug."
- "New project started. Your 3-week abandonment pattern kicks in around [date]."

**Communication drift:**
- "Your prompts today average 150 chars. Your baseline is 27. Frustrated?"

### Architecture: Hook + Cron

```
~/.claude/mind-reader/
├── state.json          # Updated by cron, read by hook
├── session-log.jsonl   # Appended by hook, processed by cron
└── last-report.md      # Most recent full analysis
```

**Cron job** (runs nightly or weekly):
- Preprocesses `~/.claude/history.jsonl`
- Optionally runs BERTopic if deps are installed
- Writes `state.json` with aggregated patterns

**Hook** (runs on every prompt):
- Reads `state.json` (fast, already computed)
- Compares current session against historical patterns
- Emits nudge if threshold crossed

**Cron setup** (user-level, no sudo):
- Plugin generates `~/.claude/mind-reader/update.sh`
- Instructions: "Run `crontab -e` and add this line..."
- Or auto-detect and offer to add via `crontab -l | ... | crontab -`

### ML as Opt-in Async

```
/mind-reader:init
  → Sets up cron for lightweight preprocessing (always)
  → Asks: "Install ML dependencies for topic modeling? (~1GB, runs weekly)"
  → If yes: extends cron to run topic_model.py after preprocess
```

The hook never waits for ML. It reads whatever state exists.

## Key Insight

The report tells you what happened. The hook catches you *while it's happening*.

The `:qa` awareness from the original report is exactly the kind of thing a hook could surface:
> "You've typed `:qa` 12 times today. Vim reflexes in chat mode."

It's not actionable advice. It's a mirror.

## Open Questions

1. What thresholds feel useful vs. annoying? (Too many nudges = ignored)
2. Should nudges be suppressible? (`/mind-reader:quiet` for deep work)
3. What's the minimum viable state file? (Just enough for meaningful hooks)
4. How does the hook discover "your patterns" without running ML every time?
5. Integration with other vibe-garden plugins (compass-rose, lore-development)?

## Decisions Made

- Audience: Public vibe-garden users (system owners analyzing their own usage)
- Value proposition: Ongoing feedback, not one-time reports
- Direction: Hook-based active feedback is most compelling
- Architecture: Cron for heavy preprocessing, hooks for fast runtime checks

## Scope Reduction (Jan 31 - continued)

After further exploration, reduced to two core systems:

### 1. Temporal Anomalies

Detect when current session deviates from your historical baseline:
- Session duration vs. your average
- Time of day vs. your typical patterns
- Prompt count vs. your baseline

**Architecture:**
```
~/.claude/mind-reader/
├── baseline.json    # Updated by daily cron, read-only during sessions
└── update.sh        # Cron job: reads history.jsonl, writes baseline
```

All concurrent sessions read the same `baseline.json`. No per-session cost for baseline computation.

### 2. Sentiment/Frustration Detection

**Heuristics rejected** for this user's patterns:
- Does both short AND very long messages (length spike is noise)
- Doesn't repeat prompts
- Rapid-fire isn't the pattern (frustration is Claude spiraling, user waiting)
- Unknown frustration keywords, doesn't swear at the AI

**VADER chosen instead:**
- Lightweight sentiment analysis (~1MB, no torch)
- Runs synchronously in hook (fast enough)
- Trained on general text, but phrases like "no, I said X" or "that's not what I meant" carry negative sentiment

**Hook flow:**
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

def check_sentiment(prompt, session_state):
    score = analyzer.polarity_scores(prompt)["compound"]

    # Rolling window (last 5 prompts)
    session_state["scores"].append(score)
    session_state["scores"] = session_state["scores"][-5:]

    rolling_avg = sum(session_state["scores"]) / len(session_state["scores"])

    if rolling_avg < -0.2 and len(session_state["scores"]) >= 3:
        return "Sentiment trending negative. Everything okay?"

    return None
```

**Limitation identified:** The "Claude spiraling for 20 minutes" problem is a *dialogue* pattern, not a prompt pattern. `history.jsonl` only contains user prompts, not Claude's responses. Detecting Claude failures requires either:
- Proxy signals (long gaps between user prompts = Claude talking)
- Access to Claude's output (unclear if hooks expose this)

For v1: detect user frustration signals, not Claude failure patterns.

## BERT Clarification

BERT/BERTopic is **not necessary** for the core hook functionality. It's an enhancement that adds:
- Topic clustering ("you've been doing database debugging")
- Semantic session classification
- Topic evolution over time

The two core systems (temporal + sentiment) work without it. BERT can remain an optional offline analysis via cron for users who want deeper insights.

## Updated Architecture

```
~/.claude/mind-reader/
├── baseline.json        # Daily cron: temporal baselines from history.jsonl
├── session-state.json   # Per-session: rolling sentiment scores
└── scripts/
    ├── update-baseline.sh   # Cron job
    └── hooks/
        ├── temporal-check.py
        └── sentiment-check.py
```

## Open Questions (Revised)

1. ~~What thresholds feel useful vs. annoying?~~ → Test with real usage
2. ~~Should nudges be suppressible?~~ → Yes, but details TBD
3. ~~Minimum viable state file?~~ → baseline.json (temporal) + session-state.json (sentiment)
4. ~~How does hook discover patterns without ML?~~ → Daily cron for baseline, VADER inline for sentiment
5. **NEW:** Plugin structure - standalone `mind-reader/` plugin? Utility for other plugins? Part of existing?
6. **NEW:** How to handle the "Claude spiraling" detection gap?

## Decisions Made (Updated)

- Audience: Public vibe-garden users (system owners)
- Value: Ongoing feedback via hooks
- Scope: Two systems only - temporal anomalies + sentiment
- Sentiment: VADER (not heuristics, not LLM)
- BERT: Optional enhancement, not core
- Architecture: Daily cron for baseline, synchronous hooks for detection

## Next Steps

- Write spec for mind-reader plugin
- Define baseline.json schema
- Define session-state.json schema
- Prototype temporal hook
- Prototype sentiment hook with VADER
