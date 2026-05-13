#!/bin/bash
# Hosteva OpenClaw Watchdog
# Runs via cron every 5 minutes.
# Checks for frozen subagent/ACP sessions.

export HOME=/home/rdogen
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH

WORKSPACE_DIR="/home/rdogen/OpenClaw_Factory/projects/Hosteva/.openclaw/.openclaw"
SESSIONS_DIR="$WORKSPACE_DIR/agents"

FROZEN=$(python3 -c "
import json
import time
import glob

current_time = time.time() * 1000
frozen = []
for path in glob.glob('$WORKSPACE_DIR/agents/*/sessions/sessions.json'):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        for key, info in data.items():
            if key == 'agent:main:main':
                continue
            status = info.get('status')
            if status == 'running':
                updated_at = info.get('updatedAt', 0)
                age_ms = current_time - updated_at
                if 600000 <= age_ms <= 3600000:
                    frozen.append(key)
    except Exception:
        pass
if frozen:
    print('FROZEN')
")

if [ -n "$FROZEN" ]; then
    if [ ! -f /tmp/openclaw_watchdog_last_alert ] || [ $(find /tmp/openclaw_watchdog_last_alert -mmin +30) ]; then
        /usr/local/bin/openclaw message send --channel telegram --target 8675276831 --message "🚨 **Watchdog Alert:** An active subagent or ACP harness session appears to have frozen (no activity in >10 minutes). Director, I am ready to dispatch Rocket to terminate it and reset the bridge upon your mark."
        touch /tmp/openclaw_watchdog_last_alert
    fi
fi
exit 0
