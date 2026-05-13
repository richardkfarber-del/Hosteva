import sys

file_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/system/swarm_workflow.py"

with open(file_path, "r") as f:
    content = f.read()

old_block = """    except subprocess.CalledProcessError as e:
        print(f"Agent {agent_name} failed: {e.stderr}")
        return f"Error executing {agent_name}\""""

new_block = """    except subprocess.CalledProcessError as e:
        print(f"Agent {agent_name} failed: {e.stderr}")
        send_telegram_alert(f"[{agent_name.capitalize()}] 🚨 CRITICAL ERROR: {e.stderr[:500]}")
        return f"Error executing {agent_name}\""""

content = content.replace(old_block, new_block)

with open(file_path, "w") as f:
    f.write(content)
