import os
import sys

# Ensure src is in the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from swarm.graph import send_telegram_alert

if __name__ == "__main__":
    print("Testing Telegram Alert...")
    send_telegram_alert("Hello Director, this is Iron Man. The Telegram CLI syntax patch is successful.")
    print("Test finished.")
