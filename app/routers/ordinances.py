from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import SessionLocal
from app.db_models import Ordinance

router = APIRouter(
    prefix="/api/ordinances",
    tags=["ordinances"]
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schemas
class OrdinanceIngestRequest(BaseModel):
    jurisdiction: str
    ordinance_text: str

class OrdinanceResponse(BaseModel):
    id: int
    jurisdiction: str
    ordinance_text: str

    class Config:
        orm_mode = True
        from_attributes = True

@router.post("/ingest", response_model=OrdinanceResponse)
def ingest_ordinance(payload: OrdinanceIngestRequest, db: Session = Depends(get_db)):
    new_ordinance = Ordinance(
        jurisdiction=payload.jurisdiction,
        ordinance_text=payload.ordinance_text
    )
    db.add(new_ordinance)
    db.commit()
    db.refresh(new_ordinance)
    return new_ordinance

@router.get("/", response_model=List[OrdinanceResponse])
def get_ordinances(db: Session = Depends(get_db)):
    return db.query(Ordinance).all()
