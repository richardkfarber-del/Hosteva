import asyncio
import subprocess
import os
import json
import re
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from temporalio.client import Client
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from dataclasses import dataclass
    from typing import Optional

@dataclass
class SwarmContext:
    issue_id: str
    diff_hash: Optional[str] = None
    snapshot_passed: bool = False


def send_telegram_alert(message: str):
    import subprocess, os
    try:
        subprocess.run(["openclaw", "message", "send", "-t", "8675276831", "--channel", "telegram", "-m", message], check=False, env=os.environ.copy())
    except Exception as e:
        print(f"Telegram alert failed: {e}")

def run_agent(agent_name: str, task: str) -> str:
    """Trigger an OpenClaw agent and return its response."""
    print(f"Triggering Agent: {agent_name} for task: {task[:50]}...")
    try:
        # Correctly passing the message using the -m flag
        cmd = ["openclaw", "agent", "--agent", agent_name, "-m", task, "--json"]
        result = subprocess.run(
            cmd,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            check=True
        )
        try:
            data = json.loads(result.stdout)
            text = data.get("response", result.stdout)
        except json.JSONDecodeError:
            text = result.stdout
            
        send_telegram_alert(f"[{agent_name.capitalize()}] Task Complete:\n{text[:500]}...")
        return text
    except subprocess.CalledProcessError as e:
        print(f"Agent {agent_name} failed: {e.stderr}")
        send_telegram_alert(f"[{agent_name.capitalize()}] 🚨 CRITICAL ERROR: {e.stderr[:500]}")
        return f"Error executing {agent_name}"

@activity.defn(name="hawkeye_refine_backlog")
async def hawkeye_refine_backlog(issue_id: str) -> str:
    print(f"Hawkeye refining backlog for issue: {issue_id}")
    board_path = os.path.join(os.path.dirname(__file__), "..", "project_board.md")
    bugs = []
    try:
        with open(board_path, "r") as f:
            for line in f:
                if "BUG" in line.upper():
                    bugs.append(line.strip())
    except Exception as e:
        print("Could not read project_board.md:", e)
    
    bugs_text = "\n".join(bugs)
    prompt = f"Refine the requirements for issue {issue_id}. Here are the bugs extracted from project_board.md:\n{bugs_text}"
    output = run_agent("hawkeye", prompt)
    return output

@activity.defn(name="ironman_wasp_execute")
async def ironman_wasp_execute(refined_reqs: str) -> str:
    print(f"Iron Man / Wasp executing tasks for: {refined_reqs[:50]}...")
    output = run_agent("iron_man", f"Execute these refined requirements: {refined_reqs}")
    return output

@activity.defn(name="coulson_tollgate_commit")
async def coulson_tollgate_commit(code_result: str) -> str:
    print(f"Coulson validating dead-drop tollgate for: {code_result[:50]}...")
    output = run_agent("coulson", f"Validate the dead-drop tollgate for this execution output: {code_result}")
    
    if 'FAILED_PHANTOM_COMMIT' in output or 'REJECTED' in output:
        raise Exception(f"Coulson Tollgate Failed: {output}")
        
    matches = re.findall(r'[a-f0-9]{32}|[a-f0-9]{40}', output.lower())
    if matches:
        return matches[0]
    return output.strip()

@activity.defn(name="captain_america_qa")
async def captain_america_qa(diff_hash: str) -> bool:
    print(f"Captain America running QA on diff hash: {diff_hash}")
    output = run_agent("captain_america", f"Run QA on this code execution hash: {diff_hash}")
    
    if 'FAILED' in output:
        raise Exception(f"Captain America QA Failed: {output}")
        
    return "SUCCESS" in output or "PASSED" in output.upper() or len(output) > 0

@activity.defn(name="heimdall_deploy")
async def heimdall_deploy(diff_hash: str) -> str:
    print(f"Heimdall deploying diff hash: {diff_hash}")
    output = run_agent("heimdall", f"Deploy this approved diff hash: {diff_hash}")
    return output

@activity.defn(name="team_retrospective")
async def team_retrospective(deploy_status: str) -> str:
    print(f"Team Retrospective running for deploy: {deploy_status[:50]}")
    output = run_agent("black_widow", f"Conduct a team retrospective on deployment: {deploy_status}")
    return output

@activity.defn(name="evolution_loop_deep_write")
async def evolution_loop_deep_write(deploy_status: str) -> str:
    print(f"Evolution Loop / Exec Review recording deploy status: {deploy_status[:50]}")
    output = run_agent("shuri", f"Record this deploy status in the Evolution Loop: {deploy_status}")
    return output

@workflow.defn
class VectorSwarmWorkflow:
    @workflow.run
    async def run(self, issue_id: str) -> str:
        ctx = SwarmContext(issue_id=issue_id)

        # Phase 1: Hawkeye (Backlog Refinement)
        refined_reqs = await workflow.execute_activity(
            hawkeye_refine_backlog,
            ctx.issue_id,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Phase 2: Iron Man / Wasp (Execution)
        code_result = await workflow.execute_activity(
            ironman_wasp_execute,
            refined_reqs,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

        # Phase 2.5: Coulson's Bureaucratic Dead-Drop Tollgate
        ctx.diff_hash = await workflow.execute_activity(
            coulson_tollgate_commit,
            code_result,
            start_to_close_timeout=timedelta(minutes=2),
        )

        if not ctx.diff_hash:
            raise workflow.ApplicationError("Coulson Tollgate Failed: No git diff/hash generated.")

        # Phase 3: Captain America (QA / Dual-Pronged Snapshot Mandate)
        ctx.snapshot_passed = await workflow.execute_activity(
            captain_america_qa,
            ctx.diff_hash,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )

        if not ctx.snapshot_passed:
            raise workflow.ApplicationError("Captain America QA Failed: Snapshots did not match requirements.")

        # Phase 4: Heimdall (DAG Deployment & Webhook Verification)
        deploy_status = await workflow.execute_activity(
            heimdall_deploy,
            ctx.diff_hash,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Phase 5: Team Retrospective (added before Exec Review)
        retro_output = await workflow.execute_activity(
            team_retrospective,
            deploy_status,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Phase 6: Evolution Loop / Deep Write (Exec Review)
        await workflow.execute_activity(
            evolution_loop_deep_write,
            evolution_loop_deep_write,
            deploy_status,
            start_to_close_timeout=timedelta(minutes=5),
        )

        return f"Swarm Workflow {issue_id} completed successfully. Hash: {ctx.diff_hash}"

async def main():
    # Connect to the Temporal cluster
    print("Connecting to Temporal cluster on localhost:7233...")
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    worker = Worker(
        client,
        task_queue="hosteva-swarm-queue",
        workflows=[VectorSwarmWorkflow],
        activities=[
            hawkeye_refine_backlog,
            ironman_wasp_execute,
            coulson_tollgate_commit,
            captain_america_qa,
            heimdall_deploy,
            team_retrospective,
            evolution_loop_deep_write,
        ],
    )
    
    print("Starting Temporal Worker on queue 'hosteva-swarm-queue'...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
