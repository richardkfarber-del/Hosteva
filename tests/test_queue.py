import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch
from sqlalchemy import text
from app.queue import task_queue
from app.db_models import QueueTask

@pytest.fixture
def mock_db_session():
    with patch("app.queue.SessionLocal") as mock_session_local:
        mock_session = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_session
        yield mock_session

@pytest.mark.anyio
async def test_enqueue(mock_db_session):
    await task_queue.enqueue("test_task", {"key": "value"})
    
    # Verify add and commit were called
    mock_db_session.add.assert_called_once()
    added_task = mock_db_session.add.call_args[0][0]
    assert isinstance(added_task, QueueTask)
    assert added_task.task_name == "test_task"
    assert added_task.payload == json.dumps({"key": "value"})
    assert added_task.status == "pending"
    mock_db_session.commit.assert_called_once()

@pytest.mark.anyio
async def test_worker_processing(mock_db_session):
    # Setup mock to return a task once, then None
    mock_db_session.execute.return_value.fetchone.side_effect = [
        (1, "test_task", '{"key": "value"}'),
        None
    ]
    
    # Start worker manually for one iteration
    task_queue.running = True
    
    # We will run the worker loop for a tiny bit then cancel it
    worker_task = asyncio.create_task(task_queue.worker(1))
    await asyncio.sleep(0.2)
    task_queue.running = False
    worker_task.cancel()
    
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    # Ensure execute was called multiple times (select, update processing, update completed)
    assert mock_db_session.execute.call_count >= 3

@pytest.fixture
def anyio_backend():
    return 'asyncio'
