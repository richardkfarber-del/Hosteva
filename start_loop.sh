#!/bin/bash

cd /home/rdogen/OpenClaw_Factory/projects/Hosteva

echo "🚀 IGNITING MODULAR ASSEMBLY LINE..."

# Array of phases
phases=(
    "run_00_memory_injection.py"
    "run_phase1.py"
    "run_audit1.py"
    "run_02_ticket_creation.py"
    "run_audit_02.py"
    "run_03_planning_poker.py"
    "run_audit_03.py"
    "run_04_environment_setup.py"
    "run_audit_04.py"
    "run_05_development.py"
    "run_audit_05.py"
    "run_06_qa_deploy.py"
    "run_audit_06.py"
    "run_07_shadow_ops.py"
    "run_audit_07.py"
    "run_08_retrospective.py"
    "run_audit_08.py"
)

for phase in "${phases[@]}"; do
    echo "⚙️ Executing $phase..."
    /home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python "$phase"
    exit_code=$?

    if [ $exit_code -eq 3 ]; then
        echo "🚨 KICKBACK DETECTED in $phase! Routing to Coulson Intervention..."
        /home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python run_coulson_intervention.py
        coulson_exit=$?
        if [ $coulson_exit -ne 0 ]; then
            echo "🛑 COULSON RAISED THE ALARM. HALTING ASSEMBLY LINE."
            exit 1
        fi
        echo "🔄 Coulson resolved the kickback. Resuming loop..."
        # Note: In a real loop, we would route back to a specific phase based on Coulson's output.
        # For now, we continue or halt based on his exit code.
    elif [ $exit_code -eq 4 ]; then
        echo "🔥 VRAM CEILING HIT! HALTING ASSEMBLY LINE IMMEDIATELY."
        exit 1
    elif [ $exit_code -ne 0 ]; then
        echo "💥 UNKNOWN CRASH in $phase! Exit code: $exit_code. Halting."
        exit 1
    fi
done

echo "✅ FULL SPRINT PIPELINE COMPLETE."
