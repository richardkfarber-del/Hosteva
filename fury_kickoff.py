import subprocess
import sys
import os

# Set the working directory to the script's location
os.chdir('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
python_executable = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python'

print("🚀 IGNITING MODULAR ASSEMBLY LINE (Fury's Python Kickoff)...")

phases = [
    "run_00_memory_injection.py",
    "run_phase1.py",
    "run_audit1.py",
    "run_02_ticket_creation.py",
    "run_audit_02.py",
    "run_03_planning_poker.py",
    "run_audit_03.py",
    "run_04_environment_setup.py",
    "run_audit_04.py",
    "run_05_development.py",
    "run_audit_05.py",
    "run_06_qa_deploy.py",
    "run_audit_06.py",
    "run_07_shadow_ops.py",
    "run_audit_07.py",
    "run_08_retrospective.py",
    "run_audit_08.py",
]

for phase in phases:
    print(f"⚙️ Executing {phase}...")
    result = subprocess.run([python_executable, phase])
    exit_code = result.returncode

    if exit_code == 3:
        print(f"🚨 KICKBACK DETECTED in {phase}! Routing to Coulson Intervention...")
        coulson_result = subprocess.run([python_executable, "run_coulson_intervention.py"])
        coulson_exit = coulson_result.returncode
        if coulson_exit != 0:
            print("🛑 COULSON RAISED THE ALARM. HALTING ASSEMBLY LINE.")
            sys.exit(1)
        print("🔄 Coulson resolved the kickback. Resuming loop...")
    elif exit_code == 4:
        print("🔥 VRAM CEILING HIT! HALTING ASSEMBLY LINE IMMEDIATELY.")
        sys.exit(1)
    elif exit_code != 0:
        print(f"💥 UNKNOWN CRASH in {phase}! Exit code: {exit_code}. Halting.")
        sys.exit(1)

print("✅ FULL SPRINT PIPELINE COMPLETE.")
