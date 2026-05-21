from app.core.short_term_memory import append_to_short_term_memory
import threading

def worker(agent_id, num):
    for i in range(num):
        append_to_short_term_memory(agent_id, f"test {i}", {"run": i})

threads = [
    threading.Thread(target=worker, args=("agent_1", 10)),
    threading.Thread(target=worker, args=("agent_2", 10))
]

for t in threads:
    t.start()
for t in threads:
    t.join()

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/short_term_memory.jsonl", "r") as f:
    lines = f.readlines()
    print(f"Total lines: {len(lines)}")
    assert len(lines) == 20
    print("SUCCESS: 20 lines written concurrently.")
