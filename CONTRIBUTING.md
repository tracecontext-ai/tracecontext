# Contributing to TraceContext

Thank you for your interest in contributing! TraceContext is an open-source project and welcomes contributions of all kinds — bug fixes, new agents, documentation improvements, and ideas.

---

## Getting Started

### 1. Fork and clone

```bash
git clone https://github.com/tracecontext-ai/tracecontext.git
cd tracecontext
```

### 2. Install in editable mode

```bash
pip install -e ".[db]"
```

### 3. Set up environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Run the tests

```bash
pip install pytest httpx
pytest tests/ -v
```

All tests must pass before submitting a pull request.

---

## Project Structure

```
tracecontext/
├── tracecontext/
│   ├── agents/          # AI agents: distiller, dead_end, ranker
│   ├── orchestrator/    # FastAPI server + LangGraph pipeline + DB layer
│   ├── cli.py           # Click CLI (serve, mcp, init, search, status)
│   └── mcp_server.py    # MCP server for Claude Code / Cursor / Windsurf
├── tests/               # Smoke tests (no API key required)
├── infrastructure/      # Docker Compose (Postgres + Redis)
├── demo_ui.py           # Browser-based demo UI
└── run_demo.py          # Terminal demo script
```

---

## How to Add a New Agent

1. Create `tracecontext/agents/your_agent.py` following the pattern in `distiller.py`:
   - Accept `OPENAI_API_KEY` from env
   - Always provide a graceful fallback when no key is present
   - Return a Pydantic model

2. Wire it into `tracecontext/orchestrator/graph.py`:
   - Add a new node function
   - Add a router branch
   - Connect edges to `storer`

3. Add a smoke test in `tests/test_smoke.py` verifying the fallback path

---

## Pull Request Guidelines

- One feature or fix per PR
- All existing tests must pass
- New features should include a test covering the fallback (no-API-key) path
- Keep commits clean — one logical change per commit
- Update `README.md` if you add a new CLI command or MCP tool

---

## Reporting Bugs

Open an issue at [github.com/tracecontext-ai/tracecontext/issues](https://github.com/tracecontext-ai/tracecontext/issues) with:
- TraceContext version (`pip show tracecontext`)
- Python version
- Steps to reproduce
- Expected vs actual behaviour

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
