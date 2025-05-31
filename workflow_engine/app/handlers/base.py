# handlers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import asyncio
from core.schemas import HandlerSchema, ParameterSchema, ActionResult

def handler(name: str, display_name: str = None, description: str = "", 
           category: str = "general", tags: List[str] = None):
    """Decorator để auto-register handlers"""
    def decorator(cls):
        cls._handler_name = name
        cls._display_name = display_name or name.replace('_', ' ').title()
        cls._description = description
        cls._category = category
        cls._tags = tags or []
        cls._is_handler = True
        return cls
    return decorator

def parameter(name: str, param_type: str, description: str = "", 
              required: bool = True, default: Any = None, **kwargs):
    """Decorator để define parameters"""
    def decorator(func):
        if not hasattr(func, '_parameters'):
            func._parameters = []
        
        func._parameters.append(ParameterSchema(
            name=name,
            type=param_type,
            description=description,
            required=required,
            default=default,
            **kwargs
        ))
        return func
    return decorator

def output(name: str, param_type: str, description: str = ""):
    """Decorator để define outputs"""
    def decorator(func):
        if not hasattr(func, '_outputs'):
            func._outputs = []
        
        func._outputs.append(ParameterSchema(
            name=name,
            type=param_type,
            description=description,
            required=False
        ))
        return func
    return decorator

class BaseHandler(ABC):
    """Base class cho tất cả handlers"""
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Execute handler logic"""
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        schema = self.get_schema()
        required_params = [p.name for p in schema.input_schema if p.required]
        
        for param in required_params:
            if param not in params:
                return False
        return True
    
    @classmethod
    def get_schema(cls) -> HandlerSchema:
        """Generate schema từ class definition và decorators"""
        # Get execute method
        execute_method = getattr(cls, 'execute', None)
        if not execute_method:
            raise ValueError(f"Handler {cls.__name__} must have execute method")
        
        # Get parameters từ decorator
        input_params = getattr(execute_method, '_parameters', [])
        output_params = getattr(execute_method, '_outputs', [])
        
        # Get class info từ decorator
        name = getattr(cls, '_handler_name', cls.__name__.lower())
        display_name = getattr(cls, '_display_name', cls.__name__)
        description = getattr(cls, '_description', cls.__doc__ or "")
        category = getattr(cls, '_category', 'general')
        tags = getattr(cls, '_tags', [])
        
        return HandlerSchema(
            name=name,
            display_name=display_name,
            description=description,
            category=category,
            input_schema=input_params,
            output_schema=output_params,
            class_path=f"{cls.__module__}.{cls.__name__}",
            tags=tags
        )

class FileHandler(BaseHandler):
    """Base class cho file handlers"""
    
    @classmethod
    @abstractmethod
    def get_supported_file_types(cls) -> List[str]:
        """Return list of supported file extensions"""
        pass