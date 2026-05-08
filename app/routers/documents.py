from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/documents", tags=["documents"])

class DocumentRequest(BaseModel):
    address: str

async def mock_redis_pdf_generation(address: str):
    """Mock background worker for PDF generation (TKT-201)."""
    await asyncio.sleep(2)
    print(f"Worker: Fetched template for property address {address}")
    print(f"Worker: Uploaded PDF to S3 storage for property address {address}")
    print(f"Worker: Saved S3 file_url to database for property address {address}")

@router.post("/generate")
async def generate_document(request: DocumentRequest, background_tasks: BackgroundTasks):
    """
    Triggers async Redis PDF generation.
    TKT-201
    """
    if not request.address:
        raise HTTPException(status_code=400, detail="Missing required property address data")
        
    background_tasks.add_task(mock_redis_pdf_generation, request.address)
    
    return {
        "status": "pending",
        "message": "Document generation task queued."
    }
