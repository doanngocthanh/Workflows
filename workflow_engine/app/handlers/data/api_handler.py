# api/handlers.py
from fastapi import APIRouter
from typing import List, Optional
from core.registry import HandlerRegistry
from core.schemas import HandlerSchema
from fastapi import HTTPException
router = APIRouter(prefix="/api/handlers", tags=["handlers"])

@router.get("/", response_model=List[HandlerSchema])
async def list_handlers(category: Optional[str] = None):
    """List all available handlers"""
    return HandlerRegistry.list_handlers(category=category)

@router.get("/categories")
async def list_categories():
    """List all handler categories"""
    return {"categories": HandlerRegistry.list_categories()}

@router.get("/{handler_name}", response_model=HandlerSchema)
async def get_handler_schema(handler_name: str):
    """Get detailed schema for a specific handler"""
    schema = HandlerRegistry.get_schema(handler_name)
    if not schema:
        raise HTTPException(status_code=404, detail="Handler not found") 
    return schema

@router.get("/{handler_name}/validate")
async def validate_handler_params(handler_name: str, params: dict):
    """Validate parameters for a handler"""
    handler_class = HandlerRegistry.get_handler(handler_name)
    if not handler_class:
        raise HTTPException(status_code=404, detail="Handler not found")
    
    handler = handler_class()
    is_valid = handler.validate_params(params)
    
    return {
        "valid": is_valid,
        "handler_name": handler_name,
        "params": params
    }

@router.post("/discover")
async def discover_handlers():
    """Rediscover and register handlers from codebase"""
    try:
        HandlerRegistry.auto_discover_handlers()
        return {
            "message": "Handler discovery completed",
            "total_handlers": len(HandlerRegistry._handlers),
            "categories": HandlerRegistry.list_categories()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")