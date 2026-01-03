from typing import Dict, Any
from tools.base import Tool
import sympy

class MathTool(Tool):
    def __init__(self):
        super().__init__(name="math", description="Solve a math expression step-by-step.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            },
            "required": ["expression"]
        }

    def execute(self, expression: str) -> str:
        try:
            from sympy import sympify, latex, solve, integrate, diff
            # Simple heuristic to determine operation
            expr = sympify(expression)
            
            result = expr
            
            # Return a user-friendly response
            response = f"The answer is: {result}"
            
            # Add LaTeX formatting if useful
            latex_form = latex(result)
            if latex_form != str(result):
                response += f"\n\nMathematical notation: {latex_form}"
            
            return response
            
        except Exception as e:
            return f"❌ Sorry, I couldn't solve that. Error: {str(e)}"
