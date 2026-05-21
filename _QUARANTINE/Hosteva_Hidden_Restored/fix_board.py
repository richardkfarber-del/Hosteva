import re

with open("project_board.md", "r") as f:
    content = f.read()

# Replace Gherkin scenarios with bulleted lists
replacements = {
    "**Given** an execution agent is initialized and assigned a task, **When** the worker is actively processing or waiting on local LLM inference, **Then** the worker must emit a background pulse to Redis every 30 seconds containing its current PID and timestamp.": "- Worker must emit a background pulse to Redis every 30 seconds containing its current PID and timestamp when actively processing or waiting on local LLM inference.",
    
    "**Given** the Watchdog daemon is running natively in WSL2, **When** the daemon reads the Redis hash and identifies a pulse timestamp older than 5 minutes, **Then** the daemon must flag the associated PID as unresponsive and terminate it.": "- Daemon must read the Redis hash and flag/terminate any PID with a pulse timestamp older than 5 minutes.",
    
    "**And** the daemon must strictly use system monotonic time to calculate the drift to ignore Windows sleep states.": "- Daemon must use system monotonic time to calculate drift to bypass Windows sleep states.",
    
    "**Given** the Watchdog daemon is actively monitoring the swarm, **When** a `MAINTENANCE.lock` file is detected on the native Linux EXT4 filesystem, **Then** the daemon must instantly suspend all monitoring, killing, and auto-restart actions.": "- Daemon must check for `MAINTENANCE.lock` on the Linux filesystem and instantly suspend all actions if detected.",
    
    "**And** the daemon must remain in a standby sleep loop until the lock file is removed.": "- Daemon must remain in a sleep loop until the lock file is removed.",
    
    "**Given** the persona migration script is initiated, **When** the backup process begins, **Then** it MUST route all backups to an isolated, timestamped directory (e.g., /archives/personas_YYYYMMDD_HHMMSS/).": "- Migration script MUST route all backups to an isolated, timestamped directory before proceeding.",
    
    "**Given** the Python orchestrator is preparing to compile the prompt context, **When** the orchestrator accesses the current state, **Then** the Python orchestrator patch MUST use atomic Redis locking.": "- Python orchestrator MUST use atomic Redis locking when accessing current state for context compilation."
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open("project_board.md", "w") as f:
    f.write(content)
