from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, Date, JSON, String, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"
    enrollment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    enrollment_date = Column(Date, server_default=func.current_date())

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class ClassSession(Base):
    __tablename__ = "class_sessions"
    session_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    session_date = Column(Date)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # --- NEW FIELDS FOR GPS & OTP ---
    location_lat = Column(Numeric)
    location_lng = Column(Numeric)
    otp_code = Column(String(6))
    is_active = Column(Boolean, default=True)
    # --------------------------------

    # Relationship to allow: session.attendances
    attendances = relationship("Attendance", back_populates="session")

class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.session_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    present = Column(Boolean, default=False)
    marked_by = Column(Integer, ForeignKey("users.user_id")) # For manual overrides
    marked_at = Column(DateTime, server_default=func.now())

    # Relationships
    session = relationship("ClassSession", back_populates="attendances")
    student = relationship("Student") # Used to get names for the Live Feed

class AttendanceAudit(Base):
    __tablename__ = "attendance_audit"
    audit_id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("attendance.attendance_id"))
    changed_by = Column(Integer, ForeignKey("users.user_id"))
    changed_at = Column(DateTime, server_default=func.now())
    action = Column(String) # 'UPDATE', 'DELETE'
    details = Column(JSON)