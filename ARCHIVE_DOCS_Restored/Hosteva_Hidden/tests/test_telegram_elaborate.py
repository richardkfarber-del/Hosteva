import os
import sys
import subprocess

def send_detailed_alert(node_name, status, details):
    message = f"[{node_name}] {status}\nDetails: {details}"
    try:
        subprocess.run(["openclaw", "message", "send", "-t", "8675276831", "--channel", "telegram", "-m", message], check=False)
        print("Alert sent.")
    except Exception as e:
        print(f"Alert failed: {e}")

if __name__ == "__main__":
    send_detailed_alert("Coulson", "Routing Complete", "Ticket BUG-001 routed to Phase 2 (Iron Man).")
