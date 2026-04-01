from pydantic import BaseModel
from typing import List

class DepartmentStat(BaseModel):
    name: str
    students: int
    attendance: float
    status: str

class AdminStatsResponse(BaseModel):
    total_students: int
    total_faculty: int
    total_departments: int
    global_attendance: float
    department_stats: List[DepartmentStat]

class AdminCreateFaculty(BaseModel):
    username: str
    password: str
    role: str = "faculty"
    first_name: str
    last_name: str
    department_id: int