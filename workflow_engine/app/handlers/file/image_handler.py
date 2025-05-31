# handlers/file/image_handler.py
from typing import Dict, Any, List
from handlers.base import BaseHandler, FileHandler, handler, parameter, output
from core.schemas import ActionResult, ParameterType
import asyncio

@handler(
    name="process_image",
    display_name="Image Processor", 
    description="Process images with various operations like resize, convert, compress",
    category="file",
    tags=["image", "processing", "resize", "convert"]
)
class ImageHandler(FileHandler):
    
    @classmethod
    def get_supported_file_types(cls) -> List[str]:
        return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    @parameter("file_path", ParameterType.FILE_PATH, "Path to the image file", example="/uploads/image.jpg")
    @parameter("operation", ParameterType.STRING, "Operation to perform", choices=["resize", "convert", "compress", "rotate"], default="resize")
    @parameter("width", ParameterType.INTEGER, "Target width in pixels", required=False, default=800, min_value=1, max_value=5000)
    @parameter("height", ParameterType.INTEGER, "Target height in pixels", required=False, default=600, min_value=1, max_value=5000)
    @parameter("quality", ParameterType.INTEGER, "JPEG quality (1-100)", required=False, default=85, min_value=1, max_value=100)
    @parameter("format", ParameterType.STRING, "Output format", required=False, choices=["JPEG", "PNG", "WEBP"], default="JPEG")
    @output("processed_file", ParameterType.FILE_PATH, "Path to processed image")
    @output("original_size", ParameterType.OBJECT, "Original image dimensions")
    @output("new_size", ParameterType.OBJECT, "New image dimensions")
    @output("file_size_bytes", ParameterType.INTEGER, "File size in bytes")
    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        try:
            file_path = params['file_path']
            operation = params.get('operation', 'resize')
            
            # Simulate processing
            await asyncio.sleep(0.1)  # Simulate work
            
            if operation == "resize":
                result_data = {
                    "processed_file": f"/processed/{file_path.split('/')[-1]}",
                    "original_size": {"width": 1920, "height": 1080},
                    "new_size": {"width": params.get('width', 800), "height": params.get('height', 600)},
                    "file_size_bytes": 256000
                }
            elif operation == "convert":
                new_format = params.get('format', 'JPEG').lower()
                base_name = file_path.split('/')[-1].rsplit('.', 1)[0]
                result_data = {
                    "processed_file": f"/processed/{base_name}.{new_format}",
                    "original_size": {"width": 1920, "height": 1080},
                    "new_size": {"width": 1920, "height": 1080},
                    "file_size_bytes": 512000
                }
            else:
                result_data = {"processed_file": file_path, "message": f"Applied {operation} operation"}
            
            return ActionResult(success=True, data=result_data)
            
        except Exception as e:
            return ActionResult(success=False, error=str(e))
