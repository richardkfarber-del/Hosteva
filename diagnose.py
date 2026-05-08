import subprocess

tracer_code = """
import sys
import trace
tracer = trace.Trace(count=False, trace=True, ignoredirs=[sys.prefix, sys.exec_prefix])
tracer.run('import workflow')
"""

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_trace.py", "w") as f:
    f.write(tracer_code)

try:
    res = subprocess.run(
        ["/home/rdogen/OpenClaw_Factory/projects/Hosteva/venv/bin/python", "/home/rdogen/OpenClaw_Factory/projects/Hosteva/run_trace.py"],
        cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva",
        capture_output=True,
        text=True,
        timeout=3600
    )
    print("PROCESS COMPLETED WITHOUT HANGING.")
    print("STDOUT (last 20 lines):")
    print("\n".join(res.stdout.splitlines()[-20:]))
    if res.stderr:
        print("STDERR:", res.stderr)
except subprocess.TimeoutExpired as e:
    print("PROCESS TIMED OUT (HANG DETECTED).")
    if e.stdout:
        out = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else e.stdout
        print("\nLast 30 lines of execution trace before hang:")
        print("\n".join(out.splitlines()[-30:]))
    if e.stderr:
        err = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else e.stderr
        print("\nSTDERR:", err)
