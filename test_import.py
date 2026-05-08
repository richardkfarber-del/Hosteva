import sys
import traceback
sys.path.insert(0, '/home/rdogen/OpenClaw_Factory/projects/Hosteva')

try:
    from app.main import app
    print('SUCCESS: App imported')
except Exception as e:
    traceback.print_exc()
