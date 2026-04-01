from pydantic import BaseModel, ConfigDict
from typing import Optional

class StudentBase(BaseModel):
    roll_no: str
    first_name: str  # Must match the DB column exactly
    last_name: str   # Must match the DB column exactly
    year_of_study: int
    department_id: int

class StudentCreate(StudentBase):
    user_id: int

class StudentResponse(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    roll_no: str
    # 🚨 CRITICAL FIX: The 'Optional' allows the API to handle 
    # students who have a missing year in the database.
    year_of_study: Optional[int] = None 
    department_id: int
    email: Optional[str] = None 

    class Config:
        from_attributes = True

    
    
class StudentLogin(BaseModel):
    email: str
    password: str

    # This allows Pydantic to read SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
    