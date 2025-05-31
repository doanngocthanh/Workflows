# handlers/data/database_handler.py
import asyncio
from typing import Dict, Any
from handlers.base import BaseHandler, handler, parameter, output
from core.schemas import ActionResult, ParameterType
@handler(
    name="database_query",
    display_name="Database Query",
    description="Execute SQL queries on connected databases",
    category="data",
    tags=["sql", "database", "query", "data"]
)
class DatabaseHandler(BaseHandler):
    
    @parameter("query", ParameterType.STRING, "SQL query to execute")
    @parameter("database", ParameterType.STRING, "Database connection name", 
              choices=["primary", "analytics", "reporting"], default="primary")
    @parameter("timeout", ParameterType.INTEGER, "Query timeout in seconds", 
              required=False, default=30, min_value=1, max_value=300)
    @parameter("read_only", ParameterType.BOOLEAN, "Restrict to read-only operations", 
              default=True, required=False)
    @output("rows", ParameterType.ARRAY, "Query result rows")
    @output("row_count", ParameterType.INTEGER, "Number of rows returned")
    @output("execution_time", ParameterType.FLOAT, "Query execution time in seconds")
    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        try:
            query = params['query']
            database = params.get('database', 'primary')
            read_only = params.get('read_only', True)
            
            # Validate read-only constraint
            if read_only and any(keyword in query.upper() for keyword in ['INSERT', 'UPDATE', 'DELETE', 'DROP']):
                return ActionResult(success=False, error="Write operations not allowed in read-only mode")
            
            await asyncio.sleep(0.5)  # Simulate query execution
            
            # Mock result
            result_data = {
                "rows": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
                ],
                "row_count": 2,
                "execution_time": 0.125,
                "database": database
            }
            
            return ActionResult(success=True, data=result_data)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))