from typing import Dict, Any, List
from tools.base import Tool
from tools.context_manager import ContextManagerTool

class ChatTool(Tool):
    def __init__(self):
        super().__init__(name="chat", description="Answer general questions using AI.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        }

    def execute(self, message: str, conversation_context: List[Dict[str, str]] = None, use_enhanced_context: bool = True) -> str:
        """Use Ollama to answer general questions with enhanced conversation context."""
        
        # Initialize context manager
        context_manager = ContextManagerTool()
        
        # Generate enhanced system prompt if requested
        if use_enhanced_context:
            system_prompt = context_manager.generate_enhanced_system_prompt()
        else:
            # Create a helpful AI assistant prompt
            system_prompt = """You are StudBotty, a friendly AI study companion. Your role is to:
- Explain concepts clearly and concisely
- Answer questions about any subject
- Help students learn and understand topics
- Use examples and analogies when helpful
- Keep responses brief but informative (2-3 paragraphs max)
- Maintain conversation context and refer back to previous topics when relevant

Be encouraging and educational in your responses."""

        user_prompt = message
         
        try:
            import ollama
            from config import config
            
            # Build conversation context
            messages = [
                {'role': 'system', 'content': system_prompt}
            ]
            
            # Add conversation history if provided
            if conversation_context:
                messages.extend(conversation_context)
            
            # Add current user message
            messages.append({'role': 'user', 'content': user_prompt})
            
            response = ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=messages
            )
            
            # Extract important topics from the conversation if enhanced context is enabled
            if use_enhanced_context and message:
                self._extract_and_store_topics(message, context_manager)
            
            return response['message']['content'].strip()
            
        except ImportError:
            return "❌ Ollama is not installed. Please install it to use chat features."
        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    def _extract_and_store_topics(self, message: str, context_manager: ContextManagerTool):
        """Extract potential topics from user message and store important ones."""
        import re
        
        # Common educational/academic keywords that indicate important topics
        topic_indicators = [
            'explain', 'understand', 'learn about', 'study', 'concept of',
            'what is', 'how does', 'why does', 'definition of', 'theory of',
            'principle of', 'process of', 'method of', 'technique of'
        ]
        
        message_lower = message.lower()
        
        # Check if message contains topic indicators
        for indicator in topic_indicators:
            if indicator in message_lower:
                # Extract potential topic after the indicator
                parts = message_lower.split(indicator, 1)
                if len(parts) > 1:
                    potential_topic = parts[1].strip()
                    # Clean up the topic (remove common words, punctuation)
                    potential_topic = re.sub(r'^(the|a|an|to|how|why|what)\s+', '', potential_topic)
                    potential_topic = re.sub(r'[^\w\s]', '', potential_topic).strip()
                    
                    # Only store if it's a meaningful topic (2+ words, not just 'is' etc.)
                    if len(potential_topic.split()) >= 2 and potential_topic not in ['is', 'are', 'do', 'does']:
                        context_manager.execute('add_topic', topic=potential_topic)
                        break
        
        # Also check for explicit study requests
        study_patterns = [
            r'quiz me on (.+)',
            r'test me on (.+)',
            r'flashcards for (.+)',
            r'study (.+)',
            r'review (.+)'
        ]
        
        for pattern in study_patterns:
            match = re.search(pattern, message_lower)
            if match:
                topic = match.group(1).strip()
                if topic:
                    context_manager.execute('add_topic', topic=topic)
                    break
