from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.sql import func
from app.database import Base

class MonthlyAttendanceSummary(Base):
    __tablename__ = "monthly_attendance_summary"
    summary_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    year = Column(Integer)
    month = Column(Integer)
    total_classes = Column(Integer)
    present_count = Column(Integer)
    percentage = Column(Numeric(5, 2))
    eligible = Column(Boolean)
    last_updated = Column(DateTime, onupdate=func.now())

class SemesterAttendanceSummary(Base):
    __tablename__ = "semester_attendance_summary"
    semester_summary_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    course_id = Column(Integer, ForeignKey("courses.course_id"))
    year = Column(Integer)
    semester_name = Column(String)
    total_classes = Column(Integer)
    total_present = Column(Integer)
    percentage = Column(Numeric(5, 2))
    eligible = Column(Boolean)
    last_updated = Column(DateTime, server_default=func.now())

class StudentMonthlyReport(Base):
    __tablename__ = "student_monthly_report"
    # This matches your text list for denormalized reporting
    id = Column(Integer, primary_key=True) # Adding a primary key for SQLAlchemy
    student_id = Column(Integer, ForeignKey("students.student_id"))
    first_name = Column(String)
    last_name = Column(String)
    month = Column(Integer)
    year = Column(Integer)
    percentage = Column(Numeric(5, 2))
    eligible = Column(Boolean)