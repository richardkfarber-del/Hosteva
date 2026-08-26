import os
import json
import sqlite3
from dream_worker import process_and_wipe_memory, MEMORY_FILE

class MockDB:
    def __init__(self, fail=False):
        self.fail = fail
    def cursor(self):
        class MockCursor:
            def __init__(self, fail):
                self.fail = fail
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            def execute(self, *args):
                if self.fail:
                    raise Exception("Mock DB Failure")
        return MockCursor(self.fail)
    def commit(self):
        if self.fail:
            raise Exception("Mock Commit Failure")
    def rollback(self):
        pass

# Setup fake memory file
with open(MEMORY_FILE, 'w') as f:
    f.write('{"agent_id": "test", "content": "hello", "metadata": {}, "embedding": [0.1, 0.2]}\n')

# Test 1: Successful DB Insert
print("Test 1: Success path")
process_and_wipe_memory(MockDB(fail=False))
assert os.path.getsize(MEMORY_FILE) == 0, "File should be truncated"

# Setup fake memory file again
with open(MEMORY_FILE, 'w') as f:
    f.write('{"agent_id": "test", "content": "hello", "metadata": {}, "embedding": [0.1, 0.2]}\n')

# Test 2: Failed DB Insert
print("Test 2: Failure path")
process_and_wipe_memory(MockDB(fail=True))
assert os.path.getsize(MEMORY_FILE) > 0, "File should NOT be truncated"

print("All tests passed.")
