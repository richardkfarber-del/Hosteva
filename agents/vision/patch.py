import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

# Add LUA script
lua_script = """
    LUA_SAFE_MOVE = '''
    local removed = redis.call('LREM', KEYS[1], 1, ARGV[1])
    if removed > 0 then
        if KEYS[2] and KEYS[2] ~= '' then
            redis.call('RPUSH', KEYS[2], ARGV[2])
        end
        return 1
    end
    return 0
    '''
"""
content = content.replace('    def __init__(', lua_script + '\n    def __init__(')

# Add safe_move method
safe_move_method = """
    def safe_move(self, source_queue: str, target_queue: str, old_raw: str, new_raw: str) -> bool:
        if not target_queue:
            target_queue = ""
        res = self.redis_client.eval(self.LUA_SAFE_MOVE, 2, source_queue, target_queue, old_raw, new_raw)
        return bool(res)
"""
content = content.replace('    def connect_redis_with_backoff', safe_move_method + '\n    def connect_redis_with_backoff')

# Replace LREM/RPUSH pipes in handle_pending and handle_auditing
content = re.sub(
    r'pipe = self\.redis_client\.pipeline\(\)\s*pipe\.rpush\(self\.queue_name, json\.dumps\(data\)\)\s*pipe\.lrem\(self\.processing_queue_name, 1, raw_message\)\s*pipe\.execute\(\)',
    r'self.safe_move(self.processing_queue_name, self.queue_name, raw_message, json.dumps(data))',
    content
)
content = re.sub(
    r'pipe = self\.redis_client\.pipeline\(\)\s*pipe\.lrem\(self\.processing_queue_name, 1, raw_message\)\s*pipe\.execute\(\)',
    r'self.safe_move(self.processing_queue_name, "", raw_message, "")',
    content
)
content = re.sub(
    r'pipe = self\.redis_client\.pipeline\(\)\s*pipe\.rpush\(self\.dlq_name, json\.dumps\(data\)\)\s*pipe\.lrem\(self\.processing_queue_name, 1, raw_message\)\s*pipe\.execute\(\)',
    r'self.safe_move(self.processing_queue_name, self.dlq_name, raw_message, json.dumps(data))',
    content
)

# Replace recover_orphaned_tasks
new_recover = """    def recover_orphaned_tasks(self) -> None:
        \"\"\"Drains orphaned tasks from the processing queue back to the main queue.\"\"\"
        logger.info("Recovering orphaned tasks from processing queue...")
        tasks = self.redis_client.lrange(self.processing_queue_name, 0, -1)
        for task_str in tasks:
            try:
                task_data = json.loads(task_str)
                ticket_id = task_data.get("ticket_id", "UNKNOWN")
                lock_key = f"swarm:lock:{ticket_id}"
                
                if not self.redis_client.exists(lock_key):
                    logger.info(f"Recovering orphaned task: {ticket_id}")
                    self.safe_move(self.processing_queue_name, self.queue_name, task_str, task_str)
            except (json.JSONDecodeError, ValueError, TypeError):
                logger.error(f"Malformed task in processing queue. Moving to DLQ: {task_str}")
                self.safe_move(self.processing_queue_name, self.dlq_name, task_str, task_str)
        logger.info("Orphaned tasks recovery complete.")"""

content = re.sub(r'    def recover_orphaned_tasks\(self\) -> None:.*?(?=    def run\(self\) -> None:)', new_recover + '\n\n', content, flags=re.DOTALL)

# Add threading import if needed
if 'import threading' not in content:
    content = content.replace('import time', 'import time\nimport threading')

# Wrap run() handling with heartbeat
run_search = """                ticket_id = data.get("ticket_id", "UNKNOWN")
                status = data.get("status", TaskState.PENDING.value)
                task_desc = data.get("task", "")
                retry_count = data.get("retry_count", 0)
                
                logger.info(f"--- Received Event | Ticket: {ticket_id} | Status: {status} | Strikes: {retry_count} ---")
                
                if status == TaskState.PENDING.value:
                    self.handle_pending(data, ticket_id, task_desc, raw_message)
                elif status == TaskState.AUDITING.value:
                    self.handle_auditing(data, ticket_id, task_desc, raw_message)
                else:
                    logger.warning(f"[{ticket_id}] Unhandled state: {status}. Dropping task.")
                    pipe = self.redis_client.pipeline()
                    pipe.lrem(self.processing_queue_name, 1, raw_message)
                    pipe.execute()"""

run_replace = """                ticket_id = data.get("ticket_id", "UNKNOWN")
                status = data.get("status", TaskState.PENDING.value)
                task_desc = data.get("task", "")
                retry_count = data.get("retry_count", 0)
                
                logger.info(f"--- Received Event | Ticket: {ticket_id} | Status: {status} | Strikes: {retry_count} ---")
                
                stop_heartbeat = threading.Event()
                def heartbeat():
                    lock_key = f"swarm:lock:{ticket_id}"
                    self.redis_client.setex(lock_key, 60, "locked")
                    while not stop_heartbeat.is_set():
                        stop_heartbeat.wait(30)
                        if not stop_heartbeat.is_set():
                            self.redis_client.expire(lock_key, 60)
                            
                hb_thread = threading.Thread(target=heartbeat, daemon=True)
                hb_thread.start()
                
                try:
                    if status == TaskState.PENDING.value:
                        self.handle_pending(data, ticket_id, task_desc, raw_message)
                    elif status == TaskState.AUDITING.value:
                        self.handle_auditing(data, ticket_id, task_desc, raw_message)
                    else:
                        logger.warning(f"[{ticket_id}] Unhandled state: {status}. Dropping task.")
                        self.safe_move(self.processing_queue_name, "", raw_message, "")
                finally:
                    stop_heartbeat.set()
                    hb_thread.join()"""

content = content.replace(run_search, run_replace)

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)

