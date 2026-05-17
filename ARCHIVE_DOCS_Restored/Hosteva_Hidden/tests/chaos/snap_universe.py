import random
import sys

def snap(universe):
    print(f"[JARVIS] Original architecture nodes: {len(universe)}")
    random.shuffle(universe)
    survivors = universe[:len(universe)//2]
    dusted = universe[len(universe)//2:]
    print(f"[JARVIS] Nodes dusted: {len(dusted)}")
    print(f"[JARVIS] Nodes surviving: {len(survivors)}")
    return survivors

if __name__ == "__main__":
    nodes = [
        "api-gateway", "auth-service", "user-db-primary", "user-db-replica",
        "redis-cache-1", "redis-cache-2", "payment-worker", "notification-worker",
        "search-elastic-1", "search-elastic-2"
    ]
    print("Tony Stark: Let's test the fault tolerance of this macro-architecture. Initiating Chaos Protocol: The Snap.")
    print("Tony Stark: And I... am... Iron Man. *SNAP*")
    survivors = snap(nodes)
    print(f"Remaining active nodes: {survivors}")
    print("Tony Stark: If the system goes down, it's a structural flaw. Rebuild it better.")
    sys.exit(0)
