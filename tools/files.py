from typing import Any, Dict
from tools.base import Tool
import os

class FilesTool(Tool):
    def __init__(self):
        super().__init__(name="files", description="Read a file.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }

    def execute(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {"error": "File not found"}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "content": content,
            "meta": {"ext": os.path.splitext(path)[1], "size": os.path.getsize(path)}
        }
