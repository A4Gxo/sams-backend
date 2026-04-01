from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

# 1. Basic Attendance Schemas
class AttendanceBase(BaseModel):
    student_id: int
    session_id: int

class AttendanceCreate(AttendanceBase):
    pass # Used for manual marking

class AttendanceResponse(AttendanceBase):
    attendance_id: int
    present: bool
    marked_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 2. Live Session Schemas (For Faculty)
class SessionStart(BaseModel):
    course_id: int
    lat: float
    lng: float

# 3. Check-In Schemas (For Students)
class CheckInRequest(BaseModel):
    session_id: int
    student_id: int
    otp_code: int
    lat: float
    lng: float

    class Config:
        # This allows the API to accept data even if it's sent as a 
        # dictionary or an ORM object
        from_attributes = True

# 4. Live Feed Schemas (For the Live Monitor)
class LiveStudent(BaseModel):
    id: int
    name: str
    roll_no: str
    time: str