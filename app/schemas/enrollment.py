from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

# A small helper schema to send just the course details
class CourseShortResponse(BaseModel):
    course_name: str
    course_code: str
    
    model_config = ConfigDict(from_attributes=True)

class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentResponse(EnrollmentBase):
    enrollment_id: int
    enrollment_date: date
    # This is the "Magic" line that lets React see the names
    course: Optional[CourseShortResponse] = None

    model_config = ConfigDict(from_attributes=True)