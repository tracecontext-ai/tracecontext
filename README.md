# TraceContext

**"Git tracks your code history. TraceContext tracks your intent history."**

TraceContext is a Python package that solves the "memory loss" problem in AI-assisted development. It captures your architectural decisions and intent signals passively, orchestrates them using intelligent agents, and injects them back into your AI tools (Cursor, Claude, ChatGPT) so they never lose context.

---

## 🚀 Easy Installation

For any developer team, simply install the package using pip:

```bash
pip install traceContext
```

*Note: For this local development version, run `pip install -e .` from the root directory.*

---

## ⚡ Quick Start

### 1. Initialize Your Repository
Go to any git repository you want to track and run:
```bash
tracecontext init
```
This installs a **passive Git hook** that listens for commits and diffs, automatically sending them to the TraceContext brain.

### 2. Start the Brain (Orchestrator)
Open a terminal and start the orchestration server:
```bash
tracecontext serve
```
This spins up the local AI agents running on port `8000`.

### 3. Retrieve Context
You can now ask TraceContext for relevant memory:
```bash
tracecontext search "why did we choose docker?"
```

---

## 🎬 Visual Demo

We have included a visual demonstration of the installation and architecture.

1. **Run the interactive demo script:**
   ```bash
   cd TraceContext_Demo
   python demonstrate_install.py
   ```
   This simulates the entire developer experience in your terminal.

2. **View the live animation:**
   Open **[TraceContext_Demo/index.html](TraceContext_Demo/index.html)** in your browser to see a beautiful visualization of the agents capturing intents in real-time.

---

## 🧠 Architecture & Agents

TraceContext is not just a database; it is an **Agentic System** powered by **LangGraph**.

### The Orchestrator (`orchestrator/graph.py`)
The system uses a **State Graph** to route events to the correct specialized agent. It acts as the central brain, deciding whether an event is a simple commit, a reverted change, or a major refactor.

### The Agents

#### 1. 🏗️ Architecture Distiller (`agents/distiller.py`)
- **Role**: triggered by `git_commit` events.
- **Function**: Reads raw diffs and commit messages.
- **Output**: Generates **ADRs (Architecture Decision Records)** in MADR format.
- **Why**: Turns "changed file x" into "Decided to use Redis for caching due to latency checks."

#### 2. 🛑 Dead-End Tracker (`agents/dead_end.py`)
- **Role**: Triggered by `revert_detected` events.
- **Function**: analyzes code that was deleted or rolled back.
- **Output**: Logs a **Dead-End Record**.
- **Why**: Prevents your AI from making the same mistake twice. "Do not try to use Library X again, we already failed with it."

#### 3. 🗺️ Map Updater (`agents/mapper.py`)
- **Role**: Triggered by file structure changes.
- **Function**: Updates the cognitive map of the codebase.
- **Output**: High-level repository structure summaries.

### Data Flow
1. **Event Capture**: CLI Hook sends JSON payload to Orchestrator.
2. **Router**: LangGraph Router sends payload to Distiller/Tracker.
3. **Processing**: Agent processes data using LLMs (Claude/Gemini).
4. **Storage**: Distilled context is stored in the persistent vector/graph memory.
5. **Retrieval**: MCP Server or CLI fetches context for your IDE.


---

## 🔌 Connecting to AI (Cursor / Claude / Antigravity)

TraceContext connects to your IDEs using the **Model Context Protocol (MCP)**. This is an open standard that allows AI assistants to talk to local data sources.

### Which Agent Does This?
The **Delivery Agent** (implemented in TypeScript) resides in the `mcp-server/` directory. It acts as the bridge between your IDE and the TraceContext Orchestrator.

**File Location:** `mcp-server/src/index.ts`

### How It Works (Code Explanation)
The MCP server exposes specific **Tools** and **Resources** that the AI in your IDE can call.

1.  **Resources**:
    -   `tracecontext://active-context`: The AI can read this "file" to get the current distilled context.
    -   *Code in `index.ts`: `server.setRequestHandler(ReadResourceRequestSchema, ...)`*

2.  **Tools**:
    -   `get_relevant_context(query: string)`: The AI can call this function to search your intent history.
    -   *Code in `index.ts`: `server.setRequestHandler(CallToolRequestSchema, ...)`*

When you ask Claude or Cursor "Why did we add this feature?", the IDE sends a tool call to the MCP server, which queries the Orchestrator, and returns the answer.


### Setup Instructions by IDE

#### 1. 🖱️ Cursor
Cursor requires adding the MCP server in its settings.

1.  Open **Cursor Settings** (cmd/ctrl + ,).
2.  Navigate to **Features** -> **MCP Servers**.
3.  Click **+ Add New MCP Server**.
4.  Enter the following:
    -   **Name**: `tracecontext`
    -   **Type**: `stdio`
    -   **Command**: `node c:/Users/stungare/sanikaperf/git/TraceContext/mcp-server/build/index.js` *(Update path if needed)*
    -   **Environment Variables**: `ORCHESTRATOR_URL=http://localhost:8000`

#### 2. 🏄 Windsurf (Codeium)
Windsurf uses a config file located in your home directory.

1.  Locate `~/.codeium/windsurf/mcp_config.json`.
2.  Add the `tracecontext` server to the list:
    ```json
    {
      "mcpServers": {
        "tracecontext": {
          "command": "node",
          "args": ["c:/Users/stungare/sanikaperf/git/TraceContext/mcp-server/build/index.js"],
          "env": {
            "ORCHESTRATOR_URL": "http://localhost:8000"
          }
        }
      }
    }
    ```

#### 3. 🤖 Antigravity & Claude Desktop
Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "tracecontext": {
      "command": "node",
      "args": ["c:/Users/stungare/sanikaperf/git/TraceContext/mcp-server/build/index.js"],
      "env": { "ORCHESTRATOR_URL": "http://localhost:8000" }
    }
  }
}
```


*For ChatGPT, see `TraceContext_Demo/CONNECTING_TO_AI.md`.*

---

## 🧪 How to Test Locally (Before Publishing)

To test the package on your machine without publishing to PyPI:

1.  **Install in Editable Mode**:
    This links the package to your current directory, so changes are reflected immediately.
    ```bash
    pip install -e .
    ```

2.  **Verify CLI Installation**:
    ```bash
    tracecontext --help
    ```

3.  **Run the Validation Script**:
    We have included a script that simulates a full user install.
    ```bash
    cd TraceContext_Demo
    python demonstrate_install.py
    ```

4.  **Run with Local Orchestrator**:
    Open two terminals:
    -   **Terminal 1**: `tracecontext serve` (Starts the brain)
    -   **Terminal 2**: `tracecontext status` (Checks connectivity)
    -   **Terminal 2**: `tracecontext search "Redis"` (Tests retrieval)
