# models/workflow.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey

from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base 
class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), default="1.0.0")
    status = Column(String(20), default="draft")  # draft, active, archived
    config = Column(JSON)  # Additional workflow configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow")

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    handler_name = Column(String(255), nullable=False)
    parameters = Column(JSON, nullable=False)
    output_mapping = Column(JSON)  # Map handler outputs to context variables
    condition_expression = Column(Text)  # Conditional execution
    retry_count = Column(Integer, default=0)
    retry_delay_seconds = Column(Integer, default=5)
    timeout_seconds = Column(Integer, default=300)
    stop_on_error = Column(Boolean, default=True)
    depends_on = Column(JSON)  # Array of step numbers
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    context_data = Column(JSON)
    results = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    triggered_by = Column(String(100))
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")

# API Schemas
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class WorkflowStepCreate(BaseModel):
    step_number: int
    name: str
    handler_name: str
    parameters: Dict[str, Any]
    output_mapping: Optional[Dict[str, str]] = None
    condition_expression: Optional[str] = None
    retry_count: Optional[int] = 0
    retry_delay_seconds: Optional[int] = 5
    timeout_seconds: Optional[int] = 300
    stop_on_error: Optional[bool] = True
    depends_on: Optional[List[int]] = None

class WorkflowStepUpdate(BaseModel):
    name: Optional[str] = None
    handler_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    output_mapping: Optional[Dict[str, str]] = None
    condition_expression: Optional[str] = None
    retry_count: Optional[int] = None
    retry_delay_seconds: Optional[int] = None
    timeout_seconds: Optional[int] = None
    stop_on_error: Optional[bool] = None
    depends_on: Optional[List[int]] = None

class WorkflowStepResponse(BaseModel):
    id: int
    step_number: int
    name: str
    handler_name: str
    parameters: Dict[str, Any]
    output_mapping: Optional[Dict[str, str]]
    condition_expression: Optional[str]
    retry_count: int
    retry_delay_seconds: int
    timeout_seconds: int
    stop_on_error: bool
    depends_on: Optional[List[int]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = "1.0.0"
    config: Optional[Dict[str, Any]] = None
    steps: List[WorkflowStepCreate] = []

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    version: str
    status: str
    config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    steps: List[WorkflowStepResponse] = []
    
    class Config:
        from_attributes = True

class WorkflowExecutionCreate(BaseModel):
    context_data: Optional[Dict[str, Any]] = None

class WorkflowExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    status: str
    context_data: Optional[Dict[str, Any]]
    results: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    triggered_by: Optional[str]
    
    class Config:
        from_attributes = True