from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

# 1. Base fields shared by all User schemas
class UserBase(BaseModel):
    username: str  # This is the email
    role: str      # 'admin', 'faculty', or 'student'

# 2. UPDATED: Schema for creating a user
class UserCreate(UserBase):
    password: str
    # --- ADD THESE FIELDS ---
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roll_no: Optional[str] = None
    department_id: Optional[int] = None
    year_of_study: Optional[int] = 1
    institution: Optional[str] = None  # For external users

# 3. Schema for Login requests
class UserLogin(BaseModel):
    email: str
    password: str

# 4. Schema for API responses
class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExternalRegisterRequest(BaseModel):
    first_name: str
    last_name: str
    username: str  # React sends formData.email as 'username'
    password: str
    role: str      # 'external_student' or 'external_faculty'
    institution: str

    class Config:
        from_attributes = True