import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def dispatch_email_alert(host_email: str, property_id: str, old_status: str, new_status: str):
    """
    Mock email service. Writes the payload to a JSON queue to simulate sending an email webhook.
    """
    payload = {
        "host_email": host_email,
        "property_id": property_id,
        "old_status": old_status,
        "new_status": new_status,
        "message": f"Alert: Your property {property_id} zoning status changed from {old_status} to {new_status}"
    }
    
    queue_path = Path("/tmp/email_queue.json")
    
    # In a real app we'd use async background tasks or Celery. For MVP, synchronous file append.
    with open(queue_path, "a") as f:
        f.write(json.dumps(payload) + "\n")
        
    logger.info(f"DISPATCHED EMAIL: to {host_email} regarding {property_id} status change to {new_status}")
