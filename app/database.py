import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# CRITICAL FIX: SQLAlchemy 1.4+ requires "postgresql://" instead of "postgres://"
# Neon often provides URLs starting with "postgres://", so we must convert it on the fly.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# FIX 2: Prevent crashes by handling SQLite vs PostgreSQL connection arguments safely
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# IMPORTANT: This creates the Base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()