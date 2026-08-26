import sys
import pytest
import os
os.chdir('/home/rdogen/OpenClaw_Factory/projects/Hosteva')
sys.path.insert(0, '/home/rdogen/OpenClaw_Factory/projects/Hosteva')
os.makedirs('app/static', exist_ok=True)
pytest.main(['-v', '-p', 'no:warnings', 'tests/test_subscriptions.py'])
