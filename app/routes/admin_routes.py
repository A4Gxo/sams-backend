from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app import models
from app.models.profiles import Student, Faculty 
from app.models.user import Department, User 
from app.models.attendance import Attendance
from app.schemas.admin import AdminStatsResponse, AdminCreateFaculty
from datetime import datetime
# The prefix "/admin" is applied to ALL routes in this file automatically.
router = APIRouter( tags=["Admin Control"])

# --- 1. DASHBOARD STATS ---
@router.get("/stats") 
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    """Calculates Admin Dashboard metrics using exact schema relationships."""
    total_students = db.query(models.Student).count()
    total_faculty = db.query(models.Faculty).count()
    total_departments = db.query(models.Department).count()
    
    total_marks = db.query(models.Attendance).count()
    total_presents = db.query(models.Attendance).filter(models.Attendance.present == True).count()
    global_attendance = round((total_presents / total_marks) * 100, 1) if total_marks > 0 else 0.0

    department_stats = []
    departments = db.query(models.Department).all()
    
    for dept in departments:
        student_count = db.query(models.Student).filter(
            models.Student.department_id == dept.department_id
        ).count()
        
        base_dept_attendance = db.query(models.Attendance).join(
            models.ClassSession, models.Attendance.session_id == models.ClassSession.session_id
        ).join(
            models.Course, models.ClassSession.course_id == models.Course.course_id
        ).filter(
            models.Course.department_id == dept.department_id
        )
        
        d_total_marks = base_dept_attendance.count()
        d_presents = base_dept_attendance.filter(models.Attendance.present == True).count()
            
        d_percent = round((d_presents / d_total_marks) * 100, 1) if d_total_marks > 0 else 0.0
        
        if d_percent >= 75:
            status = "Good"
        elif d_percent >= 60:
            status = "Warning"
        else:
            status = "Critical"

        dept_name = getattr(dept, 'department_name', getattr(dept, 'name', f"Dept {dept.department_id}"))

        department_stats.append({
            "name": dept_name,
            "students": student_count,
            "attendance": d_percent,
            "status": status
        })

    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_departments": total_departments, 
        "global_attendance": global_attendance,
        "department_stats": department_stats
    }

# --- 2. APPROVALS ---
@router.put("/approvals/{user_id}/approve")
def approve_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # --- 1. PREVENT DUPLICATES ---
    # Check if a profile already exists before creating a new one
    existing_student = db.query(models.Student).filter(models.Student.user_id == user_id).first()
    existing_faculty = db.query(models.Faculty).filter(models.Faculty.user_id == user_id).first()
    
    if existing_student or existing_faculty:
        user.is_approved = True # Ensure they are approved even if profile existed
        db.commit()
        return {"message": "User was already approved and profile exists."}

    # --- 2. GET NAMES SAFELY ---
    # Since 'first_name' isn't in your User table, we use a placeholder 
    # or get it from the registration data if you stored it elsewhere.
    f_name = getattr(user, 'first_name', "External")
    l_name = getattr(user, 'last_name', "Guest")

    try:
        user.is_approved = True

        if user.role == "external_student":
            new_student = models.Student(
                user_id=user.user_id,
                first_name=f_name,
                last_name=l_name,
                department_id=1, # Default Dept for Externals
                roll_no=f"EXT-{user.user_id}"
            )
            db.add(new_student)
            
        elif user.role == "external_faculty":
            new_faculty = models.Faculty(
                user_id=user.user_id,
                first_name=f_name,
                last_name=l_name,
                department_id=1 
            )
            db.add(new_faculty)

        db.commit()
        return {"message": f"Successfully approved {user.username} and created profile."}
        
    except Exception as e:
        db.rollback()
        # Log the error for debugging
        print(f"Approval Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create profile during approval.")
@router.get("/approvals/pending")
def get_all_pending_requests(db: Session = Depends(get_db)):
    """
    This is what the React 'Pending Approvals' page calls to 
    show the list of students/faculty waiting for access.
    """
    # Look for any user where is_approved is False
    pending_users = db.query(models.User).filter(models.User.is_approved == False).all()
    
    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "role": u.role,
            "institution": u.institution or "Guest",
            "date": u.created_at.strftime("%Y-%m-%d")
        } for u in pending_users
    ]

