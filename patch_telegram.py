import sys
import re

file_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_workflow.py"

with open(file_path, "r") as f:
    content = f.read()

telegram_func = """
def send_telegram_alert(message: str):
    import subprocess, os
    try:
        subprocess.run(["openclaw", "message", "send", "-t", "8675276831", "--channel", "telegram", "-m", message], check=False, env=os.environ.copy())
    except Exception as e:
        print(f"Telegram alert failed: {e}")

"""

# Add the function near the top, after the dataclass
if "def send_telegram_alert" not in content:
    content = content.replace("def run_agent(", telegram_func + "def run_agent(")

# Patch run_agent to send the alert
old_return = """        try:
            data = json.loads(result.stdout)
            return data.get("response", result.stdout)
        except json.JSONDecodeError:
            return result.stdout"""

new_return = """        try:
            data = json.loads(result.stdout)
            text = data.get("response", result.stdout)
        except json.JSONDecodeError:
            text = result.stdout
            
        send_telegram_alert(f"[{agent_name.capitalize()}] Task Complete:\\n{text[:500]}...")
        return text"""

content = content.replace(old_return, new_return)

with open(file_path, "w") as f:
    f.write(content)

print("Patch applied.")
