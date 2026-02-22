# TraceContext

**"Git tracks your code history. TraceContext tracks your intent history."**

TraceContext is a persistent AI coding context platform for engineering teams. It makes AI coding tools context-aware, session-persistent, and team-shared.

## Project Structure

- `orchestrator/`: FastAPI + LangGraph core
- `agents/`: Specialist sub-agents (ADR Distiller, Dead-End Tracker, etc.)
- `cli/`: Node.js/TypeScript CLI tool for developer interaction
- `mcp-server/`: Model Context Protocol server for context injection
- `web/`: React dashboard for context management
- `extension/`: VSCode/Cursor extension boilerplate
- `infrastructure/`: Docker Compose and Helm charts
- `docs/`: Architecture Decision Records (ADRs) and design docs

## Core Value Props

1. **Zero-Friction Capture**: Passive capture of IDE and Git activity.
2. **Tool Agnostic**: Works with any AI tool via MCP.
3. **Dead-End Memory**: Records why approaches failed.
4. **Team-Shared**: Context is shared across the codebase.
5. **Self-Hostable**: Privacy-first design.

## Quick Start

1. **Start Infrastructure**:
   ```bash
   cd infrastructure
   docker-compose up -d
   ```

2. **Initialize CLI**:
   ```bash
   cd cli
   npm install
   npx ts-node src/index.ts init
   ```

3. **Run Dashboard**:
   ```bash
   cd web
   npm install
   npm run dev
   ```

4. **Add to Cursor/Claude Code**:
   - Register the MCP server using `node mcp-server/dist/index.js` as the command.
