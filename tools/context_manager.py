from typing import Any, Dict, List, Optional
from tools.base import Tool
from tools.persist import PersistTool
import json
import os
from datetime import datetime

class ContextManagerTool(Tool):
    def __init__(self):
        super().__init__(name="context_manager", description="Manage enhanced AI context including user preferences, topics, and persistent memory.")
        self.persist_tool = PersistTool()
        self.context_keys = {
            'user_profile': 'user_profile',
            'learning_preferences': 'learning_preferences', 
            'important_topics': 'important_topics',
            'session_summary': 'session_summary',
            'conversation_topics': 'conversation_topics'
        }

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["set_profile", "get_profile", "add_topic", "get_topics", 
                            "set_preference", "get_preferences", "summarize_session", 
                            "get_enhanced_context", "clear_topics"]
                },
                "key": {"type": "string"},
                "value": {"type": "any"},
                "topic": {"type": "string"},
                "context_length": {"type": "integer", "default": 10}
            },
            "required": ["action"]
        }

    def execute(self, action: str, key: str = None, value: Any = None, 
                topic: str = None, context_length: int = 10) -> Any:
        """Execute context management actions."""
        
        if action == "set_profile":
            return self._set_user_profile(key, value)
        elif action == "get_profile":
            return self._get_user_profile(key)
        elif action == "add_topic":
            return self._add_important_topic(topic)
        elif action == "get_topics":
            return self._get_important_topics()
        elif action == "set_preference":
            return self._set_learning_preference(key, value)
        elif action == "get_preferences":
            return self._get_learning_preferences()
        elif action == "summarize_session":
            return self._summarize_session()
        elif action == "get_enhanced_context":
            return self._get_enhanced_context(context_length)
        elif action == "clear_topics":
            return self._clear_topics()
        else:
            return {"error": f"Unknown action: {action}"}

    def _set_user_profile(self, key: str, value: Any) -> Dict[str, bool]:
        """Set user profile information."""
        profile = self._get_data(self.context_keys['user_profile']) or {}
        profile[key] = value
        profile['updated_at'] = datetime.now().isoformat()
        return self.persist_tool.execute(self.context_keys['user_profile'], profile)

    def _get_user_profile(self, key: str = None) -> Dict[str, Any]:
        """Get user profile information."""
        profile = self._get_data(self.context_keys['user_profile']) or {}
        if key:
            return profile.get(key, None)
        return profile

    def _add_important_topic(self, topic: str) -> Dict[str, bool]:
        """Add an important topic to the user's learning list."""
        if not topic:
            return {"error": "Topic cannot be empty"}
            
        topics = self._get_data(self.context_keys['important_topics']) or []
        if topic.lower() not in [t.lower() for t in topics]:
            topics.append(topic)
            topics = topics[-20:]  # Keep last 20 topics
        return self.persist_tool.execute(self.context_keys['important_topics'], topics)

    def _get_important_topics(self) -> List[str]:
        """Get user's important topics."""
        return self._get_data(self.context_keys['important_topics']) or []

    def _set_learning_preference(self, key: str, value: Any) -> Dict[str, bool]:
        """Set learning preferences."""
        preferences = self._get_data(self.context_keys['learning_preferences']) or {}
        preferences[key] = value
        preferences['updated_at'] = datetime.now().isoformat()
        return self.persist_tool.execute(self.context_keys['learning_preferences'], preferences)

    def _get_learning_preferences(self) -> Dict[str, Any]:
        """Get learning preferences."""
        return self._get_data(self.context_keys['learning_preferences']) or {}

    def _summarize_session(self) -> str:
        """Create a session summary based on conversation history."""
        # This would typically be called with conversation data
        # For now, return a placeholder
        summary = f"Session summary created at {datetime.now().isoformat()}"
        self.persist_tool.execute(self.context_keys['session_summary'], summary)
        return summary

    def _get_enhanced_context(self, context_length: int = 10) -> Dict[str, Any]:
        """Get enhanced context including profile, preferences, and topics."""
        return {
            'user_profile': self._get_user_profile(),
            'learning_preferences': self._get_learning_preferences(),
            'important_topics': self._get_important_topics(),
            'session_summary': self._get_data(self.context_keys['session_summary']),
            'available_at': datetime.now().isoformat()
        }

    def _clear_topics(self) -> Dict[str, bool]:
        """Clear all important topics."""
        return self.persist_tool.execute(self.context_keys['important_topics'], [])

    def _get_data(self, key: str) -> Any:
        """Helper method to get data from persistence."""
        try:
            # Read directly from the persistence file
            if os.path.exists("studbotty_data.json"):
                with open("studbotty_data.json", 'r') as f:
                    data = json.load(f)
                    return data.get(key)
        except Exception:
            pass
        return None

    def generate_enhanced_system_prompt(self, base_prompt: str = None) -> str:
        """Generate an enhanced system prompt with user context."""
        if not base_prompt:
            base_prompt = """You are StudBotty, a friendly AI study companion. Your role is to:
- Explain concepts clearly and concisely
- Answer questions about any subject
- Help students learn and understand topics
- Use examples and analogies when helpful
- Keep responses brief but informative (2-3 paragraphs max)
- Maintain conversation context and refer back to previous topics when relevant

Be encouraging and educational in your responses."""

        enhanced_context = self._get_enhanced_context()
        additional_context = []

        # Add user profile context
        profile = enhanced_context.get('user_profile', {})
        if profile:
            additional_context.append("User Profile Context:")
            if 'name' in profile:
                additional_context.append(f"- User's name: {profile['name']}")
            if 'study_level' in profile:
                additional_context.append(f"- Study level: {profile['study_level']}")
            if 'subjects' in profile:
                additional_context.append(f"- Main subjects: {', '.join(profile['subjects'])}")

        # Add learning preferences
        preferences = enhanced_context.get('learning_preferences', {})
        if preferences:
            additional_context.append("Learning Preferences:")
            for key, value in preferences.items():
                if key != 'updated_at':
                    additional_context.append(f"- {key}: {value}")

        # Add important topics
        topics = enhanced_context.get('important_topics', [])
        if topics:
            additional_context.append("Important Topics for this user:")
            additional_context.append(f"- {', '.join(topics[-5:])}")  # Show last 5 topics

        if additional_context:
            enhanced_prompt = base_prompt + "\n\n" + "\n".join(additional_context)
            return enhanced_prompt
        
        return base_prompt