# TraceContext

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/tracecontext-ai/tracecontext/actions/workflows/ci.yml/badge.svg)](https://github.com/tracecontext-ai/tracecontext/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tracecontext.svg)](https://pypi.org/project/tracecontext/)

> **"Git tracks your code history. TraceContext tracks your intent history."**

TraceContext is a persistent AI coding context platform. It solves the #1 broken experience in AI-assisted development: every time a session ends, the AI loses all memory — forcing developers to re-explain their architecture, past decisions, and failed approaches every single session.

TraceContext is the memory layer that sits underneath every AI coding tool — Cursor, Claude Code, Copilot, Windsurf — making them context-aware, session-persistent, and team-shared.

**github.com/tracecontext-ai/tracecontext** · MIT License · by [Sanika Deshmukh Tungare](https://github.com/tracecontext-ai)

---

## Install

```bash
pip install tracecontext
```

Requires Python 3.9+. For PostgreSQL + Redis persistence, add the `db` extra:

```bash
pip install "tracecontext[db]"
```

---

## Quick Start

### 1. Set your API key

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### 2. Start the orchestrator

```bash
tracecontext serve
```

### 3. Initialize a repository

In any git repository:

```bash
tracecontext init
```

This installs a passive git post-commit hook that sends diffs and commit messages to the orchestrator automatically.

### 4. Search your intent history

```bash
tracecontext search "why did we choose Redis?"
```

### 5. Check orchestrator status

```bash
tracecontext status
```

---

## CLI Reference

| Command | Description |
|---|---|
| `tracecontext serve` | Start the orchestrator on `localhost:8000` |
| `tracecontext mcp` | Start the MCP server for Claude Code / Cursor / Windsurf |
| `tracecontext init` | Install git hooks in the current repository |
| `tracecontext status` | Check if the orchestrator is running |
| `tracecontext search <query>` | Search stored context by keyword |

---

## Connect to Claude Code / Cursor / Windsurf (MCP)

TraceContext exposes a **Model Context Protocol (MCP) server** that plugs into any MCP-compatible AI tool. Once connected, the AI is automatically briefed with your team's decisions at the start of every session.

### Setup (2 steps)

**Step 1 — Start the orchestrator** (keep this running):
```bash
tracecontext serve
```

**Step 2 — Add to your AI tool config**

**Claude Code** (`~/.claude/settings.json`):
```json
{
  "mcpServers": {
    "tracecontext": {
      "command": "tracecontext",
      "args": ["mcp"],
      "env": { "ORCHESTRATOR_URL": "http://localhost:8000" }
    }
  }
}
```

**Cursor** (Settings → Features → MCP Servers → Add New):
```
Name:    tracecontext
Type:    stdio
Command: tracecontext
Args:    mcp
Env:     ORCHESTRATOR_URL=http://localhost:8000
```

**Windsurf** (`~/.codeium/windsurf/mcp_config.json`):
```json
{
  "mcpServers": {
    "tracecontext": {
      "command": "tracecontext",
      "args": ["mcp"],
      "env": { "ORCHESTRATOR_URL": "http://localhost:8000" }
    }
  }
}
```

### What the AI can do via MCP

| MCP Tool | When it fires |
|---|---|
| `search_context(query)` | When asked about architecture, past decisions, or why something was built |
| `add_decision(...)` | When a significant design choice is made during the session |
| `add_dead_end(...)` | When an approach is abandoned — records it so it's never repeated |

The resource `tracecontext://active-context` is read automatically at session start — the AI is already briefed before you type a single word.

---

## How It Works

```
Git commit  ──►  Git Hook  ──►  Orchestrator (FastAPI + LangGraph)
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
               Architecture       Dead-End          Context
               Distiller          Tracker           Ranker
               (ADRs)             (failed paths)    (relevance)
                        │               │               │
                        └───────────────┼───────────────┘
                                        ▼
                               Context Store
                                        │
                                        ▼
                               tracecontext search
                               (or MCP injection)
```

**Agents:**

- **Architecture Distiller** — converts diffs + commit messages into Architecture Decision Records (ADRs)
- **Dead-End Tracker** — records reverted approaches so teams never repeat failed experiments
- **Context Ranker** — re-ranks stored context by relevance when a query is given

---

## Demo

Run the interactive terminal demo (requires `OPENAI_API_KEY`):

```bash
python run_demo.py
```

Or launch the browser-based demo UI:

```bash
python demo_ui.py
# Opens http://localhost:8080
```

---

## Docker

```bash
docker compose -f infrastructure/docker-compose.yml up
```

This starts the orchestrator, PostgreSQL (with pgvector), and Redis.

---

## Environment Variables

See [.env.example](.env.example) for all options.

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required for AI agents (GPT-4o-mini) |
| `ORCHESTRATOR_URL` | `http://localhost:8000` | Orchestrator endpoint |
| `DATABASE_URL` | — | PostgreSQL URL (optional) |
| `REDIS_HOST` | `localhost` | Redis host (optional) |
| `REDIS_PORT` | `6379` | Redis port (optional) |

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, project structure, and pull request guidelines.

---

## License

MIT © 2025 [Sanika Deshmukh Tungare](https://github.com/tracecontext-ai) — see [LICENSE](LICENSE) for full text.
