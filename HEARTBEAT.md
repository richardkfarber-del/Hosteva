# SWARM HEARTBEAT PROTOCOL

A background Python daemon (Rocket's Watchdog) runs every 5 minutes independent of the Orchestrator. 

**Orchestrator Instructions:**
1. Check if `/home/rdogen/OpenClaw_Factory/projects/Hosteva/CRITICAL_ALERT.txt` exists.
2. If the file DOES NOT exist: The swarm is healthy. You MUST reply EXACTLY `HEARTBEAT_OK` with no other text. Do not perform any manual analysis.
3. If the file DOES exist: Read the alert, immediately escalate the failure to the Director via Telegram, and then delete the alert file.
