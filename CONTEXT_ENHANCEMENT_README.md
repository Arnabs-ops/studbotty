# Enhanced Context Management System for StudBotty

## Overview

The StudBotty AI study companion has been enhanced with a comprehensive context management system that allows for persistent user information, adaptive AI responses, and intelligent conversation tracking.

## New Features

### 1. ContextManagerTool
A new tool that manages persistent user context across sessions:

**Capabilities:**
- User profile management (name, study level, subjects, etc.)
- Learning preferences storage
- Important topics tracking
- Session summaries
- Enhanced system prompt generation

**Commands:**
- `:profile set key value` - Set user profile information
- `:profile get key` - Get specific profile field
- `:profile show` - Display all profile data
- `:topics` - Show important topics being studied
- `:preferences` - View or set learning preferences

### 2. Enhanced Chat System
The chat tool now includes:
- **Dynamic System Prompts**: AI responses adapt based on user context
- **Topic Extraction**: Automatically identifies and stores important study topics
- **Context-Aware Responses**: AI considers user profile and preferences

### 3. Intelligent Context Management
- **Persistent Storage**: User context saved across sessions using JSON storage
- **Smart Topic Detection**: Automatically extracts study topics from conversations
- **Adaptive Responses**: AI tailors responses based on user's study level and preferences

## Usage Examples

### Setting Up User Profile
```
:profile set name "John Doe"
:profile set study_level "undergraduate"
:profile set subjects "mathematics,physics,computer science"
```

### Managing Topics
```
:topics
# Shows automatically detected important topics
```

### Learning Preferences
```
:preferences set explanation_style "detailed with examples"
:preferences set quiz_difficulty "adaptive"
:preferences
# Shows all preferences
```

### Natural Conversation
```
User: "Explain quantum mechanics"
AI: [Provides explanation tailored to user's study level and preferences]
[Automatically adds "quantum mechanics" to important topics]
```

## Technical Implementation

### Files Modified/Created:
1. **`tools/context_manager.py`** - New context management tool
2. **`tools/chat.py`** - Enhanced with dynamic prompts and topic extraction
3. **`agent.py`** - Added ContextManagerTool registration and enhanced context methods
4. **`main.py`** - Added command handling for profile/topics/preferences
5. **`tools/__init__.py`** - Added ContextManagerTool export

### Key Methods:
- `ContextManagerTool.execute()` - Main interface for context operations
- `ChatTool.execute()` - Enhanced with `use_enhanced_context` parameter
- `Agent.get_enhanced_chat_context()` - Provides comprehensive context data
- `generate_enhanced_system_prompt()` - Creates adaptive AI prompts

### Data Storage:
- User context stored in `studbotty_data.json` (configurable via `.env`)
- Persistent across application restarts
- Includes timestamps for context versioning

## Benefits

1. **Personalized Experience**: AI responses adapt to individual user needs
2. **Learning Continuity**: Important topics and preferences persist across sessions
3. **Automatic Topic Tracking**: System learns what users are studying
4. **Enhanced Accuracy**: Context-aware responses are more relevant and helpful
5. **User Control**: Full transparency and control over stored context

## Configuration

The system uses existing configuration from `config.py`:
- `PERSISTENCE_FILE` - Location of user context storage
- All other settings remain unchanged

## Backward Compatibility

The enhanced context system is fully backward compatible:
- Existing chat functionality works unchanged
- New features are opt-in via commands
- Legacy conversation history still supported
- No breaking changes to existing APIs

## Testing

Run the test suite to verify the enhanced context system:
```bash
python test_context_system.py
```

All tests should pass, confirming:
- Import functionality
- Context manager operations
- Agent tool registration
- Chat enhancements

## Future Enhancements

Potential future improvements:
- Context import/export functionality
- Advanced topic clustering and relationship mapping
- Learning progress tracking
- Collaborative context sharing
- Advanced preference learning algorithms