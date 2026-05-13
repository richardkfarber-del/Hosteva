import os
import time
import signal
import redis
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - WATCHDOG - %(levelname)s - %(message)s')

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
PULSE_HASH = "worker:pulses"
MAINTENANCE_LOCK = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/MAINTENANCE.lock"
TIMEOUT_SECONDS = 300  # 5 minutes

def run_watchdog():
    logging.info(f"Starting Watchdog Daemon. Monitoring Redis hash: {PULSE_HASH}")
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    
    while True:
        # Check for Maintenance Lock
        if os.path.exists(MAINTENANCE_LOCK):
            logging.info("MAINTENANCE.lock detected. Suspending monitoring...")
            time.sleep(10)
            continue
        
        try:
            pulses = r.hgetall(PULSE_HASH)
            # System monotonic time ensures we don't trip falsely when Windows WSL2 wakes from sleep
            current_time = time.monotonic()
            
            for pid_str, pulse_str in pulses.items():
                try:
                    pid = int(pid_str)
                    pulse_time = float(pulse_str)
                    
                    drift = current_time - pulse_time
                    if drift > TIMEOUT_SECONDS:
                        logging.warning(f"PID {pid} flagged as unresponsive! Drift: {drift:.2f}s > {TIMEOUT_SECONDS}s.")
                        try:
                            os.kill(pid, signal.SIGKILL)
                            logging.info(f"Successfully terminated unresponsive PID {pid}.")
                        except ProcessLookupError:
                            logging.warning(f"PID {pid} not found. It may have already exited.")
                        except PermissionError:
                            logging.error(f"Permission denied when attempting to kill PID {pid}.")
                        except Exception as e:
                            logging.error(f"Unexpected error killing PID {pid}: {e}")
                        
                        # Remove from hash after termination
                        r.hdel(PULSE_HASH, pid_str)
                        
                except ValueError:
                    logging.error(f"Invalid pulse data for PID {pid_str}: {pulse_str}")
                    
        except redis.exceptions.ConnectionError:
            logging.error("Redis connection failed. Retrying...")
        except Exception as e:
            logging.error(f"Unexpected watchdog error: {e}")
            
        time.sleep(10)

if __name__ == "__main__":
    run_watchdog()
