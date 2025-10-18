---
title: "Subagents"
source: "https://docs.claude.com/en/docs/claude-code/sub-agents"
author:
  - "[[Claude Docs]]"
published:
created: 2025-10-18
description: "Create and use specialized AI subagents in Claude Code for task-specific workflows and improved context management."
tags:
  - "clippings"
---
Custom subagents in Claude Code are specialized AI assistants that can be invoked to handle specific types of tasks. They enable more efficient problem-solving by providing task-specific configurations with customized system prompts, tools and a separate context window.

## What are subagents?

Subagents are pre-configured AI personalities that Claude Code can delegate tasks to. Each subagent:
- Has a specific purpose and expertise area
- Uses its own context window separate from the main conversation
- Can be configured with specific tools it’s allowed to use
- Includes a custom system prompt that guides its behavior
When Claude Code encounters a task that matches a subagent’s expertise, it can delegate that task to the specialized subagent, which works independently and returns results.

## Key benefits

## Quick start

To create your first subagent:

## Subagent configuration

### File locations

Subagents are stored as Markdown files with YAML frontmatter in two possible locations:

| Type | Location | Scope | Priority |
| --- | --- | --- | --- |
| **Project subagents** | `.claude/agents/` | Available in current project | Highest |
| **User subagents** | `~/.claude/agents/` | Available across all projects | Lower |

When subagent names conflict, project-level subagents take precedence over user-level subagents.

### Plugin agents

