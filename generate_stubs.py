import os

d = '/home/rdogen/OpenClaw_Factory/projects/Hosteva/scrum_pipelines'
os.makedirs(d, exist_ok=True)

files = [
    '01_intake.py', '02_planning.py', '03_backlog.py', '04_tdd.py', 
    '06_review.py', '07_security.py', '08_deploy.py', '09_uat.py', 
    '10_retro.py', '11_memory.py', '12_executive.py', '13_consolidation.py'
]

for f in files:
    with open(os.path.join(d, f), 'w') as file:
        file.write(f"print('Running Phase {f} (Stub)')\n")

print("Stubs generated successfully.")
