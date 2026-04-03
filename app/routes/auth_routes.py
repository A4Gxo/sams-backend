from fastapi import APIRouter, Depends, HTTPException, status
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
    
    print(f"--- NEW LOGIN ATTEMPT: '{credentials.email}' ---") # <--- ADD THIS
    
    # 1. Look up user by username
    db_user = db.query(models.User).filter(
        models.User.username == credentials.email
    ).first()

    # --- ADD THIS ENTIRE DIAGNOSTIC BLOCK ---
    if not db_user:
        print("DIAGNOSTIC: User literally not found in the database.")
    else:
        print(f"DIAGNOSTIC: Found user! Their role is '{db_user.role}'")
        print(f"DIAGNOSTIC: The exact DB password is: '{db_user.password_hash}'")
        print(f"DIAGNOSTIC: The typed password is: '{credentials.password}'")
    # ----------------------------------------

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    # ... (rest of your code stays the same) ...

    # 2. Check Password (With Smart On-The-Fly Migration)
    # Check if the database has an unhashed, plain-text password (hashes start with '$')
    if not db_user.password_hash.startswith("$"):
        # If it's plain text, check if it matches what the user typed exactly
        if credentials.password == db_user.password_hash:
            # It matches! Now, instantly upgrade it to a secure hash for the future
            db_user.password_hash = hash_password(credentials.password) 
            db.commit() # Save the fixed hash to the database!
            db.refresh(db_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )
    else:
        # The normal, secure verification for users who already have hashed passwords
        if not verify_password(credentials.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )

    # --- 🚨 THE CRITICAL GATEKEEPER FIX 🚨 ---
    # This blocks Guest/External users until you click 'Approve' in the dashboard
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

    # 4. Fetch Specific Profile IDs (Includes External Roles)
    student_id_val = None
    faculty_id_val = None
    full_name = "User"

    # Handle both Internal and External Students
    if db_user.role in ["student", "external_student"]:
        student_profile = db.query(models.Student).filter(models.Student.user_id == db_user.user_id).first()
        if student_profile:
            student_id_val = student_profile.student_id
            full_name = f"{student_profile.first_name} {student_profile.last_name}"
            
    # Handle both Internal and External Faculty
    elif db_user.role in ["faculty", "external_faculty"]:
        faculty_profile = db.query(models.Faculty).filter(models.Faculty.user_id == db_user.user_id).first()
        if faculty_profile:
            faculty_id_val = faculty_profile.faculty_id
            full_name = f"{faculty_profile.first_name} {faculty_profile.last_name}"

    # 5. Return everything React needs!
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
    
    # 1. Check for existing user
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="This email is already registered"
        )

    try:
        # 2. Create the Base User
        new_user = User(
            username=user.username,
            # ✨ FIXED: New users will now be securely hashed immediately!
            password_hash=hash_password(user.password), 
            role=user.role.lower(),
            is_approved=False,
            institution=getattr(user, 'institution', None) 
        )

        db.add(new_user)
        
        # FLUSH sends the data to the DB to generate the new_user.user_id, 
        # but DOES NOT save it permanently yet.
        db.flush() 

        # 3. Create Specific Profiles based on Role
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
            # TODO: Create your ExternalStudent profile here if needed
            pass 
            
        elif role == "faculty":
            # TODO: Create your Faculty profile here if needed
            pass

        # 4. Commit EVERYTHING together
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
        # This looks for the sams_data.sql file in your main backend folder
        # You may need to adjust the "../" depending on exactly where you put the file!
        file_path = os.path.join(os.path.dirname(__file__), "C:\Users\Gyanaranjan Moharana\OneDrive\Documents\sams_data.sql")
        
        with open(file_path, 'r') as file:
            sql_script = file.read()
            
        # Tell the live Render server to execute it inside Neon
        db.execute(text(sql_script))
        db.commit()
        
        return {"message": "DATA SUCCESSFULLY INJECTED FROM THE CLOUD! THE FIREWALL IS BYPASSED."}
        
    except Exception as e:
        db.rollback()
        return {"error": str(e), "hint": "Check if sams_data.sql is in the correct folder!"}