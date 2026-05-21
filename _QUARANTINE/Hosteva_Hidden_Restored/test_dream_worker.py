import json
import os
import pytest
from unittest.mock import patch, mock_open
import dream_worker

def test_process_short_term_memory():
    mock_data = '{"content": "test1", "agent_id": "A1"}\n{"content": "test2", "agent_id": "A2"}\n'
    
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=mock_data)):
            memories = dream_worker.process_short_term_memory()
            assert len(memories) == 2
            assert memories[0]['content'] == 'test1'
            assert memories[1]['content'] == 'test2'

