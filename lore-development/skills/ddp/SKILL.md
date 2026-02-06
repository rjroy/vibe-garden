---
name: ddp
description: This skill visualizes flows, relationships, and architectures using Mermaid diagrams when text descriptions fail to communicate. Use when needing to see how data flows, map class relationships, visualize control flow, or explain architecture. Triggers include "draw this", "visualize how", "diagram the flow", "show me the architecture", "I can't hold this in my head".
artifact_path: .lore/diagrams
---

# DDP: Draw the Damn Picture

## Purpose

Sometimes specs aren't enough. You need to **see** how things connect.

This skill generates Mermaid diagrams to visualize:
- Data flows between components
- Class hierarchies and relationships
- System architectures
- State machines and transitions
- Sequence of operations

When you can't hold the mental model in your head, draw the damn picture.

## When to Use

- Understanding how data flows through a system
- Mapping relationships between classes or modules
- Visualizing complex control flow
- Explaining architecture to yourself or others
- When you keep re-reading code and it's not clicking

## Invocation

```
/lore-development:ddp <what to visualize>
```

### Examples

```
/lore-development:ddp how chat messages flow between user and AI
/lore-development:ddp the inheritance hierarchy of BaseView
/lore-development:ddp the request lifecycle from HTTP to database
/lore-development:ddp state transitions in the order fulfillment system
/lore-development:ddp how the plugin system loads and registers skills
```

## Process

### Step 1: Understand the Subject

Clarify what needs visualization:
- What's the scope? (One feature? Whole system? Specific interaction?)
- What's the perspective? (Data flow? Control flow? Structure?)
- What level of detail? (High-level overview? Implementation specifics?)

### Step 2: Explore the Code

Trace through the codebase to understand:
- Entry points and exit points
- Key actors (classes, functions, services, users)
- Relationships (calls, extends, contains, depends on)
- Data transformations along the way

### Step 3: Choose the Right Diagram Type

| Need to Show | Diagram Type | Good For |
|--------------|--------------|----------|
| Sequential interactions | `sequenceDiagram` | API calls, message passing, request/response |
| Class relationships | `classDiagram` | Inheritance, composition, dependencies |
| System structure | `graph` / `flowchart` | Components, modules, architecture |
| State changes | `stateDiagram-v2` | Workflows, lifecycles, FSMs |
| Data flow | `flowchart` | Pipelines, transformations |
| Entity relationships | `erDiagram` | Data models, database schemas |

### Step 4: Draw the Picture

Create a Mermaid diagram that:
- Shows the essential relationships (not every detail)
- Uses clear labels
- Groups related items when helpful
- Includes a legend if notation isn't obvious

### Step 5: Annotate

Add context around the diagram:
- What triggered this visualization
- Key insights revealed by the picture
- Things that aren't captured in the diagram
- Questions that emerged

## Output

Save to `.lore/diagrams/[subject].md`

Use kebab-case. Be descriptive (e.g., `chat-message-flow.md`, `view-class-hierarchy.md`).

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for diagrams.

```markdown
---
[frontmatter per schema]
---

# Diagram: [Subject]

## Context

What prompted this visualization. What question are we answering?

## Diagram

```mermaid
[diagram code]
```

## Reading the Diagram

Explanation of what the diagram shows. Call out non-obvious elements.

## Key Insights

What becomes clear when you see it visually:
- Insight 1
- Insight 2

## Not Shown

Important aspects not captured in this view:
- Error paths
- Edge cases
- Implementation details
- etc.

## Related

Links to specs, other diagrams, or code that provides more context.
```

## Additional Resources

### Reference Files

For Mermaid syntax patterns and diagram examples, consult:
- **`references/mermaid-patterns.md`** - Flow, structure, architecture, and lifecycle diagram patterns with tips

## Context

Check `.lore/specs/` for feature documentation that might need visualization.
Check `.lore/brainstorm/` for ideas that might benefit from a picture.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help identify what needs visualization. Architecture agents can highlight complex relationships worth diagramming. Invoke relevant agents via Task tool and incorporate their insights.
