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
    BACKLOG = "BACKLOG"
    REFINEMENT = "REFINEMENT"
    FAILED_REFINEMENT = "FAILED_REFINEMENT"
    BUILDING = "BUILDING"
    BLOCKED = "BLOCKED"
    AUDITING = "AUDITING"
    TESTING = "TESTING"
    REJECTED = "REJECTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    DEPLOYING = "DEPLOYING"
    DONE = "DONE"

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

    def send_telegram_alert(self, ticket_id: str, agent_name: str, status: str, coulson_summary: str) -> None:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        if not bot_token or not chat_id:
            logger.warning(f"[{ticket_id}] Telegram credentials missing. Skipping alert.")
            return

        text = f"[{ticket_id}] - [{agent_name}] - [{status}] - [{coulson_summary}]"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        try:
            response = self.http_session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"[{ticket_id}] Telegram alert sent ({status}).")
        except RequestException as e:
            logger.error(f"[{ticket_id}] Failed to send Telegram alert: {e}")

    def sync_fastapi_state(self, ticket_id: str, status: TaskState, payload_data: Dict[str, Any]) -> bool:
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
            return True
        except RequestException as e:
            logger.error(f"[{ticket_id}] Exception syncing state to FastAPI: {e}")
            return False

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
        # Strictly enforce Redis state decoupling
        filtered_data = {
            "ticket_id": data.get("ticket_id"),
            "status": data.get("status"),
            "previous_response": data.get("previous_response", "")
        }
        self.redis_client.xadd(self.stream_name, {"payload": json.dumps(filtered_data)})
        self.ack_task(stream_id)

    def dlq_task(self, stream_id: str, data: Dict[str, Any]) -> None:
        self.redis_client.xadd(self.dlq_name, {"payload": json.dumps(data)})
        self.ack_task(stream_id)


    def handle_backlog(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        logger.info(f"[{ticket_id}] BACKLOG -> Transitioning to REFINEMENT")
        data["status"] = TaskState.REFINEMENT.value
        success = self.sync_fastapi_state(ticket_id, TaskState.REFINEMENT, {"reason": "Auto-transition to refinement"})
        if success:
            self.requeue_task(stream_id, data)
        else:
            raise RequestException(f"Failed to sync state REFINEMENT for {ticket_id}")

    def handle_refinement(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.REFINEMENT, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] REFINEMENT -> Spawning Hawkeye/Vision for feasibility")
        prompt = f"""Refine this ticket for technical feasibility.\nTicket: {ticket_id}\nUse your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\nReply with JSON containing status 'BUILDING' or 'FAILED_REFINEMENT'."""
        output = self.spawn_subagent("vision", prompt, ticket_id)
        if output and "FAILED_REFINEMENT" in output:
            data["status"] = TaskState.FAILED_REFINEMENT.value
            self.sync_fastapi_state(ticket_id, TaskState.FAILED_REFINEMENT, {"reason": output})
            self.send_telegram_alert(ticket_id, "vision", TaskState.FAILED_REFINEMENT.value, output)
        else:
            data["status"] = TaskState.BUILDING.value
            self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Refinement successful"})
        self.requeue_task(stream_id, data)

    def handle_testing(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.TESTING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] TESTING -> Spawning Captain America")
        prompt = f"""Run headless QA tests for Ticket: {ticket_id}. Requires PNG snapshot path.\nUse your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\nReply with JSON containing status 'VERIFIED' or 'REJECTED'."""
        output = self.spawn_subagent("captain_america", prompt, ticket_id)
        if output and "REJECTED" in output:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": output})
        else:
            data["status"] = TaskState.PENDING_APPROVAL.value
            self.sync_fastapi_state(ticket_id, TaskState.PENDING_APPROVAL, {"reason": "Testing passed, awaiting approval"})
        self.requeue_task(stream_id, data)

    def handle_deploying(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.DEPLOYING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] DEPLOYING -> Spawning Heimdall")
        prompt = f"""Deploy ticket {ticket_id} to production.\nUse your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\nReply with 'DEPLOY_SUCCESS' or 'DEPLOY_FAILED'."""
        output = self.spawn_subagent("heimdall", prompt, ticket_id)
        if output and "DEPLOY_SUCCESS" in output:
            data["status"] = TaskState.DONE.value
            self.sync_fastapi_state(ticket_id, TaskState.DONE, {"reason": "Deployment successful"})
            self.send_telegram_alert(ticket_id, "heimdall", TaskState.DONE.value, "Deployment successful")
            self.ack_task(stream_id)
        else:
            data["status"] = TaskState.REJECTED.value
            self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": "Deployment failed"})
            self.requeue_task(stream_id, data)


    def handle_building(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] Routing to Jarvis for LOE & Compute Tier analysis...")
        jarvis_prompt = (
            f"Analyze the Level of Effort (LOE) for this ticket: {ticket_id}\n\n"
            f"Use your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\n\n"
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

        # Assign agent based on ticket description or context
        # Since we removed task_desc, we'll try to infer from data or default to iron_man
        assigned_agent = data.get("assigned_agent", "iron_man")
        
        logger.info(f"[{ticket_id}] Routing to Execution Squad ({assigned_agent}) on {compute_tier}...")
        
        previous_response = data.get("previous_response", "")
        fallback_context = f"\nPrevious Agent Response / Rejection:\n{previous_response}\n" if previous_response else ""
        
        agent_prompt = (
            f"Sprint Task for Ticket: {ticket_id}\n"
            f"Assigned Compute Tier: {compute_tier}\n"
            f"{fallback_context}\n"
            f"Use your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\n\n"
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
            data["previous_response"] = exec_output
            
            self.requeue_task(stream_id, data)
            self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"previous_response": exec_output})
        else:
            logger.error(f"[{ticket_id}] Execution failed. Re-queueing as PENDING.")
            time.sleep(5)
            self.requeue_task(stream_id, data)

    def handle_auditing(self, data: Dict[str, Any], ticket_id: str, stream_id: str) -> None:
        self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"reason": "Executing phase"})
        logger.info(f"[{ticket_id}] Routing to Coulson Tollbooth for physical verification...")
        exec_output = data.get("previous_response", "No output provided.")
        
        coulson_prompt = (
            f"Audit this execution for {ticket_id}:\n\n"
            f"Use your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\n\n"
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
            logger.info(f"[{ticket_id}] Coulson VERIFIED. Transitioning ticket to TESTING.")
            self.redis_client.delete(f"swarm:strikes:{ticket_id}")
            data["status"] = TaskState.TESTING.value
            data["previous_response"] = coulson_output
            self.requeue_task(stream_id, data)
            self.sync_fastapi_state(ticket_id, TaskState.TESTING, {"coulson_audit": coulson_output})
            self.send_telegram_alert(ticket_id, "phil_coulson", TaskState.TESTING.value, coulson_output)
        else:
            retry_count = self.redis_client.incr(f"swarm:strikes:{ticket_id}")
            logger.warning(f"[{ticket_id}] Coulson REJECTED. Strike count: {retry_count}")
            
            if retry_count >= 3:
                logger.error(f"[{ticket_id}] 3-Strike Limit Hit. Escalating to Rocket Raccoon.")
                
                rocket_prompt = (
                    f"A ticket has failed 3 consecutive times.\n\n"
                    f"Ticket: {ticket_id}\n"
                    f"Use your tools to read project_board.md, find your specific ticket_id, and extract your requirements.\n"
                    f"Execution Output: {exec_output}\n"
                    f"Coulson Audit Failure: {coulson_output}\n\n"
                    f"DIRECTIVE: Perform a root-cause diagnostic on this failure loop. Propose a permanent fix. Do not write the code. Output your recommendation for the Secretary's review."
                )
                
                rocket_analysis = self.spawn_subagent("rocket_raccoon", rocket_prompt, ticket_id)
                
                data["status"] = TaskState.FAILED_ESCALATED.value
                self.redis_client.delete(f"swarm:strikes:{ticket_id}")
                self.dlq_task(stream_id, data)
                
                self.sync_fastapi_state(ticket_id, TaskState.FAILED_ESCALATED, {
                    "reason": "3 strikes hit", 
                    "last_audit": coulson_output,
                    "rocket_diagnostic": rocket_analysis
                })
                self.send_telegram_alert(ticket_id, "rocket_raccoon", TaskState.FAILED_ESCALATED.value, rocket_analysis)
            else:
                # Transition to REJECTED first to satisfy FastAPI state machine
                sync_success = self.sync_fastapi_state(ticket_id, TaskState.REJECTED, {"reason": "Rejected by Coulson", "retry_count": retry_count})
                
                # If sync is successful, then move it back to BUILDING
                if sync_success:
                    self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Re-queueing after rejection"})
                    data["status"] = TaskState.BUILDING.value
                    data["previous_response"] = f"PREVIOUS REJECTION REASON:\n{coulson_output}"
                    self.requeue_task(stream_id, data)
                
                self.send_telegram_alert(ticket_id, "phil_coulson", "REJECTED", coulson_output)

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
        status = data.get("status", TaskState.BACKLOG.value)
        
        logger.info(f"--- Received Event | Ticket: {ticket_id} | Status: {status} ---")
        

        try:
            if status == TaskState.BACKLOG.value:
                self.handle_backlog(data, ticket_id, stream_id)
            elif status == TaskState.REFINEMENT.value:
                self.handle_refinement(data, ticket_id, stream_id)
            elif status == TaskState.BUILDING.value:
                self.handle_building(data, ticket_id, stream_id)
            elif status == TaskState.AUDITING.value:
                self.handle_auditing(data, ticket_id, stream_id)
            elif status == TaskState.TESTING.value:
                self.handle_testing(data, ticket_id, stream_id)
            elif status == TaskState.DEPLOYING.value:
                self.handle_deploying(data, ticket_id, stream_id)
            elif status in [TaskState.DONE.value, TaskState.PENDING_APPROVAL.value, TaskState.BLOCKED.value, TaskState.REJECTED.value, TaskState.FAILED_REFINEMENT.value]:
                logger.info(f"[{ticket_id}] State {status} is passive. No active handler required.")
                self.ack_task(stream_id)
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