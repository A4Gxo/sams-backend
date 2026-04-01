from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_ # FIXED: Added 'or_' for search filtering
from typing import List, Optional

from app.database import get_db
from app import models   
from app.schemas.student import StudentCreate, StudentResponse
from app.utils.auth import get_current_user

router = APIRouter(tags=["Students"])

# --- 1. GET ALL STUDENTS (Combined Search & List) ---
@router.get("/", response_model=List[StudentResponse])
def get_students(search: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Unified route for the Admin Grid. 
    If a search query is provided, it filters by name.
    """
    query = db.query(models.Student)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.Student.first_name.ilike(search_filter),
                models.Student.last_name.ilike(search_filter)
            )
        )
    
    students = query.all()
    
    # Map email from User table if linked
    for s in students:
        if s.user:
            s.email = s.user.username 
        else:
            s.email = None
    return students

# --- 2. CREATE STUDENT ---
@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = models.Student(
        first_name=student.first_name,
        last_name=student.last_name,
        roll_no=student.roll_no,
        department_id=student.department_id,
        year_of_study=student.year_of_study,
        user_id=student.user_id 
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

# --- 3. UPDATE STUDENT ---
@router.put("/{student_id}")
def update_student(student_id: int, student_data: dict, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    db_student.first_name = student_data.get("first_name", db_student.first_name)
    db_student.last_name = student_data.get("last_name", db_student.last_name)
    db_student.roll_no = student_data.get("roll_no", db_student.roll_no)
    db_student.year_of_study = student_data.get("year_of_study", db_student.year_of_study)
    db_student.department_id = student_data.get("department_id", db_student.department_id)
    
    db.commit()
    db.refresh(db_student)
    
    return {"message": "Success", "student": db_student}

@router.get("/dashboard-data")
def get_student_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    
    # --- FIX 1: Correctly link the Student table to the logged-in User ---
    student = db.query(models.Student).filter(models.Student.user_id == current_user.user_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    enrollments = db.query(models.Enrollment, models.Course).join(
        models.Course, models.Enrollment.course_id == models.Course.course_id
    ).filter(models.Enrollment.student_id == student.student_id).all()

    enrolled_subjects = []
    total_present = 0
    total_sessions = 0

    for enrollment, course in enrollments:
        # 1. Count only FINISHED classes
        sessions_count = db.query(models.ClassSession).filter(
            models.ClassSession.course_id == course.course_id,
            models.ClassSession.is_active == False 
        ).count()

        # --- FIX 2: Join ClassSession to only count presence in FINISHED classes ---
        present_count = db.query(models.Attendance).join(
            models.ClassSession, models.Attendance.session_id == models.ClassSession.session_id
        ).filter(
            models.Attendance.student_id == student.student_id,
            models.ClassSession.course_id == course.course_id,
            models.ClassSession.is_active == False, # Must match sessions_count!
            models.Attendance.present == True
        ).count()

        # Calculate percentage safely
        percentage = (present_count / sessions_count * 100) if sessions_count > 0 else 0.0
        
        enrolled_subjects.append({
            "course_code": course.course_code,
            "course_name": course.course_name,
            "attendance": round(percentage, 1)
        })
        
        total_present += present_count
        total_sessions += sessions_count

    # Find live classes for enrolled subjects
    live_sessions = db.query(models.ClassSession, models.Course).join(
        models.Course, models.ClassSession.course_id == models.Course.course_id
    ).filter(
        models.ClassSession.is_active == True,
        models.ClassSession.course_id.in_(db.query(models.Enrollment.course_id).filter(models.Enrollment.student_id == student.student_id))
    ).all()

    return {
        "enrolled_subjects": enrolled_subjects,
        "overall_attendance": round((total_present / total_sessions * 100), 1) if total_sessions > 0 else 0.0,
        "live_sessions": [
            {
                "session_id": s.session_id,
                "subject": c.course_name, 
                "code": c.course_code,
                "room": "Main Block"
            } for s, c in live_sessions
        ]
    }

# --- 5. STUDENT REPORTS ---
@router.get("/reports/{student_id}")
def get_student_reports(student_id: int, db: Session = Depends(get_db)):
    report_data = []
    
    enrollments = db.query(models.Enrollment, models.Course).join(
        models.Course, models.Enrollment.course_id == models.Course.course_id
    ).filter(models.Enrollment.student_id == student_id).all()

    for enrollment, course in enrollments:
        total_classes = db.query(models.ClassSession).filter(
            models.ClassSession.course_id == course.course_id,
            models.ClassSession.is_active == False 
        ).count()
        
        present_count = db.query(models.Attendance).filter(
            models.Attendance.student_id == student_id,
            models.Attendance.session_id.in_(
                db.query(models.ClassSession.session_id).filter(models.ClassSession.course_id == course.course_id)
            ),
            models.Attendance.present == True
        ).count()
        
        absent_count = total_classes - present_count
        percentage = (present_count / total_classes * 100) if total_classes > 0 else 0.0
        
        report_data.append({
            "id": course.course_id,
            "subject": f"{course.course_name} ({course.course_code})",
            "totalClasses": total_classes,
            "present": present_count,
            "absent": absent_count,
            "percentage": round(percentage, 1)
        })

    return report_data