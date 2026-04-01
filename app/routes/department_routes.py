from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import Department # Ensure this points to where 'Department' is defined

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/")
def get_departments(db: Session = Depends(get_db)):
    # This fetches EVERY department currently in your database
    return db.query(Department).all()