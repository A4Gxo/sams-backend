from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User 
from app.schemas.user import UserCreate, UserResponse, UserLogin 
from app.models.profiles import Student 
from app.utils.auth import verify_password, create_access_token, hash_password 
from app import models
import os 

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    
    # Clean the email input to prevent hidden spaces
    clean_email = credentials.email.strip().lower()
    print(f"--- NEW LOGIN ATTEMPT: '{clean_email}' ---") 
    
    # 1. Look up user by cleaned username
    db_user = db.query(models.User).filter(
        models.User.username == clean_email
    ).first()

    # --- DIAGNOSTIC BLOCK ---
    if not db_user:
        print("DIAGNOSTIC: User literally not found in the database.")
    else:
        print(f"DIAGNOSTIC: Found user! Their role is '{db_user.role}'")
        print(f"DIAGNOSTIC: The exact DB password is: '{db_user.password_hash}'")
        print(f"DIAGNOSTIC: The typed password is: '{credentials.password}'")
    # ------------------------

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    # 2. Check Password (With Smart On-The-Fly Migration)
    if not db_user.password_hash.startswith("$"):
        if credentials.password == db_user.password_hash:
            db_user.password_hash = hash_password(credentials.password) 
            db.commit() 
            db.refresh(db_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )
    else:
        if not verify_password(credentials.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )

    # 🚨 THE CRITICAL GATEKEEPER FIX 🚨
    if not db_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your account is pending Admin approval. Please check back later."
        )

    # 3. Generate the JWT
    token = create_access_token({
        "sub": db_user.username,
        "role": db_user.role,
        "user_id": db_user.user_id
    })

    # 4. Fetch Specific Profile IDs
    student_id_val = None
    faculty_id_val = None
    full_name = "User"

    if db_user.role in ["student", "external_student"]:
        student_profile = db.query(models.Student).filter(models.Student.user_id == db_user.user_id).first()
        if student_profile:
            student_id_val = student_profile.student_id
            full_name = f"{student_profile.first_name} {student_profile.last_name}"
            
    elif db_user.role in ["faculty", "external_faculty"]:
        faculty_profile = db.query(models.Faculty).filter(models.Faculty.user_id == db_user.user_id).first()
        if faculty_profile:
            faculty_id_val = faculty_profile.faculty_id
            full_name = f"{faculty_profile.first_name} {faculty_profile.last_name}"

    # 5. Return everything React needs
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role,
        "user_id": db_user.user_id,
        "student_id": student_id_val,
        "faculty_id": faculty_id_val,
        "full_name": full_name
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This email is already registered"
        )

    try:
        new_user = User(
            username=user.username,
            password_hash=hash_password(user.password), 
            role=user.role.lower(),
            is_approved=False,
            institution=getattr(user, 'institution', None) 
        )

        db.add(new_user)
        db.flush() 

        role = new_user.role
        
        if role == "student":
            new_student = Student(
                user_id=new_user.user_id,
                roll_no=user.roll_no or f"TEMP-{new_user.user_id}",
                first_name=getattr(user, 'first_name', 'New'),
                last_name=getattr(user, 'last_name', 'Student'),
                department_id=getattr(user, 'department_id', 1),
                year_of_study=getattr(user, 'year_of_study', 1)
            )
            db.add(new_student)
            
        elif role == "external_student":
            pass 
            
        elif role == "faculty":
            pass

        db.commit() 
        db.refresh(new_user)

        return new_user

    except Exception as e:
        db.rollback() 
        print(f"Registration Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/inject-data")
def inject_database_data(db: Session = Depends(get_db)):
    try:
        # ✨ FIXED: This uses a Relative Path that works on Render! 
        # It goes up two folders (from routes -> app -> backend root) to find the file.
        file_path = os.path.join(os.path.dirname(__file__), r"C:\Users\Gyanaranjan Moharana\sams\backend\sams_data.sql")
        
        # Safety Check: Did the file actually make it to Render?
        if not os.path.exists(file_path):
            return {"error": "File not found!", "looked_in": file_path, "hint": "Did you drag sams_data.sql into VS Code and push it to GitHub?"}
        
        with open(file_path, 'r') as file:
            sql_script = file.read()
            
        # Tell the live Render server to execute it inside Neon
        db.execute(text(sql_script))
        db.commit()
        
        return {"message": "DATA SUCCESSFULLY INJECTED FROM THE CLOUD! THE FIREWALL IS BYPASSED."}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e), "hint": "Database execution failed."}