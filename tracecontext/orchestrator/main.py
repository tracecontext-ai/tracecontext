from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from .graph import app_graph
from .db import DatabaseManager

app = FastAPI(title="TraceContext Orchestrator")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock storage for demo purposes
demo_context = [
    "[ADR] Title: Use Redis for Caching\nDecision: Accepted\nStatus: Active\nReason: Low latency requirements for context retrieval.",
    "[DEAD_END] Approach: SQL-based Vector Search\nReason: Too slow under high concurrency.\nAlternative: Use pgvector or specialized vector DB."
]

class Event(BaseModel):
    type: str
    data: dict
    metadata: dict

@app.get("/")
async def root():
    return {"status": "TraceContext Orchestrator Online"}

@app.post("/events")
async def receive_event(event: Event, background_tasks: BackgroundTasks):
    logger.info(f"Received event: {event.type}")
    result = app_graph.invoke({
        "event_type": event.type,
        "event_data": event.data,
        "context_buffer": [],
        "next_step": ""
    })
    return {"status": "received", "event_id": "...", "graph_result": result}

@app.get("/context")
async def get_context(query: str = None):
    # Return mock context for demo
    global demo_context
    if not query:
        return {"context": demo_context}
    # Simple keyword filter for demo
    filtered = [c for c in demo_context if query.lower() in str(c).lower()]
    return {"context": filtered or demo_context, "query": query}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
