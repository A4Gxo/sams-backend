from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])


# 1. Get attendance percentage of a student
@router.get("/student-percentage/{student_id}")
def get_student_percentage(student_id: int, db: Session = Depends(get_db)):

    query = text("""
        SELECT 
            student_id,
            ROUND(
                (COUNT(CASE WHEN status = 'Present' THEN 1 END) * 100.0) / COUNT(*), 
                2
            ) AS attendance_percentage
        FROM attendance
        WHERE student_id = :student_id
        GROUP BY student_id
    """)

    result = db.execute(query, {"student_id": student_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="No attendance data found")

    return {
        "student_id": result[0],
        "attendance_percentage": result[1]
    }


# 2. Monthly attendance report (using your VIEW)
@router.get("/monthly")
def get_monthly_report(db: Session = Depends(get_db)):

    query = text("SELECT * FROM student_monthly_report")

    result = db.execute(query).fetchall()

    return [dict(row._mapping) for row in result]


# 3. Course-wise attendance summary
@router.get("/course-summary/{course_id}")
def get_course_summary(course_id: int, db: Session = Depends(get_db)):

    query = text("""
        SELECT 
            course_id,
            COUNT(*) AS total_classes,
            COUNT(CASE WHEN status = 'Present' THEN 1 END) AS present_count,
            ROUND(
                (COUNT(CASE WHEN status = 'Present' THEN 1 END) * 100.0) / COUNT(*),
                2
            ) AS attendance_percentage
        FROM attendance
        WHERE course_id = :course_id
        GROUP BY course_id
    """)

    result = db.execute(query, {"course_id": course_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="No data found for this course")

    return {
        "course_id": result[0],
        "total_classes": result[1],
        "present_count": result[2],
        "attendance_percentage": result[3]
    }