@router.delete("/approvals/{user_id}/reject")
def reject_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id, User.is_approved == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pending user not found")

    try:
        db.delete(user)
        db.commit()
        return {"message": "User request rejected and deleted."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reject user.")


# --- 3. COURSE ASSIGNMENT & FETCHING ---
class AssignFacultyRequest(BaseModel):
    faculty_id: int

@router.put("/courses/{course_id}/assign-faculty")
def assign_course_to_faculty(course_id: int, request: AssignFacultyRequest, db: Session = Depends(get_db)):
    """Links an existing course to a professor"""
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course.faculty_id = request.faculty_id
    db.commit()
    db.refresh(course)
    
    return {"message": "Course assigned successfully!", "course_name": course.course_name}

@router.get("/courses/")
def get_all_courses(db: Session = Depends(get_db)):
    """Fetches all available courses from the database."""
    courses = db.query(models.Course).all()
    return courses


# app/routes/faculty_routes.py (or admin_routes.py)

@router.post("/faculty")
def create_faculty(data: AdminCreateFaculty, db: Session = Depends(get_db)):
    # 1. Check if the email already exists
    existing_user = db.query(models.User).filter(models.User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # 2. Create the User account FIRST
        # Note: In production, hash the password!
        new_user = models.User(
            username=data.username,
            password_hash=data.password, 
            role=data.role,
            is_approved=True # Since Admin is creating them, approve immediately
        )
        db.add(new_user)
        
        # db.flush() assigns an ID to new_user without permanently saving to DB yet
        db.flush() 

        # 3. Create the Faculty profile using the newly generated user_id
        new_faculty = models.Faculty(
            user_id=new_user.user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            department_id=data.department_id
        )
        db.add(new_faculty)
        
        # 4. Save both to the database together!
        db.commit()
        return {"message": "Faculty member created successfully!"}
        
    except Exception as e:
        db.rollback() # If anything fails, cancel the whole operation
        raise HTTPException(status_code=500, detail=str(e))
    
# app/routes/admin_routes.py
from sqlalchemy import func

@router.get("/master-report")
def get_master_analytics_report(db: Session = Depends(get_db)):
    # 1. Gather Total Counts
    total_students = db.query(models.Student).count()
    total_faculty = db.query(models.Faculty).count()
    total_courses = db.query(models.Course).count()
    
    # Assuming you have a ClassSession table for attendance:
    total_classes_held = db.query(models.ClassSession).count() 

    # 2. Get ALL Students details (Joined with User table for email, and Dept for name)
    students_query = db.query(models.Student, models.User.username.label("email"), models.Department.department_name)\
        .join(models.User, models.Student.user_id == models.User.user_id)\
        .join(models.Department, models.Student.department_id == models.Department.department_id).all()
    
    all_students = [{
        "student_id": s.Student.student_id,
        "first_name": s.Student.first_name,
        "last_name": s.Student.last_name,
        "email": s.email,
        "department_name": s.department_name,
        "year_of_study": s.Student.year_of_study
    } for s in students_query]

    # 3. Get ALL Faculty details
    faculty_query = db.query(models.Faculty, models.User.username.label("email"), models.Department.department_name)\
        .join(models.User, models.Faculty.user_id == models.User.user_id)\
        .join(models.Department, models.Faculty.department_id == models.Department.department_id).all()
        
    all_faculty = [{
        "faculty_id": f.Faculty.faculty_id,
        "first_name": f.Faculty.first_name,
        "last_name": f.Faculty.last_name,
        "email": f.email,
        "department_name": f.department_name
    } for f in faculty_query]

    # 4. Get Class & Attendance Logs
    # Note: Adjust these field names based on exactly what your Attendance and Session models are called!
    # 4. Get Class & Attendance Logs
    sessions = db.query(models.ClassSession).all()
    attendance_logs = []
    for session in sessions:
        # Get course
        course = db.query(models.Course).filter(models.Course.course_id == session.course_id).first()
        
        # ✅ NEW FIX: Get faculty from the Course instead of the Session!
        faculty = None
        if course:
             faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == course.faculty_id).first()
        
        present_count = db.query(models.Attendance).filter(
            models.Attendance.session_id == session.session_id, 
            models.Attendance.present == True 
        ).count()
        total_enrolled = db.query(models.Enrollment).filter(models.Enrollment.course_id == session.course_id).count()
        
        attendance_logs.append({
            "session_id": session.session_id,
            "created_at": str(session.created_at), 
            "course_name": course.course_name if course else "Unknown",
            "faculty_name": f"{faculty.first_name} {faculty.last_name}" if faculty else "Unknown",
            "students_present": present_count,
            "total_enrolled": total_enrolled,
            "attendance_percentage": round((present_count / total_enrolled * 100), 1) if total_enrolled > 0 else 0
        })
    
    # --- MISSING DATA QUERIES ---
    
    # Department Stats
    departments = db.query(models.Department).all()
    dept_stats = []
    for dept in departments:
        dept_stats.append({
            "department_id": dept.department_id,
            "department_name": dept.department_name,
            "student_count": db.query(models.Student).filter(models.Student.department_id == dept.department_id).count(),
            "faculty_count": db.query(models.Faculty).filter(models.Faculty.department_id == dept.department_id).count()
        })

    # Course Stats
    courses = db.query(models.Course).all()
    course_stats = []
    for course in courses:
        enrollment_count = db.query(models.Enrollment).filter(models.Enrollment.course_id == course.course_id).count()
        course_stats.append({
            "course_id": course.course_id,
            "course_name": course.course_name,
            "course_code": course.course_code,
            "enrolled_students": enrollment_count
        })

    # Year Stats
    year_stats = db.query(
        models.Student.year_of_study, 
        func.count(models.Student.student_id).label("count")
    ).group_by(models.Student.year_of_study).all()
    
    formatted_year_stats = [{"year": y.year_of_study or "Unknown", "count": y.count} for y in year_stats]

    # --- COMPLETE RETURN STATEMENT ---
    return {
        "overview": {
            "total_students": total_students,
            "total_faculty": total_faculty,
            "total_courses": total_courses,
            "total_classes_held": total_classes_held
        },
        "all_students": all_students,
        "all_faculty": all_faculty,
        "attendance_logs": attendance_logs,
        
        # Now these are fully populated!
        "by_department": dept_stats,
        "by_course": course_stats,
        "by_year": formatted_year_stats
    }

    


@router.get("/attendance-summaries")
def get_attendance_summaries(
    department_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
    semester_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # 1. Start a query that joins the Summary, Student, and Course tables
    query = db.query(
        models.SemesterAttendanceSummary,
        models.Student.first_name,
        models.Student.last_name,
        models.Student.department_id,
        models.Course.course_name
    ).join(
        models.Student, models.SemesterAttendanceSummary.student_id == models.Student.student_id
    ).join(
        models.Course, models.SemesterAttendanceSummary.course_id == models.Course.course_id
    )

    # 2. Apply Filters dynamically based on what the Admin selected
    if department_id:
        query = query.filter(models.Student.department_id == department_id)
    if course_id:
        query = query.filter(models.SemesterAttendanceSummary.course_id == course_id)
    if semester_name:
        query = query.filter(models.SemesterAttendanceSummary.semester_name == semester_name)

    # 3. Execute the query
    results = query.all()

    # 4. Format the output for React
    formatted_reports = []
    for summary, first_name, last_name, dept_id, course_name in results:
        formatted_reports.append({
            "id": summary.semester_summary_id,
            "student_name": f"{first_name} {last_name}",
            "course_name": course_name,
            "department_id": dept_id,
            "semester_name": summary.semester_name,
            "total_classes": summary.total_classes,
            "total_present": summary.total_present,
            "percentage": float(summary.percentage) if summary.percentage else 0.0,
            "eligible": summary.eligible
        })

    return formatted_reports


@router.get("/activity-logs")
def get_recent_activity(db: Session = Depends(get_db)):
    logs = []
    
    # 1. Fetch the 3 newest users (Auth Pulse)
    # Assuming your User model has a created_at column
    recent_users = db.query(models.User).order_by(models.User.user_id.desc()).limit(3).all()
    for user in recent_users:
        logs.append({
            "id": f"user_{user.user_id}",
            "user": user.username.split('@')[0], # Just use the first part of the email
            "action": f"Registered as {user.role}",
            "time": getattr(user, 'created_at', datetime.utcnow().isoformat()), 
            "type": "auth"
        })

    # 2. Fetch the 3 newest class sessions (Session Pulse)
    recent_sessions = db.query(models.ClassSession).order_by(models.ClassSession.session_id.desc()).limit(3).all()
    for session in recent_sessions:
        # ✅ THE FIX: Get the course first, then get the faculty from the course!
        course = db.query(models.Course).filter(models.Course.course_id == session.course_id).first()
        faculty = None
        if course:
            faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == course.faculty_id).first()
            
        name = f"Prof. {faculty.last_name}" if faculty else "System"
        
        logs.append({
            "id": f"session_{session.session_id}",
            "user": name,
            "action": f"Started {course.course_name if course else 'Session'}",
            "time": getattr(session, 'created_at', datetime.utcnow().isoformat()),
            "type": "session"
        })

    # 3. Sort by newest
    try:
        logs.sort(key=lambda x: str(x["time"]), reverse=True)
    except Exception:
        pass 

    return logs[:5]