from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
# Ensure the model import is consistent
from app.models.profiles import Course 
from app.schemas.course import CourseCreate, CourseResponse
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/courses", tags=["Courses"])

# 1. CREATE: Create and Assign Course
@router.post("/", response_model=CourseResponse)
def create_course(course_in: CourseCreate, db: Session = Depends(get_db)):
    """
    Creates a new course and assigns it to a faculty member.
    FastAPI automatically validates 'course_in' using your CourseCreate schema.
    """
    
    # Check if course code already exists to avoid 500 errors
    existing_course = db.query(Course).filter(Course.course_code == course_in.course_code).first()
    if existing_course:
        raise HTTPException(
            status_code=400, 
            detail=f"Course code '{course_in.course_code}' is already registered."
        )

    try:
        new_course = Course(
            course_code=course_in.course_code,
            course_name=course_in.course_name,
            faculty_id=course_in.faculty_id,
            department_id=course_in.department_id
        )
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return new_course
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error: Check if Faculty or Department IDs exist.")
    except Exception as e:
        db.rollback()
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 2. READ ALL: Get all courses
@router.get("/", response_model=List[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

# 3. READ ONE: Get course by id
@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# 4. UPDATE: Update Course/Assignment (Fixes your "Update Failed" issue)
@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course_in: CourseCreate, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.course_id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")

    db_course.course_code = course_in.course_code
    db_course.course_name = course_in.course_name
    db_course.faculty_id = course_in.faculty_id
    db_course.department_id = course_in.department_id

    try:
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed. Check your data.")

# 5. DELETE: Remove Course
@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        db.delete(course)
        db.commit()
        return {"message": "Course deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete course. Students might be enrolled.")