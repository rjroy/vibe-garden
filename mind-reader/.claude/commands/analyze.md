---
description: Analyze Claude Code usage history and generate insights report
arguments:
  - name: history_file
    description: Path to history.jsonl (defaults to ./history.jsonl)
    required: false
---

# Claude Code Usage Analysis

Analyze the user's Claude Code usage history from `$ARGUMENTS` (or `./history.jsonl` if not specified).

## Process

1. **Preprocess**: Run `python3 preprocess.py` to split the JSONL into analysis chunks
2. **Topic Modeling**: Run `python3 topic_model.py` to discover topics with BERTopic (requires `uv sync --group ml` first)
3. **Parallel Analysis**: Launch 6 sub-agents to analyze different dimensions:
   - Temporal patterns (when do they work?)
   - Project focus (what do they build?)
   - Command patterns (how do they interact?)
   - Session behavior (how long/deep are sessions?)
   - Prompt complexity (terse vs verbose?)
   - Discovered topics (what themes emerge from BERTopic?)
3. **Synthesize**: Combine findings into `USAGE_REPORT.md`

## Agent Prompts

### Temporal Analysis
Read `analysis_chunks/temporal.json` and provide insights about peak hours, day-of-week patterns, usage trends over time, and work schedule inferences. Be specific with numbers.

### Project Analysis
Read `analysis_chunks/projects.json` and provide insights about project focus distribution, project types based on names and sample prompts, project lifecycle patterns, and focus vs switching behavior. Be specific with numbers.

### Command Analysis
Read `analysis_chunks/commands.json` and provide insights about slash command usage, file reference patterns, common short responses, and natural language communication style. Be specific with numbers.

### Session Analysis
Read `analysis_chunks/sessions.json` and provide insights about session length distribution, prompts per session, what happens in long sessions, and workflow patterns. Be specific with numbers.

### Complexity Analysis
Read `analysis_chunks/complexity.json` and provide insights about prompt length distribution, what triggers verbose prompts, technical depth (file refs, code blocks), and communication efficiency. Be specific with numbers.

### Topic Analysis
Read `analysis_chunks/topics.json` and provide insights about:
- The main topics discovered by BERTopic and what they reveal about work focus
- Topic evolution over time (how has focus shifted week-to-week?)
- Surprising or unexpected topic clusters that keywords wouldn't catch
- Representative prompts that best illustrate each major topic
Be specific with topic counts, keywords, and evolution patterns.

## Output

Generate `USAGE_REPORT.md` with sections:
- Executive Summary
- When You Work (temporal)
- What You Build (projects)
- How You Interact (commands, complexity)
- Session Behavior
- Discovered Topics (BERTopic analysis, topic evolution)
- Key Takeaways

Keep insights specific and data-driven. Include notable quotes from prompts that reveal personality or working style.
