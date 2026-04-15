import os
import sys
import time
import asyncio
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from temporalio.client import Client

# The Temporal workflow we are triggering
from swarm_workflow import VectorSwarmWorkflow

# Paths to watch
BASE_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"
BOARD_FILE = os.path.join(BASE_DIR, "project_board.md")

class SwarmStateWatcher(FileSystemEventHandler):
    def __init__(self):
        self.last_trigger = time.time()
        self.loop = asyncio.new_event_loop()

    def on_modified(self, event):
        # Only trigger on the exact board file
        if event.src_path == BOARD_FILE:
            # Debounce: Prevent rapid-fire double triggers (e.g. from editor saving swaps)
            current_time = time.time()
            if current_time - self.last_trigger > 5:
                self.last_trigger = current_time
                print(f"\n[Watcher] State change detected on {BOARD_FILE}")
                print("[Watcher] Firing webhook to Temporal.io cluster...")
                # Run the async temporal trigger
                self.loop.run_until_complete(self.trigger_temporal_workflow())

    async def trigger_temporal_workflow(self):
        try:
            client = await Client.connect("localhost:7233")
            
            # Generate a unique run ID based on the timestamp
            run_id = f"swarm-auto-trigger-{int(time.time())}"
            
            handle = await client.start_workflow(
                VectorSwarmWorkflow.run,
                "Dynamic_Sprint_Update",  # Passed to the workflow
                id=run_id,
                task_queue="hosteva-swarm-queue",
            )
            print(f"✅ Workflow pushed to queue successfully. Run ID: {handle.id}")
            
        except Exception as e:
            print(f"❌ Failed to trigger Temporal workflow: {e}")

def main():
    print(f"🚀 Initializing Temporal File-System Watcher (inotify) on: {BOARD_FILE}")
    event_handler = SwarmStateWatcher()
    observer = Observer()
    
    # Watch the directory, but the handler filters for the specific file
    observer.schedule(event_handler, path=BASE_DIR, recursive=False)
    observer.start()
    
    print("👀 Watcher is active. Waiting for file modifications...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
