---
title: Session analysis and hooks prior art
date: 2026-01-31
status: active
tags: [hooks, session-analysis, quantified-self, behavioral-nudges, developer-productivity]
modules: [mind-reader]
related: [.lore/brainstorm/mind-reader/mind-reader-plugin.md]
---

# Research: Session Analysis and Hooks Prior Art

## Summary

Prior art for mind-reader falls into three categories: (1) quantified-self time tracking for developers, (2) hook/middleware patterns in AI coding assistants, and (3) behavioral nudge systems. The key insight is that most tools focus on measurement and retrospective analysis, while active feedback (nudges during work) remains underexplored in the developer tooling space.

## Key Findings

### 1. Developer Time Tracking: Measurement Without Intervention

**WakaTime** pioneered "quantified self for your IDE" with automatic time tracking per project, file, branch, language, and editor. It provides dashboards, goals, and leaderboards, but focuses on awareness rather than active intervention. Users set goals, view metrics, and compete on leaderboards, but the tool doesn't nudge them in the moment.

**ActivityWatch** is the open-source equivalent, emphasizing privacy and self-hosted data. Same pattern: collect data, visualize it, let users draw their own conclusions.

**RescueTime** goes further with real-time alerts and "Distraction Nudges" (subtle prompts without workflow interruption). This is closer to what mind-reader hooks could do. RescueTime's feedback loop philosophy: "A good feedback loop tells you where you are right now, and allows you to make small changes that lead to big improvements over time."

**Gap identified**: These tools track time in applications, not conversational patterns with an AI assistant. Session length, prompt characteristics, and context-switching within Claude Code are uncharted territory.

### 2. Claude Code Hooks: Emerging Patterns

The Claude Code hooks ecosystem is still young, but creative patterns are emerging:

**Pre-prompt middleware**: Hooks that inject organizational context (security policies, coding standards, acceptance criteria) before every interaction. The pattern uses `UserPromptSubmit` to read markdown files and inject them as `additionalContext`. This keeps standards versioned and auditable.

**Safety guardrails**: `PreToolUse` hooks that block dangerous operations (mass deletions, modifying `.env`, fork bombs) or require confirmation for ambiguous cases. Three permission modes: allow, deny, ask.

**Multi-agent coordination**: Hooks that track which files are being worked on across parallel Claude instances, using Redis to prevent conflicts and enable agents to "know" what others are doing.

**Voice notifications**: Text-to-speech hooks that announce test completion and session status without requiring visual attention. This keeps developers in flow.

**Post-tool validation**: `PostToolUse` hooks that check outputs against requirements and block completion until violations are addressed, creating an iterative refinement cycle.

**Gap identified**: No examples of session-aware behavioral feedback, such as "you've been in this session for 2 hours" or "this is your 4th debugging session this week."

### 3. Behavioral Nudges and Feedback Loops

**RescueTime's approach**: Real-time alerts for time spent on specific activities. Alerts can be positive (5 hours of productive time) or negative (1 hour of distracting time). Weekly summaries track productivity scores and behavioral trends.

**Research on interruption costs**: Each distraction triggers a "23-minute reset" to refocus. RescueTime's "Focus Sessions" block distractions, and Distraction Nudges provide subtle prompts without full interruption.

**TimeAware research** (from academic literature): Ambient widgets showing productivity scores help sustain engagement with data and enhance self-awareness. Framing effects matter: how information is presented affects behavior change.

**Key principle**: Feedback loops work when they tell you where you are right now and suggest small changes. They adapt to your baseline rather than imposing fixed standards.

### 4. Developer Mood and Sentiment Analysis

**code-mood**: A CLI tool that estimates developer mood from git commit history using sentiment analysis, code churn (lines added/deleted), and commit timing (late nights, weekends). Research on 1 million commits found correlations between positive commit message sentiment and job satisfaction.

**Axify**: Tracks team morale alongside git analytics, integrating with Slack, Teams, Jira, and GitHub.

**Insight**: Temporal patterns (late nights, weekends, commit frequency) serve as proxies for developer state. This aligns with mind-reader's existing analysis of peak hours, session duration, and weekend usage.

### 5. Developer Journaling and Reflection

A parallel tradition exists in developer journaling: daily logs of what you worked on, what worked, and what you learned. Benefits include:

