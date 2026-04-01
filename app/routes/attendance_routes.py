import random
import math
from datetime import date, datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel # <-- Added for the autonomous mark schema

from app.database import get_db
# Ensure these imports match your actual file structure
from app import models 
from app.schemas.attendance import (
    AttendanceCreate, AttendanceResponse, 
    SessionStart, CheckInRequest
)

router = APIRouter(tags=["Attendance & Live Session"])

# --- HELPER: CALCULATE DISTANCE (METERS) ---
def calculate_distance(lat1, lng1, lat2, lng2):
    R = 6371000  # Radius of earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- 1. SMART STUDENT ENDPOINTS ---

@router.get("/active/{student_id}")
def get_student_active_sessions(student_id: int, db: Session = Depends(get_db)):
    """Returns only active sessions for courses the student is ENROLLED in."""
    active_sessions = db.query(models.ClassSession, models.Course).join(
        models.Course, models.ClassSession.course_id == models.Course.course_id
    ).join(
        models.Enrollment, models.Course.course_id == models.Enrollment.course_id
    ).filter(
        models.ClassSession.is_active == True,
        models.Enrollment.student_id == student_id
    ).all()

    return [
        {
            "session_id": s.session_id,
            "course_id": c.course_id,
            "course_name": c.course_name,
            "course_code": c.course_code,
            "otp_required": True # Security flag for frontend
        } for s, c in active_sessions
    ]

@router.get("/history/{student_id}/{course_id}")
def get_attendance_history(student_id: int, course_id: int, db: Session = Depends(get_db)):
    """Fetches the past attendance records for the Success Calendar."""
    records = db.query(models.Attendance).join(
        models.ClassSession, models.Attendance.session_id == models.ClassSession.session_id
    ).filter(
        models.Attendance.student_id == student_id,
        models.ClassSession.course_id == course_id
    ).all()
    
    return [{"date": r.marked_at.strftime("%Y-%m-%d"), "status": "Present"} for r in records]


# --- 2. LIVE GEOFENCING CHECK-IN ---

