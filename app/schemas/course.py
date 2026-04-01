from pydantic import BaseModel

class CourseBase(BaseModel):
    course_name: str
    department_id: int = None 
class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    course_id: int
    course_name: str
    department_id: int
    
    class Config:
        from_attributes = True