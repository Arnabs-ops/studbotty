from typing import Any, Dict, List
from tools.base import Tool

class QuizTool(Tool):
    def __init__(self):
        super().__init__(name="quiz", description="Generate a quiz on a topic.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "level": {"type": "string", "enum": ["easy", "medium", "hard"]},
                "count": {"type": "integer"}
            },
            "required": ["topic"]
        }

    def execute(self, topic: str, level: str = "medium", count: int = 5) -> str:
        prompt = f"Generate {count} {level} multiple-choice questions on '{topic}'. Return ONLY a JSON array with keys: question, options (list), answer (string), rationale."
        
        try:
            import ollama
            from config import config
            
            response = ollama.chat(model=config.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            
            # extract json from content
            import json
            import re
            
            # Try to find JSON block
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                quiz_data = json.loads(json_str)
                return self._format_quiz(quiz_data, topic, level)
            else:
                # Fallback if no JSON found
                return f"❌ Could not parse quiz response. Raw response: {content}"
                
        except ImportError:
            return "❌ Ollama is not installed. Please install it to use quiz features."
        except Exception as e:
            return f"❌ Sorry, I encountered an error generating the quiz: {str(e)}"
    
    def _format_quiz(self, quiz_data: List[Dict[str, Any]], topic: str, level: str) -> str:
        """Format quiz data into a user-friendly string."""
        if not isinstance(quiz_data, list) or not quiz_data:
            return f"❌ No quiz questions could be generated for '{topic}'."
        
        formatted_quiz = [f"🎯 **{topic.title()} Quiz ({level.capitalize()})**\n"]
        
        for i, question_data in enumerate(quiz_data, 1):
            if not isinstance(question_data, dict):
                continue
                
            question = question_data.get('question', 'No question text')
            options = question_data.get('options', [])
            answer = question_data.get('answer', 'No answer')
            rationale = question_data.get('rationale', 'No explanation')
            
            # Format question
            formatted_quiz.append(f"\n**Question {i}:** {question}\n")
            
            # Format options
            if options and isinstance(options, list):
                option_labels = ['A', 'B', 'C', 'D', 'E', 'F']
                for j, option in enumerate(options):
                    if j < len(option_labels):
                        formatted_quiz.append(f"{option_labels[j]}. {option}")
            
            formatted_quiz.append(f"\n**Answer:** {answer}")
            formatted_quiz.append(f"**Explanation:** {rationale}")
            formatted_quiz.append("\n" + "-" * 50)
        
        formatted_quiz.append(f"\n📚 Quiz complete! You got {len(quiz_data)} questions on '{topic}'.")
        
        return "\n".join(formatted_quiz)
