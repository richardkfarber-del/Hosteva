import os
import sys
import random

def snap_universe(target_dir):
    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory.")
        sys.exit(1)

    entities = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    total = len(entities)
    to_dust = total // 2

    print(f"Total entities: {total}. Snapping {to_dust} out of existence. Perfect balance.")

    # O(N) time complexity Fisher-Yates shuffle
    random.shuffle(entities)

    for i in range(to_dust):
        target = os.path.join(target_dir, entities[i])
        os.remove(target)
        print(f"Dust: {entities[i]}")

    print("The deed is done.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 snap_algorithm.py <target_directory>")
        sys.exit(1)
    snap_universe(sys.argv[1])
