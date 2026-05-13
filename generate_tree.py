import os

with open('project_structure.txt', 'w') as f:
    for d in ['app', 'frontend', 'backend']:
        for root, dirs, files in os.walk(d):
            if '__pycache__' in root or 'node_modules' in root:
                continue
            for file in files:
                if not file.endswith('.pyc'):
                    f.write(os.path.join(root, file) + '\n')
