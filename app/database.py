# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./workflow_engine.db")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://puser:pPassword@localhost:5432/workflows")
# For PostgreSQL: "postgresql://user:password@localhost/dbname"
# For MySQL: "mysql://user:password@localhost/dbname"
print(f"Using database URL: {DATABASE_URL}")
engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create all tables in the database
#Base.metadata.create_all(bind=engine)

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()