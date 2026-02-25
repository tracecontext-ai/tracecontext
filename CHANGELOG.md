# Changelog

All notable changes to TraceContext will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-24

### Added
- Initial open-source release
- FastAPI orchestrator with LangGraph pipeline
- AI distiller agent (GPT-4o-mini) — converts git commits into ADRs
- Dead-end agent — records reverted approaches with reasons
- Context ranker agent — re-ranks context chunks by relevance
- MCP server with `search_context`, `add_decision`, `add_dead_end` tools
- CLI: `tracecontext serve`, `mcp`, `init`, `search`, `status`
- Browser-based demo UI (`demo_ui.py`)
- Terminal demo script (`run_demo.py`)
- Docker + Docker Compose support
- In-memory context store (PostgreSQL/Redis optional via `[db]` extras)
- Smoke tests with no-API-key fallback mode
