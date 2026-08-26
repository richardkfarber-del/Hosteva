#!/bin/bash

# =========================================================================
# ZERO-DOWNTIME SWARM EXECUTION LOOP (V3 PIPELINE)
# =========================================================================

# Ensure we are in the correct directory
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva

# Source the virtual environment
source venv/bin/activate

# Start the V3 Scrum Master pipeline
echo "🚀 IGNITING V3 MODULAR ASSEMBLY LINE..."
python scrum_master.py > scrum_master.log 2>&1

echo "✅ V3 Pipeline Execution Complete."
