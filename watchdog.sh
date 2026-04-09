#!/bin/bash
# Hosteva OpenClaw Watchdog
# Runs via cron every 5 minutes.
# Checks for frozen subagent/ACP sessions.

export HOME=/home/rdogen
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH

WORKSPACE_DIR="/home/rdogen/OpenClaw_Factory/projects/Hosteva/.openclaw/.openclaw"
SESSIONS_DIR="$WORKSPACE_DIR/agents"

FROZEN=$(find "$SESSIONS_DIR" -type f -name "*.jsonl" -not -path "*/agents/main/*" -mmin +10 -mmin -60 2>/dev/null)

if [ -n "$FROZEN" ]; then
    if [ ! -f /tmp/openclaw_watchdog_last_alert ] || [ $(find /tmp/openclaw_watchdog_last_alert -mmin +30) ]; then
        /usr/local/bin/openclaw message send --channel telegram --target 8675276831 --message "🚨 **Watchdog Alert:** An active subagent or ACP harness session appears to have frozen (no activity in >10 minutes). Director, I am ready to dispatch Rocket to terminate it and reset the bridge upon your mark."
        touch /tmp/openclaw_watchdog_last_alert
    fi
fi
exit 0
