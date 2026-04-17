import re

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'r') as f:
    content = f.read()

# I will use a precise regex to replace the if/elif/else block in run() with the heartbeat-wrapped block.

search = """                if status == TaskState.PENDING.value:
                    self.handle_pending(data, ticket_id, task_desc, raw_message)
                elif status == TaskState.AUDITING.value:
                    self.handle_auditing(data, ticket_id, task_desc, raw_message)
                else:
                    logger.warning(f"[{ticket_id}] Unhandled state: {status}. Dropping task.")
                    self.safe_move(self.processing_queue_name, "", raw_message, "")"""

replace = """                stop_heartbeat = threading.Event()
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

content = content.replace(search, replace)

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_worker.py', 'w') as f:
    f.write(content)
