---
title: mind-reader known limitations
date: 2026-04-25
status: approved
tags: [mind-reader, limitations, claude-code-hooks, scope]
modules: [mind-reader]
---

# mind-reader Known Limitations

## Claude-failure detection is out of scope

mind-reader sees user prompts only. `~/.claude/history.jsonl` does not contain Claude's responses, so "Claude has been talking to itself for 20 minutes" is invisible to the hook. Sentiment analysis runs on the user's text, not on the dialogue.

**Why:** this was investigated and named as a limitation, not an oversight. Detecting Claude failures would require proxy signals (long gaps between user prompts implying Claude is busy) or access to assistant output that the hook does not receive.

**How to apply:** sentiment detection is for *user* frustration, not Claude failure. Don't add checks that assume response visibility or dialogue-level pattern access. If response visibility becomes available later (new hook surface, new log fields), this is the constraint to revisit.
