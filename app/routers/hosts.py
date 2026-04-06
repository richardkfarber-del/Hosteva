from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.host import Host
from app.schemas.host import HostCreate, HostResponse
from app.dependencies import get_api_key
from passlib.context import CryptContext
import uuid

# Task 1: Fix passlib/bcrypt 72-byte limit by using bcrypt_sha256 backend
# Task 2: Use response_model to prevent password hashes from leaking
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/hosts", tags=["Hosts"], dependencies=[Depends(get_api_key)])

@router.post("/", response_model=HostResponse, status_code=status.HTTP_201_CREATED)
def create_host(request: HostCreate, db: Session = Depends(get_db)):
    # Check if host exists
    existing_host = db.query(Host).filter((Host.username == request.username) | (Host.email == request.email)).first()
    if existing_host:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    
    # Hash password (bcrypt_sha256 handles passwords > 72 chars)
    hashed_password = pwd_context.hash(request.password)
    
    new_host = Host(
        id=str(uuid.uuid4()),
        username=request.username,
        email=request.email,
        password_hash=hashed_password
    )
    
    db.add(new_host)
    db.commit()
    db.refresh(new_host)
    
    return new_host

@router.get("/", response_model=List[HostResponse])
def get_hosts(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    limit = min(limit, 100)
    return db.query(Host).offset(skip).limit(limit).all()
