# api/workflows.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.workflow import Workflow, WorkflowStep
from models.workflow import WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowStepCreate
from core.executor import WorkflowExecutor
from core.registry import HandlerRegistry
import datetime
from models.workflow import WorkflowExecutionCreate
router = APIRouter(prefix="/api/workflows", tags=["workflows"])

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all workflows with optional filtering"""
    query = db.query(Workflow)
    
    if status:
        query = query.filter(Workflow.status == status)
    
    workflows = query.offset(skip).limit(limit).all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get workflow by ID"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """Create new workflow"""
    
    # Validate handlers exist
    for step in workflow.steps:
        if not HandlerRegistry.get_handler(step.handler_name):
            raise HTTPException(
                status_code=400, 
                detail=f"Handler '{step.handler_name}' not found"
            )
    
    # Create workflow
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        version=workflow.version,
        config=workflow.config,
        created_by="current_user"  # TODO: Get from auth
    )
    db.add(db_workflow)
    db.flush()  # Get ID
    
    # Create steps
    for step_data in workflow.steps:
        db_step = WorkflowStep(
            workflow_id=db_workflow.id,
            step_number=step_data.step_number,
            name=step_data.name,
            handler_name=step_data.handler_name,
            parameters=step_data.parameters,
            output_mapping=step_data.output_mapping,
            condition_expression=step_data.condition_expression,
            retry_count=step_data.retry_count,
            retry_delay_seconds=step_data.retry_delay_seconds,
            timeout_seconds=step_data.timeout_seconds,
            stop_on_error=step_data.stop_on_error,
            depends_on=step_data.depends_on
        )
        db.add(db_step)
    
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int, 
    workflow_update: WorkflowUpdate, 
    db: Session = Depends(get_db)
):
    """Update workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update fields
    for field, value in workflow_update.dict(exclude_unset=True).items():
        setattr(workflow, field, value)
    
    workflow.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(workflow)
    return workflow

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Delete workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: int,
    execution_data: WorkflowExecutionCreate,
    db: Session = Depends(get_db)
):
    """Execute workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.status != "active":
        raise HTTPException(status_code=400, detail="Only active workflows can be executed")
    
    # Convert to execution format
    workflow_config = {
        "id": workflow.id,
        "name": workflow.name,
        "steps": [
            {
                "step_number": step.step_number,
                "name": step.name,
                "handler_name": step.handler_name,
                "parameters": step.parameters,
                "output_mapping": step.output_mapping or {},
                "stop_on_error": step.stop_on_error
            }
            for step in workflow.steps
        ]
    }
    
    # Execute workflow
    executor = WorkflowExecutor()
    result = await executor.execute_workflow(workflow_config, execution_data.context_data)
    
    # Save execution record
    from models.workflow import WorkflowExecution
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        status="completed" if result['success'] else "failed",
        context_data=execution_data.context_data,
        results=result,
        completed_at=datetime.utcnow() if result['success'] else None,
        triggered_by="current_user"
    )
    db.add(execution)
    db.commit()
    
    return result