@router.post("/verify")
def student_gps_check_in(data: CheckInRequest, db: Session = Depends(get_db)):
    # 1. Find the active session
    session = db.query(models.ClassSession).filter(
        models.ClassSession.session_id == data.session_id, 
        models.ClassSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session expired or not active.")

    # 2. Verify OTP
    if str(data.otp_code) != str(session.otp_code):
        raise HTTPException(status_code=401, detail="Invalid OTP Code. Please check with your teacher.")

    # 3. Verify Distance (Geofence: 50 Meters)
    # Using float() to ensure numeric comparison
    dist = calculate_distance(
        data.lat, 
        data.lng, 
        float(session.location_lat), 
        float(session.location_lng)
    )
    
    if dist > 50000000: # 50 meters tolerance
        raise HTTPException(
            status_code=403, 
            detail=f"Out of range. You are {round(dist)}m away from the classroom."
        )

    # 4. Check for duplicate
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == data.student_id, 
        models.Attendance.session_id == data.session_id
    ).first()
    
    if existing:
        return {"message": "Attendance already recorded!"}

    # 5. Save Attendance
    try:
        attendance = models.Attendance(
            session_id=data.session_id,
            student_id=data.student_id, 
            present=True,
            marked_at=datetime.now()
        )
        db.add(attendance)
        db.commit()
        return {"message": "Check-in successful! Presence verified."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during check-in.")


# --- 3. FACULTY SESSION MGMT ---

@router.post("/session/start")
def start_live_session(data: SessionStart, db: Session = Depends(get_db)):
    """Faculty starts a class session. OTP is generated randomly."""
    # Close any other active sessions for this course first
    db.query(models.ClassSession).filter(
        models.ClassSession.course_id == data.course_id, 
        models.ClassSession.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    new_session = models.ClassSession(
        course_id=data.course_id,
        session_date=date.today(),
        location_lat=data.lat,
        location_lng=data.lng,
        otp_code=otp,
        is_active=True,
        created_at=datetime.now()
    )
    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return {"session_id": new_session.session_id, "otp_code": otp}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.get("/live/{session_id}")
def get_live_attendance(session_id: int, db: Session = Depends(get_db)):
    """Real-time list of students checked into the current session."""
    records = db.query(models.Attendance).join(
        models.Student, models.Attendance.student_id == models.Student.student_id
    ).filter(
        models.Attendance.session_id == session_id
    ).all()
    
    return {
        "students": [
            {
                "id": r.student.student_id,
                "name": f"{r.student.first_name} {r.student.last_name}",
                "roll_no": r.student.roll_no,
                "time": r.marked_at.strftime("%H:%M:%S")
            } for r in records
        ]
    }

@router.post("/session/terminate/{session_id}")
def terminate_session(session_id: int, db: Session = Depends(get_db)):
    """Ends an active class session."""
    # 1. Find the session
    session = db.query(models.ClassSession).filter(
        models.ClassSession.session_id == session_id,
        models.ClassSession.is_active == True
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Active session not found.")

    # 2. Mark it as inactive
    session.is_active = False
    
    # 3. Save to database
    db.commit()
    
    return {"message": "Session terminated successfully", "session_id": session_id}


# --- 4. SMART MANUAL OVERRIDE ---

# Schema for the incoming request
class AutonomousAttendance(BaseModel):
    course_id: int
    student_id: int
    status: str 
    date: str = None # "Present" or "Absent"

@router.post("/autonomous-mark")
def autonomous_manual_mark(data: AutonomousAttendance, db: Session = Depends(get_db)):
    """Allows Faculty to mark attendance safely for TODAY or ANY PAST DATE"""
    
    # 1. Determine the target date (Use provided date, or default to today)
    if data.date:
        target_date = datetime.strptime(data.date, "%Y-%m-%d").date()
    else:
        target_date = date.today()

    target_date_str = str(target_date)
    
    # 2. Safely find the session for THIS SPECIFIC DATE
    session = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == data.course_id,
        models.ClassSession.session_date == target_date
    ).first()

    try:
        # 3. If no session exists for this date, CREATE ONE silently!
        if not session:
            session = models.ClassSession(
                course_id=data.course_id,
                session_date=target_date,            
                created_at=datetime.now(),     
                location_lat=0.0,              
                location_lng=0.0,
                is_active=False, 
                otp_code="MANUAL" 
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
        # 4. Mark the student
        is_present = (data.status.lower() == "present")
        
        attendance = db.query(models.Attendance).filter(
            models.Attendance.session_id == session.session_id,
            models.Attendance.student_id == data.student_id
        ).first()
        
        if attendance:
            attendance.present = is_present
        else:
            new_attendance = models.Attendance(
                session_id=session.session_id,
                student_id=data.student_id,
                present=is_present,
                marked_at=datetime.now()
            )
            db.add(new_attendance)
            
        db.commit()
        
        return {
            "message": f"Successfully marked {data.status} for {target_date_str}", 
            "session_id": session.session_id
        }
        
    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@router.get("/faculty/history/{course_id}")
def get_course_session_history(course_id: int, db: Session = Depends(get_db)):
    """Fetches all past sessions for a specific course for the Calendar UI."""
    
    # 1. Find all sessions for this specific course
    sessions = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == course_id
    ).order_by(models.ClassSession.session_date.desc()).all()

    history = []
    for s in sessions:
        # 2. Count how many students were marked "Present" on this day
        present_count = db.query(models.Attendance).filter(
            models.Attendance.session_id == s.session_id,
            models.Attendance.present == True
        ).count()

        history.append({
            "session_id": s.session_id,
            "date": str(s.session_date), # Formats as "YYYY-MM-DD"
            "present_count": present_count,
            "is_active": s.is_active
        })

    return {"history": history}

@router.get("/roster/{course_id}/{target_date}")
def get_daily_roster(course_id: int, target_date: str, db: Session = Depends(get_db)):
    """Fetches the student list and their attendance status for a specific date."""
    # 1. Get all students enrolled in the course
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).all()
    student_ids = [e.student_id for e in enrollments]
    students = db.query(models.Student).filter(models.Student.student_id.in_(student_ids)).all()

    # 2. Check if a session exists for this date
    session = db.query(models.ClassSession).filter(
        models.ClassSession.course_id == course_id,
        models.ClassSession.session_date == target_date
    ).first()

    # 3. Map attendance
    result = []
    for student in students:
        status = "Absent"
        if session:
            att = db.query(models.Attendance).filter(
                models.Attendance.session_id == session.session_id,
                models.Attendance.student_id == student.student_id
            ).first()
            if att and att.present:
                status = "Present"
        
        result.append({
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "roll_no": student.roll_no,
            "status": status
        })
        
    return {"students": result}