import os
import signal
import subprocess

def halt_swarm():
    try:
        # Find processes matching our scripts
        cmd = "ps -ef | grep -E 'start_loop\.sh|run_[0-9]+.*\.py' | grep -v grep | awk '{print $2}'"
        result = subprocess.check_output(cmd, shell=True, text=True)
        pids = result.strip().split('\n')
        
        killed = 0
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGTERM)
                killed += 1
        print(f"SUCCESS: Halted {killed} Swarm processes.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    halt_swarm()
