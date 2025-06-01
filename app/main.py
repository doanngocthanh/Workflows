# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import sys
from api.workflows import router as workflows_router
from core.registry import HandlerRegistry
from database import engine, Base
from pathlib import Path
# Import routers
# sys.path.append(str(Path(__file__).parent.parent / "api"))
# Add the parent directory to sys.path to allow importing from 'api'
# from app.api.handlers import router as handlers_router
# from app.api.executions import router as executions_router
# Import core components
# Import all models so they are registered with SQLAlchemy's Base before table creation
# Ensure this imports all model classes (e.g., from models import *)
# from workflows import router as workflows_router

app = FastAPI(
    title="Workflow Engine API",
    description="Dynamic workflow execution system with auto-discovery",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(workflows_router)
# app.include_router(handlers_router)
# app.include_router(executions_router)

# Serve static files
static_path = Path(__file__).parent.parent / "client"
# app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/")
async def serve_client():
    """Serve the client application"""
    return FileResponse(str(static_path / "index.html"))

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Workflow Engine...")
    
    # Create database tables
    print("📊 Creating database tables...")
    try:
        # Ensure all models are imported before this line
        # Set the schema to "workflows" before creating tables
        # with engine.connect() as connection:
        #     connection.execute('CREATE SCHEMA IF NOT EXISTS workflows')
        # Base.metadata.schema = "workflows"
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
    
    # Auto-discover and register handlers
    print("🔍 Discovering handlers...")
    HandlerRegistry.auto_discover_handlers("handlers")
    
    registered_count = len(HandlerRegistry._handlers)
    categories = HandlerRegistry.list_categories()
    
    print(f"✅ Registered {registered_count} handlers in {len(categories)} categories:")
    for category in categories:
        handlers_in_category = len([h for h in HandlerRegistry.list_handlers() if h.category == category])
        print(f"   📦 {category}: {handlers_in_category} handlers")
    
    print("🎉 Workflow Engine is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down Workflow Engine...")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "handlers_registered": len(HandlerRegistry._handlers),
        "categories": HandlerRegistry.list_categories()
    }

# Debug endpoint to inspect handlers
@app.get("/debug/handlers")
async def debug_handlers():
    """Debug endpoint to inspect registered handlers"""
    return {
        "total_handlers": len(HandlerRegistry._handlers),
        "file_handlers": len(HandlerRegistry._file_handlers),
        "handlers": {name: schema.dict() for name, schema in HandlerRegistry._schemas.items()},
        "categories": HandlerRegistry.list_categories()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