[Plugins](https://docs.claude.com/en/docs/claude-code/plugins) can provide custom subagents that integrate seamlessly with Claude Code. Plugin agents work identically to user-defined agents and appear in the `/agents` interface.**Plugin agent locations**: Plugins include agents in their `agents/` directory (or custom paths specified in the plugin manifest).**Using plugin agents**:
- Plugin agents appear in `/agents` alongside your custom agents
- Can be invoked explicitly: “Use the code-reviewer agent from the security-plugin”
- Can be invoked automatically by Claude when appropriate
- Can be managed (viewed, inspected) through `/agents` interface
See the [plugin components reference](https://docs.claude.com/en/docs/claude-code/plugins-reference#agents) for details on creating plugin agents.

### CLI-based configuration

You can also define subagents dynamically using the `--agents` CLI flag, which accepts a JSON object:

```
claude --agents '{

  "code-reviewer": {

    "description": "Expert code reviewer. Use proactively after code changes.",

    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",

    "tools": ["Read", "Grep", "Glob", "Bash"],

    "model": "sonnet"

  }

}'
```

**Priority**: CLI-defined subagents have lower priority than project-level subagents but higher priority than user-level subagents.**Use case**: This approach is useful for:
- Quick testing of subagent configurations
- Session-specific subagents that don’t need to be saved
- Automation scripts that need custom subagents
- Sharing subagent definitions in documentation or scripts
For detailed information about the JSON format and all available options, see the [CLI reference documentation](https://docs.claude.com/en/docs/claude-code/cli-reference#agents-flag-format).

### File format

Each subagent is defined in a Markdown file with this structure:

```
---

name: your-sub-agent-name

description: Description of when this subagent should be invoked

tools: tool1, tool2, tool3  # Optional - inherits all tools if omitted

model: sonnet  # Optional - specify model alias or 'inherit'

---

Your subagent's system prompt goes here. This can be multiple paragraphs

and should clearly define the subagent's role, capabilities, and approach

to solving problems.

Include specific instructions, best practices, and any constraints

the subagent should follow.
```

#### Configuration fields

| Field | Required | Description |
| --- | --- | --- |
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | Natural language description of the subagent’s purpose |
| `tools` | No | Comma-separated list of specific tools. If omitted, inherits all tools from the main thread |
| `model` | No | Model to use for this subagent. Can be a model alias (`sonnet`, `opus`, `haiku`) or `'inherit'` to use the main conversation’s model. If omitted, defaults to the [configured subagent model](https://docs.claude.com/en/docs/claude-code/model-config) |

### Model selection

The `model` field allows you to control which [AI model](https://docs.claude.com/en/docs/claude-code/model-config) the subagent uses:
- **Model alias**: Use one of the available aliases: `sonnet`, `opus`, or `haiku`
- **`'inherit'`**: Use the same model as the main conversation (useful for consistency)
- **Omitted**: If not specified, uses the default model configured for subagents (`sonnet`)

Using `'inherit'` is particularly useful when you want your subagents to adapt to the model choice of the main conversation, ensuring consistent capabilities and response style throughout your session.

### Available tools

Subagents can be granted access to any of Claude Code’s internal tools. See the [tools documentation](https://docs.claude.com/en/docs/claude-code/settings#tools-available-to-claude) for a complete list of available tools.You have two options for configuring tools:
- **Omit the `tools` field** to inherit all tools from the main thread (default), including MCP tools
- **Specify individual tools** as a comma-separated list for more granular control (can be edited manually or via `/agents`)
**MCP Tools**: Subagents can access MCP tools from configured MCP servers. When the `tools` field is omitted, subagents inherit all MCP tools available to the main thread.

## Managing subagents

The `/agents` command provides a comprehensive interface for subagent management:

```
/agents
```

This opens an interactive menu where you can:
- View all available subagents (built-in, user, and project)
- Create new subagents with guided setup
- Edit existing custom subagents, including their tool access
- Delete custom subagents
- See which subagents are active when duplicates exist
- **Easily manage tool permissions** with a complete list of available tools

### Direct file management

You can also manage subagents by working directly with their files:

```
# Create a project subagent

mkdir -p .claude/agents

echo '---

name: test-runner

description: Use proactively to run tests and fix failures

---

You are a test automation expert. When you see code changes, proactively run the appropriate tests. If tests fail, analyze the failures and fix them while preserving the original test intent.' > .claude/agents/test-runner.md

# Create a user subagent

mkdir -p ~/.claude/agents

# ... create subagent file
```

## Using subagents effectively

### Automatic delegation

Claude Code proactively delegates tasks based on:
- The task description in your request
- The `description` field in subagent configurations
- Current context and available tools

To encourage more proactive subagent use, include phrases like “use PROACTIVELY” or “MUST BE USED” in your `description` field.

### Explicit invocation

Request a specific subagent by mentioning it in your command:

```
> Use the test-runner subagent to fix failing tests

> Have the code-reviewer subagent look at my recent changes

> Ask the debugger subagent to investigate this error
```

## Example subagents

### Code reviewer

```
---

name: code-reviewer

description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.

tools: Read, Grep, Glob, Bash

model: inherit

---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:

1. Run git diff to see recent changes

2. Focus on modified files

3. Begin review immediately

Review checklist:

- Code is simple and readable

- Functions and variables are well-named

- No duplicated code

- Proper error handling

- No exposed secrets or API keys

- Input validation implemented

- Good test coverage

- Performance considerations addressed

Provide feedback organized by priority:

- Critical issues (must fix)

- Warnings (should fix)

- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger

```
---

name: debugger

description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.

tools: Read, Edit, Bash, Grep, Glob

---

You are an expert debugger specializing in root cause analysis.

When invoked:

1. Capture error message and stack trace

2. Identify reproduction steps

3. Isolate the failure location

4. Implement minimal fix

5. Verify solution works

Debugging process:

- Analyze error messages and logs

- Check recent code changes

- Form and test hypotheses

- Add strategic debug logging

- Inspect variable states

For each issue, provide:

- Root cause explanation

- Evidence supporting the diagnosis

- Specific code fix

- Testing approach

- Prevention recommendations

Focus on fixing the underlying issue, not just symptoms.
```

### Data scientist

```
---

name: data-scientist

description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.

tools: Bash, Read, Write

model: sonnet

---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:

1. Understand the data analysis requirement

2. Write efficient SQL queries

3. Use BigQuery command line tools (bq) when appropriate

4. Analyze and summarize results

5. Present findings clearly

Key practices:

- Write optimized SQL queries with proper filters

- Use appropriate aggregations and joins

- Include comments explaining complex logic

- Format results for readability

- Provide data-driven recommendations

For each analysis:

- Explain the query approach

- Document any assumptions

- Highlight key findings

- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

## Best practices

- **Start with Claude-generated agents**: We highly recommend generating your initial subagent with Claude and then iterating on it to make it personally yours. This approach gives you the best results - a solid foundation that you can customize to your specific needs.
- **Design focused subagents**: Create subagents with single, clear responsibilities rather than trying to make one subagent do everything. This improves performance and makes subagents more predictable.
- **Write detailed prompts**: Include specific instructions, examples, and constraints in your system prompts. The more guidance you provide, the better the subagent will perform.
- **Limit tool access**: Only grant tools that are necessary for the subagent’s purpose. This improves security and helps the subagent focus on relevant actions.
- **Version control**: Check project subagents into version control so your team can benefit from and improve them collaboratively.

## Advanced usage

### Chaining subagents

For complex workflows, you can chain multiple subagents:

```
> First use the code-analyzer subagent to find performance issues, then use the optimizer subagent to fix them
```

### Dynamic subagent selection

Claude Code intelligently selects subagents based on context. Make your `description` fields specific and action-oriented for best results.

## Performance considerations

- **Context efficiency**: Agents help preserve main context, enabling longer overall sessions
- **Latency**: Subagents start off with a clean slate each time they are invoked and may add latency as they gather context that they require to do their job effectively.
- [Plugins](https://docs.claude.com/en/docs/claude-code/plugins) - Extend Claude Code with custom agents through plugins
- [Slash commands](https://docs.claude.com/en/docs/claude-code/slash-commands) - Learn about other built-in commands
- [Settings](https://docs.claude.com/en/docs/claude-code/settings) - Configure Claude Code behavior
- [Hooks](https://docs.claude.com/en/docs/claude-code/hooks) - Automate workflows with event handlers

[Common workflows](https://docs.claude.com/en/docs/claude-code/common-workflows) [Plugins](https://docs.claude.com/en/docs/claude-code/plugins)