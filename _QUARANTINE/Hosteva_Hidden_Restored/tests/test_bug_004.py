import json
from unittest.mock import MagicMock
from system.swarm_worker import SwarmWorker, TaskState

def test_swarm_worker_passive_states():
    worker = SwarmWorker()
    worker.ack_task = MagicMock()
    worker.requeue_task = MagicMock()
    worker.redis_client = MagicMock()
    
    passive_states = [
        TaskState.DONE.value, TaskState.PENDING_APPROVAL.value, TaskState.BLOCKED.value, 
        TaskState.SPIKE_REVIEW.value, TaskState.PROD_DEPLOYED.value, TaskState.POST_PROD_QA.value, 
        TaskState.RETROSPECTIVE.value, TaskState.EXECUTIVE_REVIEW.value, TaskState.DEEP_WRITE_DONE.value
    ]
    
    for state in passive_states:
        worker.ack_task.reset_mock()
        worker.requeue_task.reset_mock()
        
        data = {
            "ticket_id": "BUG-004",
            "status": state
        }
        message_data = {"payload": json.dumps(data)}
        
        worker.process_message("test-stream-id", message_data)
        
        worker.ack_task.assert_called_once_with("test-stream-id")
        worker.requeue_task.assert_not_called()

def test_requeue_task_drops_passive_states():
    worker = SwarmWorker()
    worker.ack_task = MagicMock()
    worker.redis_client = MagicMock()
    
    passive_states = [
        TaskState.DONE.value, TaskState.PENDING_APPROVAL.value, TaskState.BLOCKED.value, 
        TaskState.SPIKE_REVIEW.value, TaskState.PROD_DEPLOYED.value, TaskState.POST_PROD_QA.value, 
        TaskState.RETROSPECTIVE.value, TaskState.EXECUTIVE_REVIEW.value, TaskState.DEEP_WRITE_DONE.value
    ]
    
    for state in passive_states:
        worker.ack_task.reset_mock()
        worker.redis_client.xadd.reset_mock()
        
        data = {
            "ticket_id": "BUG-004",
            "status": state
        }
        
        worker.requeue_task("test-stream-id", data)
        
        worker.ack_task.assert_called_once_with("test-stream-id")
        worker.redis_client.xadd.assert_not_called()