- Reference for solutions (searchable knowledge base)
- Performance review material (tracking accomplishments)
- Forced reflection on progress and struggles

**Stack Overflow's advice**: "Making relevant notes as you go about your tasks can help the future you. The technology industry requires continuous learning, and having a journal helps you keep track of your learnings."

**Connection to mind-reader**: The USAGE_REPORT already serves as a form of automated journal. The hook approach could prompt for reflection at natural breakpoints ("This session is ending. Anything worth noting?").

## Synthesis: What's Missing

| Capability | Existing Tools | Gap |
|------------|----------------|-----|
| Time tracking | WakaTime, ActivityWatch | Tracks apps, not AI conversation patterns |
| Behavioral nudges | RescueTime | Not integrated with AI assistants |
| Hook middleware | Claude Code hooks | No session-awareness patterns documented |
| Mood analysis | code-mood, Axify | Based on git, not conversational patterns |
| Reflection prompts | Dev journals | Manual, not automated |

**The unique opportunity**: mind-reader could combine:
1. Session-aware hooks (from the Claude ecosystem)
2. Behavioral nudges (from RescueTime's model)
3. Pattern recognition from history (from quantified-self tradition)
4. Reflection prompts (from journaling practices)

No existing tool does all four for AI coding assistants.

## Sources

### Developer Productivity Platforms
- [WakaTime - Quantified Self for Your IDE](https://wakatime.com/quantified-self-for-your-ide)
- [ActivityWatch - Open-source time tracker](https://activitywatch.net/)
- [RescueTime - Personal Productivity](https://help.rescuetime.com/article/36-personal-productivity)
- [RescueTime - Feedback Loops](https://blog.rescuetime.com/feedback-loops-your-secret-weapon-for-productivity-in-the-workplace/)
- [Gartner - Developer Productivity Insight Platforms](https://www.gartner.com/reviews/market/developer-productivity-insight-platforms)

### Claude Code Hooks
- [Mastering Claude Hooks: Building Observable AI Systems (Part 2)](https://dev.to/bredmond1019/mastering-claude-hooks-building-observable-ai-systems-part-2-2ic4)
- [Pre-Prompt Middleware with Claude Code Hooks](https://debugg.ai/resources/pre-prompt-middleware-claude-code-hooks-enforce-pm-and-coding-standards)
- [Having Fun with Claude Code Hooks](https://stacktoheap.com/blog/2025/08/03/having-fun-with-claude-code-hooks/)

### AI SDK Middleware
- [Vercel AI SDK 3.4 - Language Model Middleware](https://vercel.com/blog/ai-sdk-3-4)
- [CrewAI - LLM Call Hooks](https://docs.crewai.com/en/learn/llm-hooks)

### Mood and Sentiment Analysis
- [code-mood - Analyze Developer Mood from Git Commits](https://medium.com/@srikanthenjamoori/code-mood-a-cli-tool-to-analyze-your-developer-mood-from-git-commits-8c047776148d)
- [Exploring the Relationship Between Git Commits and Developers' Moods](https://hackernoon.com/exploring-the-relationship-between-git-commits-and-developers-moods)

### Developer Journaling
- [Stack Overflow - You should keep a developer's journal](https://stackoverflow.blog/2024/12/24/you-should-keep-a-developer-s-journal/)
- [Why Every Developer Should Keep a Daily Code Journal](https://blog.developerpurpose.com/why-every-developer-should-keep-a-daily-code-journal-fb83ab848c6)
- [Keep journals to become a better developer](https://dbader.org/blog/keep-journals-to-become-a-better-developer)

### Research
- [TimeAware: Leveraging Framing Effects to Enhance Personal Productivity (PDF)](https://terpconnect.umd.edu/~choe/download/CHI-2016-Kim-TimeAware.pdf)
- [METR - Measuring AI Impact on Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

## Notes

The METR study found an interesting counterpoint: developers using AI tools took 19% longer on tasks in their own repositories than without AI. This suggests that the relationship between AI assistance and productivity is nuanced, and self-awareness about usage patterns (what mind-reader provides) may be valuable precisely because the impact isn't always positive.

RescueTime's philosophy of adapting feedback to your baseline rather than imposing fixed standards is worth adopting. A nudge like "you're at 40 prompts, which is high for you" is more useful than "you're at 40 prompts" with no context.
