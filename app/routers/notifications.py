from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
import subprocess
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

class StatusChangePayload(BaseModel):
    email: str
    property_address: str
    old_status: str
    new_status: str

def dispatch_email_script(payload: StatusChangePayload):
    # Calls Spider-Man's Web-Shooter script
    script_path = "/home/rdogen/agents/IronMan/web_shooter_email.sh"
    try:
        subprocess.run(
            [script_path, payload.email, payload.property_address, payload.old_status, payload.new_status],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error dispatching email for {payload.property_address}", exc_info=True)
    except FileNotFoundError as e:
        logger.error(f"Email script not found: {script_path}", exc_info=True)

@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_status_change_email(payload: StatusChangePayload, background_tasks: BackgroundTasks):
    """
    Simulates a zoning compliance engine status change.
    Dispatches a background task to send an email notification.
    """
    background_tasks.add_task(dispatch_email_script, payload)
    return {"message": "Notification dispatch triggered successfully"}
