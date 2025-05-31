# Workflow Engine

A dynamic workflow execution system with auto-discovery of handlers and a visual workflow builder.

## Features

- 🔍 **Auto-Discovery**: Automatically discover and register handlers from codebase
- 🎯 **Type-Safe**: Pydantic schemas for validation and IDE support  
- 🖥️ **Visual Builder**: Drag-and-drop workflow builder interface
- 🔄 **Dynamic Execution**: Execute workflows with context sharing between steps
- 📊 **Monitoring**: Detailed execution tracking and results
- 🛡️ **Secure**: Registry pattern prevents arbitrary code execution
- 🚀 **Extensible**: Easy to add new handlers and action types

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database**:
   ```bash
   python scripts/init_db.py
   python scripts/seed_data.py
   ```

3. **Start the server**:
   ```bash
   python app/main.py
   ```

4. **Open the workflow builder**:
   Navigate to http://localhost:8000

## Architecture

- **`/handlers/`**: Handler implementations organized by domain
- **`/api/`**: REST API endpoints for CRUD operations
- **`/core/`**: Core engine with registry and executor
- **`/client/`**: Web-based workflow builder interface

## Adding Custom Handlers

1. Create a new handler class inheriting from `BaseHandler`
2. Use decorators to define metadata and parameters
3. The system will auto-discover and register your handler

Example:
```python
@handler(name="my_handler", category="custom")
class MyHandler(BaseHandler):
    @parameter("input_text", ParameterType.STRING, "Input text to process")
    @output("result", ParameterType.STRING, "Processed result")
    async def execute(self, params):
        # Your logic here
        return ActionResult(success=True, data={"result": "processed"})
```

## API Endpoints

- `GET /api/handlers/` - List available handlers
- `GET /api/workflows/` - List workflows
- `POST /api/workflows/` - Create workflow
- `POST /api/workflows/{id}/execute` - Execute workflow
- `GET /health` - Health check

## Docker Deployment

```bash
docker-compose up -d
```

## License

MIT License