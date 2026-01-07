# StudBotty - AI Study Companion

A powerful, modular, and study-focused AI agent CLI designed to help students learn, understand, and master any subject through interactive tools and intelligent assistance.

## 🚀 Quick Start

### Installation

1. **Install Python 3.10+**
   ```bash
   # Check your Python version
   python --version
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   # or install manually:
   pip install rich ollama sympy python-dotenv requests ddgs colorama
   ```

3. **Install Ollama (Required for AI Features)**
   - Download from [ollama.ai](https://ollama.ai/)
   - Start the Ollama service: `ollama serve`

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run StudBotty**
   ```bash
   python main.py
   ```

## 📋 System Requirements

- **Python**: 3.10 or higher
- **Ollama**: Required for AI features (install from [ollama.ai](https://ollama.ai/))
- **Memory**: 4GB+ RAM recommended
- **Storage**: 100MB+ for dependencies and data files

## 🛠️ Architecture Overview

StudBotty follows a modular, plugin-based architecture with the following key components:

### Core Components

1. **Main Application** ([`main.py`](main.py))
   - CLI interface with rich formatting
   - Voice mode support (text-to-speech)
   - Command routing and user interaction
   - Terminal compatibility for various platforms

2. **Agent System** ([`agent.py`](agent.py))
   - Dynamic tool discovery and registration
   - Intent parsing using AI (Ollama)
   - Conversation history management
   - Enhanced context system

3. **Tool System** ([`tools/`](tools/))
   - Modular, extensible tool architecture
   - Automatic tool discovery from `tools/` directory
   - JSON schema validation for tool inputs
   - Base class for consistent tool implementation

4. **Configuration** ([`config.py`](config.py))
   - Environment variable management
   - Model and service configuration
   - Persistence settings

### Tool Architecture

Each tool follows a consistent pattern:

```python
class ToolName(Tool):
    def __init__(self):
        super().__init__(name="tool_name", description="Tool description")
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        # JSON schema for tool inputs
    
    def execute(self, **kwargs) -> str:
        # Tool implementation
```

## 🧰 Available Tools

### Core Study Tools

#### 🎯 Quiz Tool
Generate interactive quizzes on any topic.
```bash
User: "Quiz me on Python programming"
StudBotty: Generates 5 multiple-choice questions with explanations
```

#### 🧮 Math Tool
Solve mathematical expressions and equations.
```bash
User: "Solve 2x + 5 = 15"
StudBotty: Provides step-by-step solution
```

#### 📊 Visualization Tool
Create diagrams and visualizations using Mermaid.
```bash
User: "Visualize the water cycle"
StudBotty: Generates interactive diagram in browser
```

#### 🔍 Search Tool
Web search capabilities (when online).
```bash
User: "Search quantum computing"
StudBotty: Returns top 5 search results with summaries
```

#### 📁 Files Tool
Read and analyze local files.
```bash
User: "Read notes.txt"
StudBotty: Displays file content with metadata
```

### Learning Enhancement Tools

#### 🗂️ Flashcards Tool
Create and manage study flashcards.
```bash
User: "Create flashcards on biology"
StudBotty: Generates interactive HTML flashcards
```

#### 🧠 Active Recall Tool
Test knowledge using spaced repetition principles.
```bash
User: "Test my knowledge on math"
StudBotty: Provides recall questions with answers
```

#### 📝 Summary Tool
Summarize long texts into concise study notes.
```bash
User: "Summarize this chapter"
StudBotty: Creates structured summary
```

#### 💬 Chat Tool
General Q&A and explanations with enhanced context.
```bash
User: "Explain photosynthesis"
StudBotty: Provides detailed explanation with user context
```

#### 🔊 Text-to-Speech Tool
Convert text to speech for audio learning.
```bash
User: "Speak this text"
StudBotty: Reads text aloud with various voice options
```

### System Tools

#### 💾 Persistence Tool
Save data locally for cross-session continuity.
```bash
# Automatically used by other tools
```

#### 🧠 Context Manager Tool
Manage user profiles, preferences, and learning context.
```bash
:profile set name "John Doe"
:topics
:preferences set explanation_style "detailed"
```

## 🎮 Commands

### Basic Commands
- `:help` - Show onboarding guide and examples
- `:quit` or `:exit` - Exit StudBotty
- `:tools` - List all available tools
- `:profile` - Manage user profile
- `:topics` - Show important topics
- `:preferences` - Set learning preferences

### Voice Mode
- `enable voice mode` - Turn on speech output
- `disable voice mode` - Turn off speech output
- `/voicemode` - Toggle voice mode

### Profile Management
```bash
:profile set name "Your Name"
:profile set study_level "undergraduate"
:profile set subjects "math,science,history"
:profile get name
:profile show
```

### Learning Preferences
```bash
:preferences set explanation_style "detailed with examples"
:preferences set quiz_difficulty "adaptive"
:preferences
```

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# AI Model Configuration
OLLAMA_MODEL=gemma3:1b          # Ollama model to use
OFFLINE_MODE=false              # Enable offline mode

# Anki Integration
ANKI_CONNECT_URL=http://localhost:8765

# Logging and Persistence
LOG_LEVEL=INFO                  # Logging level
PERSISTENCE_FILE=studbotty_data.json

# Terminal Output
STUDBOTTY_SIMPLE=false         # Force simple text output
```

### Model Selection

StudBotty supports any Ollama-compatible model. Recommended models:

- **gemma3:1b** - Fast, lightweight (default)
- **llama3.2:latest** - Balanced performance
- **mistral:latest** - Good for technical content
- **qwen2:latest** - Strong reasoning capabilities

To change models:
1. Install your preferred model: `ollama pull model_name`
2. Update `.env`: `OLLAMA_MODEL=model_name`

## 📚 Usage Examples

### Academic Subjects

**Mathematics:**
```
User: "Solve x² + 5x + 6 = 0"
User: "Explain calculus concepts"
User: "Quiz me on algebra"
```

**Science:**
```
User: "Explain photosynthesis"
User: "Visualize the water cycle"
User: "Create flashcards on biology"
```

**Programming:**
```
User: "Explain Python decorators"
User: "Quiz me on JavaScript"
User: "Search React best practices"
```

**General Learning:**
```
User: "Summarize this article"
User: "Test my knowledge on history"
User: "Read file notes.txt"
```

### Advanced Features

**Context-Aware Learning:**
```
:profile set study_level "graduate"
:profile set subjects "machine learning,statistics"
User: "Explain neural networks"
# AI tailors response to graduate level
```

**Interactive Diagrams:**
```
User: "Visualize machine learning pipeline"
# Opens interactive Mermaid diagram in browser
```

**Audio Learning:**
```
enable voice mode
User: "Explain the concept of gravity"
# AI speaks the explanation
```

## 🏗️ Architecture Details

### Intent Parsing System

StudBotty uses AI-powered intent parsing to route user input to appropriate tools:

1. **Input Analysis**: AI analyzes user input to determine intent
2. **Tool Selection**: Matches intent to available tools
3. **Parameter Extraction**: Extracts tool parameters from natural language
4. **Execution**: Routes to appropriate tool with extracted parameters

### Context Management

The enhanced context system provides:

- **User Profiles**: Name, study level, subjects, preferences
- **Learning History**: Important topics and study progress
- **Adaptive Responses**: AI responses tailored to user context
- **Persistent Storage**: Context saved across sessions

### Tool Discovery

Tools are automatically discovered and registered:

1. **Directory Scan**: Scans `tools/` directory for Python files
2. **Class Detection**: Finds classes inheriting from `Tool`
3. **Registration**: Automatically registers tools with the agent
4. **Schema Validation**: Validates tool input schemas

## 🧪 Testing

### Running Tests

```bash
# Test context system
python test_context_system.py

# Test visualization tool
python test_viz_tool.py
```

### Test Coverage

- ✅ Import functionality
- ✅ Context manager operations
- ✅ Agent tool registration
- ✅ Chat enhancements
- ✅ Tool functionality

## 🚨 Troubleshooting

### Common Issues

**Ollama Not Found:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve
```

**Model Not Available:**
```bash
# List available models
ollama list

# Pull a model
ollama pull gemma3:1b
```

**Permission Errors:**
```bash
# On Linux/Mac, ensure proper permissions
chmod +x main.py
```

**Voice Mode Issues:**
```bash
# Install pyttsx3
pip install pyttsx3

# On Linux, install speech-dispatcher
sudo apt install speech-dispatcher
```

### Debug Mode

Enable debug logging:
```bash
# Set in .env
LOG_LEVEL=DEBUG
```

### Offline Mode

Enable offline mode for limited functionality:
```bash
# Set in .env
OFFLINE_MODE=true
```

## 🔌 Extending StudBotty

### Adding New Tools

1. **Create Tool File** in `tools/` directory:
   ```python
   from tools.base import Tool
   
   class NewTool(Tool):
       def __init__(self):
           super().__init__(name="new_tool", description="Tool description")
       
       @property
       def input_schema(self):
           return {"type": "object", "properties": {...}}
       
       def execute(self, **kwargs):
           return "Tool result"
   ```

2. **Import in `tools/__init__.py`**:
   ```python
   from .new_tool import NewTool
   ```

3. **Restart StudBotty** - Tool will be automatically discovered

### Customizing the Agent

Modify [`agent.py`](agent.py) to:
- Change intent parsing logic
- Add custom tool routing
- Modify conversation history management
- Implement custom context handling

### Configuration Customization

Edit [`config.py`](config.py) to:
- Add new configuration options
- Modify default values
- Implement custom configuration loading

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** - For providing the AI backend
- **Rich** - For beautiful terminal formatting
- **Sympy** - For mathematical computation
- **All contributors** - For making this project possible

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration examples

---

**Happy Learning with StudBotty! 🎓**