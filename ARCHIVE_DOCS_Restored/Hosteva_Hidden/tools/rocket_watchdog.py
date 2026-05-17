import time
import os
import re
from datetime import datetime

LEDGER_PATH = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/daily_ledger.md"
ALERT_PATH = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt"

def check_ledger():
    if not os.path.exists(LEDGER_PATH):
        return
    
    with open(LEDGER_PATH, 'r') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    if not lines:
        return

    # Basic loop detection: check if last 3 non-empty lines contain identical failure/feedback strings
    recent_lines = [l for l in lines if l.strip()][-3:]
    if len(recent_lines) == 3:
        if all("[FEEDBACK]" in l for l in recent_lines) or all("FAILED" in l for l in recent_lines):
            # Check if they are exactly the same type of failure
            if recent_lines[0] == recent_lines[1] == recent_lines[2]:
                trigger_alert("INFINITE LOOP DETECTED: The same feedback/failure has occurred 3 times consecutively.")
                return

def trigger_alert(message):
    with open(ALERT_PATH, 'w') as f:
        f.write(f"WATCHDOG ALERT: {message}\n")

if __name__ == "__main__":
    while True:
        try:
            check_ledger()
        except Exception as e:
            pass
        time.sleep(300)  # Check every 5 minutes
