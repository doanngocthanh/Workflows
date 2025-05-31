# core/schemas.py
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import inspect

class ParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FILE_PATH = "file_path"
    EMAIL = "email"
    URL = "url"

class ParameterSchema(BaseModel):
    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Any = None
    choices: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    example: Any = None

class HandlerSchema(BaseModel):
    name: str
    display_name: str
    description: str
    category: str
    input_schema: List[ParameterSchema]
    output_schema: List[ParameterSchema]
    class_path: str
    method_name: str = "execute"
    supported_file_types: Optional[List[str]] = None
    tags: List[str] = []
    version: str = "1.0.0"

class ActionResult(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None