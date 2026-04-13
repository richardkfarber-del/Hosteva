import os, time, subprocess, glob, json

log_dir = "/tmp/openclaw/"
# Find the active OpenClaw log file
list_of_files = glob.glob(f"{log_dir}/openclaw-*.log")
if not list_of_files:
    print("No log files found. Exiting.")
    exit(1)

latest_file = max(list_of_files, key=os.path.getctime)
print(f"🦞 Sidecar Daemon online. Tailing: {latest_file}")

with open(latest_file, "r") as f:
    f.seek(0, 2) # Start at the end of the file
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.5)
            continue
        try:
            data = json.loads(line)
            # OpenClaw stores the raw chat text in the "0" index of the log payload
            msg = data.get("0", "")
            if isinstance(msg, str) and ("```bash" in msg or "```python" in msg):
                print("\n🦞 Caught Markdown Payload! Executing Vibranium Bridge...")
                process = subprocess.Popen(["python3", "scripts/lobster_interceptor.py"], stdin=subprocess.PIPE)
                process.communicate(input=msg.encode())
        except Exception:
            pass
