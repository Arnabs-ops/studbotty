from typing import Any, Dict, List
from tools.base import Tool
from config import config
import os

class SummaryTool(Tool):
    def __init__(self):
        super().__init__(
            name="summary", 
            description="Summarize documents or text into concise study notes."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "path": {"type": "string"},
                "style": {"type": "string", "enum": ["bullet", "structured", "concise"], "default": "structured"}
            }
        }

    def execute(self, content: str = None, path: str = None, style: str = "structured") -> str:
        """Summarize text or file content."""
        if path:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                return f"❌ File not found: {path}"
        
        if not content:
            return "❌ No content provided to summarize."

        prompt = f"Summarize the following content into {style} study notes. Focus on key concepts and definitions:\n\n{content[:4000]}"
        
        try:
            import ollama
            response = ollama.chat(model=config.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
            return f"📝 **Study Summary**\n\n{response['message']['content']}"
        except Exception as e:
            return f"❌ Error in summary tool: {str(e)}"
