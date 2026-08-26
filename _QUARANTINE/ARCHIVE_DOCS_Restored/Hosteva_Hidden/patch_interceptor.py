import re

with open('system/swarm_worker.py', 'r') as f:
    content = f.read()

interceptor_code = """
    def verify_execution_output(self, exec_output: str, ticket_id: str) -> Optional[str]:
        import re, os, hashlib
        paths = re.findall(r'`([a-zA-Z0-9_\\-\\./]+?\\.(?:py|js|json|html|sh|yml|txt|md))`', exec_output)
        paths += re.findall(r'(alembic/versions/[a-zA-Z0-9_]+\\.py)', exec_output)
        
        missing_files = []
        for p in set(paths):
            full_path = os.path.join("/home/rdogen/OpenClaw_Factory/projects/Hosteva", p)
            if "alembic/versions" in p or "app/" in p or "scripts/" in p:
                if not os.path.exists(full_path):
                    missing_files.append(p)
                else:
                    with open(full_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        logger.info(f"[{ticket_id}] Interceptor verified physical file {p} with MD5 {file_hash}")
                        
        if missing_files:
            error_msg = f"[INTERCEPTOR VETO] Execution Squad hallucinated files that do not exist physically on disk: {', '.join(missing_files)}"
            logger.warning(f"[{ticket_id}] {error_msg}")
            return error_msg
        return None

"""

if "def verify_execution_output(" not in content:
    content = content.replace("    def handle_building(", interceptor_code + "    def handle_building(")

old_interceptor_call = """        if exec_output:
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
            self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"previous_response": exec_output})"""

new_interceptor_call = """        if exec_output:
            interceptor_error = self.verify_execution_output(exec_output, ticket_id)
            if interceptor_error:
                logger.info(f"[{ticket_id}] Interceptor VETO. Re-queueing as BUILDING.")
                data["status"] = TaskState.BUILDING.value
                data["previous_response"] = f"Execution VETOED by Courier:\\n{interceptor_error}\\n\\nPlease try again and actually write the files."
                self.requeue_task(stream_id, data)
                self.sync_fastapi_state(ticket_id, TaskState.BUILDING, {"reason": "Interceptor Veto"})
            else:
                data["status"] = TaskState.AUDITING.value
                data["previous_response"] = exec_output
                self.requeue_task(stream_id, data)
                self.sync_fastapi_state(ticket_id, TaskState.AUDITING, {"previous_response": exec_output})"""

if old_interceptor_call in content:
    content = content.replace(old_interceptor_call, new_interceptor_call)
else:
    print("Warning: old interceptor call not found")

with open('system/swarm_worker.py', 'w') as f:
    f.write(content)
