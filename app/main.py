from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models
from app.database import get_db
# Make sure faculty_routes is imported in your routes __init__.py or here
from app.routes import (
    student_routes, 
    attendance_routes, 
    enrollment_routes, 
    course_routes, 
    report_routes, 
    auth_routes, 
    admin_routes,
    faculty_routes # <-- Ensure this is imported
)

app = FastAPI(title="Student Attendance Management System API")

# --- CORS Configuration ---
origins = ["https://sams-frontend-18w7a9439-a4gxos-projects.vercel.app",
    "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- Routes Registration ---
app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])
app.include_router(faculty_routes.router, prefix="/faculty", tags=["Faculty"]) # <-- Standardized Prefix
app.include_router(student_routes.router, prefix="/students", tags=["Students"])
app.include_router(attendance_routes.router, prefix="/attendance", tags=["Attendance"])
app.include_router(course_routes.router, prefix="/courses", tags=["Courses"])
app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])
app.include_router(student_routes.router, prefix="/student", tags=["Student"])
app.include_router(enrollment_routes.router, prefix="/enrollments", tags=["Enrollments"])
# --- Essential Utility Routes ---

@app.get("/")
def root():
    return {"message": "SAMS API is fully operational"}

# This handles the dropdowns for the Frontend
@app.get("/departments/")
def read_departments(db: Session = Depends(get_db)):
    # Use the correct model path based on your models.py structure
    return db.query(models.Department).all()

@app.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    try:
        # Using .count() on the models
        t_students = db.query(models.Student).count()
        t_faculty = db.query(models.Faculty).count()
        t_depts = db.query(models.Department).count()
        
        departments = db.query(models.Department).all()
        dept_stats = []
        for d in departments:
            s_count = db.query(models.Student).filter(models.Student.department_id == d.department_id).count()
            dept_stats.append({
                "name": d.department_name,
                "students": s_count,
                "attendance": 0,
                "status": "Good" if s_count > 0 else "Neutral"
            })

        return {
            "total_students": t_students,
            "total_faculty": t_faculty,
            "total_departments": t_depts,
            "global_attendance": 0,
            "department_stats": dept_stats,
            "recent_assignments": [] 
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))