from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.stripe import StripePlan

app = FastAPI()

@app.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    return db.query(StripePlan).all()