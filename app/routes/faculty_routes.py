from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func  # Ensure or_ and func are both here
from pydantic import BaseModel
from typing import List, Optional

from app import models 
from app.database import get_db
from app.utils.auth import get_current_user 

router = APIRouter(tags=["Faculty"])

# --- 1. SCHEMAS ---
class FacultyUpdateSchema(BaseModel):
    first_name: str
    last_name: str
    department_id: int

    class Config:
        from_attributes = True

# --- 2. FACULTY DASHBOARD DATA ---
@router.get("/dashboard-data")
def get_faculty_dashboard(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # 1. Find the Faculty profile linked to the user
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")

    # 2. Fetch assigned courses
    courses = db.query(models.Course).filter(models.Course.faculty_id == faculty.faculty_id).all()

    # 3. Get active sessions for lookup
    active_sessions = db.query(models.ClassSession).filter(models.ClassSession.is_active == True).all()
    active_map = {s.course_id: s.session_id for s in active_sessions}

    return {
        "full_name": f"Prof. {faculty.first_name} {faculty.last_name}",
        "subjects": [
            {
                "id": c.course_id,
                "name": c.course_name,
                "code": c.course_code,
                "is_live": c.course_id in active_map,
                "session_id": active_map.get(c.course_id)
            } for c in courses
        ]
    }

# --- 3. GET ALL FACULTY (Admin Grid support) ---
@router.get("/")
def get_faculties(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Faculty)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.Faculty.first_name.ilike(search_filter),
                models.Faculty.last_name.ilike(search_filter)
            )
        )
    return query.all()

# --- 4. UPDATE FACULTY ---
@router.put("/{faculty_id}")
def update_faculty(faculty_id: int, faculty_data: FacultyUpdateSchema, db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    faculty.first_name = faculty_data.first_name
    faculty.last_name = faculty_data.last_name
    faculty.department_id = faculty_data.department_id
    
    try:
        db.commit()
        db.refresh(faculty)
        return {"message": "Updated successfully", "faculty": faculty.first_name}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database update failed")

# --- 5. DELETE FACULTY ---
@router.delete("/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db)):
    db_faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty_id).first()
    if not db_faculty:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    try:
        db.delete(db_faculty)
        db.commit()
        return {"message": "Faculty member deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete faculty. They might be assigned to subjects."
        )

# --- 6. ENROLLMENTS BY COURSE ---
@router.get("/enrollments/course/{course_id}")
def get_enrolled_students(course_id: int, db: Session = Depends(get_db)):
    enrolled_students = db.query(models.Student).join(
        models.Enrollment, models.Student.student_id == models.Enrollment.student_id
    ).filter(models.Enrollment.course_id == course_id).all()

    return [
        {
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "roll_no": student.roll_no,
            "status": "Absent" 
        }
        for student in enrolled_students
    ]

# --- 7. FACULTY ANALYTICS (Recharts support) ---
@router.get("/analytics")
def get_faculty_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")

    analytics_data = []
    courses = db.query(models.Course).filter(models.Course.faculty_id == faculty.faculty_id).all() 

    for course in courses:
        student_count = db.query(models.Enrollment).filter(models.Enrollment.course_id == course.course_id).count()
        classes_taken = db.query(models.ClassSession).filter(models.ClassSession.course_id == course.course_id).count()
        
        # Calculate real attendance for this course
        total_attendance_records = db.query(models.Attendance).join(models.ClassSession).filter(
            models.ClassSession.course_id == course.course_id
        ).count()
        
        present_records = db.query(models.Attendance).join(models.ClassSession).filter(
            models.ClassSession.course_id == course.course_id,
            models.Attendance.present == True
        ).count()

        attendance_percent = round((present_records / total_attendance_records * 100), 1) if total_attendance_records > 0 else 0.0
        
        analytics_data.append({
            "course": course.course_name,
            "students": student_count,
            "classesTaken": classes_taken,
            "attendance": attendance_percent
        })

    return analytics_data

# --- 8. DETAILED COURSE REPORT ---
@router.get("/course-report/{course_id}") 
def get_course_student_report(course_id: int, db: Session = Depends(get_db)):
    sessions = db.query(models.ClassSession).filter(models.ClassSession.course_id == course_id).all()
    session_ids = [s.session_id for s in sessions]
    total_classes = len(session_ids)

    enrollments = db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).all()
    student_ids = [e.student_id for e in enrollments]
    students = db.query(models.Student).filter(models.Student.student_id.in_(student_ids)).all()

    student_reports = []
    for student in students:
        presents = 0
        if total_classes > 0:
            presents = db.query(models.Attendance).filter(
                models.Attendance.session_id.in_(session_ids),
                models.Attendance.student_id == student.student_id,
                models.Attendance.present == True
            ).count()
            
        absents = total_classes - presents
        percentage = round((presents / total_classes * 100), 1) if total_classes > 0 else 0.0

        student_reports.append({
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "roll_no": student.roll_no,
            "present": presents,
            "absent": absents,
            "percentage": percentage
        })

    student_reports.sort(key=lambda x: x["first_name"])
    return {"total_classes": total_classes, "student_reports": student_reports}

# --- 9. HIGH-LEVEL CUMULATIVE REPORTS ---
@router.get("/reports-data")
def get_faculty_reports(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")

    courses = db.query(models.Course).filter(models.Course.faculty_id == faculty.faculty_id).all() 
    
    total_classes_all = 0
    total_present_all = 0
    total_absent_all = 0
    course_reports = []
    
    for course in courses:
        sessions = db.query(models.ClassSession).filter(models.ClassSession.course_id == course.course_id).all()
        session_ids = [s.session_id for s in sessions]
        c_total_classes = len(sessions)
        
        c_present = 0
        c_absent = 0
        
        if session_ids:
            c_present = db.query(models.Attendance).filter(
                models.Attendance.session_id.in_(session_ids),
                models.Attendance.present == True
            ).count()
            
            c_absent = db.query(models.Attendance).filter(
                models.Attendance.session_id.in_(session_ids),
                models.Attendance.present == False
            ).count()
            
        total_classes_all += c_total_classes
        total_present_all += c_present
        total_absent_all += c_absent
        
        c_total_marks = c_present + c_absent
        c_percentage = round((c_present / c_total_marks * 100), 1) if c_total_marks > 0 else 0.0
        
        course_reports.append({
            "subject_name": course.course_name,
            "subject_code": course.course_code,
            "total_classes": c_total_classes,
            "present": c_present,
            "absent": c_absent,
            "percentage": c_percentage
        })

    overall_marks = total_present_all + total_absent_all
    cumulative_percent = round((total_present_all / overall_marks * 100), 1) if overall_marks > 0 else 0.0

    return {
        "cumulative_percentage": cumulative_percent,
        "total_classes": total_classes_all,
        "total_present": total_present_all,
        "total_absent": total_absent_all,
        "course_reports": course_reports
    }

@router.post("/kill-zombie-sessions")
def kill_zombie_sessions(db: Session = Depends(get_db)):
    # Find ALL sessions that are currently marked as active
    zombies = db.query(models.ClassSession).filter(models.ClassSession.is_active == True).all()
    
    count = 0
    for zombie in zombies:
        zombie.is_active = False
        count += 1
        
    db.commit()
    return {"message": f"Successfully killed {count} zombie sessions!"}