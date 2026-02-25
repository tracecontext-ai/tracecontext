"""
Smoke tests for TraceContext — verify core components import and
run correctly with no external dependencies (no API key, no DB, no Redis).
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


# ── Package import ────────────────────────────────────────────────────────────

def test_package_imports():
    import tracecontext
    assert tracecontext.__version__ == "0.1.0"
    assert tracecontext.__author__ == "Sanika Deshmukh Tungare"


# ── Agents — demo/fallback mode (no API key) ─────────────────────────────────

def test_distiller_fallback_no_api_key():
    """Distiller must return a valid ADRModel even without OPENAI_API_KEY."""
    with patch.dict("os.environ", {}, clear=False):
        import os; os.environ.pop("OPENAI_API_KEY", None)
        from tracecontext.agents.distiller import ArchitectureDistiller, ADRModel
        agent = ArchitectureDistiller()
        result = agent.distill(diff="+print('hello')", commit_msg="test: smoke")
    assert isinstance(result, ADRModel)
    assert result.title
    assert result.decision


def test_dead_end_tracker_fallback_no_api_key():
    """DeadEndTracker must return a valid DeadEndRecord without OPENAI_API_KEY."""
    with patch.dict("os.environ", {}, clear=False):
        import os; os.environ.pop("OPENAI_API_KEY", None)
        from tracecontext.agents.dead_end import DeadEndTracker, DeadEndRecord
        agent = DeadEndTracker()
        result = agent.track(event_sequence="reverted braintree integration")
    assert isinstance(result, DeadEndRecord)
    assert result.approach
    assert result.failure_reason


def test_ranker_fallback_no_api_key():
    """ContextRanker must return scores for all chunks without OPENAI_API_KEY."""
    with patch.dict("os.environ", {}, clear=False):
        import os; os.environ.pop("OPENAI_API_KEY", None)
        from tracecontext.agents.ranker import ContextRanker, RankingResult
        agent = ContextRanker()
        chunks = [
            {"id": "1", "content": "Use Redis for caching"},
            {"id": "2", "content": "Avoid float for money"},
        ]
        result = agent.rank(task_description="caching strategy", context_chunks=chunks)
    assert isinstance(result, RankingResult)
    assert len(result.scores) == 2
    assert all(0.0 <= s.relevance_score <= 1.0 for s in result.scores)


# ── Orchestrator API ─────────────────────────────────────────────────────────

@pytest.fixture
def client():
    from tracecontext.orchestrator.main import app
    return TestClient(app)


def test_root_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "TraceContext Orchestrator Online"


def test_post_git_commit_event(client):
    payload = {
        "type": "git_commit",
        "data": {"message": "feat: smoke test commit", "diff": "+x = 1"},
        "metadata": {"repo": "test-repo", "user": "tester"},
    }
    r = client.post("/events", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "received"
    assert "event_id" in r.json()


def test_post_revert_event(client):
    payload = {
        "type": "revert_detected",
        "data": {"approach": "test approach", "reason": "did not work"},
        "metadata": {},
    }
    r = client.post("/events", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "received"


def test_get_context_no_query(client):
    r = client.get("/context")
    assert r.status_code == 200
    assert "context" in r.json()
    assert isinstance(r.json()["context"], list)


def test_get_context_with_query(client):
    r = client.get("/context", params={"query": "Redis"})
    assert r.status_code == 200
    data = r.json()
    assert "context" in data
    assert data["query"] == "Redis"


def test_reset_context(client):
    r = client.post("/reset")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── MCP server — import only ─────────────────────────────────────────────────

def test_mcp_server_imports():
    from tracecontext.mcp_server import mcp, search_context, add_decision, add_dead_end
    assert mcp is not None
    assert callable(search_context)
    assert callable(add_decision)
    assert callable(add_dead_end)
