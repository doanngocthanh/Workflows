# scripts/seed_data.py
"""Seed sample data for testing"""
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.workflow import Workflow, WorkflowStep

def seed_sample_workflows():
    """Create sample workflows for testing"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Sample workflow 1: Image Processing Pipeline
        workflow1 = Workflow(
            name="Image Processing Pipeline",
            description="Process uploaded images with resize and analysis",
            version="1.0.0",
            status="active",
            created_by="system"
        )
        db.add(workflow1)
        db.flush()
        
        steps1 = [
            WorkflowStep(
                workflow_id=workflow1.id,
                step_number=1,
                name="Resize Image",
                handler_name="process_image",
                parameters={
                    "file_path": "{{context.input_file}}",
                    "operation": "resize",
                    "width": 800,
                    "height": 600,
                    "quality": 85
                },
                output_mapping={
                    "processed_file": "resized_image"
                }
            ),
            WorkflowStep(
                workflow_id=workflow1.id,
                step_number=2,
                name="Analyze Image",
                handler_name="analyze_text",  # Using text analysis as example
                parameters={
                    "text": "Sample image analysis text",
                    "analysis_type": "all"
                },
                output_mapping={
                    "keywords": "image_keywords"
                }
            )
        ]
        
        for step in steps1:
            db.add(step)
        
        # Sample workflow 2: Data Processing Pipeline
        workflow2 = Workflow(
            name="Data Processing Pipeline",
            description="Query database and send email notification",
            version="1.0.0",
            status="active",
            created_by="system"
        )
        db.add(workflow2)
        db.flush()
        
        steps2 = [
            WorkflowStep(
                workflow_id=workflow2.id,
                step_number=1,
                name="Query Database",
                handler_name="database_query",
                parameters={
                    "query": "SELECT * FROM users WHERE active = true",
                    "database": "primary",
                    "timeout": 30
                },
                output_mapping={
                    "rows": "user_data",
                    "row_count": "user_count"
                }
            ),
            WorkflowStep(
                workflow_id=workflow2.id,
                step_number=2,
                name="Send Report Email",
                handler_name="send_email",
                parameters={
                    "to": "admin@example.com",
                    "subject": "Daily User Report",
                    "body": "Found {{context.user_count}} active users"
                },
                output_mapping={
                    "message_id": "email_id"
                }
            )
        ]
        
        for step in steps2:
            db.add(step)
        
        db.commit()
        
        print("✅ Sample workflows created:")
        print(f"   📋 {workflow1.name} (ID: {workflow1.id})")
        print(f"   📋 {workflow2.name} (ID: {workflow2.id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_workflows()