"""
TraceContext MCP Server

Exposes TraceContext context to Claude Code, Cursor, Windsurf, and any
MCP-compatible AI tool. When connected, the AI is automatically briefed
with your team's architectural decisions and dead-end records at the start
of every session — no re-explaining required.

Usage
-----
Start via CLI (recommended):
    tracecontext mcp

Or directly:
    python -m tracecontext.mcp_server

Claude Code config (~/.claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "tracecontext": {
          "command": "tracecontext",
          "args": ["mcp"],
          "env": { "ORCHESTRATOR_URL": "http://localhost:8000" }
        }
      }
    }

Note: The TraceContext orchestrator must be running separately:
    tracecontext serve
"""

import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")

mcp = FastMCP(
    "TraceContext",
    instructions=(
        "TraceContext is the persistent memory layer for this codebase. "
        "ALWAYS call `search_context` before answering questions about architecture, "
        "past decisions, or why something was built a certain way. "
        "If the user makes a significant architectural decision during this session, "
        "call `add_decision` to persist it. "
        "If an approach is abandoned or fails, call `add_dead_end` immediately so "
        "future sessions never repeat the mistake."
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(path: str, params: dict = None) -> dict:
    """GET from the orchestrator. Returns {} on connection failure."""
    try:
        r = requests.get(f"{ORCHESTRATOR_URL}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"_offline": True}
    except Exception as e:
        return {"_error": str(e)}


def _post(path: str, body: dict) -> dict:
    """POST to the orchestrator. Returns {} on connection failure."""
    try:
        r = requests.post(f"{ORCHESTRATOR_URL}{path}", json=body, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"_offline": True}
    except Exception as e:
        return {"_error": str(e)}


def _offline_msg() -> str:
    return (
        "[TraceContext] Orchestrator is offline.\n"
        "Start it first with: tracecontext serve"
    )


def _format_records(records: list[str]) -> str:
    return "\n\n---\n\n".join(records) if records else "No context records found."


# ---------------------------------------------------------------------------
# Resource — injected automatically at session start
# ---------------------------------------------------------------------------

@mcp.resource("tracecontext://active-context")
def active_context() -> str:
    """
    All active TraceContext records for this codebase: ADRs, dead-ends, and
    codebase maps. Read this at the start of every session so the AI is
    already briefed before the developer types a single word.
    """
    data = _get("/context")
    if "_offline" in data:
        return _offline_msg()
    if "_error" in data:
        return f"[TraceContext] Error: {data['_error']}"
    return _format_records(data.get("context", []))


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_context(query: str) -> str:
    """
    Search TraceContext for relevant architectural decisions and dead-end records.

    Call this whenever the developer asks:
    - Why a technology, library, or pattern was chosen
    - Why a previous approach was abandoned or reverted
    - How a specific component or service is structured
    - What decisions were made around a feature area

    Args:
        query: Keywords or a natural language question about the codebase.
               Examples: "why Stripe", "payment pattern", "Redis caching decision"
    """
    data = _get("/context", params={"query": query})
    if "_offline" in data:
        return _offline_msg()
    if "_error" in data:
        return f"[TraceContext] Error: {data['_error']}"

    records = data.get("context", [])
    if not records:
        return f"No context found for '{query}'."
    return f"Found {len(records)} record(s) for '{query}':\n\n" + _format_records(records)


@mcp.tool()
def add_decision(
    title: str,
    decision: str,
    context: str,
    consequences: str = "",
) -> str:
    """
    Record an Architecture Decision Record (ADR) from the current session.

    Call this when the developer makes a significant architectural choice so
    future sessions and teammates automatically know about it.

    Args:
        title:        Short title (e.g. "Use Stripe instead of Braintree")
        decision:     What was decided and the key reasoning
        context:      The problem or situation that drove this decision
        consequences: Trade-offs, pros/cons (optional)
    """
    diff_text = f"Context: {context}\nDecision: {decision}"
    if consequences:
        diff_text += f"\nConsequences: {consequences}"

    result = _post("/events", {
        "type": "git_commit",
        "data": {"message": title, "diff": diff_text},
        "metadata": {"source": "mcp-session"},
    })

    if "_offline" in result:
        return _offline_msg()
    if "_error" in result:
        return f"[TraceContext] Error: {result['_error']}"
    return f"Decision recorded: '{title}'. Available in all future sessions and to all teammates."


@mcp.tool()
def add_dead_end(
    approach: str,
    reason: str,
    alternative: str = "",
) -> str:
    """
    Record a failed or abandoned approach so it is never repeated.

    Call this immediately when an approach is reverted, abandoned, or proven
    unworkable. This is the most valuable record TraceContext stores — it
    prevents the entire team from repeating the same mistake.

    Args:
        approach:    What was tried (e.g. "Strategy pattern for payment routing")
        reason:      Why it failed or was abandoned
        alternative: What was done instead (optional)
    """
    result = _post("/events", {
        "type": "revert_detected",
        "data": {
            "approach": approach,
            "reason": reason,
            "alternative": alternative,
        },
        "metadata": {"source": "mcp-session"},
    })

    if "_offline" in result:
        return _offline_msg()
    if "_error" in result:
        return f"[TraceContext] Error: {result['_error']}"
    return (
        f"Dead-end recorded: '{approach}'.\n"
        "This approach will never be suggested again in future sessions."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
