import os
import re

HIDDEN_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/Hosteva_Hidden"
OUT_DIR = "/home/rdogen/OpenClaw_Factory/projects/Hosteva"

def read_file(filename):
    path = os.path.join(HIDDEN_DIR, filename)
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# 1. Load raw files
project_overview = read_file("PROJECT_OVERVIEW.md")
design_state = read_file("DESIGN_STATE.md")
infra_profile = read_file("INFRASTRUCTURE_PROFILE.md")

# 2. Audit and clean OpenClaw/Lobster references
def clean_openclaw_refs(text):
    # Remove lines containing OpenClaw or Lobster references
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        if 'openclaw' not in line.lower() and 'lobster' not in line.lower():
            cleaned.append(line)
    return '\n'.join(cleaned)

clean_infra = clean_openclaw_refs(infra_profile)

# 3. Create specialized contexts

# Planning / Executive (Nick Fury, Vision, Falcon)
planning_context = f"""# Core Project Context
{project_overview}

## Architecture & Infrastructure
{clean_infra}
"""

# Engineering - Frontend (Wasp, Black Widow)
frontend_context = f"""# Core Project Context
{project_overview}

## UI/UX Design State
{design_state}
"""

# Engineering - Backend (Iron Man, Spider-Man, Hawkeye)
backend_context = f"""# Core Project Context
{project_overview}

## Infrastructure Constraints
{clean_infra}
"""

# Marketing (Star-Lord)
marketing_context = f"""# Core Project Context
{project_overview}
"""

# Compliance (Wanda)
compliance_context = f"""# Core Project Context
{project_overview}
"""

# Write artifacts
with open(os.path.join(OUT_DIR, "00_context_planning.md"), "w") as f:
    f.write(planning_context)
with open(os.path.join(OUT_DIR, "00_context_frontend.md"), "w") as f:
    f.write(frontend_context)
with open(os.path.join(OUT_DIR, "00_context_backend.md"), "w") as f:
    f.write(backend_context)
with open(os.path.join(OUT_DIR, "00_context_marketing.md"), "w") as f:
    f.write(marketing_context)
with open(os.path.join(OUT_DIR, "00_context_compliance.md"), "w") as f:
    f.write(compliance_context)

print("Memory injection complete. Specialized contexts created.")
