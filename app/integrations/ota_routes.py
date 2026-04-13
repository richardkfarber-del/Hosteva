import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/integrations/ota",
    tags=["OTA Integrations"]
)

# Inline schemas for standardizing responses (these can map to your ota_schemas if preferred)
class AuthResponse(BaseModel):
    auth_url: str
    provider: str

class CallbackResponse(BaseModel):
    status: str
    provider: str
    message: str

class SyncResponse(BaseModel):
    sync_job_id: str
    status: str
    message: str

VALID_PROVIDERS = {"airbnb", "vrbo", "booking"}

@router.get("/{provider}/auth", response_model=AuthResponse)
async def ota_auth(provider: str):
    """
    Initiates the OAuth/auth flow for the specified OTA provider.
    """
    if provider.lower() not in VALID_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    # Mock auth URL generation
    auth_url = f"https://mock-{provider}.com/oauth/authorize?client_id=hosteva_mock&redirect_uri=https://api.hosteva.com/callback"
    return AuthResponse(auth_url=auth_url, provider=provider)


@router.get("/{provider}/callback", response_model=CallbackResponse)
async def ota_callback(provider: str, code: str = None, error: str = None):
    """
    Handles the callback from the OTA provider after the auth flow.
    """
    if provider.lower() not in VALID_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
    if error:
        raise HTTPException(status_code=400, detail=f"Auth error from {provider}: {error}")
        
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
        
    # Mock token exchange and storage logic here
    return CallbackResponse(
        status="success",
        provider=provider,
        message=f"Successfully authenticated and stored credentials for {provider}."
    )


async def mock_ingestion_job(provider: str, job_id: str):
    """
    Mock background task for ingesting listings from the OTA.
    """
    print(f"[JOB {job_id}] Starting sync from {provider}...")
    # Simulate network requests and database writes
    await asyncio.sleep(5)
    print(f"[JOB {job_id}] Finished syncing listings from {provider}.")


@router.post("/{provider}/sync", response_model=SyncResponse, status_code=status.HTTP_202_ACCEPTED)
async def ota_sync(provider: str, background_tasks: BackgroundTasks):
    """
    Triggers an asynchronous sync job to ingest listings from the specified OTA provider.
    """
    if provider.lower() not in VALID_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
    job_id = str(uuid.uuid4())
    
    # Queue the ingestion job in the background
    background_tasks.add_task(mock_ingestion_job, provider, job_id)
    
    return SyncResponse(
        sync_job_id=job_id,
        status="accepted",
        message=f"Sync job initiated for {provider}. Processing in the background."
    )