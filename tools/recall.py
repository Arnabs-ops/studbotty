from typing import Any, Dict, List
import json
import re
from tools.base import Tool
from config import config

class RecallTool(Tool):
    def __init__(self):
        super().__init__(
            name="recall", 
            description="Active recall tool to test knowledge on a topic using flashcards."
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "count": {"type": "integer", "default": 3}
            },
            "required": ["topic"]
        }

    def execute(self, topic: str, count: int = 3) -> str:
        """Generate active recall questions (flashcards) for a topic."""
        prompt = f"Generate {count} active recall questions for the topic: '{topic}'. For each question, provide a 'front' (the question) and a 'back' (the answer/explanation). Return ONLY a JSON array of objects with 'front' and 'back' keys."
        
        try:
            import ollama
            response = ollama.chat(model=config.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            
            # Extract JSON
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                cards = json.loads(match.group(0))
                return self._format_recall_session(cards, topic)
            else:
                return f"❌ Could not generate recall questions. Raw response: {content}"
                
        except Exception as e:
            return f"❌ Error in recall tool: {str(e)}"

    def _format_recall_session(self, cards: List[Dict[str, str]], topic: str) -> str:
        output = [f"🧠 **Active Recall: {topic.title()}**\n"]
        output.append("Try to answer these questions in your head before looking at the answer!\n")
        
        for i, card in enumerate(cards, 1):
            output.append(f"**Q{i}:** {card.get('front')}")
            output.append(f"**Answer:** ||{card.get('back')}||") # Using spoiler-like syntax if terminal supports or just text
            output.append("-" * 30)
            
        output.append("\n💡 *Tip: Spaced repetition works best! Revisit these later.*")
        return "\n".join(output)
