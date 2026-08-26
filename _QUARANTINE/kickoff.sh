#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
nohup bash start_loop.sh > swarm_loop.log 2>&1 &
echo "Swarm restarted with PID $!"
