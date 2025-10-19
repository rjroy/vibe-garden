# Model Context Protocol (MCP) Overview

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. It enables seamless integration between AI assistants and various data sources and tools.

## Key Concepts

### Servers
MCP servers provide context, tools, and capabilities to clients. Each server can:
- Expose **tools** that LLMs can invoke
- Provide **resources** (data sources)
- Send **prompts** to guide LLM behavior

### Clients
MCP clients (like Claude Desktop) connect to MCP servers and make their capabilities available to LLMs.

### Transport
MCP uses stdio (standard input/output) for communication between client and server.

## Architecture

```
┌─────────────────┐
│   LLM Client    │
│ (Claude Desktop)│
└────────┬────────┘
         │ MCP Protocol
         │ (stdio)
┌────────┴────────┐
│   MCP Server    │
│  (wyrd-gen)     │
└────────┬────────┘
         │ API Calls
         │
┌────────┴────────┐
│   Replicate     │
│      API        │
└─────────────────┘
```

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
