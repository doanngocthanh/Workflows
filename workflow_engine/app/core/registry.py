# core/registry.py
import importlib
import pkgutil
import inspect
from typing import Dict, List, Type, Optional
from pathlib import Path
from core.schemas import HandlerSchema
from handlers.base import BaseHandler

class HandlerRegistry:
    """Registry để manage và discover handlers"""
    _handlers: Dict[str, Type[BaseHandler]] = {}
    _schemas: Dict[str, HandlerSchema] = {}
    _file_handlers: Dict[str, Type[BaseHandler]] = {}
    
    @classmethod
    def register_handler(cls, handler_class: Type[BaseHandler]):
        """Register a handler class"""
        if not issubclass(handler_class, BaseHandler):
            raise ValueError(f"{handler_class} must inherit from BaseHandler")
        
        schema = handler_class.get_schema()
        cls._handlers[schema.name] = handler_class
        cls._schemas[schema.name] = schema
        
        # Register file handlers
        if hasattr(handler_class, 'get_supported_file_types'):
            for file_type in handler_class.get_supported_file_types():
                cls._file_handlers[file_type.lower()] = handler_class
    
    @classmethod
    def get_handler(cls, name: str) -> Optional[Type[BaseHandler]]:
        """Get handler by name"""
        return cls._handlers.get(name)
    
    @classmethod
    def get_file_handler(cls, file_extension: str) -> Optional[Type[BaseHandler]]:
        """Get handler for file type"""
        return cls._file_handlers.get(file_extension.lower())
    
    @classmethod
    def get_schema(cls, name: str) -> Optional[HandlerSchema]:
        """Get handler schema"""
        return cls._schemas.get(name)
    
    @classmethod
    def list_handlers(cls, category: str = None) -> List[HandlerSchema]:
        """List all registered handlers"""
        schemas = list(cls._schemas.values())
        if category:
            schemas = [s for s in schemas if s.category == category]
        return schemas
    
    @classmethod
    def list_categories(cls) -> List[str]:
        """List all available categories"""
        return list(set(schema.category for schema in cls._schemas.values()))
    
    @classmethod
    def auto_discover_handlers(cls, package_name: str = "handlers"):
        """Auto-discover và register handlers từ package"""
        try:
            package = importlib.import_module(package_name)
            package_path = package.__path__
            
            # Walk through all modules in package
            for _, module_name, is_pkg in pkgutil.walk_packages(package_path, f"{package_name}."):
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find all classes that inherit from BaseHandler
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseHandler) and 
                            obj != BaseHandler and
                            hasattr(obj, '_is_handler')):
                            
                            cls.register_handler(obj)
                            print(f"Registered handler: {obj.get_schema().name}")
                            
                except Exception as e:
                    print(f"Error importing {module_name}: {e}")
                    
        except Exception as e:
            print(f"Error discovering handlers: {e}")