from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    roll_no = Column(String(20), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    year_of_study = Column(Integer)
    department_id = Column(Integer, ForeignKey("departments.department_id"))

    # Relationships
    user = relationship("User", back_populates="student")
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")

class Faculty(Base):
    __tablename__ = "faculty"

    faculty_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    first_name = Column(String(100))
    last_name = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.department_id"))

    # Relationships
    user = relationship("User", back_populates="faculty")
    department = relationship("Department", back_populates="faculty")
    courses = relationship("Course", back_populates="faculty")

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True)
    course_name = Column(String(200))
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id"))
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    
    # Relationships
    faculty = relationship("Faculty", back_populates="courses")
    department = relationship("Department", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")   