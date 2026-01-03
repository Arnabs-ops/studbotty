import logging
from typing import Dict, Any, List
from tools.base import Tool
from tools import QuizTool, MathTool, VizTool, SearchTool, FilesTool, AnkiTool, PersistTool, ChatTool, TTSTool, ContextManagerTool

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.conversation_history: List[Dict[str, str]] = []
        self.register_tools()

    def register_tools(self):
        self.register_tool(QuizTool())
        self.register_tool(MathTool())
        self.register_tool(VizTool())
        self.register_tool(SearchTool())
        self.register_tool(FilesTool())
        self.register_tool(AnkiTool())
        self.register_tool(PersistTool())
        self.register_tool(ChatTool())
        self.register_tool(TTSTool())
        self.register_tool(ContextManagerTool())

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse the user input to determine the intent and arguments.
        For now, we will use a simple rule-based approach or LLM call.
        """
        user_input_lower = user_input.lower().strip()
        
        # Check for specific tool keywords first
        if any(keyword in user_input_lower for keyword in ["quiz", "start quiz", "take quiz", "quiz me", "make a quiz", "create quiz", "generate quiz"]):
            # Extract topic from various quiz patterns
            topic = ""
            
            # Handle "make a quiz on [topic]" and "create quiz about [topic]" patterns
            if "on " in user_input_lower:
                topic = user_input.split("on ", 1)[1].strip()
            elif "about " in user_input_lower:
                topic = user_input.split("about ", 1)[1].strip()
            elif "make a quiz" in user_input_lower or "create quiz" in user_input_lower or "generate quiz" in user_input_lower:
                # For "make a quiz [topic]" pattern, extract after the command
                for prefix in ["make a quiz ", "create quiz ", "generate quiz "]:
                    if user_input_lower.startswith(prefix.lower()):
                        topic = user_input[len(prefix):].strip()
                        break
            else:
                # Handle simple patterns like "quiz me on [topic]", "take quiz [topic]", etc.
                if "quiz me" in user_input_lower:
                    if "on " in user_input_lower:
                        topic = user_input.split("on ", 1)[1].strip()
                    else:
                        topic = user_input_lower.replace("quiz me", "").strip()
                elif "take quiz" in user_input_lower:
                    if "on " in user_input_lower:
                        topic = user_input.split("on ", 1)[1].strip()
                    else:
                        topic = user_input_lower.replace("take quiz", "").strip()
                elif "start quiz" in user_input_lower:
                    topic = user_input_lower.replace("start quiz", "").strip()
                else:
                    # Fallback to simple keyword removal
                    topic = user_input_lower.replace("quiz", "").replace("start", "").replace("take", "").replace("me", "").replace("make a", "").replace("create", "").replace("generate", "").strip()
            
            return {"intent": "quiz", "args": {"topic": topic, "level": "medium", "count": 5}}
        elif any(keyword in user_input_lower for keyword in ["flashcards", "flashcard", "anki", "study cards"]):
            # Handle flashcards with improved natural language parsing
            
            # Check for list commands first
            if any(cmd in user_input_lower for cmd in ["list", "show", "display"]):
                return {"intent": "flashcards", "args": {"action": "list", "deck": None}}
            
            # Extract topic and action from various patterns
            topic = ""
            action = "generate"  # Default action
            
            # Handle "create flashcards for [topic]" pattern
            if " for " in f" {user_input_lower} ":
                topic = user_input.split(" for ", 1)[1].strip()
            elif " about " in f" {user_input_lower} ":
                topic = user_input.split(" about ", 1)[1].strip()
            elif " on " in f" {user_input_lower} ":
                topic = user_input.split(" on ", 1)[1].strip()
            elif any(prefix in user_input_lower for prefix in ["create ", "make ", "generate "]):
                # Handle "create flashcards [topic]" pattern
                for prefix in ["create ", "make ", "generate "]:
                    if user_input_lower.startswith(prefix.lower()):
                        remaining = user_input[len(prefix):].strip()
                        # Remove flashcards/flashcard/anki/study cards/cards from remaining text
                        topic = remaining.replace("flashcards", "").replace("flashcard", "").replace("anki", "").replace("study cards", "").replace("cards", "").strip()
                        break
            else:
                # Fallback: extract topic by removing command words
                topic = user_input_lower.replace("flashcards", "").replace("flashcard", "").replace("anki", "").replace("study cards", "").replace("cards", "").replace("create", "").replace("make", "").replace("generate", "").strip()
            
            return {"intent": "flashcards", "args": {"action": action, "topic": topic}}
        elif any(keyword in user_input_lower for keyword in ["solve", "calculate", "compute", "math"]):
            expression = user_input_lower.replace("solve", "").replace("calculate", "").replace("compute", "").replace("math", "").strip()
            return {"intent": "math", "args": {"expression": expression}}
        elif any(keyword in user_input_lower for keyword in ["search", "look up", "find", "google"]):
            query = user_input_lower.replace("search", "").replace("look up", "").replace("find", "").replace("google", "").strip()
            return {"intent": "search", "args": {"query": query}}
        elif any(keyword in user_input_lower for keyword in ["read", "open", "view", "show file"]):
            path = user_input_lower.replace("read", "").replace("open", "").replace("view", "").replace("show file", "").strip()
            return {"intent": "files", "args": {"path": path}}
        elif any(keyword in user_input_lower for keyword in ["flashcards", "flashcard", "anki", "study cards"]):
            # Handle flashcards with improved natural language parsing
            
            # Check for list commands first
            if any(cmd in user_input_lower for cmd in ["list", "show", "display"]):
                return {"intent": "flashcards", "args": {"action": "list", "deck": None}}
            
            # Extract topic and action from various patterns
            topic = ""
            action = "generate"  # Default action
            
            # Handle "create flashcards for [topic]" pattern
            if "for " in user_input_lower:
                topic = user_input.split("for ", 1)[1].strip()
            elif "about " in user_input_lower:
                topic = user_input.split("about ", 1)[1].strip()
            elif "on " in user_input_lower:
                topic = user_input.split("on ", 1)[1].strip()
            elif any(prefix in user_input_lower for prefix in ["create ", "make ", "generate "]):
                # Handle "create flashcards [topic]" pattern
                for prefix in ["create ", "make ", "generate "]:
                    if user_input_lower.startswith(prefix.lower()):
                        topic = user_input[len(prefix):].strip()
                        # Remove flashcards/flashcard/anki/study cards from topic
                        topic = topic.replace("flashcards", "").replace("flashcard", "").replace("anki", "").replace("study cards", "").strip()
                        break
            else:
                # Fallback: extract topic by removing command words
                topic = user_input_lower.replace("flashcards", "").replace("flashcard", "").replace("anki", "").replace("study cards", "").replace("create", "").replace("make", "").replace("generate", "").strip()
            
            return {"intent": "flashcards", "args": {"action": action, "topic": topic}}
        
        # Check for visualization keywords (before generic question patterns)
        elif any(keyword in user_input_lower for keyword in ["visualize", "visualization", "diagram", "draw", "chart", "graph", "flowchart", "show me", "make a diagram", "make a chart", "make a graph", "make a flowchart", "viz", "viz tool", "create diagram", "create chart", "create graph", "create flowchart"]):
            # Extract the content after visualization keywords
            content = user_input
            for keyword in ["visualize ", "visualization of ", "visualization ", "make a visualization of ", "make a diagram of ", "make a diagram ", "diagram of ", "draw ", "chart of ", "graph of ", "flowchart of ", "show me ", "make a chart ", "make a graph ", "make a flowchart ", "viz ", "viz tool ", "create diagram ", "create chart ", "create graph ", "create flowchart "]:
                if keyword in user_input_lower:
                    idx = user_input_lower.find(keyword)
                    content = user_input[idx + len(keyword):].strip()
                    break
            return {"intent": "viz", "args": {"content": content, "kind": "mermaid"}}
        
        # Check for TTS commands
        elif any(keyword in user_input_lower for keyword in ["speak", "say", "tts", "read aloud", "text to speech", "voice"]):
            # Extract text after command
            text = user_input
            for prefix in ["speak ", "say ", "tts ", "read aloud ", "text to speech ", "voice "]:
                if user_input_lower.startswith(prefix.lower()):
                    text = user_input[len(prefix):].strip()
                    break
            return {"intent": "tts", "args": {"text": text, "provider": "local"}}
        
        # Check for explanation/question patterns
        elif user_input_lower.startswith(("explain", "what is", "what are", "who is", "who are", "how does", "how do", "why")):
            # Route explanation/question queries to chat tool
            return {"intent": "chat", "args": {"message": user_input}}
        
        # Default to chat for everything else
        else:
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
        
        # Limit conversation history to prevent memory issues
        # Keep last 20 exchanges (40 messages total)
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]
    
    def get_conversation_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context for maintaining continuity."""
        # Return most recent messages, up to max_messages
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
