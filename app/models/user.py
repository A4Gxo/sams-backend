from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(Text)
    role = Column(String)  # admin, faculty, student, external_student, external_faculty
    created_at = Column(DateTime, server_default=func.now())

    # --- NEW FIELDS FOR GUEST/EXTERNAL APPROVAL WORKFLOW ---
    # is_approved defaults to False. Admins/internal users must be set to True manually upon creation.
    is_approved = Column(Boolean, default=False) 
    # Optional field to track where the guest is coming from
    institution = Column(String, nullable=True) 

    # Relationships
    student = relationship("Student", back_populates="user", uselist=False)
    faculty = relationship("Faculty", back_populates="user", uselist=False)

class Department(Base):
    __tablename__ = "departments"
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String, unique=True)

    students = relationship("Student", back_populates="department")
    faculty = relationship("Faculty", back_populates="department")
    courses = relationship("Course", back_populates="department")