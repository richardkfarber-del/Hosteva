import os
import random

def execute_snap(target_dir):
    """
    O(N) complexity to simulate the Infinity Stones' effect.
    If we're going to snap the universe, we do it with structural efficiency.
    No spaghetti code. Just a clean, randomized halving of the target state.
    """
    try:
        entities = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
        if not entities:
            print("The universe is already empty.")
            return

        snap_count = len(entities) // 2
        victims = random.sample(entities, snap_count)
        
        for victim in victims:
            os.remove(os.path.join(target_dir, victim))
            
        print(f"Initialization complete. Snapped {snap_count} out of {len(entities)} entities.")
        print("I am Iron Man.")
    except Exception as e:
        print(f"Arc Reactor failure during snap sequence: {e}")

if __name__ == "__main__":
    test_dir = "universe_test_bed"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    execute_snap(test_dir)
