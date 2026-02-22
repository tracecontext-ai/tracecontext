# ADR-001: TraceContext Project Inception

## Status
Proposed

## Context
AI coding tools (Cursor, Claude Code, Copilot) lose context between sessions. Developers waste time re-explaining architecture and intent. There is no team-shared intent memory.

## Decision
We will build **TraceContext**, a multi-agent orchestration system that:
1. Passively captures developer activity.
2. Distills it into persistent context (ADRs, dead-ends).
3. Injects context back into AI tools via MCP.

### Technology Choices
- **Orchestration**: LangGraph (for complex agent workflows).
- **LLMs**: Claude 3.5 Sonnet (reasoning) and Claude 3.5 Haiku (extraction).
- **Communication**: Model Context Protocol (MCP) for tool-agnostic delivery.
- **Persistence**: PostgreSQL with `pgvector` for semantic search.

## Consequences
- **Pros**: Solves the "memory loss" problem, tool-agnostic, low friction.
- **Cons**: Requires managing LLM token costs, ensuring low latency (<500ms) for injection.
