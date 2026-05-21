import os
import json
from unittest.mock import MagicMock, patch
from dream_worker import process_and_wipe_memory, MEMORY_FILE

def test_successful_wipe():
    # 1. Setup mock memory file
    with open(MEMORY_FILE, 'w') as f:
        f.write(json.dumps({"agent_id": "test", "content": "test memory"}) + "\n")
        
    # 2. Mock DB and Embedding
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value = mock_cursor

    with patch('dream_worker.get_embedding', return_value=[0.1, 0.2, 0.3]):
        # Run function
        success = process_and_wipe_memory(db_conn=mock_db)
        
    # 3. Assertions
    assert success is True
    mock_db.commit.assert_called_once()
    
    # File should be empty
    assert os.path.getsize(MEMORY_FILE) == 0
    print("TEST PASSED: Memory file wiped successfully on DB commit.")

def test_failed_db_no_wipe():
    # 1. Setup mock memory file
    with open(MEMORY_FILE, 'w') as f:
        f.write(json.dumps({"agent_id": "test", "content": "test memory"}) + "\n")
        
    # 2. Mock DB to throw exception
    mock_db = MagicMock()
    mock_db.cursor.side_effect = Exception("DB Error")

    # Run function
    success = process_and_wipe_memory(db_conn=mock_db)
        
    # 3. Assertions
    assert success is False
    
    # File should NOT be empty
    assert os.path.getsize(MEMORY_FILE) > 0
    print("TEST PASSED: Memory file retained on DB failure.")
    
    # Cleanup
    os.remove(MEMORY_FILE)

if __name__ == "__main__":
    test_successful_wipe()
    test_failed_db_no_wipe()
