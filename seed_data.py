from app.database import SessionLocal, engine, Base
from app.models.user import User, Department
from app.models.profiles import Student, Faculty, Course
from app.models.attendance import Enrollment
from app.utils.auth import hash_password

# Ensure tables exist
Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed():
    try:
        # 1. Get or Create Department
        dept = db.query(Department).filter_by(department_name="Computer Science").first()
        if not dept:
            dept = Department(department_name="Computer Science")
            db.add(dept)
            db.commit()
            db.refresh(dept)
            print("Added Department: Computer Science")
        else:
            print("Department 'Computer Science' already exists.")

        # 2. Get or Create Faculty
        f_user = db.query(User).filter_by(username="teacher@sams.com").first()
        if not f_user:
            f_user = User(username="teacher@sams.com", password_hash=hash_password("password123"), role="faculty")
            db.add(f_user)
            db.commit()
            db.refresh(f_user)
            
            faculty = Faculty(user_id=f_user.user_id, first_name="Alan", last_name="Turing", department_id=dept.department_id)
            db.add(faculty)
            print("Added Faculty: Alan Turing")
        else:
            print("Faculty user already exists.")

        # 3. Get or Create Student
        s_user = db.query(User).filter_by(username="student@sams.com").first()
        if not s_user:
            s_user = User(username="student@sams.com", password_hash=hash_password("password123"), role="student")
            db.add(s_user)
            db.commit()
            db.refresh(s_user)

            student = Student(user_id=s_user.user_id, roll_no="CS101", first_name="Gyan", last_name="Moharana", year_of_study=3, department_id=dept.department_id)
            db.add(student)
            print("Added Student: Gyan Moharana")
        else:
            print("Student user already exists.")

        # 4. Get or Create Course
        course = db.query(Course).filter_by(course_code="CS402").first()
        if not course:
            faculty = db.query(Faculty).first() # Just grab the first faculty for the test
            course = Course(course_code="CS402", course_name="Operating Systems", faculty_id=faculty.faculty_id, department_id=dept.department_id)
            db.add(course)
            db.commit()
            print("Added Course: CS402")
        else:
            print("Course 'CS402' already exists.")

        db.commit()
        print("\n✅ Seed Process Complete!")
        print("Log in with: student@sams.com / password123")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()