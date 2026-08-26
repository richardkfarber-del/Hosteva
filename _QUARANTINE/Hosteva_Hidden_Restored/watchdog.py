import time
import redis
import os
import signal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Using system monotonic time for WSL2 compatibility
def run_watchdog():
    logger.info("Starting Watchdog daemon...")
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    while True:
        try:
            # Check for maintenance lock
            if os.path.exists("MAINTENANCE.lock"):
                logger.info("Maintenance lock detected. Suspending monitoring...")
                time.sleep(10)
                continue

            # Read worker pulses from Redis hash 'worker_pulses'
            pulses = r.hgetall("worker_pulses")
            current_time = time.monotonic()
            
            for pid_str, last_pulse_str in pulses.items():
                pid = int(pid_str)
                last_pulse = float(last_pulse_str)
                
                # Check if pulse is older than 5 minutes (300 seconds)
                if current_time - last_pulse > 300:
                    logger.warning(f"Worker PID {pid} is unresponsive (>5 mins). Terminating.")
                    try:
                        os.kill(pid, signal.SIGTERM)
                        r.hdel("worker_pulses", pid_str)
                        logger.info(f"Successfully terminated PID {pid} and removed from Redis.")
                    except ProcessLookupError:
                        logger.info(f"PID {pid} not found. Removing from tracking.")
                        r.hdel("worker_pulses", pid_str)
                    except Exception as e:
                        logger.error(f"Error killing PID {pid}: {e}")
                        
        except Exception as e:
            logger.error(f"Watchdog loop error: {e}")
            
        time.sleep(10)

if __name__ == "__main__":
    run_watchdog()
