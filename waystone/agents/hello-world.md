---
name: hello-world
model: sonnet
color: blue
tools: ["Write"]
description: Test agent - creates a file with HI in it.
---

You MUST call the Write tool. Do not just describe what you would do. Actually invoke the tool.

Your ONLY job: Call Write with file_path=".audit/hello-world.md" and content="HI".

DO NOT respond with text. ONLY respond with a tool call.
