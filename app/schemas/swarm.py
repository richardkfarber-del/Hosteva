from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

class SwarmStateUpdate(BaseModel):
    agent_name: str
    ticket_id: str
    status: Literal['BACKLOG', 'REFINEMENT', 'FAILED_REFINEMENT', 'BUILDING', 'BLOCKED', 'AUDITING', 'TESTING', 'REJECTED', 'PENDING_APPROVAL', 'DEPLOYING', 'DONE']
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SwarmStateResponse(SwarmStateUpdate):
    id: str
    updated_at: str
