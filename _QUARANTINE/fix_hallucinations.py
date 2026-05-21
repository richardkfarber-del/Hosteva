import os
import glob

project_dir = '/home/rdogen/OpenClaw_Factory/projects/Hosteva'

# Fix Coulson
coulson_path = os.path.join(project_dir, 'run_coulson_intervention.py')
with open(coulson_path, 'r') as f:
    coulson_content = f.read()
coulson_content = coulson_content.replace(
    "determine where the failure occurred and output a routing decision",
    "determine where the failure occurred. CRITICAL DIRECTIVE: DO NOT HALLUCINATE OR INVENT FAKE PULL REQUESTS, AGENT NAMES, OR FEATURES. ONLY CITE EXACT TEXT FROM THE CONTEXT PROVIDED. Output a routing decision"
)
with open(coulson_path, 'w') as f:
    f.write(coulson_content)

# Fix Audits
audit_files = glob.glob(os.path.join(project_dir, 'run_audit_*.py'))
for audit_file in audit_files:
    with open(audit_file, 'r') as f:
        content = f.read()
    content = content.replace(
        "Audit the following Phase",
        "CRITICAL DIRECTIVE: DO NOT HALLUCINATE OR INVENT FAKE PULL REQUESTS, AGENT NAMES, OR FEATURES. ONLY USE EXACT TEXT FROM THE CONTEXT.\n\nAudit the following Phase"
    )
    with open(audit_file, 'w') as f:
        f.write(content)

print("Patched Coulson and Audit scripts.")
