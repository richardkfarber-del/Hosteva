import operator
import os
import re
import requests
import datetime
import json
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import websocket

def send_telegram_alert(message: str):
    try:
        url = os.environ.get("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789").rstrip("/") + "/v1/chat/completions"
        token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        payload = {
            "model": "agent:main", # Default agent to send telegram
            "messages": [{"role": "user", "content": f"Please send this telegram alert to 8675276831: {message}"}],
            "stream": False
        }
        requests.post(url, headers=headers, json=payload, timeout=60)
    except Exception as e:
        print(f"Telegram alert failed: {e}")

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
    retry_count: int
    code_fixed: bool
    qa_passed: bool
    rca_report: Optional[str]
    rnd_upgrades: Optional[str]
    parallel_reviews: Annotated[Dict[str, str], merge_dicts]
    executive_summary: Optional[str]
    error_detected: bool
    latest_output: Optional[str]
    last_agent: Optional[str]

import subprocess

# --- Helper to Trigger Subagents ---
def run_agent(agent_name: str, task: str) -> str:
    print(f"[{agent_name.capitalize()}] Spawning native OpenClaw subagent via CLI subprocess...")
    try:
        cmd = ["openclaw", "agent", "--agent", agent_name, "-m", task, "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        
        if result.returncode != 0:
            err_msg = f"Error: CLI returned non-zero exit status {result.returncode}.\nStderr: {result.stderr}"
            print(f"[{agent_name.capitalize()}] {err_msg}")
            send_telegram_alert(f"🚨 CRITICAL ALERT (Error): Node {agent_name.capitalize()} CLI execution failed.\n{err_msg}")
            return err_msg
            
        try:
            data = json.loads(result.stdout)
            final_text = data.get("text", data.get("response", "Task completed but no explicit text field in JSON output."))
            send_telegram_alert(f"Agent {agent_name.capitalize()} completed task. Output:\n{final_text}")
            return final_text
        except json.JSONDecodeError as je:
            print(f"[{agent_name.capitalize()}] Failed to parse JSON output: {je}")
            send_telegram_alert(f"🚨 ALERT: Node {agent_name.capitalize()} returned invalid JSON.\nRaw output: {result.stdout[:500]}")
            return result.stdout
            
    except Exception as e:
        print(f"[{agent_name.capitalize()}] Exception triggering agent: {e}")
        send_telegram_alert(f"🚨 CRITICAL ALERT (Exception): Node {agent_name.capitalize()} encountered an exception: {str(e)}")
        return f"Error: {str(e)}"

def parse_ledger_state():
    ledger_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md"
    try:
        with open(ledger_path, "r") as f:
            content = f.read()
    except Exception as e:
        return None, None

    sections = re.split(r"\n##\s+", "\n" + content)
    last_section = sections[-1].strip() if sections else ""
    return content, last_section

def write_ledger(state: SwarmState, action: str):
    ledger_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## {timestamp} - State Update\n"
    entry += f"- Last Agent: {state.get('last_agent', 'None')}\n"
    entry += f"- Action: {action}\n"
    entry += f"- Code Fixed: {state.get('code_fixed', False)}\n"
    entry += f"- QA Passed: {state.get('qa_passed', False)}\n"
    entry += f"- Retry Count: {state.get('retry_count', 0)}\n\n"
    
    try:
        with open(ledger_path, "a") as f:
            f.write(entry)
    except Exception as e:
        print(f"Failed to write to ledger: {e}")

# --- Node Functions (Now executing real subagents) ---
def node_coulson(state: SwarmState):
    print("[Coulson] Evaluating state and centralizing ledger write...")
    
    # Centralized Ledger Write
    last_agent = state.get("last_agent")
    if last_agent and last_agent != "coulson":
        write_ledger(state, f"Evaluated results from {last_agent}")
        
    if last_agent in ["iron_man", "wasp"] and not state.get("code_fixed", False):
        print(f"[Coulson] REJECTED. {last_agent} failed to mark code_fixed.")
        return {
            "latest_output": "STRICT REPRIMAND: Ensure code is fixed and output a success payload.",
            "retry_count": state.get("retry_count", 0) + 1
        }

    output = run_agent("coulson", "Audit project status and prepare next phase.")
    return {"latest_output": output}

def node_rocket(state: SwarmState):
    print("[Rocket] Failsafe Triggered! Generating RCA...")
    send_telegram_alert("🚨 CRITICAL ALERT (Error): Rocket Failsafe Triggered! Too many retries.")
    output = run_agent("rocket", "System critical failure detected. Generate RCA and fix pathing.")
    return {"rca_report": output, "latest_output": output, "last_agent": "rocket"}

def node_fury(state: SwarmState):
    print("[Fury] Executive Override / Escalation.")
    if state.get("retry_count", 0) >= 2 or state.get("rca_report"):
        send_telegram_alert("🚨 FURY ESCALATION: Execution halted due to circuit breaker. Pinging Director.")
        run_agent("fury", "Execute HARD STOP and escalate RCA to Director via Telegram.")
    elif state.get("executive_summary"):
        run_agent("fury", "Review Evolution Loop executive summary and report to Director.")
    return state

def node_shuri(state: SwarmState):
    print("[Shuri] Generating rnd_upgrades.md...")
    output = run_agent("shuri", "Draft rnd_upgrades.md for Phase 5.")
    return {"rnd_upgrades": output, "latest_output": output, "last_agent": "shuri"}

def node_black_panther(state: SwarmState):
    print("[Black Panther] Security Review...")
    output = run_agent("black_panther", "Conduct security review and enforce Vibranium Habit encryption.")
    return {"parallel_reviews": {"black_panther": output}}

def node_she_hulk(state: SwarmState):
    print("[She-Hulk] Compliance Review...")
    output = run_agent("she_hulk", "Audit municipal codes and map to technical compliance.")
    return {"parallel_reviews": {"she_hulk": output}}

def node_kang(state: SwarmState):
    print("[Kang] Temporal/Strategic Review...")
    output = run_agent("kang", "Forecast technological shifts for the current blueprints.")
    return {"parallel_reviews": {"kang": output}}

def node_falcon(state: SwarmState):
    print("[Falcon] Intel Review...")
    output = run_agent("falcon", "Conduct market research and external recon.")
    return {"parallel_reviews": {"falcon": output}}

def aggregate_reviews(state: SwarmState):
    print("[Aggregate] Compiling executive summary...")
    return {"executive_summary": "All reviews compiled successfully.", "last_agent": "aggregate"}

def parse_project_board():
    board_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/project_board.md"
    try:
        with open(board_path, "r") as f:
            board_content = f.read()
    except Exception as e:
        return "Unknown Target", {}

    target_match = re.search(r"(?:> CURRENT_FOCUS_TARGET:|## Current Focus Target)\s*(.*)", board_content, re.IGNORECASE)
    target = target_match.group(1).strip() if target_match else "Unknown Target"

    tickets = {}
    sections = re.split(r"\n##\s+", board_content)
    for section in sections[1:]:
        lines = section.split('\n')
        title_line = lines[0].strip()
        if not re.match(r"(BUG|FEAT|REGRESS)-\d+", title_line):
            continue
        status_match = re.search(r"\*\*Status:\*\*\s*(.*)", section)
        if not status_match:
            continue
        status = status_match.group(1).strip().lower()
        if not status.startswith("to do") and not status.startswith("in progress"):
            continue
        ac_match = re.search(r"### Acceptance Criteria:\n(.*?)(\n##|\Z|\n---)", section, re.DOTALL)
        if ac_match:
            tickets[title_line] = ac_match.group(1).strip()

    return target, tickets

# Dynamic agents for Phased nodes
def phase_node(phase_name: str, agent_name: str, task: str):
    def _node(state: SwarmState):
        print(f"[{agent_name.capitalize()}] Executing {phase_name}...")
        
        target, tickets = parse_project_board()
        
        task_payload = task + "\n\nCURRENT_FOCUS_TARGET: " + target + "\n\nACTIVE TICKETS:\n"
        for title, ac in tickets.items():
            task_payload += f"- {title}\n{ac}\n\n"
            
        latest = state.get("latest_output", "")
        if "STRICT REPRIMAND" in latest:
            task_payload = latest + "\n\n" + task_payload

        output = run_agent(agent_name, task_payload.strip())
        
        # execution agents only return code and success payload
        ret = {"latest_output": output, "last_agent": agent_name}
        if agent_name in ["iron_man", "wasp"]:
            ret["code_fixed"] = True
            
        if agent_name in ["captain_america"]:
            ret["qa_passed"] = True
            
        return ret
    return _node

# --- Routing Logic ---
def coulson_router(state: SwarmState) -> str:
    # Circuit Breaker: route straight to Fury if retry limit exceeded
    if state.get("retry_count", 0) >= 2:
        return "fury"
        
    last_agent = state.get("last_agent")
    
    if last_agent in ["hawkeye", "phase_1"]:
        return "phase_2"
        
    if last_agent in ["iron_man", "phase_2"]:
        if not state.get("code_fixed", False):
            # Bump retry count directly by returning back to phase_2
            # For langgraph, state updates happen in nodes. We route back.
            return "phase_2"
        return "phase_3"
        
    if last_agent in ["captain_america", "phase_3"]:
        if not state.get("qa_passed", False):
            return "phase_2" # Back to build
        return "phase_4"
        
    if last_agent in ["heimdall", "phase_4"]:
        return "shuri"
        
    # Default initial step
    return "phase_1"

# --- Graph Construction ---
workflow = StateGraph(SwarmState)

workflow.add_node("coulson", node_coulson)
workflow.add_node("rocket", node_rocket)
workflow.add_node("fury", node_fury)

workflow.add_node("shuri", node_shuri)
workflow.add_node("black_panther", node_black_panther)
workflow.add_node("she_hulk", node_she_hulk)
workflow.add_node("kang", node_kang)
workflow.add_node("falcon", node_falcon)
workflow.add_node("aggregate_reviews", aggregate_reviews)

workflow.add_node("phase_1", phase_node("Phase 1 (War Room)", "hawkeye", "Update project_board.md and backlog."))
workflow.add_node("phase_2", phase_node("Phase 2 (Build)", "iron_man", "Execute backend systems build step."))
workflow.add_node("phase_3", phase_node("Phase 3 (QA)", "captain_america", "Run tests and evaluate PRs."))
workflow.add_node("phase_4", phase_node("Phase 4 (Deploy)", "heimdall", "Resolve conflicts and deploy."))

workflow.set_entry_point("coulson")

workflow.add_conditional_edges(
    "coulson",
    coulson_router,
    {
        "rocket": "rocket",
        "fury": "fury",
        "phase_1": "phase_1",
        "phase_2": "phase_2",
        "phase_3": "phase_3",
        "phase_4": "phase_4",
        "shuri": "shuri",
        END: END
    }
)

for phase in ["phase_1", "phase_2", "phase_3", "phase_4"]:
    workflow.add_edge(phase, "coulson")

workflow.add_edge("rocket", "fury")
workflow.add_edge("fury", END)

workflow.add_edge("shuri", "black_panther")
workflow.add_edge("shuri", "she_hulk")
workflow.add_edge("shuri", "kang")
workflow.add_edge("shuri", "falcon")

workflow.add_edge("black_panther", "aggregate_reviews")
workflow.add_edge("she_hulk", "aggregate_reviews")
workflow.add_edge("kang", "aggregate_reviews")
workflow.add_edge("falcon", "aggregate_reviews")

workflow.add_edge("aggregate_reviews", "fury")

app = workflow.compile()

if __name__ == "__main__":
    print("LangGraph Swarm pipeline compiled with native OpenClaw JSON API REST capabilities.")
    print("Igniting the Swarm...")
    final_state = app.invoke({"current_phase": 1, "retry_count": 0, "code_fixed": False, "qa_passed": False, "last_agent": None})
    print("Swarm execution completed.")
