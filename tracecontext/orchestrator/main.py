import uuid
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from .graph import app_graph
from ..agents.ranker import ContextRanker

app = FastAPI(
    title="TraceContext Orchestrator",
    description="Persistent AI coding context platform",
    version="0.1.0",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory context store (used for demo; replace with PostgreSQL/vector DB for production)
context_store: list[str] = [
    "[ADR] Title: Use Redis for Caching\nDecision: Accepted\nStatus: Active\nReason: Low latency requirements for context retrieval.",
    "[DEAD_END] Approach: SQL-based Vector Search\nReason: Too slow under high concurrency.\nAlternative: Use pgvector or a dedicated vector DB.",
]


class Event(BaseModel):
    type: str
    data: dict
    metadata: dict = {}


@app.get("/")
async def root():
    return {"status": "TraceContext Orchestrator Online", "version": "0.1.0"}


@app.post("/events")
async def receive_event(event: Event):
    event_id = str(uuid.uuid4())
    logger.info(f"Received event [{event_id}]: {event.type}")

    result = app_graph.invoke({
        "event_type": event.type,
        "event_data": event.data,
        "context_buffer": [],
        "next_step": "",
    })

    # Persist graph output to in-memory store
    for chunk in result.get("context_buffer", []):
        context_store.append(f"[{chunk['type']}] {chunk['content']}")

    return {"status": "received", "event_id": event_id}


@app.get("/context")
async def get_context(query: str = ""):
    if not query:
        return {"context": context_store}

    # Keyword filter first
    filtered = [c for c in context_store if query.lower() in c.lower()]
    candidates = filtered or context_store

    # Re-rank by relevance using ContextRanker when a query is given
    try:
        ranker = ContextRanker()
        chunks = [{"id": str(i), "content": c} for i, c in enumerate(candidates)]
        ranking = ranker.rank(task_description=query, context_chunks=chunks)
        scored = sorted(
            zip(ranking.scores, candidates),
            key=lambda x: x[0].relevance_score,
            reverse=True,
        )
        ranked_results = [c for _, c in scored]
        return {"context": ranked_results, "query": query}
    except Exception as exc:
        logger.warning("Ranker failed, returning unranked results: %s", exc)
        return {"context": candidates, "query": query}


@app.post("/reset")
async def reset_context():
    context_store.clear()
    return {"status": "ok", "message": "Context store cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
