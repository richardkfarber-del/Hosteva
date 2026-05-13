import json
from src.swarm.graph import run_agent

print("Deploying Hawkeye to draft SPIKE-008...")
prompt = """
Read PIPELINE_OVERHAUL_DIRECTIVE.md. 
Draft a comprehensive SPIKE-008 ticket documenting the new 13-step pipeline. 
Include all state transitions, the fixes for REFINEMENT and REJECTED states, and the new post-prod QA, Retro, Exec Review, Security Review, and Deep Write steps. 
Output the draft as a markdown document.
"""
output = run_agent("hawkeye", prompt)
with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/SPIKE-008_DRAFT.md", "w") as f:
    f.write(output)
print("Draft complete.")
