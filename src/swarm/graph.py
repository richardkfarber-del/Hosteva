import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

def merge_dicts(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, str]:
    if not a: a = {}
    if not b: b = {}
    res = a.copy()
    res.update(b)
    return res

# --- State Definition ---
class SwarmState(TypedDict):
    messages: Annotated[list, add_messages]
    current_phase: int
    rocket_trigger_count: int
    rca_report: Optional[str]
    rnd_upgrades: Optional[str]
    parallel_reviews: Annotated[Dict[str, str], merge_dicts]
    executive_summary: Optional[str]
    error_detected: bool

# --- Node Functions (Mocks for Implementation) ---
def node_coulson(state: SwarmState):
    print("[Coulson] Evaluating state and routing...")
    return state

def node_rocket(state: SwarmState):
    print("[Rocket] Failsafe Triggered! Generating RCA...")
    return {"rca_report": "RCA: System critical failure at Phase " + str(state.get("current_phase", 0))}

def node_fury(state: SwarmState):
    print("[Fury] Executive Override / Escalation.")
    if state.get("rca_report"):
        print("  -> HARD STOP executed due to RCA.")
    elif state.get("executive_summary"):
        print("  -> Escalating Evolution Loop executive summary.")
    return state

def node_shuri(state: SwarmState):
    print("[Shuri] Generating rnd_upgrades.md...")
    return {"rnd_upgrades": "Phase 5 upgrades proposed.", "current_phase": state.get("current_phase", 5) + 1}

def node_black_panther(state: SwarmState):
    print("[Black Panther] Security Review...")
    return {"parallel_reviews": {"black_panther": "Approved"}}

def node_she_hulk(state: SwarmState):
    print("[She-Hulk] Compliance Review...")
    return {"parallel_reviews": {"she_hulk": "Approved"}}

def node_kang(state: SwarmState):
    print("[Kang] Temporal/Strategic Review...")
    return {"parallel_reviews": {"kang": "Approved"}}

def node_falcon(state: SwarmState):
    print("[Falcon] Intel Review...")
    return {"parallel_reviews": {"falcon": "Approved"}}

def aggregate_reviews(state: SwarmState):
    print("[Aggregate] Compiling executive summary...")
    return {"executive_summary": "All reviews compiled successfully."}

# Placeholder generic agents
def generic_agent(name):
    def _agent(state: SwarmState):
        print(f"[{name}] Executing task...")
        return {"current_phase": state.get("current_phase", 1) + 1}
    return _agent

# --- Routing Logic ---
def coulson_router(state: SwarmState) -> str:
    # Global Law #3: Rocket Failsafe
    if state.get("rocket_trigger_count", 0) >= 2:
        return "rocket"
    
    phase = state.get("current_phase", 1)
    
    # Simple phase progression mock
    if phase == 1:
        return "phase_1"
    elif phase == 2:
        return "phase_2"
    elif phase == 3:
        return "phase_3"
    elif phase == 4:
        return "phase_4"
    elif phase == 5:
        return "shuri"
    else:
        return END

# --- Graph Construction ---
workflow = StateGraph(SwarmState)

# Add Nodes
workflow.add_node("coulson", node_coulson)
workflow.add_node("rocket", node_rocket)
workflow.add_node("fury", node_fury)

# Phase 5 Nodes
workflow.add_node("shuri", node_shuri)
workflow.add_node("black_panther", node_black_panther)
workflow.add_node("she_hulk", node_she_hulk)
workflow.add_node("kang", node_kang)
workflow.add_node("falcon", node_falcon)
workflow.add_node("aggregate_reviews", aggregate_reviews)

# Placeholder nodes for other phases
workflow.add_node("phase_1", generic_agent("War Room"))
workflow.add_node("phase_2", generic_agent("Build"))
workflow.add_node("phase_3", generic_agent("QA"))
workflow.add_node("phase_4", generic_agent("Deploy"))

# Set Entry Point
workflow.set_entry_point("coulson")

# Conditional Routing from Coulson
workflow.add_conditional_edges(
    "coulson",
    coulson_router,
    {
        "rocket": "rocket",
        "phase_1": "phase_1",
        "phase_2": "phase_2",
        "phase_3": "phase_3",
        "phase_4": "phase_4",
        "shuri": "shuri",
        END: END
    }
)

# Return to Coulson after phases (Hub and Spoke)
for phase in ["phase_1", "phase_2", "phase_3", "phase_4"]:
    workflow.add_edge(phase, "coulson")

# Rocket Failsafe Path
workflow.add_edge("rocket", "fury")
workflow.add_edge("fury", END)

# Phase 5: Evolution Loop Path
workflow.add_edge("shuri", "black_panther")
workflow.add_edge("shuri", "she_hulk")
workflow.add_edge("shuri", "kang")
workflow.add_edge("shuri", "falcon")

workflow.add_edge("black_panther", "aggregate_reviews")
workflow.add_edge("she_hulk", "aggregate_reviews")
workflow.add_edge("kang", "aggregate_reviews")
workflow.add_edge("falcon", "aggregate_reviews")

workflow.add_edge("aggregate_reviews", "fury")

# Compile
app = workflow.compile()

if __name__ == "__main__":
    print("LangGraph Swarm pipeline compiled successfully.")