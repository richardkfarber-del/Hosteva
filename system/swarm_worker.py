import os
import json
import time
import logging
import subprocess
import uuid
from enum import Enum
from typing import Dict, Any, Optional

import redis
import requests
from requests.exceptions import RequestException

# ==========================================
# ENTERPRISE TELEMETRY (STARK ARCHITECTURE)
# ==========================================
LOG_FILE = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/pipeline.log'
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SwarmWorker] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# ENUMS (SHANG-CHI STRICT TYPING)
# ==========================================
class FatalRosterError(Exception):
    pass

class TaskState(str, Enum):
    PENDING = "PENDING"
    AUDITING = "AUDITING"
    DREAMSTATE_READY = "DREAMSTATE_READY"
    DONE = "DONE"
    FAILED_ESCALATED = "FAILED_ESCALATED"

# ==========================================
# WORKER DAEMON
# ==========================================
class SwarmWorker:
    """
    Enterprise-grade Swarm Worker.
    Built for resilience, scale, and uncompromising fault tolerance.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        fastapi_state_url: Optional[str] = None,
        openclaw_gateway_url: Optional[str] = None,
        openclaw_token: Optional[str] = None
    ) -> None:
        # Dependency Injection (Captain America Sandbox Protocol)
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.fastapi_state_url = fastapi_state_url or os.getenv("FASTAPI_STATE_URL", "http://localhost:8000/state/update")
        self.openclaw_gateway_url = openclaw_gateway_url or os.getenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789/v1/chat/completions")
        self.openclaw_token = openclaw_token or os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
        
        self.stream_name = "swarm:stream:tasks"
        self.group_name = "swarm_group"
        self.dlq_name = "swarm:stream:dlq"
        self.worker_id = f"worker-{uuid.uuid4().hex}"
        self.redis_client: Optional[redis.Redis] = None
        self.http_session = requests.Session()
        
        # API Circuit Breaker (Black Widow Protocol)
        self.circuit_breaker_fails = 0
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_cooldown = 60  # seconds
        self.last_failure_time = 0.0

    def connect_redis_with_backoff(self) -> None:
        """Shang-Chi: Resilient connection handling with exponential backoff."""
        self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        retries = 0
        while True:
            try:
                self.redis_client.ping()
                logger.info("Redis connection established.")
                try:
                    self.redis_client.xgroup_create(self.stream_name, self.group_name, id="0", mkstream=True)
                except redis.exceptions.ResponseError as e:
                    if "BUSYGROUP" not in str(e):
                        raise
                return
            except FatalRosterError as fre:
                logger.critical(f"Pipeline Halting: {fre}")
                raise
            except redis.exceptions.ConnectionError:
                retries += 1
                backoff = min(60, 2 ** retries)
                logger.error(f"Redis connection failed. Re-engaging in {backoff} seconds...")
                time.sleep(backoff)

    def _is_circuit_breaker_open(self) -> bool:
        """Prevents infinite loops when the Gateway goes dark."""
        if self.circuit_breaker_fails >= self.circuit_breaker_threshold:
            if time.time() - self.last_failure_time > self.circuit_breaker_cooldown:
                logger.info("Circuit Breaker half-open: attempting API call...")
                return False
            return True
        return False

    def sync_fastapi_state(self, ticket_id: str, status: TaskState, payload_data: Dict[str, Any]) -> None:
        """Syncs the final state to the FastAPI backend."""
        try:
            req = {
                "ticket_id": ticket_id,
                "status": status.value,
                "payload": payload_data
            }
            response = self.http_session.post(self.fastapi_state_url, json=req, timeout=10)
            response.raise_for_status()
            logger.info(f"[{ticket_id}] Synced state {status.value} to FastAPI backend.")
        except RequestException as e:
            logger.error(f"[{ticket_id}] Exception syncing state to FastAPI: {e}")

    def spawn_subagent(self, agent_id: str, prompt: str, ticket_id: str = "UNKNOWN") -> Optional[str]:
        # [SECURITY LOCK] Physical Roster Verification (Anti-Fragmentation)
        kebab_id = agent_id.replace('_', '-')
        agent_dir = f"/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents/{kebab_id}"
        if not os.path.exists(agent_dir):
            error_msg = f"[CRITICAL ANOMALY] Attempted to spawn non-existent agent '{agent_id}'. Expected directory {agent_dir} is missing. Halting to prevent memory fragmentation."
            logger.critical(error_msg)
            if ticket_id != "UNKNOWN":
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {"reason": "Missing Agent Configuration", "error": error_msg})
            raise FatalRosterError(error_msg)

        if self._is_circuit_breaker_open():
            logger.warning(f"Gateway Circuit Breaker is OPEN. Task execution for {agent_id} aborted.")
            return None

        headers = {"Content-Type": "application/json"}
        if self.openclaw_token:
            headers["Authorization"] = f"Bearer {self.openclaw_token}"
        
        payload = {
            "model": f"agent:{agent_id}",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            logger.info(f"Spawning native API request for agent: {agent_id}...")
            response = self.http_session.post(self.openclaw_gateway_url, headers=headers, json=payload, timeout=300)
            response.raise_for_status()
            
            data = response.json()
            result = data['choices'][0]['message']['content']
            
            self.circuit_breaker_fails = 0  # Reset on success
            return result
            
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Malformed OpenClaw Gateway API response schema: {e}")
            self.circuit_breaker_fails += 1
            self.last_failure_time = time.time()
            return None
        except RequestException as e:
            logger.error(f"Network exception spawning {agent_id}: {e}")
            self.circuit_breaker_fails += 1
            self.last_failure_time = time.time()
            return None

    def ack_task(self, stream_id: str) -> None:
        self.redis_client.xack(self.stream_name, self.group_name, stream_id)

    def requeue_task(self, stream_id: str, data: Dict[str, Any]) -> None:
        self.redis_client.xadd(self.stream_name, {"payload": json.dumps(data)})
        self.ack_task(stream_id)

    def dlq_task(self, stream_id: str, data: Dict[str, Any]) -> None:
        self.redis_client.xadd(self.dlq_name, {"payload": json.dumps(data)})
        self.ack_task(stream_id)

    def handle_pending(self, data: Dict[str, Any], ticket_id: str, task_desc: str, stream_id: str) -> None:
        logger.info(f"[{ticket_id}] Routing to Jarvis for LOE & Compute Tier analysis...")
        jarvis_prompt = (
            f"Analyze the Level of Effort (LOE) for this ticket: {ticket_id}\n\n"
            f"REQUIREMENTS:\n{task_desc}\n\n"
            f"DIRECTIVE: Determine if this is a simple/routine task or a difficult/complex task. "
            f"If routine, we will downgrade the team to local hardware to save compute. Reply with 'COMPUTE: LOCAL'. "
            f"If difficult, we will upgrade the team to Gemini. Reply with 'COMPUTE: GEMINI'. "
            f"Include a 1-sentence justification."
        )
        
        jarvis_output = self.spawn_subagent("jarvis", jarvis_prompt, ticket_id)
        compute_tier = "GEMINI (google/gemini-3-pro-preview)"
        
        if jarvis_output:
            if "COMPUTE: LOCAL" in jarvis_output.upper():
                compute_tier = "LOCAL (qwen2.5-coder / RTX 4070)"
            elif "COMPUTE: GEMINI" in jarvis_output.upper():
                compute_tier = "GEMINI (google/gemini-3-pro-preview)"
            logger.info(f"[{ticket_id}] Jarvis LOE Analysis Complete. Assigned Tier: {compute_tier}")
        else:
            logger.warning(f"[{ticket_id}] Jarvis analysis timed out. Defaulting to GEMINI.")

        assigned_agent = "iron_man"
        task_desc_lower = task_desc.lower()
        if "frontend" in task_desc_lower or "wasp" in task_desc_lower:
            assigned_agent = "wasp"
        elif "ant-man" in task_desc_lower:
            assigned_agent = "ant_man"
        elif "shang-chi" in task_desc_lower:
            assigned_agent = "shang_chi"
        elif "heimdall" in task_desc_lower or "deploy" in task_desc_lower:
            assigned_agent = "heimdall"
        elif "captain america" in task_desc_lower or "qa" in task_desc_lower or "uat" in task_desc_lower:
            assigned_agent = "captain_america"
        elif "wanda" in task_desc_lower or "scarlet witch" in task_desc_lower or "retro" in task_desc_lower or "deep write" in task_desc_lower:
            assigned_agent = "scarlet_witch"
            
        logger.info(f"[{ticket_id}] Routing to Execution Squad ({assigned_agent}) on {compute_tier}...")
        
        agent_prompt = (
            f"Sprint Task for Ticket: {ticket_id}\n"
            f"Assigned Compute Tier: {compute_tier}\n\n"
            f"REQUIREMENTS:\n{task_desc}\n\n"
            f"DIRECTIVE: You are locked out of the 'DONE' state. "
            f"You must write the code, verify locally, and yield a summary of your physical file changes. "
            f"Do not attempt to transition this ticket to DONE."
        )
        
        exec_output = self.spawn_subagent(assigned_agent, agent_prompt, ticket_id)
        
        if exec_output:
            try:
                subprocess.run(
                    ["python3", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/scripts/lobster_interceptor.py", "-"],
                    input=exec_output,
                    text=True,
                    check=True
                )
                logger.info(f"[{ticket_id}] Interceptor successfully processed execution output.")
            except Exception as e:
                logger.error(f"[{ticket_id}] Interceptor failed: {e}")
                
            data["status"] = TaskState.AUDITING.value
            data["execution_output"] = exec_output
            
            self.requeue_task(stream_id, data)
            self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"execution_output": exec_output})
        else:
            logger.error(f"[{ticket_id}] Iron Man execution failed. Re-queueing as PENDING.")
            time.sleep(5)
            self.requeue_task(stream_id, data)

    def handle_auditing(self, data: Dict[str, Any], ticket_id: str, task_desc: str, stream_id: str) -> None:
        logger.info(f"[{ticket_id}] Routing to Coulson Tollbooth for physical verification...")
        exec_output = data.get("execution_output", "No output provided.")
        
        coulson_prompt = (
            f"Audit this execution for {ticket_id}:\n\n"
            f"Original Task Requirements:\n{task_desc}\n\n"
            f"Execution Squad Output:\n{exec_output}\n\n"
            f"DIRECTIVE: Verify physical reality. Check file paths, hashes, or run tests. "
            f"You MUST reply with a strict JSON object containing a 'status' key set to exactly 'VERIFIED' or 'REJECTED'. "
            f"If rejected, include a 'reason' key. Example: {{\"status\": \"VERIFIED\"}} or {{\"status\": \"REJECTED\", \"reason\": \"<explicit reasoning>\"}}."
        )
        
        coulson_output = self.spawn_subagent("phil_coulson", coulson_prompt, ticket_id)
        
        if not coulson_output:
            logger.warning(f"[{ticket_id}] Transient Gateway failure during QA. Re-queueing AUDITING. No strike burned.")
            time.sleep(5)
            self.requeue_task(stream_id, data)
            return

        try:
            coulson_json = coulson_output
            if "```json" in coulson_json:
                coulson_json = coulson_json.split("```json")[1].split("```")[0]
            elif "```" in coulson_json:
                coulson_json = coulson_json.split("```")[1].split("```")[0]
            
            audit_result = json.loads(coulson_json.strip())
            audit_status = audit_result.get("status", "").upper()
            audit_reason = audit_result.get("reason", coulson_output)
        except Exception as e:
            logger.warning(f"[{ticket_id}] Coulson output failed strict JSON parsing: {e}. Defaulting to REJECTED.")
            audit_status = "REJECTED"
            audit_reason = f"Prompt injection or schema violation detected. Raw output: {coulson_output}"

        if audit_status == "VERIFIED":
            logger.info(f"[{ticket_id}] Coulson VERIFIED. Transitioning ticket to DONE.")
            self.ack_task(stream_id)
            self.sync_fastapi_state(ticket_id, TaskState.DONE, {"coulson_audit": coulson_output})
        else:
            retry_count = data.get("retry_count", 0) + 1
            logger.warning(f"[{ticket_id}] Coulson REJECTED. Strike count: {retry_count}")
            
            if retry_count >= 3:
                logger.error(f"[{ticket_id}] 3-Strike Limit Hit. Escalating to Rocket Raccoon.")
                
                rocket_prompt = (
                    f"A ticket has failed 3 consecutive times.\n\n"
                    f"Ticket: {ticket_id}\n"
                    f"Task: {task_desc}\n"
                    f"Execution Output: {exec_output}\n"
                    f"Coulson Audit Failure: {coulson_output}\n\n"
                    f"DIRECTIVE: Perform a root-cause diagnostic on this failure loop. Propose a permanent fix. Do not write the code. Output your recommendation for the Secretary's review."
                )
                
                rocket_analysis = self.spawn_subagent("rocket_raccoon", rocket_prompt, ticket_id)
                
                data["status"] = TaskState.FAILED_ESCALATED.value
                self.dlq_task(stream_id, data)
                
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {
                    "reason": "3 strikes hit", 
                    "last_audit": coulson_output,
                    "rocket_diagnostic": rocket_analysis
                })
            else:
                data["status"] = TaskState.PENDING.value
                data["retry_count"] = retry_count
                data["task"] = f"{task_desc}\n\nPREVIOUS REJECTION REASON:\n{coulson_output}"
                self.requeue_task(stream_id, data)
                self.sync_fastapi_state(ticket_id, TaskState.PENDING, {"reason": "Rejected by Coulson", "retry_count": retry_count})

    def recover_orphaned_tasks(self) -> None:
        logger.info("Recovering orphaned tasks via XAUTOCLAIM...")
        try:
            response = self.redis_client.xautoclaim(
                self.stream_name,
                self.group_name,
                self.worker_id,
                300000,
                "0-0",
                count=100
            )
            
            if response and len(response) >= 2:
                claimed_messages = response[1]
                for message_id, message_data in claimed_messages:
                    logger.info(f"Recovered orphaned task: {message_id}")
                    self.process_message(message_id, message_data)
        except Exception as e:
            logger.error(f"Failed to recover orphaned tasks: {e}")
        logger.info("Orphaned tasks recovery complete.")

    def process_message(self, stream_id: str, message_data: Dict[str, str]) -> None:
        raw_message = message_data.get("payload")
        if not raw_message:
            if "ticket_id" in message_data:
                data = message_data
            else:
                logger.error(f"Malformed message data. Moving to DLQ: {message_data}")
                self.dlq_task(stream_id, message_data)
                return
        else:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                logger.error(f"Malformed JSON received. Moving to DLQ: {raw_message}")
                self.dlq_task(stream_id, {"payload": raw_message})
                return

        if not isinstance(data, dict):
            logger.warning(f"Payload is not a dictionary. Moving to DLQ: {raw_message}")
            self.dlq_task(stream_id, {"payload": str(raw_message)})
            return

        ticket_id = data.get("ticket_id", "UNKNOWN")
        status = data.get("status", TaskState.PENDING.value)
        task_desc = data.get("task", "")
        retry_count = data.get("retry_count", 0)
        
        logger.info(f"--- Received Event | Ticket: {ticket_id} | Status: {status} | Strikes: {retry_count} ---")
        
        try:
            if status == TaskState.PENDING.value:
                self.handle_pending(data, ticket_id, task_desc, stream_id)
            elif status == TaskState.AUDITING.value:
                self.handle_auditing(data, ticket_id, task_desc, stream_id)
            else:
                logger.warning(f"[{ticket_id}] Unhandled state: {status}. Dropping task.")
                self.ack_task(stream_id)
                
        except FatalRosterError as fre:
            logger.critical(f"Pipeline Halting for Ticket {ticket_id}: {fre}")
            data["status"] = TaskState.FAILED_ESCALATED.value
            self.dlq_task(stream_id, data)
            with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt", "w") as alert:
                alert.write(f"DIRECTOR ALERT: A fragmented or non-existent agent ({ticket_id}) was requested. The daemon has executed a Hard Stop to prevent memory bleeding. Check DLQ.")
        except redis.exceptions.ConnectionError:
            logger.error("Lost connection to Redis during processing.")
            self.connect_redis_with_backoff()
        except Exception as e:
            logger.error(f"Unexpected worker error processing {stream_id}: {e}")
            time.sleep(5)

    def run(self) -> None:
        self.connect_redis_with_backoff()
        self.recover_orphaned_tasks()
        logger.info(f"SwarmWorker {self.worker_id} started. Listening for tasks (XREADGROUP)...")
        
        while True:
            try:
                response = self.redis_client.xreadgroup(
                    self.group_name, 
                    self.worker_id, 
                    {self.stream_name: '>'}, 
                    block=0
                )
                
                if not response:
                    continue
                
                for stream, messages in response:
                    for message_id, message_data in messages:
                        self.process_message(message_id, message_data)
                        
            except FatalRosterError:
                logger.critical("Fatal roster error. Exiting.")
                break
            except redis.exceptions.ConnectionError:
                logger.error("Lost connection to Redis during xreadgroup.")
                self.connect_redis_with_backoff()
            except Exception as e:
                logger.error(f"Unexpected worker error in main loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    worker = SwarmWorker()
    worker.run()