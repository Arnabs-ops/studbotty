import logging
import json
import os
from typing import Dict, Any, List, Optional
from tools.base import Tool
from config import config

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.conversation_history: List[Dict[str, str]] = []
        self.discover_and_register_tools()

    def discover_and_register_tools(self):
        """Dynamically discover and register tools from the tools directory."""
        tools_dir = os.path.join(os.path.dirname(__file__), "tools")
        for filename in os.listdir(tools_dir):
            if filename.endswith(".py") and filename not in ["__init__.py", "base.py", "persist.py"]:
                module_name = f"tools.{filename[:-3]}"
                try:
                    module = __import__(module_name, fromlist=["*"])
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Tool) and 
                            attr is not Tool):
                            tool_instance = attr()
                            self.register_tool(tool_instance)
                except Exception as e:
                    logger.error(f"Failed to load tool from {module_name}: {e}")

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def _get_tools_specification(self) -> str:
        """Generate a string representation of available tools and their schemas."""
        specs = []
        for name, tool in self.tools.items():
            spec = {
                "name": name,
                "description": tool.description,
                "parameters": tool.input_schema
            }
            specs.append(spec)
        return json.dumps(specs, indent=2)

    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse the user input using LLM to determine the intent and arguments.
        """
        try:
            import ollama
            
            tools_spec = self._get_tools_specification()
            enhanced_context = self.get_enhanced_chat_context()
            
            system_prompt = f"""You are a tool router for StudBotty. Your job is to analyze the user's input and decide which tool to call and with what arguments.

AVAILABLE TOOLS:
{tools_spec}

USER CONTEXT:
{json.dumps(enhanced_context.get('enhanced_context', {}), indent=2)}

RESPONSE FORMAT:
Return ONLY a JSON object with the following structure:
{{
  "intent": "tool_name",
  "args": {{ ... }}
}}

If no specific tool matches, use "chat" with the "message" argument.
If the user wants to see a diagram or visualize something, ALWAYS use the "viz" tool.
If the user wants a quiz, use the "quiz" tool.
"""
            
            response = ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input}
                ],
                format='json'
            )
            
            intent_data = json.loads(response['message']['content'])
            return intent_data
            
        except Exception as e:
            logger.error(f"Error parsing intent: {e}")
            # Fallback to chat if LLM parsing fails
            return {"intent": "chat", "args": {"message": user_input}}

    def route_and_execute(self, intent_data: Dict[str, Any]) -> Any:
        """Route the intent to the appropriate tool or logic."""
        intent = intent_data.get("intent")
        args = intent_data.get("args", {})
        
        logger.info(f"Routing intent: {intent} with args: {args}")

        try:
            if intent in self.tools:
                # For chat interactions, pass enhanced context
                if intent == "chat":
                    enhanced_context = self.get_enhanced_chat_context()
                    chat_args = {
                        **args,
                        'conversation_context': enhanced_context.get('conversation_history', []),
                        'use_enhanced_context': True
                    }
                    result = self.tools[intent].execute(**chat_args)
                    self._add_to_conversation_history(args.get("message", ""), result)
                else:
                    result = self.tools[intent].execute(**args)
                
                return result
            else:
                return f"Error: Tool '{intent}' not found."
        except Exception as e:
            logger.error(f"Error executing intent {intent}: {e}")
            return f"Error: {str(e)}"
    
    def _add_to_conversation_history(self, user_message: str, bot_response: str):
        """Add user and bot messages to conversation history."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": bot_response
        })
        
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]
    
    def get_conversation_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context."""
        return self.conversation_history[-max_messages:] if self.conversation_history else []
    
    def get_enhanced_chat_context(self, max_messages: int = 10) -> Dict[str, Any]:
        """Get enhanced context including conversation history and context manager data."""
        context_manager = self.tools.get('context_manager')
        
        return {
            'conversation_history': self.get_conversation_context(max_messages),
            'enhanced_context': context_manager.execute('get_enhanced_context') if context_manager else None
        }
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
