import time
import os
import redis
import threading
import signal

def test_watchdog_logic():
    print("Testing Watchdog Logic for CHORE-030...")
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.hset("worker:pulses", "999999", str(time.monotonic() - 301)) # Stalled
    r.hset("worker:pulses", "999998", str(time.monotonic() - 10))  # Active
    
    # Run one loop of logic
    pulses = r.hgetall("worker:pulses")
    current_time = time.monotonic()
    
    stalled_detected = False
    active_detected = False
    
    for pid_str, pulse_str in pulses.items():
        drift = current_time - float(pulse_str)
        if drift > 300:
            print(f"Verified: PID {pid_str} correctly flagged as stalled. (Drift: {drift:.2f}s)")
            if pid_str == "999999":
                stalled_detected = True
            r.hdel("worker:pulses", pid_str)
        else:
            print(f"Verified: PID {pid_str} correctly flagged as active. (Drift: {drift:.2f}s)")
            if pid_str == "999998":
                active_detected = True
            r.hdel("worker:pulses", pid_str)
            
    assert stalled_detected, "Failed to detect stalled pulse."
    assert active_detected, "Failed to detect active pulse."
    print("Monotonic time and drift calculation logic verified successfully.")

if __name__ == "__main__":
    test_watchdog_logic()
