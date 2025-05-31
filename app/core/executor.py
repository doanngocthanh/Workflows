# core/executor.py
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from core.registry import HandlerRegistry
from core.schemas import ActionResult

class WorkflowExecutor:
    """Workflow execution engine"""
    
    def __init__(self):
        self.registry = HandlerRegistry
    
    async def execute_workflow(self, workflow_config: Dict[str, Any], 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a complete workflow"""
        context = context or {}
        results = []
        
        steps = workflow_config.get('steps', [])
        sorted_steps = sorted(steps, key=lambda x: x.get('step_number', 0))
        
        for step in sorted_steps:
            try:
                step_result = await self.execute_step(step, context)
                results.append({
                    'step_number': step.get('step_number'),
                    'step_name': step.get('name'),
                    'success': step_result.success,
                    'data': step_result.data,
                    'error': step_result.error,
                    'execution_time_ms': step_result.execution_time_ms
                })
                
                # Update context with step results
                if step_result.success and step_result.data:
                    output_mapping = step.get('output_mapping', {})
                    for output_key, context_key in output_mapping.items():
                        if output_key in step_result.data:
                            context[context_key] = step_result.data[output_key]
                
                # Stop on error if configured
                if not step_result.success and step.get('stop_on_error', True):
                    break
                    
            except Exception as e:
                results.append({
                    'step_number': step.get('step_number'),
                    'step_name': step.get('name'),
                    'success': False,
                    'error': str(e),
                    'execution_time_ms': 0
                })
                if step.get('stop_on_error', True):
                    break
        
        success = all(r['success'] for r in results)
        return {
            'success': success,
            'results': results,
            'context': context,
            'total_steps': len(results),
            'completed_steps': len([r for r in results if r['success']])
        }
    
    async def execute_step(self, step_config: Dict[str, Any], 
                          context: Dict[str, Any]) -> ActionResult:
        """Execute a single workflow step"""
        start_time = datetime.now()
        
        try:
            # Get handler
            handler_name = step_config.get('handler_name')
            handler_class = self.registry.get_handler(handler_name)
            
            if not handler_class:
                return ActionResult(
                    success=False,
                    error=f"Handler '{handler_name}' not found"
                )
            
            # Create handler instance
            handler = handler_class()
            
            # Prepare parameters
            params = step_config.get('parameters', {})
            enriched_params = self._replace_context_variables(params, context)
            
            # Validate parameters
            if not handler.validate_params(enriched_params):
                return ActionResult(
                    success=False,
                    error="Invalid parameters for handler"
                )
            
            # Execute handler
            result = await handler.execute(enriched_params)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = int(execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return ActionResult(
                success=False,
                error=str(e),
                execution_time_ms=int(execution_time)
            )
    
    def _replace_context_variables(self, params: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Replace {{context.variable}} placeholders"""
        def replace_recursive(obj):
            if isinstance(obj, dict):
                return {k: replace_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_recursive(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('{{context.') and obj.endswith('}}'):
                var_name = obj[10:-2]  # Remove {{context. and }}
                return context.get(var_name, obj)
            return obj
        
        return replace_recursive(params)