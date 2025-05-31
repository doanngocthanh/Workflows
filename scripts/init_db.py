# scripts/init_db.py
"""Database initialization script"""
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.database import Base , DATABASE_URL
from app.models.workflow import Workflow, WorkflowStep, WorkflowExecution

def init_database():
    """Initialize database with tables"""
    print("Initializing database...")
    
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print(f"📍 Database location: {DATABASE_URL}")

if __name__ == "__main__":
    init_database()