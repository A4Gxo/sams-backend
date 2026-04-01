from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.attendance import Enrollment
from app.models.profiles import Course, Student # Import Student to verify existence
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse

router = APIRouter(tags=["Enrollments"])

# 1. CREATE: Enroll a Student
@router.post("/", response_model=EnrollmentResponse)
def enroll_student(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    # A. Check if the Student exists
    student_exists = db.query(Student).filter(Student.student_id == enrollment.student_id).first()
    if not student_exists:
        raise HTTPException(status_code=404, detail="Student not found")

    # B. Check if the Course exists
    course_exists = db.query(Course).filter(Course.course_id == enrollment.course_id).first()
    if not course_exists:
        raise HTTPException(status_code=404, detail="Course not found")

    # C. Check for existing duplicate enrollment
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.course_id == enrollment.course_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Student is already enrolled in this subject")

    # D. Save to Database
    try:
        new_enrollment = Enrollment(**enrollment.model_dump())
        db.add(new_enrollment)
        db.commit()
        db.refresh(new_enrollment)
        return new_enrollment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Enrollment failed due to server error")

# 2. READ: Get all enrollments for a specific Student
@router.get("/student/{student_id}", response_model=List[EnrollmentResponse])
def get_student_enrollments(student_id: int, db: Session = Depends(get_db)):
    # We use joinedload to fetch course details (name, code) in a single SQL query
    return db.query(Enrollment).options(
        joinedload(Enrollment.course)
    ).filter(Enrollment.student_id == student_id).all()

# 3. READ: Get all students enrolled in a specific Course
@router.get("/course/{course_id}", response_model=List[EnrollmentResponse])
def get_course_enrollments(course_id: int, db: Session = Depends(get_db)):
    return db.query(Enrollment).options(
        joinedload(Enrollment.course)
    ).filter(Enrollment.course_id == course_id).all()

# 4. READ: Get every enrollment in the system
@router.get("/all", response_model=List[EnrollmentResponse])
def get_all_enrollments(db: Session = Depends(get_db)):
    return db.query(Enrollment).options(joinedload(Enrollment.course)).all()

# 5. DELETE: Unenroll a Student
@router.delete("/{enrollment_id}")
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == enrollment_id).first()
    
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment record not found")

    try:
        db.delete(db_enrollment)
        db.commit()
        return {"message": "Student successfully unenrolled from the course"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove enrollment")