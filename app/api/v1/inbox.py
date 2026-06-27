from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import datetime

from app.database import get_db
from app.core.security import get_current_user
from app.models.host import Host
from app.models.property import Property
from app.db_models import GuestMessage
from app.tasks.inbox import generate_ai_suggested_reply

router = APIRouter(
    prefix="/api/v1/inbox",
    tags=["inbox"]
)

class GuestMessageCreateRequest(BaseModel):
    property_id: str
    ota_source: str
    sender_name: str
    message_text: str

class ReplyRequest(BaseModel):
    reply_text: str

@router.get("")
def get_inbox_messages(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Fetch host
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")

    # 2. Get properties owned by host
    properties = db.query(Property).filter(Property.user_id == host.id).all()
    property_ids = [p.id for p in properties]

    # 3. Retrieve guest messages
    messages = db.query(GuestMessage).filter(
        GuestMessage.property_id.in_(property_ids)
    ).order_by(GuestMessage.created_at.desc()).all()

    return messages

@router.post("")
def receive_incoming_message(
    payload: GuestMessageCreateRequest,
    db: Session = Depends(get_db)
):
    # 1. Validate property exists
    prop = db.query(Property).filter(Property.id == payload.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # 2. Save guest message
    msg = GuestMessage(
        property_id=payload.property_id,
        ota_source=payload.ota_source,
        sender_name=payload.sender_name,
        message_text=payload.message_text,
        is_replied=0,
        created_at=datetime.datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # 3. Trigger suggested reply generation Celery task
    generate_ai_suggested_reply.delay(msg.id)

    return msg

@router.post("/{message_id}/reply")
def reply_to_guest_message(
    message_id: int,
    payload: ReplyRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Fetch host
    host = db.query(Host).filter(Host.username == current_user.get("username")).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host profile not found")

    # 2. Fetch message
    msg = db.query(GuestMessage).filter(GuestMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    # 3. Check property ownership
    prop = db.query(Property).filter(
        Property.id == msg.property_id,
        Property.user_id == host.id
    ).first()
    if not prop:
        raise HTTPException(status_code=403, detail="Not authorized to access messages for this property")

    # 4. Save reply / update message
    msg.is_replied = 1
    db.commit()

    return {"status": "success", "message": "Reply saved successfully"}
