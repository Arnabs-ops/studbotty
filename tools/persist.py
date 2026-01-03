from typing import Any, Dict
from tools.base import Tool
from config import config
import json
import os

class PersistTool(Tool):
    def __init__(self):
        super().__init__(name="persist", description="Save data to local storage.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "value": {"type": "any"}
            },
            "required": ["key", "value"]
        }

    def execute(self, key: str, value: Any) -> Dict[str, bool]:
        data = {}
        if os.path.exists(config.PERSISTENCE_FILE):
            try:
                with open(config.PERSISTENCE_FILE, 'r') as f:
                    data = json.load(f)
            except:
                pass
        
        data[key] = value
        
        with open(config.PERSISTENCE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
        return {"ok": True}
