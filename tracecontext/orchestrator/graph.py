from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator

from ..agents.distiller import ArchitectureDistiller
from ..agents.dead_end import DeadEndTracker


class AgentState(TypedDict):
    event_type: str
    event_data: dict
    context_buffer: Annotated[List[dict], operator.add]
    next_step: str


def router(state: AgentState):
    event_type = state["event_type"]
    if event_type == "git_commit":
        return "distiller"
    elif event_type == "revert_detected":
        return "dead_end_tracker"
    else:
        return "mapper"


def distiller_node(state: AgentState):
    print("--- DISTILLING ARCHITECTURE ---")
    distiller = ArchitectureDistiller()
    result = distiller.distill(
        diff=state["event_data"].get("diff", ""),
        commit_msg=state["event_data"].get("message", "")
    )
    content = f"Title: {result.title}\nDecision: {result.decision}\nStatus: {result.status}"
    return {"context_buffer": [{"type": "ADR", "content": content}]}


def dead_end_tracker_node(state: AgentState):
    print("--- TRACKING DEAD END ---")
    tracker = DeadEndTracker()
    result = tracker.track(event_sequence=str(state["event_data"]))
    content = f"Approach: {result.approach}\nReason: {result.failure_reason}"
    return {"context_buffer": [{"type": "DEAD_END", "content": content}]}


def mapper_node(state: AgentState):
    print("--- MAPPING CODEBASE ---")
    return {"context_buffer": [{"type": "MAP_UPDATE", "content": "Codebase map updated."}]}


def storer_node(state: AgentState):
    # Storage is handled by main.py after the graph completes.
    # This node is a pass-through kept for future persistence logic.
    print(f"--- STORING {len(state.get('context_buffer', []))} CONTEXT CHUNK(S) ---")
    return {}


# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("distiller", distiller_node)
workflow.add_node("dead_end_tracker", dead_end_tracker_node)
workflow.add_node("mapper", mapper_node)
workflow.add_node("storer", storer_node)

workflow.set_conditional_entry_point(
    router,
    {
        "distiller": "distiller",
        "dead_end_tracker": "dead_end_tracker",
        "mapper": "mapper",
    }
)

workflow.add_edge("distiller", "storer")
workflow.add_edge("dead_end_tracker", "storer")
workflow.add_edge("mapper", "storer")
workflow.add_edge("storer", END)

app_graph = workflow.compile()
